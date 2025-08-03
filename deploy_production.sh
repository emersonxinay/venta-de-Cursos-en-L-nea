#!/bin/bash

# ================================
# SCRIPT DE DESPLIEGUE A PRODUCCIÓN
# ================================

set -e  # Salir si hay errores

echo "🚀 Iniciando despliegue a producción..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "app.py" ]; then
    log_error "No se encontró app.py. Ejecuta este script desde el directorio del proyecto."
    exit 1
fi

# 1. Verificar configuración
log_info "Verificando configuración..."
if [ -f ".env" ]; then
    log_success "Archivo .env encontrado"
else
    log_warning "Archivo .env no encontrado"
    echo "Copia .env.production.example a .env y configúralo:"
    echo "cp .env.production.example .env"
    exit 1
fi

# 2. Verificar dependencias
log_info "Verificando dependencias..."
if python3 check_config.py; then
    log_success "Configuración validada"
else
    log_error "Problemas en la configuración. Revisa los errores arriba."
    exit 1
fi

# 3. Instalar dependencias
log_info "Instalando dependencias..."
pip install -r requirements.txt

# 4. Ejecutar migraciones
log_info "Ejecutando migraciones de base de datos..."
export FLASK_APP=app.py
flask db upgrade

# 5. Optimizar archivos estáticos
if [ -f "optimize_static.py" ]; then
    log_info "Optimizando archivos estáticos..."
    python3 optimize_static.py
fi

# 6. Crear directorio de uploads
log_info "Creando directorios necesarios..."
mkdir -p static/uploads
chmod 755 static/uploads

# 7. Recopilar información del sistema
log_info "Información del sistema:"
echo "- Python: $(python3 --version)"
echo "- Pip: $(pip --version)"
echo "- Flask: $(python3 -c "import flask; print(flask.__version__)")"
echo "- PostgreSQL: $(python3 -c "import psycopg2; print(psycopg2.__version__)")"

# 8. Verificación final
log_info "Verificación final..."
python3 -c "
import app
from flask import Flask
print('✅ Aplicación importada correctamente')
print(f'✅ Base de datos: {app.app.config[\"SQLALCHEMY_DATABASE_URI\"][:20]}...')
print(f'✅ Debug mode: {app.app.debug}')
print(f'✅ Environment: {app.app.config.get(\"ENV\", \"not set\")}')
"

echo ""
log_success "¡Despliegue completado!"
echo ""
echo "🔧 Comandos para ejecutar en producción:"
echo ""
echo "# Modo desarrollo (para pruebas):"
echo "python3 app.py"
echo ""
echo "# Modo producción con Gunicorn:"
echo "gunicorn --bind 0.0.0.0:5000 --workers 3 app:app"
echo ""
echo "# Con configuración avanzada:"
echo "gunicorn --config gunicorn.conf.py app:app"
echo ""
echo "📋 Siguientes pasos:"
echo "1. Subir archivos al servidor"
echo "2. Configurar nginx como proxy reverso"
echo "3. Configurar SSL con certbot"
echo "4. Configurar monitoreo y logs"

# Opcional: crear un archivo de información del despliegue
cat > deployment_info.txt << EOF
Deployment Info
===============
Date: $(date)
Python Version: $(python3 --version)
Flask App: app.py
Database: PostgreSQL
Environment: Production

Files deployed:
- app.py (main application)
- requirements.txt
- templates/
- static/
- .env (configuration)

Next steps:
1. Configure nginx
2. Setup SSL
3. Configure monitoring
EOF

log_success "Información del despliegue guardada en deployment_info.txt"