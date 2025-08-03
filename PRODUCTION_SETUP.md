# 🚀 Guía de Configuración para Producción

## ⚠️ Problemas Resueltos

Tu `app.py` ahora está configurado para producción con:

- ✅ **Manejo seguro de variables de entorno**
- ✅ **Configuración automática de base de datos**
- ✅ **Configuración de seguridad para producción**
- ✅ **Manejo robusto de servicios de pago**

## 📋 Pasos para Configurar en Digital Ocean

### 1. **Preparar Variables de Entorno**

Crea un archivo `.env` con esta configuración mínima:

```bash
# Copia el archivo de ejemplo
cp .env.production.example .env

# Edita con tus valores reales
nano .env
```

**Variables CRÍTICAS que debes configurar:**

```bash
# Entorno
FLASK_ENV=production
FLASK_DEBUG=False

# Base de datos (obten estos datos de Digital Ocean)
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/db_venta_cursos

# Seguridad (GENERA UNA NUEVA CLAVE)
SECRET_KEY=tu_clave_secreta_muy_larga_y_aleatoria
```

### 2. **Generar Clave Secreta Segura**

```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
```

### 3. **Configurar Base de Datos en Digital Ocean**

1. Ve a Digital Ocean → Databases
2. Crea una base de datos PostgreSQL
3. Nombra la base de datos: `db_venta_cursos`
4. Copia la cadena de conexión completa
5. Pégala en `DATABASE_URL` en tu `.env`

### 4. **Verificar Configuración**

```bash
# Instalar dependencia para verificación
pip install psycopg2-binary

# Ejecutar verificador
python3 check_config.py
```

### 5. **Ejecutar Migraciones**

```bash
export FLASK_APP=app.py
flask db upgrade
```

## 🔧 Comandos para Digital Ocean

### Opción 1: App Platform (Recomendado)

1. **Conecta tu repositorio GitHub**
2. **Configura variables de entorno en el panel**:
   - `FLASK_ENV=production`
   - `DATABASE_URL=tu_url_completa`
   - `SECRET_KEY=tu_clave_generada`

3. **Comando de construcción**: `pip install -r requirements.txt`
4. **Comando de ejecución**: `gunicorn --bind 0.0.0.0:$PORT app:app`

### Opción 2: Droplet Manual

```bash
# 1. Instalar dependencias del sistema
sudo apt update
sudo apt install python3 python3-pip postgresql-client nginx

# 2. Clonar tu proyecto
git clone tu-repositorio.git
cd tu-proyecto

# 3. Instalar dependencias Python
pip3 install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.production.example .env
nano .env  # Editar con valores reales

# 5. Verificar configuración
python3 check_config.py

# 6. Ejecutar migraciones
FLASK_APP=app.py flask db upgrade

# 7. Ejecutar con Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 3 app:app
```

## 🚨 Lista de Verificación Pre-Despliegue

Ejecuta este checklist antes de desplegar:

```bash
# ✅ 1. Verificar configuración
python3 check_config.py

# ✅ 2. Probar localmente en modo producción
FLASK_ENV=production python3 app.py

# ✅ 3. Verificar que la base de datos esté accesible
# ✅ 4. Confirmar que SECRET_KEY esté configurado
# ✅ 5. Verificar que FLASK_DEBUG=False
```

## 🔒 Configuración de Seguridad

El `app.py` actualizado incluye estas mejoras de seguridad:

```python
# Configuración automática para producción
if os.getenv('FLASK_ENV') == 'production':
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
```

## 🗃️ Configuración de Base de Datos

### Estructura Requerida

Tu base de datos debe tener estas tablas:
- `usuario` - Usuarios del sistema
- `curso` - Cursos disponibles
- `seccion` - Secciones de cada curso
- `venta` - Compras realizadas

### Migración desde Local

Si tienes datos locales que quieres migrar:

```bash
# 1. Exportar datos locales
pg_dump tu_base_local > backup.sql

# 2. Importar a Digital Ocean
psql "postgresql://usuario:pass@host:puerto/db_venta_cursos" < backup.sql
```

## 🚦 Solución de Problemas Comunes

### Error: "Database does not exist"
```bash
# Crear la base de datos si no existe
createdb -h host -U usuario db_venta_cursos
```

### Error: "Connection refused"
- Verifica que la URL de base de datos sea correcta
- Confirma que Digital Ocean permita conexiones desde tu IP
- Revisa los puertos (generalmente 25060 para Digital Ocean)

### Error: "Missing SECRET_KEY"
```bash
# Generar nueva clave
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📊 Monitoreo Post-Despliegue

### Logs de Aplicación
```bash
# Ver logs en tiempo real
tail -f /var/log/gunicorn/error.log
```

### Verificar Estado
```bash
# Verificar que la app esté funcionando
curl http://tu-dominio.com/dashboard
```

## 🔄 Actualizaciones Futuras

Para actualizar la aplicación:

```bash
# 1. Hacer backup de la base de datos
pg_dump "DATABASE_URL" > backup_$(date +%Y%m%d).sql

# 2. Actualizar código
git pull origin main

# 3. Instalar nuevas dependencias
pip install -r requirements.txt

# 4. Ejecutar migraciones
flask db upgrade

# 5. Reiniciar servicio
sudo systemctl restart gunicorn
```

## 📞 Contacto

Si encuentras problemas específicos, proporciona:
1. Salida del comando `python3 check_config.py`
2. Logs de error específicos
3. Configuración de Digital Ocean (sin contraseñas)

---

🎉 **¡Tu aplicación está lista para producción!**