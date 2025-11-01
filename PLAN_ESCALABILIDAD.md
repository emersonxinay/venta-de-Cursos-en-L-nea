# Plan de Escalabilidad - CompilandoCode LMS

## 📊 Análisis de la Arquitectura Actual

### ✅ Estado Actual
```
┌─────────────────────────────────────────┐
│         Usuarios (Navegador)            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Flask App (Werkzeug/Gunicorn)      │
│  - Rutas modularizadas                  │
│  - Flask-Login (sesiones)               │
│  - Flask-WTF (CSRF)                     │
│  - Stripe/PayPal                        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      PostgreSQL Database                │
│  - Usuarios, Cursos, Ventas             │
│  - Secciones, Progresos                 │
└─────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Archivos Estáticos (local)         │
│  - CSS, JS, Videos                      │
└─────────────────────────────────────────┘
```

### 🎯 Puntos Fuertes
- ✅ Gunicorn ya instalado (WSGI production server)
- ✅ PostgreSQL (base de datos robusta y escalable)
- ✅ Rutas modularizadas (fácil de mantener)
- ✅ SQLAlchemy ORM (abstracción de DB)
- ✅ Flask-Migrate (migraciones de DB)

### ⚠️ Puntos Débiles Actuales
- ❌ Sin caché (Redis/Memcached)
- ❌ Sin procesamiento asíncrono (Celery)
- ❌ Sin CDN para archivos estáticos
- ❌ Sin load balancer
- ❌ Sin contenedorización (Docker)
- ❌ Sin monitoreo/logging centralizado
- ❌ Videos almacenados localmente

---

## 🚀 Plan de Escalabilidad por Etapas

### **FASE 1: Optimización Inmediata (1-2 semanas)**
*Capacidad: 100-500 usuarios concurrentes*

#### 1.1 Servidor de Producción con Gunicorn
```bash
# Ya tienes Gunicorn instalado, solo configurar
pip install gevent  # Para async workers
```

**Crear archivo `gunicorn_config.py`:**
```python
import multiprocessing

# Workers: 2-4 x CPU cores
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'  # Async workers
worker_connections = 1000
timeout = 120
keepalive = 5

# Binding
bind = '0.0.0.0:5004'

# Logging
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
loglevel = 'info'

# Process naming
proc_name = 'compilandocode'

# Server mechanics
daemon = False
pidfile = 'gunicorn.pid'
```

**Comando para correr:**
```bash
gunicorn -c gunicorn_config.py wsgi:app
```

#### 1.2 Nginx como Reverse Proxy
**Instalar Nginx:**
```bash
# macOS
brew install nginx

# Linux
sudo apt-get install nginx
```

**Configuración `/etc/nginx/sites-available/compilandocode`:**
```nginx
upstream compilandocode {
    server 127.0.0.1:5004 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name compilandocode.com www.compilandocode.com;

    # Seguridad
    client_max_body_size 100M;

    # Headers de seguridad
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Archivos estáticos (caché agresivo)
    location /static/ {
        alias /ruta/proyecto/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Videos (streaming optimizado)
    location /static/uploads/ {
        alias /ruta/proyecto/static/uploads/;
        mp4;
        mp4_buffer_size 1m;
        mp4_max_buffer_size 5m;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Proxy a Flask
    location / {
        proxy_pass http://compilandocode;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    location /api/ {
        limit_req zone=api burst=20;
        proxy_pass http://compilandocode;
    }
}
```

#### 1.3 Optimizaciones de Base de Datos

**1. Índices en columnas frecuentemente consultadas:**
```python
# En models.py, agregar índices
class Usuario(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(100), unique=True, nullable=False, index=True)
    rol = db.Column(db.String(20), nullable=False, index=True)

class Venta(db.Model):
    __tablename__ = 'venta'

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), index=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), index=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, index=True)
```

**2. Connection Pooling en PostgreSQL:**
```python
# En app.py
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 20
}
```

**3. Crear vistas materializadas para reportes:**
```sql
-- Para estadísticas del admin
CREATE MATERIALIZED VIEW estadisticas_ventas AS
SELECT
    DATE_TRUNC('day', fecha) as dia,
    COUNT(*) as total_ventas,
    SUM(monto) as ingresos_totales
FROM venta
GROUP BY DATE_TRUNC('day', fecha);

CREATE INDEX ON estadisticas_ventas (dia);

-- Refrescar cada hora con un cron job
REFRESH MATERIALIZED VIEW CONCURRENTLY estadisticas_ventas;
```

#### 1.4 Implementar Caché con Redis

**Instalar Redis:**
```bash
pip install redis flask-caching
```

**Configuración en `app.py`:**
```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    'CACHE_DEFAULT_TIMEOUT': 300
})

# Ejemplo de uso en rutas
@app.route('/cursos')
@cache.cached(timeout=600, key_prefix='all_cursos')
def listar_cursos():
    cursos = Curso.query.all()
    return render_template('cursos.html', cursos=cursos)

@app.route('/curso/<int:id>')
@cache.cached(timeout=3600, key_prefix=lambda: f'curso_{request.view_args["id"]}')
def ver_curso(id):
    curso = Curso.query.get_or_404(id)
    return render_template('ver_curso.html', curso=curso)
```

**Cache para sesiones (opcional pero recomendado):**
```python
from flask_session import Session

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379/1')
Session(app)
```

---

### **FASE 2: Escalabilidad Media (1 mes)**
*Capacidad: 500-5,000 usuarios concurrentes*

#### 2.1 Procesamiento Asíncrono con Celery

**Instalar Celery:**
```bash
pip install celery redis
```

**Crear `celery_app.py`:**
```python
from celery import Celery
from app import app

celery = Celery(
    app.import_name,
    broker='redis://localhost:6379/2',
    backend='redis://localhost:6379/3'
)

celery.conf.update(app.config)

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask
```

**Crear `tasks.py` para tareas pesadas:**
```python
from celery_app import celery
from models import Usuario, Certificado
from extensions import db
import smtplib
from email.mime.text import MIMEText

@celery.task
def enviar_email_bienvenida(usuario_id):
    """Enviar email de bienvenida en background"""
    usuario = Usuario.query.get(usuario_id)
    # Lógica de envío de email
    return f"Email enviado a {usuario.correo}"

@celery.task
def procesar_pago_async(venta_id):
    """Procesar confirmación de pago en background"""
    # Lógica de procesamiento
    return f"Pago {venta_id} procesado"

@celery.task
def generar_certificado(usuario_id, curso_id):
    """Generar certificado PDF en background"""
    # Lógica de generación de PDF
    certificado = Certificado(
        usuario_id=usuario_id,
        curso_id=curso_id,
        fecha_emision=datetime.utcnow()
    )
    db.session.add(certificado)
    db.session.commit()
    return certificado.id

@celery.task
def limpiar_sesiones_expiradas():
    """Tarea programada para limpiar sesiones antiguas"""
    # Lógica de limpieza
    pass
```

**Uso en rutas:**
```python
from tasks import enviar_email_bienvenida, generar_certificado

@app.route('/register', methods=['POST'])
def register():
    # ... lógica de registro ...
    db.session.commit()

    # Enviar email de forma asíncrona (no bloquea la respuesta)
    enviar_email_bienvenida.delay(nuevo_usuario.id)

    return redirect(url_for('login'))
```

**Correr workers de Celery:**
```bash
celery -A celery_app.celery worker --loglevel=info --concurrency=4
```

**Celery Beat para tareas programadas:**
```python
from celery.schedules import crontab

celery.conf.beat_schedule = {
    'limpiar-sesiones-cada-dia': {
        'task': 'tasks.limpiar_sesiones_expiradas',
        'schedule': crontab(hour=3, minute=0),  # 3 AM diario
    },
    'refrescar-estadisticas': {
        'task': 'tasks.actualizar_estadisticas',
        'schedule': crontab(minute='*/30'),  # Cada 30 minutos
    },
}
```

#### 2.2 CDN para Archivos Estáticos

**Opciones de CDN:**
1. **Cloudflare** (Gratis + fácil)
2. **AWS CloudFront**
3. **Google Cloud CDN**
4. **Azure CDN**

**Implementación con Cloudflare (Recomendado para empezar):**

1. Registrar dominio en Cloudflare
2. Activar CDN automático
3. Configurar cache rules para `/static/`:
```
Cache Everything
Edge Cache TTL: 1 month
Browser Cache TTL: 1 month
```

**Actualizar templates:**
```python
# En app.py
if app.config['USE_CDN']:
    app.config['CDN_DOMAIN'] = 'cdn.compilandocode.com'

    @app.context_processor
    def inject_cdn():
        def cdn_url(filename):
            if app.config.get('USE_CDN'):
                return f"https://{app.config['CDN_DOMAIN']}/static/{filename}"
            return url_for('static', filename=filename)
        return dict(cdn_url=cdn_url)
```

**En templates:**
```html
<!-- Antes -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">

<!-- Después -->
<link rel="stylesheet" href="{{ cdn_url('css/main.css') }}">
```

#### 2.3 Almacenamiento de Videos en Cloud

**Opción 1: AWS S3 + CloudFront**
```bash
pip install boto3
```

```python
import boto3
from werkzeug.utils import secure_filename

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
    region_name='us-east-1'
)

def subir_video_a_s3(file, curso_id):
    """Subir video a S3"""
    filename = secure_filename(file.filename)
    key = f"videos/curso_{curso_id}/{filename}"

    s3_client.upload_fileobj(
        file,
        'compilandocode-videos',
        key,
        ExtraArgs={
            'ContentType': 'video/mp4',
            'CacheControl': 'max-age=31536000'
        }
    )

    # URL del CloudFront
    return f"https://d1234567890.cloudfront.net/{key}"
```

**Opción 2: Vimeo/YouTube (Más fácil)**
- Subir videos a Vimeo
- Obtener embed code
- Guardar ID en base de datos

---

### **FASE 3: Alta Escalabilidad (2-3 meses)**
*Capacidad: 5,000-50,000+ usuarios concurrentes*

#### 3.1 Contenedorización con Docker

**Crear `Dockerfile`:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 5004

# Comando para correr
CMD ["gunicorn", "-c", "gunicorn_config.py", "wsgi:app"]
```

**Crear `docker-compose.yml`:**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5004:5004"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/compilandocode
      - REDIS_URL=redis://redis:6379/0
      - FLASK_ENV=production
    depends_on:
      - db
      - redis
    volumes:
      - ./static/uploads:/app/static/uploads
    deploy:
      replicas: 3  # 3 instancias de la app
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=compilandocode
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  celery_worker:
    build: .
    command: celery -A celery_app.celery worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/compilandocode
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  celery_beat:
    build: .
    command: celery -A celery_app.celery beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/compilandocode
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./static:/usr/share/nginx/html/static
    depends_on:
      - web

volumes:
  postgres_data:
  redis_data:
```

**Comandos Docker:**
```bash
# Build y correr
docker-compose up --build -d

# Escalar web workers
docker-compose up -d --scale web=5

# Ver logs
docker-compose logs -f web

# Detener
docker-compose down
```

#### 3.2 Load Balancer con Nginx

**Configuración Nginx para múltiples workers:**
```nginx
upstream compilandocode_cluster {
    least_conn;  # Balanceo por menor número de conexiones

    server web1:5004 max_fails=3 fail_timeout=30s weight=1;
    server web2:5004 max_fails=3 fail_timeout=30s weight=1;
    server web3:5004 max_fails=3 fail_timeout=30s weight=1;

    # Health check
    check interval=3000 rise=2 fall=3 timeout=1000;
}

server {
    listen 80;
    server_name compilandocode.com;

    location / {
        proxy_pass http://compilandocode_cluster;

        # Headers para sticky sessions si es necesario
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # WebSocket support (para features en tiempo real)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### 3.3 Monitoreo y Logging

**Instalar herramientas:**
```bash
pip install prometheus-flask-exporter
pip install sentry-sdk[flask]
```

**Configurar Sentry (Error tracking):**
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    environment=os.getenv('FLASK_ENV', 'development')
)
```

**Configurar Prometheus (Métricas):**
```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'CompilandoCode LMS', version='1.0.0')

# Métricas personalizadas
@app.route('/curso/<int:id>/comprar')
@metrics.counter('compras_curso', 'Número de compras por curso',
                 labels={'curso_id': lambda: request.view_args['id']})
def comprar_curso(id):
    # ... lógica ...
    pass
```

**Stack ELK para logs (Elasticsearch, Logstash, Kibana):**
```yaml
# docker-compose.yml
  elasticsearch:
    image: elasticsearch:8.10.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: logstash:8.10.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: kibana:8.10.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

---

### **FASE 4: Mega Escalabilidad (3-6 meses)**
*Capacidad: 50,000+ usuarios concurrentes*

#### 4.1 Kubernetes (K8s)

**Archivo `k8s/deployment.yaml`:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: compilandocode-web
spec:
  replicas: 10
  selector:
    matchLabels:
      app: compilandocode
  template:
    metadata:
      labels:
        app: compilandocode
    spec:
      containers:
      - name: web
        image: compilandocode:latest
        ports:
        - containerPort: 5004
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5004
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 5004
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: compilandocode-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: compilandocode-web
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

#### 4.2 Microservicios (Opcional)

**Separar en servicios:**
```
1. Auth Service (Autenticación/Autorización)
2. Course Service (Gestión de cursos)
3. Payment Service (Pagos)
4. Video Service (Streaming de videos)
5. Analytics Service (Estadísticas)
6. Notification Service (Emails, push notifications)
```

#### 4.3 Base de Datos: Read Replicas

**PostgreSQL con replicas de lectura:**
```python
# En app.py
SQLALCHEMY_BINDS = {
    'master': DATABASE_URL,  # Escrituras
    'slave1': READ_REPLICA_1_URL,  # Lecturas
    'slave2': READ_REPLICA_2_URL   # Lecturas
}

# En models.py - separar lecturas de escrituras
class Curso(db.Model):
    __bind_key__ = 'master'  # Para escrituras

    @classmethod
    def get_all_for_display(cls):
        # Usar replica para lecturas
        return cls.query.with_session(
            db.session(bind='slave1')
        ).all()
```

---

## 📈 Costos Estimados por Fase

### Fase 1 (hasta 500 usuarios)
- **VPS básico**: $20-40/mes (DigitalOcean, Linode)
- **Redis**: Incluido o $10/mes
- **Total**: ~$40/mes

### Fase 2 (hasta 5,000 usuarios)
- **VPS mejorado**: $80-120/mes
- **Redis/Celery**: $20/mes
- **CDN**: $20-50/mes
- **S3**: $30-100/mes
- **Total**: ~$200/mes

### Fase 3 (hasta 50,000 usuarios)
- **Cluster Kubernetes**: $300-500/mes
- **Base de datos administrada**: $100-200/mes
- **CDN**: $100-300/mes
- **S3/Almacenamiento**: $200-500/mes
- **Monitoreo**: $50-100/mes
- **Total**: ~$1,000-1,500/mes

### Fase 4 (50,000+ usuarios)
- **Kubernetes grande**: $1,000-3,000/mes
- **BD con replicas**: $500-1,000/mes
- **CDN global**: $500-1,500/mes
- **Almacenamiento**: $1,000+/mes
- **Total**: ~$5,000-10,000/mes

---

## 🎯 Recomendación de Implementación

### Para Empezar AHORA (Primera Semana):
1. ✅ Configurar Gunicorn (ya lo tienes)
2. ✅ Instalar y configurar Nginx
3. ✅ Optimizar índices en PostgreSQL
4. ✅ Implementar Redis para caché básico

### Próximos 30 Días:
1. ✅ Configurar Celery para tareas async
2. ✅ Implementar CDN con Cloudflare
3. ✅ Migrar videos a S3 o Vimeo
4. ✅ Agregar monitoreo básico

### Cuando Crezcas:
1. ✅ Dockerizar la aplicación
2. ✅ Configurar auto-scaling
3. ✅ Considerar Kubernetes

---

## 🔥 Quick Start - Implementación Inmediata

**Archivo `start_production.sh`:**
```bash
#!/bin/bash

# Instalar Redis
brew install redis  # macOS
# sudo apt-get install redis-server  # Linux

# Instalar Nginx
brew install nginx  # macOS
# sudo apt-get install nginx  # Linux

# Instalar dependencias Python
pip install gunicorn gevent redis flask-caching

# Iniciar Redis
redis-server --daemonize yes

# Iniciar Gunicorn
gunicorn -c gunicorn_config.py wsgi:app &

# Configurar y iniciar Nginx
sudo nginx -c /path/to/nginx.conf

echo "✅ Producción lista!"
```

---

## 📊 Métricas a Monitorear

1. **Request Rate**: requests/segundo
2. **Response Time**: tiempo promedio de respuesta
3. **Error Rate**: % de errores 5xx
4. **CPU Usage**: uso de CPU por worker
5. **Memory Usage**: uso de memoria
6. **Database Connections**: conexiones activas
7. **Cache Hit Rate**: % de hits en Redis
8. **Disk I/O**: lectura/escritura de disco

---

¿Quieres que implemente alguna fase específica ahora?
