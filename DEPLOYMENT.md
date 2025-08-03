# 🚀 Guía de Deployment - CompilandoCode

Esta guía te ayudará a desplegar tu aplicación Flask de cursos en Digital Ocean.

## 📋 Requisitos Previos

- Droplet en Digital Ocean (Ubuntu 22.04 LTS recomendado)
- Dominio configurado apuntando a tu servidor
- Acceso SSH al servidor

## 🛠️ Opción 1: Deployment Manual

### 1. Preparar el Servidor

```bash
# Conectar al servidor
ssh root@tu-servidor-ip

# Actualizar sistema
apt update && apt upgrade -y

# Instalar Git
apt install -y git
```

### 2. Clonar el Proyecto

```bash
# Ir al directorio web
cd /var/www

# Clonar tu repositorio
git clone https://github.com/tu-usuario/tu-repositorio.git compilandocode
cd compilandocode
```

### 3. Ejecutar Script de Deployment

```bash
# Hacer el script ejecutable
chmod +x deploy.sh

# Ejecutar deployment
sudo bash deploy.sh
```

### 4. Configurar Variables de Entorno

```bash
# Editar archivo de configuración
nano /var/www/compilandocode/.env
```

Actualizar los siguientes valores:
```env
SECRET_KEY=tu-clave-secreta-muy-segura
DATABASE_URL=postgresql://compilandocode:tu_password@localhost/compilandocode_prod
MAIL_SERVER=smtp.sendgrid.net
MAIL_PASSWORD=tu-api-key-de-email
DOMAIN=https://tu-dominio.com
```

### 5. Configurar SSL

```bash
# Obtener certificado SSL gratuito
certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

### 6. Verificar Deployment

```bash
# Verificar estado de la aplicación
supervisorctl status

# Ver logs
tail -f /var/log/gunicorn/compilandocode.log

# Verificar Nginx
nginx -t
systemctl status nginx
```

## 🐳 Opción 2: Deployment con Docker

### 1. Instalar Docker

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
apt install -y docker-compose
```

### 2. Configurar Variables de Entorno

```bash
# Copiar archivo de configuración
cp .env.production .env

# Editar configuración
nano .env
```

### 3. Desplegar con Docker Compose

```bash
# Construir y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f web
```

## 🔧 Configuración Post-Deployment

### Crear Usuario Administrador

```bash
# Activar entorno virtual
source /var/www/compilandocode/venv/bin/activate

# Ejecutar shell de Flask
flask shell

# En el shell de Python:
from models import Usuario, db
admin = Usuario(
    nombre='Admin',
    correo='admin@tu-dominio.com',
    rol='admin'
)
admin.set_password('tu-password-seguro')
db.session.add(admin)
db.session.commit()
exit()
```

### Configurar Pagos (Opcional)

Si planeas usar pagos con Stripe:

1. Registrarse en [Stripe](https://stripe.com)
2. Obtener claves API
3. Actualizar `.env`:
```env
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
```

### Configurar Email

Para notificaciones por email, configura un servicio SMTP:

**Con SendGrid:**
1. Registrarse en [SendGrid](https://sendgrid.com)
2. Crear API Key
3. Actualizar `.env`:
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=tu-api-key
```

## 📊 Monitoreo y Mantenimiento

### Logs Importantes

```bash
# Logs de la aplicación
tail -f /var/log/gunicorn/compilandocode.log

# Logs de Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Logs del sistema
journalctl -u nginx -f
```

### Backup de Base de Datos

```bash
# Crear backup
pg_dump -U compilandocode compilandocode_prod > backup_$(date +%Y%m%d).sql

# Restaurar backup
psql -U compilandocode compilandocode_prod < backup_20231201.sql
```

### Actualizar la Aplicación

```bash
cd /var/www/compilandocode

# Hacer backup
tar -czf ../backup-$(date +%Y%m%d).tar.gz .

# Actualizar código
git pull origin main

# Actualizar dependencias
source venv/bin/activate
pip install -r requirements.txt

# Ejecutar migraciones
flask db upgrade

# Reiniciar aplicación
supervisorctl restart compilandocode
```

## 🔒 Seguridad

### Firewall

```bash
# Configurar UFW
ufw allow 'Nginx Full'
ufw allow 'OpenSSH'
ufw enable
```

### Actualizaciones Automáticas

```bash
# Instalar actualizaciones automáticas
apt install -y unattended-upgrades

# Configurar
dpkg-reconfigure unattended-upgrades
```

### Backup Automatizado

```bash
# Crear script de backup
cat > /root/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U compilandocode compilandocode_prod > /var/backups/db_$DATE.sql
tar -czf /var/backups/app_$DATE.tar.gz -C /var/www compilandocode
find /var/backups -name "*.sql" -mtime +7 -delete
find /var/backups -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x /root/backup.sh

# Programar en crontab
echo "0 2 * * * /root/backup.sh" | crontab -
```

## 🆘 Troubleshooting

### La aplicación no arranca

```bash
# Verificar logs
supervisorctl status
tail -f /var/log/gunicorn/error.log

# Verificar configuración
source /var/www/compilandocode/venv/bin/activate
cd /var/www/compilandocode
python wsgi.py
```

### Error de base de datos

```bash
# Verificar conexión a PostgreSQL
sudo -u postgres psql -l

# Verificar usuario y permisos
sudo -u postgres psql -c "\du"
```

### Error de permisos

```bash
# Corregir permisos
chown -R www-data:www-data /var/www/compilandocode
chmod -R 755 /var/www/compilandocode
```

### SSL no funciona

```bash
# Renovar certificado
certbot renew

# Verificar configuración de Nginx
nginx -t
```

## 📞 Soporte

Si encuentras problemas durante el deployment:

1. Revisa los logs detalladamente
2. Verifica que todas las variables de entorno estén configuradas
3. Asegúrate de que los puertos estén abiertos
4. Verifica que el dominio esté apuntando correctamente

## 🎉 ¡Listo!

Tu aplicación de cursos debería estar funcionando en:
- **Frontend**: https://tu-dominio.com
- **Admin Panel**: https://tu-dominio.com/admin

¡Felicidades por completar el deployment! 🚀