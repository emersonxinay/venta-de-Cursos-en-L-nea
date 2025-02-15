from flask import render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user


class AuthRoutes:
    def __init__(self, app):
        self.app = app
        # Importar db y Usuario aquí para evitar la importación circular
        from app import flask_app, db, Usuario
        self.flask_app = flask_app
        self.db = db
        self.Usuario = Usuario
        self.init_routes()

    def init_routes(self):
        @self.app.route('/register', methods=['GET', 'POST'])
        def register():
            if request.method == 'POST':
                with self.flask_app.app_context():
                    nombre = request.form['nombre']
                    correo = request.form['correo']
                    contrasena = request.form['contrasena']

                    usuario_existente = self.Usuario.query.filter_by(
                        correo=correo).first()
                    if usuario_existente:
                        flash('El correo ya está registrado.')
                        return redirect(url_for('register'))

                    hashed_password = generate_password_hash(
                        contrasena, method='pbkdf2:sha256')
                    nuevo_usuario = self.Usuario(
                        nombre=nombre,
                        correo=correo,
                        contrasena=hashed_password,
                        rol='usuario'
                    )
                    self.db.session.add(nuevo_usuario)
                    self.db.session.commit()
                    flash('Registro exitoso.')
                    return redirect(url_for('login'))
            return render_template('register.html')

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            with self.flask_app.app_context():
                if request.method == 'POST':
                    usuario = self.Usuario.query.filter_by(
                        correo=request.form['correo']).first()
                    if usuario and check_password_hash(usuario.contrasena, request.form['contrasena']):
                        login_user(usuario)
                        return redirect(url_for('dashboard'))
                    else:
                        flash('Correo o contraseña incorrectos.')
                return render_template('login.html')
