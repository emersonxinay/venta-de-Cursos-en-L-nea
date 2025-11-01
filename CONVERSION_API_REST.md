# Conversión a API REST - CompilandoCode

## 🎯 Objetivo

Convertir el proyecto actual (Flask con templates) a una **API REST pura** con frontend separado.

## 📊 Arquitectura Actual vs. Nueva

### Actual (Monolito con Templates)
```
┌─────────────────────────────────────┐
│         Navegador                   │
└──────────────┬──────────────────────┘
               │ HTML completo
               ▼
┌─────────────────────────────────────┐
│      Flask App + Templates          │
│  - Routes devuelven HTML            │
│  - Flask-Login (sesiones)           │
│  - CSRF con cookies                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      PostgreSQL                     │
└─────────────────────────────────────┘
```

### Nueva (API REST + Frontend Separado)
```
┌─────────────────────┐    ┌─────────────────────┐
│   React/Vue/Next    │    │   Mobile App        │
│   (Frontend SPA)    │    │   iOS/Android       │
└──────────┬──────────┘    └──────────┬──────────┘
           │ JSON requests            │
           │ JWT tokens               │
           ▼                          ▼
┌────────────────────────────────────────────────┐
│           Flask REST API                       │
│  - Blueprints por recurso                     │
│  - JWT authentication                          │
│  - JSON responses                              │
│  - CORS habilitado                             │
│  - Swagger documentation                       │
└──────────────────┬─────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────┐
│              PostgreSQL                        │
└────────────────────────────────────────────────┘
```

---

## 🚀 Plan de Implementación

### Fase 1: Preparación (1-2 días)

#### 1.1 Instalar Dependencias

```bash
pip install flask-restful
pip install flask-jwt-extended
pip install flask-cors
pip install marshmallow
pip install marshmallow-sqlalchemy
pip install apispec
pip install apispec-webframeworks
```

#### 1.2 Actualizar requirements.txt

```txt
Flask==3.1.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.1.0
Flask-RESTful==0.3.10
Flask-JWT-Extended==4.7.1
Flask-CORS==4.0.0
marshmallow==3.20.1
marshmallow-sqlalchemy==0.29.0
apispec==6.3.0
apispec-webframeworks==0.5.2
gunicorn==23.0.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
stripe==7.4.0
```

---

### Fase 2: Estructura de Carpetas API (1 día)

```
proyecto/
├── api/
│   ├── __init__.py
│   ├── resources/          # Endpoints REST
│   │   ├── __init__.py
│   │   ├── auth.py         # POST /api/auth/login, /register, /refresh
│   │   ├── users.py        # GET/PUT /api/users/{id}
│   │   ├── courses.py      # CRUD /api/courses
│   │   ├── sections.py     # CRUD /api/courses/{id}/sections
│   │   ├── payments.py     # POST /api/payments
│   │   └── analytics.py    # GET /api/analytics
│   │
│   ├── schemas/            # Serialización con Marshmallow
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │   ├── course_schema.py
│   │   ├── section_schema.py
│   │   └── payment_schema.py
│   │
│   ├── middleware/         # Middleware personalizado
│   │   ├── __init__.py
│   │   ├── auth.py         # Decoradores JWT
│   │   └── rate_limit.py   # Rate limiting
│   │
│   └── utils/              # Utilidades
│       ├── __init__.py
│       ├── responses.py    # Respuestas estandarizadas
│       └── validators.py   # Validaciones
│
├── app.py                  # App principal
├── config.py               # Configuración
├── models.py               # Modelos SQLAlchemy (sin cambios)
└── wsgi.py                 # Entry point
```

---

### Fase 3: Implementar Autenticación JWT (1 día)

#### 3.1 Configurar JWT en app.py

```python
# app.py
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta

app = Flask(__name__)

# Configuración JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Inicializar JWT
jwt = JWTManager(app)

# Configurar CORS
CORS(app,
     resources={r"/api/*": {"origins": "*"}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

# Callbacks JWT
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return Usuario.query.filter_by(id=identity).one_or_none()
```

#### 3.2 Endpoint de Autenticación

**Archivo: `api/resources/auth.py`**
```python
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from models import Usuario
from extensions import db
from api.schemas.user_schema import UserSchema

user_schema = UserSchema()

class RegisterResource(Resource):
    """POST /api/auth/register"""

    def post(self):
        data = request.get_json()

        # Validar datos
        if not data or not data.get('correo') or not data.get('contrasena'):
            return {'error': 'Email y contraseña son requeridos'}, 400

        # Verificar si el usuario ya existe
        if Usuario.query.filter_by(correo=data['correo']).first():
            return {'error': 'El usuario ya existe'}, 409

        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            nombre=data.get('nombre', ''),
            correo=data['correo'],
            contrasena=generate_password_hash(data['contrasena']),
            rol=data.get('rol', 'estudiante')
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        # Generar tokens
        access_token = create_access_token(identity=nuevo_usuario)
        refresh_token = create_refresh_token(identity=nuevo_usuario)

        return {
            'message': 'Usuario creado exitosamente',
            'user': user_schema.dump(nuevo_usuario),
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 201


class LoginResource(Resource):
    """POST /api/auth/login"""

    def post(self):
        data = request.get_json()

        if not data or not data.get('correo') or not data.get('contrasena'):
            return {'error': 'Email y contraseña son requeridos'}, 400

        # Buscar usuario
        usuario = Usuario.query.filter_by(correo=data['correo']).first()

        if not usuario or not check_password_hash(usuario.contrasena, data['contrasena']):
            return {'error': 'Credenciales inválidas'}, 401

        # Generar tokens
        access_token = create_access_token(identity=usuario)
        refresh_token = create_refresh_token(identity=usuario)

        return {
            'message': 'Login exitoso',
            'user': user_schema.dump(usuario),
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 200


class RefreshResource(Resource):
    """POST /api/auth/refresh"""

    @jwt_required(refresh=True)
    def post(self):
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)

        return {
            'access_token': access_token
        }, 200


class MeResource(Resource):
    """GET /api/auth/me"""

    @jwt_required()
    def get(self):
        from flask_jwt_extended import current_user
        return user_schema.dump(current_user), 200
```

---

### Fase 4: Schemas de Serialización (1 día)

**Archivo: `api/schemas/user_schema.py`**
```python
from marshmallow import Schema, fields, validates, ValidationError
import re

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True)
    correo = fields.Email(required=True)
    rol = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    # No incluir la contraseña en las respuestas
    class Meta:
        fields = ('id', 'nombre', 'correo', 'rol', 'created_at')

    @validates('nombre')
    def validate_nombre(self, value):
        if len(value) < 2:
            raise ValidationError('El nombre debe tener al menos 2 caracteres')
```

**Archivo: `api/schemas/course_schema.py`**
```python
from marshmallow import Schema, fields

class SectionSchema(Schema):
    id = fields.Int(dump_only=True)
    titulo = fields.Str(required=True)
    descripcion = fields.Str()
    video_url = fields.Str()
    video_file = fields.Str()
    es_gratis = fields.Bool(default=False)
    orden = fields.Int()

    class Meta:
        fields = ('id', 'titulo', 'descripcion', 'video_url', 'video_file', 'es_gratis', 'orden')


class CourseSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True)
    descripcion = fields.Str()
    precio = fields.Float(required=True)
    thumbnail = fields.Str()
    duracion = fields.Int()  # minutos
    nivel = fields.Str()
    secciones = fields.Nested(SectionSchema, many=True, dump_only=True)
    total_secciones = fields.Method('get_total_secciones')
    created_at = fields.DateTime(dump_only=True)

    def get_total_secciones(self, obj):
        return len(obj.secciones) if obj.secciones else 0

    class Meta:
        fields = ('id', 'nombre', 'descripcion', 'precio', 'thumbnail',
                 'duracion', 'nivel', 'secciones', 'total_secciones', 'created_at')


class CourseListSchema(Schema):
    """Schema simplificado para listar cursos"""
    id = fields.Int()
    nombre = fields.Str()
    descripcion = fields.Str()
    precio = fields.Float()
    thumbnail = fields.Str()
    total_secciones = fields.Method('get_total_secciones')

    def get_total_secciones(self, obj):
        return len(obj.secciones) if obj.secciones else 0
```

---

### Fase 5: Recursos REST (2-3 días)

**Archivo: `api/resources/courses.py`**
```python
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, current_user, get_jwt_identity
from models import Curso, Seccion, Venta
from extensions import db
from api.schemas.course_schema import CourseSchema, CourseListSchema, SectionSchema
from api.utils.responses import success_response, error_response
from api.middleware.auth import admin_required

course_schema = CourseSchema()
courses_schema = CourseListSchema(many=True)
section_schema = SectionSchema()

class CourseListResource(Resource):
    """GET /api/courses - Listar todos los cursos"""

    def get(self):
        cursos = Curso.query.all()
        return success_response(
            data=courses_schema.dump(cursos),
            message='Cursos obtenidos exitosamente'
        )


class CourseResource(Resource):
    """
    GET /api/courses/{id} - Obtener un curso
    PUT /api/courses/{id} - Actualizar curso (admin)
    DELETE /api/courses/{id} - Eliminar curso (admin)
    """

    def get(self, course_id):
        curso = Curso.query.get_or_404(course_id)

        # Verificar acceso del usuario
        tiene_acceso = False
        if current_user:
            # Admin tiene acceso a todo
            if current_user.rol == 'admin':
                tiene_acceso = True
            else:
                # Verificar si el usuario compró el curso
                venta = Venta.query.filter_by(
                    usuario_id=current_user.id,
                    curso_id=course_id,
                    estado_transferencia='confirmada'
                ).first()
                tiene_acceso = venta is not None

        curso_data = course_schema.dump(curso)
        curso_data['tiene_acceso'] = tiene_acceso

        # Si no tiene acceso, solo mostrar secciones gratis/preview
        if not tiene_acceso:
            curso_data['secciones'] = [
                s for s in curso_data['secciones']
                if s.get('es_gratis', False)
            ][:2]  # Solo primeras 2

        return success_response(data=curso_data)

    @jwt_required()
    @admin_required
    def put(self, course_id):
        """Actualizar curso (solo admin)"""
        curso = Curso.query.get_or_404(course_id)
        data = request.get_json()

        if 'nombre' in data:
            curso.nombre = data['nombre']
        if 'descripcion' in data:
            curso.descripcion = data['descripcion']
        if 'precio' in data:
            curso.precio = data['precio']

        db.session.commit()

        return success_response(
            data=course_schema.dump(curso),
            message='Curso actualizado exitosamente'
        )

    @jwt_required()
    @admin_required
    def delete(self, course_id):
        """Eliminar curso (solo admin)"""
        curso = Curso.query.get_or_404(course_id)
        db.session.delete(curso)
        db.session.commit()

        return success_response(message='Curso eliminado exitosamente')


class CourseCreateResource(Resource):
    """POST /api/courses - Crear nuevo curso (admin)"""

    @jwt_required()
    @admin_required
    def post(self):
        data = request.get_json()

        nuevo_curso = Curso(
            nombre=data['nombre'],
            descripcion=data.get('descripcion', ''),
            precio=data['precio']
        )

        db.session.add(nuevo_curso)
        db.session.commit()

        return success_response(
            data=course_schema.dump(nuevo_curso),
            message='Curso creado exitosamente',
            status_code=201
        )


class CourseSectionsResource(Resource):
    """GET /api/courses/{id}/sections - Listar secciones de un curso"""

    def get(self, course_id):
        curso = Curso.query.get_or_404(course_id)
        secciones = Seccion.query.filter_by(curso_id=course_id).order_by(Seccion.id).all()

        # Verificar acceso
        tiene_acceso = False
        if current_user:
            if current_user.rol == 'admin':
                tiene_acceso = True
            else:
                venta = Venta.query.filter_by(
                    usuario_id=current_user.id,
                    curso_id=course_id,
                    estado_transferencia='confirmada'
                ).first()
                tiene_acceso = venta is not None

        secciones_data = []
        for i, seccion in enumerate(secciones):
            seccion_dict = section_schema.dump(seccion)

            # Marcar si es accesible
            if tiene_acceso:
                seccion_dict['es_accesible'] = True
            elif i < 2:  # Primeras 2 siempre preview
                seccion_dict['es_accesible'] = True
                seccion_dict['es_preview'] = True
            else:
                seccion_dict['es_accesible'] = False
                seccion_dict['video_url'] = None  # Ocultar URL
                seccion_dict['video_file'] = None

            secciones_data.append(seccion_dict)

        return success_response(data=secciones_data)
```

**Archivo: `api/resources/payments.py`**
```python
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, current_user
from models import Venta, Curso
from extensions import db
from api.utils.responses import success_response, error_response
import stripe
import os

stripe.api_key = os.getenv('STRIPE_API_KEY_SANDBOX')

class CreatePaymentIntentResource(Resource):
    """POST /api/payments/intent - Crear intención de pago"""

    @jwt_required()
    def post(self):
        data = request.get_json()
        curso_id = data.get('curso_id')

        curso = Curso.query.get_or_404(curso_id)

        # Verificar que no haya comprado ya
        venta_existente = Venta.query.filter_by(
            usuario_id=current_user.id,
            curso_id=curso_id,
            estado_transferencia='confirmada'
        ).first()

        if venta_existente:
            return error_response('Ya has comprado este curso', 400)

        # Crear Payment Intent en Stripe
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(curso.precio * 100),  # Convertir a centavos
                currency='usd',
                metadata={
                    'usuario_id': current_user.id,
                    'curso_id': curso_id
                }
            )

            return success_response({
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            })

        except Exception as e:
            return error_response(f'Error al crear pago: {str(e)}', 500)


class ConfirmPaymentResource(Resource):
    """POST /api/payments/confirm - Confirmar pago"""

    @jwt_required()
    def post(self):
        data = request.get_json()
        payment_intent_id = data.get('payment_intent_id')
        curso_id = data.get('curso_id')

        # Verificar el pago en Stripe
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if intent.status == 'succeeded':
                # Crear venta
                nueva_venta = Venta(
                    usuario_id=current_user.id,
                    curso_id=curso_id,
                    monto=intent.amount / 100,
                    metodo_pago='stripe',
                    estado_transferencia='confirmada',
                    stripe_payment_intent_id=payment_intent_id
                )

                db.session.add(nueva_venta)
                db.session.commit()

                return success_response({
                    'venta_id': nueva_venta.id,
                    'message': 'Pago confirmado exitosamente'
                })
            else:
                return error_response('Pago no completado', 400)

        except Exception as e:
            return error_response(f'Error al confirmar pago: {str(e)}', 500)
```

---

### Fase 6: Utilidades y Middleware

**Archivo: `api/utils/responses.py`**
```python
from flask import jsonify

def success_response(data=None, message='Success', status_code=200):
    """Respuesta exitosa estandarizada"""
    response = {
        'success': True,
        'message': message
    }

    if data is not None:
        response['data'] = data

    return jsonify(response), status_code


def error_response(message='Error', status_code=400, errors=None):
    """Respuesta de error estandarizada"""
    response = {
        'success': False,
        'message': message
    }

    if errors:
        response['errors'] = errors

    return jsonify(response), status_code


def paginated_response(items, page, per_page, total, message='Success'):
    """Respuesta paginada"""
    return jsonify({
        'success': True,
        'message': message,
        'data': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    }), 200
```

**Archivo: `api/middleware/auth.py`**
```python
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import jsonify

def admin_required(fn):
    """Decorator para requerir rol de admin"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        from flask_jwt_extended import current_user

        if not current_user or current_user.rol != 'admin':
            return jsonify({
                'success': False,
                'message': 'Se requieren permisos de administrador'
            }), 403

        return fn(*args, **kwargs)
    return wrapper


def optional_jwt():
    """Decorator para JWT opcional (permite requests sin autenticación)"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request(optional=True)
            except:
                pass
            return fn(*args, **kwargs)
        return wrapper
    return decorator
```

---

### Fase 7: Registrar Rutas API

**Archivo: `api/__init__.py`**
```python
from flask import Blueprint
from flask_restful import Api

from api.resources.auth import (
    RegisterResource,
    LoginResource,
    RefreshResource,
    MeResource
)
from api.resources.courses import (
    CourseListResource,
    CourseResource,
    CourseCreateResource,
    CourseSectionsResource
)
from api.resources.payments import (
    CreatePaymentIntentResource,
    ConfirmPaymentResource
)

# Crear blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)

# Auth endpoints
api.add_resource(RegisterResource, '/auth/register')
api.add_resource(LoginResource, '/auth/login')
api.add_resource(RefreshResource, '/auth/refresh')
api.add_resource(MeResource, '/auth/me')

# Courses endpoints
api.add_resource(CourseListResource, '/courses')
api.add_resource(CourseCreateResource, '/courses/create')
api.add_resource(CourseResource, '/courses/<int:course_id>')
api.add_resource(CourseSectionsResource, '/courses/<int:course_id>/sections')

# Payments endpoints
api.add_resource(CreatePaymentIntentResource, '/payments/intent')
api.add_resource(ConfirmPaymentResource, '/payments/confirm')

def init_api(app):
    """Inicializar API en la app Flask"""
    app.register_blueprint(api_bp)
```

**Actualizar `app.py`:**
```python
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from api import init_api

app = Flask(__name__)

# ... configuración existente ...

# Inicializar JWT
jwt = JWTManager(app)

# Configurar CORS
CORS(app)

# Inicializar API
init_api(app)

# Mantener rutas web existentes si quieres mantener ambos
# O comentarlas si quieres solo API
# from routes import init_routes
# init_routes(app)
```

---

### Fase 8: Documentación API con Swagger

**Instalar:**
```bash
pip install flasgger
```

**En `app.py`:**
```python
from flasgger import Swagger

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/api/docs/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/api/docs/static",
    "swagger_ui": True,
    "specs_route": "/api/docs/"
}

swagger = Swagger(app, config=swagger_config)
```

**Documentar endpoints con docstrings:**
```python
class LoginResource(Resource):
    """
    User Login
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            correo:
              type: string
              example: user@example.com
            contrasena:
              type: string
              example: password123
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            success:
              type: boolean
            access_token:
              type: string
            user:
              type: object
      401:
        description: Invalid credentials
    """
    def post(self):
        # ... código ...
```

---

## 🎨 Frontend Separado

### Opción 1: React (Recomendado)

```bash
npx create-react-app frontend-compilandocode
cd frontend-compilandocode
npm install axios react-router-dom @stripe/stripe-js @stripe/react-stripe-js
```

**Estructura:**
```
frontend/
├── src/
│   ├── api/
│   │   └── client.js          # Axios configurado
│   ├── components/
│   │   ├── Navbar.jsx
│   │   ├── CourseCard.jsx
│   │   └── ProtectedRoute.jsx
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx
│   │   ├── CourseDetail.jsx
│   │   └── Checkout.jsx
│   ├── context/
│   │   └── AuthContext.jsx   # Context para auth
│   └── App.jsx
└── package.json
```

**Ejemplo: `src/api/client.js`**
```javascript
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5004/api';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token a todas las requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_URL}/auth/refresh`, {}, {
          headers: { Authorization: `Bearer ${refreshToken}` }
        });

        const { access_token } = response.data;
        localStorage.setItem('access_token', access_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

**Ejemplo: `src/pages/Login.jsx`**
```javascript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await apiClient.post('/auth/login', {
        correo: email,
        contrasena: password
      });

      const { access_token, refresh_token, user } = response.data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user', JSON.stringify(user));

      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.message || 'Error al iniciar sesión');
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit}>
        <h2>Iniciar Sesión</h2>

        {error && <div className="alert alert-error">{error}</div>}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button type="submit">Ingresar</button>
      </form>
    </div>
  );
}

export default Login;
```

### Opción 2: Next.js (Para SEO)

```bash
npx create-next-app@latest frontend-compilandocode
```

### Opción 3: Vue.js

```bash
npm create vue@latest frontend-compilandocode
```

---

## 📱 Ventajas de la Arquitectura API

### ✅ Ventajas

1. **Escalabilidad**: Frontend y backend pueden escalar independientemente
2. **Flexibilidad**: Puedes tener múltiples frontends (web, móvil, desktop)
3. **Desarrollo paralelo**: Equipos frontend y backend trabajan separadamente
4. **Mejor performance**: SPA más rápidas, menos carga en servidor
5. **Mobile ready**: Misma API para apps iOS/Android
6. **Testabilidad**: Más fácil testear API endpoints
7. **Cacheo**: Mejor cacheo de respuestas JSON
8. **Versionado**: Puedes tener /api/v1, /api/v2, etc.

### ⚠️ Desventajas

1. **Complejidad inicial**: Más código para configurar
2. **SEO**: SPAs necesitan SSR para buen SEO (usar Next.js)
3. **CORS**: Hay que configurar CORS correctamente
4. **Autenticación**: JWT más complejo que sesiones
5. **Deploy**: Necesitas deployar frontend y backend separados

---

## 🚀 Plan de Migración Gradual

### Estrategia: Mantener ambos sistemas temporalmente

```python
# app.py
from api import init_api
from routes import init_routes

# Inicializar API REST
init_api(app)

# Mantener rutas web existentes (temporalmente)
init_routes(app)

# Ahora tienes:
# - /api/* → Endpoints REST (nuevo)
# - /* → Rutas web con templates (existente)
```

### Migración por fases:

1. **Semana 1**: Implementar API auth
2. **Semana 2**: Implementar API cursos
3. **Semana 3**: Implementar API pagos
4. **Semana 4**: Crear frontend básico
5. **Semana 5-6**: Migrar funcionalidades
6. **Semana 7**: Testing completo
7. **Semana 8**: Deploy y desactivar rutas web

---

## 📊 Testing de la API

**Con Postman:**
```
GET http://localhost:5004/api/courses
Authorization: Bearer {token}
```

**Con curl:**
```bash
# Login
curl -X POST http://localhost:5004/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"correo":"user@example.com","contrasena":"password"}'

# Obtener cursos
curl -X GET http://localhost:5004/api/courses \
  -H "Authorization: Bearer {token}"
```

**Con Python (tests):**
```python
import requests

# Login
response = requests.post('http://localhost:5004/api/auth/login', json={
    'correo': 'user@example.com',
    'contrasena': 'password'
})

token = response.json()['access_token']

# Obtener cursos
courses = requests.get(
    'http://localhost:5004/api/courses',
    headers={'Authorization': f'Bearer {token}'}
)

print(courses.json())
```

---

## 🎯 Resumen de Endpoints API

```
Authentication:
POST   /api/auth/register      - Registrar usuario
POST   /api/auth/login         - Iniciar sesión
POST   /api/auth/refresh       - Refrescar token
GET    /api/auth/me            - Obtener usuario actual

Courses:
GET    /api/courses            - Listar todos los cursos
POST   /api/courses/create     - Crear curso (admin)
GET    /api/courses/{id}       - Obtener un curso
PUT    /api/courses/{id}       - Actualizar curso (admin)
DELETE /api/courses/{id}       - Eliminar curso (admin)
GET    /api/courses/{id}/sections - Listar secciones

Payments:
POST   /api/payments/intent    - Crear intención de pago
POST   /api/payments/confirm   - Confirmar pago

Analytics (admin):
GET    /api/analytics/ventas   - Estadísticas de ventas
GET    /api/analytics/usuarios - Estadísticas de usuarios
```

---

¿Quieres que empiece a implementar la API REST ahora? Puedo comenzar con la Fase 1-3 para tener autenticación JWT funcionando.
