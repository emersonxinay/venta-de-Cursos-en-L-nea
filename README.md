# Proyecto de Venta de Cursos en Línea

## Descripción

Este proyecto es una aplicación web para la venta de cursos en línea. Los usuarios pueden navegar por los cursos disponibles, ver detalles de los cursos, y comprar acceso a los cursos. Los administradores pueden gestionar los cursos y las secciones de los cursos. Los usuarios no registrados pueden ver los detalles de los cursos y acceder a las secciones gratuitas, pero deben registrarse y comprar el curso para acceder al contenido completo.

## Funcionalidades

- **Usuarios**:
  - Ver detalles de los cursos.
  - Ver secciones gratuitas de los cursos.
  - Registrarse e iniciar sesión.
  - Comprar acceso a los cursos.
  - Ver cursos comprados y pendientes de confirmación.

- **Administradores**:
  - Crear, editar y eliminar cursos.
  - Crear, editar y eliminar secciones de los cursos.
  - Ver y gestionar transferencias pendientes.

## Instalación

1. Clona el repositorio:
   ```sh
   git clone https://github.com/tu_usuario/tu_repositorio.git
   cd tu_repositorio
   ```
2. Crea un entorno virtual e instala las dependencias:
```bash
python3 -m venv venv
```
```bash
source venv/bin/activate
```
```bash
pip install -r requirements.txt
```
3. Configura las variables de entorno en un archivo .env:
```.env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=tu_secreto
SQLALCHEMY_DATABASE_URI=sqlite:///db.sqlite3
```
4. Inicializa la base de datos:
```bash
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```
5. Ejecuta la aplicación:
```bash
flask run 
```
o tambien solo :
```bash
python3 app.py
```
# uso

- Abre tu navegador y ve a http://127.0.0.1:5000/dashboard para ver los cursos disponibles.
- Regístrate e inicia sesión para comprar cursos y acceder al contenido completo.
- Si eres administrador, puedes gestionar los cursos y las secciones desde el dashboard.
# Estructura de la Base de Datos

Usuario:

'''id: Integer, primary key
nombre: String
email: String
password: String
rol: String (admin o usuario)'''
Curso:

'''id: Integer, primary key
nombre: String
descripcion: String
precio: Float
ventas: Relationship con Venta
secciones: Relationship con Seccion'''
Seccion:

'''id: Integer, primary key
titulo: String
descripcion: String
video_url: String
curso_id: ForeignKey a Curso
es_gratis: Boolean'''
Venta:

'''id: Integer, primary key
usuario_id: ForeignKey a Usuario
curso_id: ForeignKey a Curso
metodo_pago: String
fecha_venta: DateTime
estado_transferencia: String
fecha_expiracion: DateTime'''

## Contribuciones
Las contribuciones son bienvenidas. Por favor, abre un issue o un pull request para discutir cualquier cambio que te gustaría hacer.


