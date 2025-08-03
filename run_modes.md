# 🚀 Modos de Ejecución de la Aplicación

## ✅ PROBLEMA RESUELTO

El error estaba causado por variables de entorno incorrectas. Ya está arreglado.

---

## 🔧 Cómo Ejecutar en Cada Modo

### 1. **Desarrollo Local (ACTUAL)**

```bash
# Tu configuración actual funcionando
python3 app.py

# O con Flask CLI
FLASK_APP=app.py flask run
```

**Configuración:** `.env` (ya configurado)
- Base de datos: Local PostgreSQL
- Debug: Activado
- Pagos: Sandbox/Testing

### 2. **Testing con BD de Producción**

```bash
# Configurar una vez
cp .env.local.production .env.testing
nano .env.testing  # Editar con datos de Digital Ocean

# Ejecutar
cp .env.testing .env
python3 app.py
```

### 3. **Modo Producción Local**

```bash
# Simular producción localmente
FLASK_ENV=production FLASK_DEBUG=False python3 app.py

# O configurar archivo .env.production
cp .env.production.example .env.production
nano .env.production  # Configurar variables reales
cp .env.production .env
python3 app.py
```

### 4. **Producción Real (Digital Ocean)**

```bash
# En el servidor
gunicorn --bind 0.0.0.0:5000 --workers 3 app:app

# Con configuración avanzada
gunicorn --config gunicorn.conf.py app:app
```

---

## 📁 Archivos de Configuración

| Archivo | Propósito | Estado |
|---------|-----------|---------|
| `.env` | **ACTUAL** - Desarrollo local | ✅ Funcionando |
| `.env.development` | Plantilla desarrollo | ✅ Creado |
| `.env.local.production` | Testing con BD real | ✅ Listo |
| `.env.production.example` | Plantilla producción | ✅ Listo |

---

## 🔄 Cambiar Entre Modos

### **Desarrollo → Testing**
```bash
cp .env .env.backup
cp .env.local.production .env
# Editar .env con datos de Digital Ocean
python3 app.py
```

### **Testing → Desarrollo**
```bash
cp .env.backup .env
python3 app.py
```

### **Desarrollo → Producción**
```bash
cp .env.production.example .env.production
# Configurar variables reales
cp .env.production .env
FLASK_ENV=production python3 app.py
```

---

## 🐛 Solución del Error Anterior

**Error:**
```
could not translate host name "tu-host.elephantsql.com"
```

**Causa:** Variables de entorno con valores placeholder

**Solución:** Configurar `.env` con valores reales:
```bash
DATABASE_URL=postgresql://postgres:emerson123@localhost/db_venta_cursos
SECRET_KEY=development_secret_key_123456789
```

---

## ✅ Verificar Configuración

```bash
# Verificar que todo esté bien
python3 check_config.py

# Debe mostrar:
✅ Variables críticas configuradas
✅ Conexión a base de datos exitosa
✅ Todas las tablas principales presentes
```

---

## 🎯 Para la Próxima Sesión

**Archivo actual funcionando:** `.env` (desarrollo local)

**Para probar con Digital Ocean:**
1. Obtener datos de conexión de Digital Ocean
2. Editar `.env.local.production`
3. Ejecutar `python3 test_production_local.py`

**Para desplegar:**
1. Seguir `PRODUCTION_SETUP.md`
2. Usar `.env.production.example` como base

---

🎉 **¡Tu aplicación ya está funcionando correctamente en modo desarrollo!**