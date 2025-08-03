# 🧪 Testing Local con Base de Datos de Producción

Esta guía te permite probar tu aplicación localmente usando la base de datos de Digital Ocean, simulando el entorno de producción.

## 📋 Pasos para Configurar

### 1. **Obtener Datos de Conexión de Digital Ocean**

Ve a tu panel de Digital Ocean → Databases y copia:
- **Host**: `tu-host.db.ondigitalocean.com`
- **Port**: `25060` (típicamente)
- **User**: `tu_usuario`
- **Password**: `tu_contraseña`
- **Database**: `db_venta_cursos`

### 2. **Configurar Archivo Local**

Edita el archivo `.env.local.production`:

```bash
# Editar configuración
nano .env.local.production
```

**Sustituye estos valores con los reales:**

```bash
# Tu URL real de Digital Ocean
DATABASE_URL=postgresql://tu_usuario:tu_contraseña@tu_host:25060/db_venta_cursos

# Genera una clave temporal
SECRET_KEY=mi_clave_temporal_para_testing_123456789
```

### 3. **Ejecutar Testing Automatizado**

```bash
# Instalar dependencias si no las tienes
pip install psycopg2-binary

# Ejecutar script de testing
python3 test_production_local.py
```

### 4. **Método Manual (Alternativo)**

Si prefieres hacerlo manualmente:

```bash
# 1. Hacer backup de tu .env actual
cp .env .env.backup

# 2. Usar configuración de producción
cp .env.local.production .env

# 3. Verificar configuración
python3 check_config.py

# 4. Ejecutar app en modo producción
FLASK_ENV=production python3 app.py

# 5. Restaurar configuración original
cp .env.backup .env
```

## 🔍 Verificaciones que se Realizan

El script automáticamente verifica:

✅ **Conexión a base de datos**
- Host y puerto accesibles
- Credenciales correctas
- Base de datos existe

✅ **Tablas requeridas**
- `usuario`, `curso`, `seccion`, `venta`
- Estructura correcta

✅ **Datos existentes**
- Conteo de usuarios y cursos
- Integridad básica

✅ **Configuración de aplicación**
- Variables de entorno correctas
- Modo producción activado
- Debug desactivado

## 🌐 URL de Testing

Una vez iniciado, accede a:
- **Dashboard**: http://localhost:5000/dashboard
- **Login**: http://localhost:5000/login
- **API Status**: http://localhost:5000/ (página principal)

## 🛡️ Consideraciones de Seguridad

### ⚠️ **IMPORTANTE**
- Usa **SOLO datos de sandbox** para pagos
- **NO** uses claves de producción de Stripe/PayPal
- **NO** hagas cambios destructivos a la BD

### 🔒 **Configuración Segura**
```bash
# En .env.local.production usar SANDBOX
STRIPE_API_KEY_SANDBOX=sk_test_...
PAYPAL_CLIENT_ID_SANDBOX=sandbox_id...
```

## 🐛 Solución de Problemas

### Error: "Connection refused"
```bash
# Verificar conectividad
ping tu-host.db.ondigitalocean.com

# Verificar puerto
telnet tu-host.db.ondigitalocean.com 25060
```

### Error: "Database does not exist"
- Confirma que la base de datos se llame exactamente `db_venta_cursos`
- Verifica en el panel de Digital Ocean

### Error: "Authentication failed"
- Revisa usuario y contraseña
- Copia exactamente desde Digital Ocean
- Verifica caracteres especiales en la URL

### Error: "SSL required"
Agrega `?sslmode=require` al final de la URL:
```bash
DATABASE_URL=postgresql://user:pass@host:port/db?sslmode=require
```

## 📊 Testing Checklist

Prueba estas funcionalidades:

### 🔐 **Autenticación**
- [ ] Login de usuario existente
- [ ] Registro de nuevo usuario
- [ ] Logout funcional

### 📚 **Cursos**
- [ ] Ver lista de cursos
- [ ] Acceder a preview gratuito
- [ ] Navegación entre secciones

### 🛒 **Compras (Solo Testing)**
- [ ] Proceso de compra (sin completar)
- [ ] Estados de transferencia
- [ ] Acceso post-compra

### 📱 **Responsive**
- [ ] Vista móvil funcional
- [ ] Dashboard responsive
- [ ] Navegación mobile

## 🔄 Comandos Útiles

```bash
# Iniciar testing
python3 test_production_local.py

# Verificar configuración únicamente
python3 check_config.py

# Restaurar configuración original
python3 test_production_local.py restore

# Ver logs en tiempo real
tail -f app.log

# Conectar directamente a la BD
psql "postgresql://user:pass@host:port/db_venta_cursos"
```

## 📝 Logs y Debugging

Para debugging detallado:

```python
# Agregar al inicio de app.py temporalmente
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Próximos Pasos

Una vez que el testing local funcione:

1. **✅ Confirmar funcionalidad completa**
2. **📤 Desplegar a Digital Ocean App Platform**
3. **🔧 Configurar nginx y SSL**
4. **📊 Configurar monitoreo**

---

## 🆘 Comandos de Emergencia

Si algo sale mal:

```bash
# Restaurar configuración
cp .env.backup .env

# Limpiar archivos temporales
rm -f .env.local.production

# Reiniciar desde cero
git checkout .env
```

🎉 **¡Ahora puedes probar localmente con datos reales de producción!**