from datetime import datetime
from flask_migrate import Migrate
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import stripe
import paypalrestsdk
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:emerson123@localhost/db_venta_cursos'
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Después de inicializar db
migrate = Migrate(app, db)

# Configurar Stripe y PayPal con las variables de entorno
app_mode = os.getenv('APP_MODE', 'development')

if app_mode == 'production':
    stripe.api_key = os.getenv('STRIPE_API_KEY_LIVE')
    paypalrestsdk.configure({
        "mode": "live",
        "client_id": os.getenv('PAYPAL_CLIENT_ID_LIVE'),
        "client_secret": os.getenv('PAYPAL_CLIENT_SECRET_LIVE')
    })
else:
    stripe.api_key = os.getenv('STRIPE_API_KEY_SANDBOX')
    paypalrestsdk.configure({
        "mode": "sandbox",
        "client_id": os.getenv('PAYPAL_CLIENT_ID_SANDBOX'),
        "client_secret": os.getenv('PAYPAL_CLIENT_SECRET_SANDBOX')
    })


class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.String(250), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # admin, usuario
    compras = db.relationship('Venta', backref='usuario', lazy=True)


class Curso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(500))
    precio = db.Column(db.Float, nullable=False)
    ventas = db.relationship('Venta', backref='curso',
                             lazy=True, cascade="all, delete-orphan")


class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey(
        'usuario.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    metodo_pago = db.Column(db.String(50), nullable=False)
    fecha_venta = db.Column(db.DateTime, default=datetime.utcnow)
    estado_transferencia = db.Column(
        db.String(20), nullable=True, default='pendiente')
    fecha_expiracion = db.Column(db.DateTime, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        hashed_password = generate_password_hash(
            contrasena, method='pbkdf2:sha256')
        nuevo_usuario = Usuario(
            nombre=nombre, correo=correo, contrasena=hashed_password, rol='usuario')
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Usuario registrado exitosamente. Por favor, inicia sesión.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = Usuario.query.filter_by(
            correo=request.form['correo']).first()
        if usuario and check_password_hash(usuario.contrasena, request.form['contrasena']):
            login_user(usuario)
            return redirect(url_for('dashboard'))
        else:
            flash('Correo o contraseña incorrectos.')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/nuevo_curso', methods=['GET', 'POST'])
@login_required
def nuevo_curso():
    if current_user.rol != 'admin':
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        nuevo_curso = Curso(
            nombre=request.form['nombre'],
            descripcion=request.form['descripcion'],
            precio=float(request.form['precio'])
        )
        db.session.add(nuevo_curso)
        db.session.commit()
        flash('Curso creado exitosamente.')
        return redirect(url_for('dashboard'))
    return render_template('nuevo_curso.html')


@app.route('/editar_curso/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_curso(id):
    if current_user.rol != 'admin':
        return redirect(url_for('dashboard'))
    curso = Curso.query.get_or_404(id)
    if request.method == 'POST':
        curso.nombre = request.form['nombre']
        curso.descripcion = request.form['descripcion']
        curso.precio = float(request.form['precio'])
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('editar_curso.html', curso=curso)


@app.route('/eliminar_curso/<int:id>')
@login_required
def eliminar_curso(id):
    if current_user.rol != 'admin':
        return redirect(url_for('dashboard'))
    curso = Curso.query.get_or_404(id)
    db.session.delete(curso)
    db.session.commit()
    flash('Curso eliminado exitosamente.')
    return redirect(url_for('dashboard'))


@app.route('/comprar/<int:curso_id>', methods=['GET', 'POST'])
@login_required
def comprar_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    if request.method == 'POST':
        metodo_pago = request.form['metodo']
        duracion = request.form['duracion']

        # Calcular la fecha de expiración
        if duracion == '1_mes':
            fecha_expiracion = datetime.utcnow() + timedelta(days=30)
        elif duracion == '6_meses':
            fecha_expiracion = datetime.utcnow() + timedelta(days=180)
        elif duracion == '1_ano':
            fecha_expiracion = datetime.utcnow() + timedelta(days=365)
        else:
            flash('Duración no válida.')
            return redirect(request.url)

        # Por defecto, las compras con Stripe y PayPal se confirman automáticamente
        estado_transferencia = 'confirmada'

        if metodo_pago == "stripe":
            token = request.form['stripeToken']
            pago = procesar_pago_stripe(curso.precio, token)
        elif metodo_pago == "paypal":
            return_url = url_for('confirmar_paypal',
                                 curso_id=curso.id, _external=True)
            cancel_url = url_for('dashboard', _external=True)
            pago = procesar_pago_paypal(curso.precio, return_url, cancel_url)
            if pago:
                return redirect(pago['links'][1]['href'])
        elif metodo_pago == "transferencia":
            pago = procesar_pago_transferencia(curso.precio, current_user.id)
            # Las compras con transferencia quedan pendientes
            estado_transferencia = 'pendiente'

        if pago:
            venta = Venta(usuario_id=current_user.id, curso_id=curso.id, metodo_pago=metodo_pago,
                          estado_transferencia=estado_transferencia, fecha_expiracion=fecha_expiracion)
            db.session.add(venta)
            db.session.commit()
            if estado_transferencia == 'pendiente':
                flash(
                    'Compra realizada exitosamente. Por favor, espere la confirmación de la transferencia.')
            else:
                flash('Compra realizada exitosamente.')
            return redirect(url_for('dashboard'))

        flash('Error en el pago.')
    return render_template('comprar_curso.html', curso=curso)


def procesar_pago_stripe(precio, token):
    try:
        charge = stripe.Charge.create(
            amount=int(precio * 100),  # Stripe maneja los montos en centavos
            currency='usd',
            description='Pago por curso',
            source=token
        )
        return charge['status'] == 'succeeded'
    except stripe.error.StripeError as e:
        flash(f"Error en el pago con Stripe: {e.user_message}")
        return False


def procesar_pago_paypal(precio, return_url, cancel_url):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": return_url,
            "cancel_url": cancel_url},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "Curso",
                    "sku": "curso",
                    "price": str(precio),
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": str(precio),
                "currency": "USD"},
            "description": "Pago por curso"}]})

    if payment.create():
        return payment
    else:
        flash(f"Error en el pago con PayPal: {payment.error['message']}")
        return None


@app.route('/confirmar_paypal', methods=['GET'])
@login_required
def confirmar_paypal():
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')
    curso_id = request.args.get('curso_id')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        venta = Venta.query.filter_by(
            usuario_id=current_user.id, curso_id=curso_id, metodo_pago='paypal').first()
        if venta:
            venta.estado_transferencia = 'confirmada'
            db.session.commit()
            flash('Pago con PayPal confirmado exitosamente.')
        else:
            # Crear una nueva venta si no se encuentra una existente
            nueva_venta = Venta(
                usuario_id=current_user.id,
                curso_id=curso_id,
                metodo_pago='paypal',
                estado_transferencia='confirmada'
            )
            db.session.add(nueva_venta)
            db.session.commit()
            flash('Pago con PayPal confirmado exitosamente y venta registrada.')
    else:
        flash('Error al confirmar el pago con PayPal.')

    return redirect(url_for('dashboard'))


def procesar_pago_transferencia(precio, usuario_id):
    # Aquí puedes agregar la lógica para manejar la transferencia bancaria
    # Por ejemplo, podrías registrar la intención de pago y esperar la confirmación manual
    flash("Pago por transferencia bancaria registrado. Por favor, confirme la transferencia.")
    return True


@app.route('/transferencias_pendientes')
@login_required
def transferencias_pendientes():
    if current_user.rol != 'admin':
        return redirect(url_for('dashboard'))
    ventas = Venta.query.filter_by(
        metodo_pago='transferencia', estado_transferencia='pendiente').all()
    return render_template('confirmar_transferencias.html', ventas=ventas)


@app.route('/confirmar_transferencia/<int:venta_id>', methods=['POST'])
@login_required
def confirmar_transferencia(venta_id):
    if current_user.rol != 'admin':
        return redirect(url_for('dashboard'))
    venta = Venta.query.get_or_404(venta_id)
    venta.estado_transferencia = 'confirmada'
    db.session.commit()
    flash('Transferencia confirmada exitosamente.')
    return redirect(url_for('transferencias_pendientes'))


@app.route('/dashboard')
@login_required
def dashboard():
    cursos = Curso.query.all()
    mis_ventas = Venta.query.filter_by(usuario_id=current_user.id).all()
    cursos_comprados_ids = [venta.curso_id for venta in mis_ventas if venta.estado_transferencia ==
                            'confirmada' and venta.fecha_expiracion > datetime.utcnow()]
    cursos_pendientes_ids = [
        venta.curso_id for venta in mis_ventas if venta.estado_transferencia == 'pendiente']
    current_time = datetime.utcnow()
    return render_template('dashboard.html', cursos=cursos, mis_ventas=mis_ventas, cursos_comprados_ids=cursos_comprados_ids, cursos_pendientes_ids=cursos_pendientes_ids, current_time=current_time)


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.rol != 'admin':
        return redirect(url_for('dashboard'))

    # Obtener las ventas del día, semana, mes y año
    hoy = datetime.utcnow().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_mes = hoy.replace(day=1)
    inicio_ano = hoy.replace(month=1, day=1)

    ventas_dia = Venta.query.filter(
        db.func.date(Venta.fecha_venta) == hoy).all()
    ventas_semana = Venta.query.filter(db.func.date(
        Venta.fecha_venta) >= inicio_semana).all()
    ventas_mes = Venta.query.filter(db.func.date(
        Venta.fecha_venta) >= inicio_mes).all()
    ventas_ano = Venta.query.filter(db.func.date(
        Venta.fecha_venta) >= inicio_ano).all()

    # Calcular el total de ventas
    total_dia = sum(venta.curso.precio for venta in ventas_dia)
    total_semana = sum(venta.curso.precio for venta in ventas_semana)
    total_mes = sum(venta.curso.precio for venta in ventas_mes)
    total_ano = sum(venta.curso.precio for venta in ventas_ano)

    # Obtener los cursos más vendidos
    cursos_mas_vendidos = db.session.query(
        Curso.nombre, db.func.count(Venta.id).label('total_ventas')
    ).join(Venta).group_by(Curso.id).order_by(db.func.count(Venta.id).desc()).all()

    return render_template('admin_dashboard.html',
                           total_dia=total_dia,
                           total_semana=total_semana,
                           total_mes=total_mes,
                           total_ano=total_ano,
                           cursos_mas_vendidos=cursos_mas_vendidos,
                           ventas=ventas_ano)  # Pasar las ventas del año para la gestión de accesos


@app.route('/quitar_acceso/<int:venta_id>', methods=['POST'])
@login_required
def quitar_acceso(venta_id):
    if current_user.rol != 'admin':
        flash('No tienes permiso para realizar esta acción.')
        return redirect(url_for('dashboard'))

    venta = Venta.query.get_or_404(venta_id)
    db.session.delete(venta)
    db.session.commit()
    flash('Acceso al curso quitado exitosamente.')
    return redirect(url_for('admin_dashboard'))


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
