#!/bin/bash

# Script de Deployment para Digital Ocean
# Ejecutar como: bash deploy.sh

set -e  # Exit on any error

echo "🚀 Iniciando deployment de CompilandoCode..."

# Variables
APP_DIR="/var/www/compilandocode"
BACKUP_DIR="/var/backups/compilandocode"
USER="www-data"
VENV_DIR="$APP_DIR/venv"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# Verificar que se ejecute como root
if [[ $EUID -ne 0 ]]; then
   error "Este script debe ejecutarse como root (usar sudo)"
fi

# Crear backup de la aplicación actual
log "Creando backup..."
mkdir -p $BACKUP_DIR
if [ -d "$APP_DIR" ]; then
    tar -czf "$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).tar.gz" -C "$APP_DIR" .
    log "Backup creado en $BACKUP_DIR"
fi

# Crear directorio de la aplicación
log "Preparando directorio de aplicación..."
mkdir -p $APP_DIR
mkdir -p $APP_DIR/logs
mkdir -p $APP_DIR/uploads
mkdir -p /var/log/gunicorn

# Actualizar sistema
log "Actualizando sistema..."
apt update && apt upgrade -y

# Instalar dependencias del sistema
log "Instalando dependencias del sistema..."
apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib supervisor certbot python3-certbot-nginx

# Crear usuario de la aplicación si no existe
if ! id "$USER" &>/dev/null; then
    log "Creando usuario $USER..."
    adduser --system --group --home $APP_DIR $USER
fi

# Configurar PostgreSQL
log "Configurando base de datos..."
sudo -u postgres psql -c "CREATE DATABASE compilandocode_prod;" 2>/dev/null || warn "La base de datos ya existe"
sudo -u postgres psql -c "CREATE USER compilandocode WITH ENCRYPTED PASSWORD 'secure_password_change_this';" 2>/dev/null || warn "El usuario ya existe"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE compilandocode_prod TO compilandocode;" 2>/dev/null || warn "Permisos ya otorgados"

# Configurar entorno virtual Python
log "Configurando entorno virtual Python..."
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# Instalar dependencias Python
log "Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Configurar variables de entorno
log "Configurando variables de entorno..."
if [ ! -f "$APP_DIR/.env" ]; then
    cp .env.production $APP_DIR/.env
    warn "Archivo .env creado. DEBES EDITARLO con los valores correctos"
fi

# Configurar permisos
log "Configurando permisos..."
chown -R $USER:$USER $APP_DIR
chmod -R 755 $APP_DIR
chmod -R 755 $APP_DIR/static
chmod -R 755 $APP_DIR/uploads

# Ejecutar migraciones de base de datos
log "Ejecutando migraciones de base de datos..."
sudo -u $USER $VENV_DIR/bin/flask db upgrade

# Configurar Nginx
log "Configurando Nginx..."
cp nginx.conf /etc/nginx/sites-available/compilandocode
ln -sf /etc/nginx/sites-available/compilandocode /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# Configurar Supervisor para Gunicorn
log "Configurando Supervisor..."
cat > /etc/supervisor/conf.d/compilandocode.conf << EOF
[program:compilandocode]
command=$VENV_DIR/bin/gunicorn --config gunicorn.conf.py wsgi:app
directory=$APP_DIR
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gunicorn/compilandocode.log
environment=PATH="$VENV_DIR/bin"
EOF

# Recargar Supervisor
supervisorctl reread
supervisorctl update
supervisorctl start compilandocode

# Configurar SSL con Let's Encrypt
log "Configurando SSL..."
warn "Para configurar SSL, ejecuta: certbot --nginx -d tu-dominio.com -d www.tu-dominio.com"

# Configurar firewall
log "Configurando firewall..."
ufw allow 'Nginx Full'
ufw allow 'OpenSSH'
ufw --force enable

# Configurar logrotate
log "Configurando rotación de logs..."
cat > /etc/logrotate.d/compilandocode << EOF
/var/log/gunicorn/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
    postrotate
        supervisorctl restart compilandocode
    endscript
}
EOF

# Configurar monitoreo básico
log "Configurando monitoreo..."
# Crear script de health check
cat > $APP_DIR/health_check.sh << EOF
#!/bin/bash
curl -f http://localhost:8000/health || exit 1
EOF
chmod +x $APP_DIR/health_check.sh

# Configurar crontab para health checks
(crontab -l 2>/dev/null; echo "*/5 * * * * $APP_DIR/health_check.sh") | crontab -

log "✅ Deployment completado!"
echo ""
echo "📋 Tareas pendientes:"
echo "1. Editar $APP_DIR/.env con los valores correctos"
echo "2. Configurar SSL: certbot --nginx -d tu-dominio.com"
echo "3. Configurar DNS para apuntar a este servidor"
echo "4. Verificar que la aplicación esté corriendo: supervisorctl status"
echo "5. Verificar logs: tail -f /var/log/gunicorn/compilandocode.log"
echo ""
echo "🌐 La aplicación estará disponible en: https://tu-dominio.com"
echo "📊 Panel de admin: https://tu-dominio.com/admin"