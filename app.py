from datetime import datetime
from flask_migrate import Migrate
from flask import Flask, current_app, jsonify, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from extensions import db
import stripe
import paypalrestsdk
from dotenv import load_dotenv
import os

from models import Certificado, HistoricoProgreso, ProgresoUsuario

# Cargar variables de entorno
load_dotenv()

# Configuración de la aplicación
app = Flask(__name__)

# Configuración robusta de base de datos


def get_database_url():
    """Construir URL de base de datos desde variables de entorno"""
    # Para producción con variables de entorno
    if os.getenv('DATABASE_URL'):
        return os.getenv('DATABASE_URL')

    # Para configuración manual
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'db_venta_cursos')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD')

    if not db_password:
        raise ValueError(
            "DB_PASSWORD es requerido. Configura las variables de entorno.")

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


# Configuración de aplicación
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(32))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'static/uploads')
app.config['MAX_CONTENT_PATH'] = int(
    os.getenv('MAX_CONTENT_PATH', 16 * 1024 * 1024))

# Configuración de seguridad para producción
if os.getenv('FLASK_ENV') == 'production':
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
csrf = CSRFProtect(app)


db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Después de inicializar db
migrate = Migrate(app, db)

# Configuración de servicios de pago


def configure_payment_services():
    """Configurar Stripe y PayPal según el entorno"""
    app_mode = os.getenv('FLASK_ENV', 'development')

    if app_mode == 'production':
        # Configuración de producción
        stripe_key = os.getenv('STRIPE_API_KEY_LIVE')
        stripe_pub_key = os.getenv('STRIPE_PUBLISHABLE_KEY_LIVE')
        paypal_client_id = os.getenv('PAYPAL_CLIENT_ID_LIVE')
        paypal_client_secret = os.getenv('PAYPAL_CLIENT_SECRET_LIVE')
        paypal_mode = "live"
    else:
        # Configuración de desarrollo/sandbox
        stripe_key = os.getenv('STRIPE_API_KEY_SANDBOX')
        stripe_pub_key = os.getenv('STRIPE_PUBLISHABLE_KEY_SANDBOX')
        paypal_client_id = os.getenv('PAYPAL_CLIENT_ID_SANDBOX')
        paypal_client_secret = os.getenv('PAYPAL_CLIENT_SECRET_SANDBOX')
        paypal_mode = "sandbox"

    # Configurar Stripe
    if stripe_key:
        stripe.api_key = stripe_key
        app.config['STRIPE_PUBLISHABLE_KEY'] = stripe_pub_key
    else:
        app.logger.warning("Stripe no configurado - claves no encontradas")

    # Configurar PayPal
    if paypal_client_id and paypal_client_secret:
        paypalrestsdk.configure({
            "mode": paypal_mode,
            "client_id": paypal_client_id,
            "client_secret": paypal_client_secret
        })
    else:
        app.logger.warning("PayPal no configurado - claves no encontradas")


configure_payment_services()


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'mp4'}


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
    secciones = db.relationship(
        'Seccion', backref='curso', lazy=True, cascade="all, delete-orphan")


class Seccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(500))
    video_url = db.Column(db.String(200))
    video_file = db.Column(db.String(200))
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    es_gratis = db.Column(db.Boolean, default=False)


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


globals()['flask_app'] = app
globals()['db'] = db
globals()['Usuario'] = Usuario


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# rutas modularizadas
def init_app():
    from routes import init_routes
    init_routes(app)

# fin de rutas modularizadas

# inicio de vistas de cursos, progreso y certificado


@app.route('/actualizar_progreso_seccion', methods=['POST'])
@login_required
def actualizar_progreso_seccion():
    try:
        data = request.get_json()
        seccion_id = data.get('seccion_id')
        curso_id = data.get('curso_id')

        try:
            porcentaje = min(100, max(0, int(data.get('porcentaje', 0))))
        except (ValueError, TypeError):
            porcentaje = 0

        if not all([seccion_id, curso_id]):
            return jsonify({'success': False, 'error': 'Datos incompletos'}), 400

        # Verificación más eficiente de relación sección-curso
        if not db.session.query(Seccion.query.filter_by(id=seccion_id, curso_id=curso_id).exists()).scalar():
            return jsonify({'success': False, 'error': 'Sección no encontrada en este curso'}), 404

        # Buscar o crear registro de progreso (versión optimizada)
        progreso = ProgresoUsuario.query.filter_by(
            usuario_id=current_user.id,
            seccion_id=seccion_id
        ).first()

        if not progreso:
            # Crear nuevo registro con valores iniciales
            progreso = ProgresoUsuario(
                usuario_id=current_user.id,
                seccion_id=seccion_id,
                curso_id=curso_id,
                progreso=0,  # Siempre inicia en 0
                completado=False,
                ultima_actualizacion=datetime.utcnow(),
                tiempo_total_visto=0
            )
            db.session.add(progreso)
            # No hacemos flush() aquí a menos que necesitemos el ID inmediatamente

        # Lógica de actualización mejorada
        if porcentaje > progreso.progreso:
            progreso.progreso = porcentaje
            progreso.ultima_actualizacion = datetime.utcnow()

            if porcentaje >= 95 and not progreso.completado:
                progreso.completado = True
                progreso.fecha_completado = datetime.utcnow()

            # Incrementar tiempo visto (1 unidad por actualización)
            progreso.tiempo_total_visto = progreso.tiempo_total_visto + 1

        db.session.commit()

        # Calcular progreso del curso (versión optimizada)
        progreso_curso = db.session.query(
            func.coalesce(func.avg(ProgresoUsuario.progreso), 0.0)
        ).filter(
            ProgresoUsuario.curso_id == curso_id,
            ProgresoUsuario.usuario_id == current_user.id
        ).scalar() or 0

        return jsonify({
            'success': True,
            'progreso_curso': round(float(progreso_curso), 2),
            'seccion_completada': progreso.completado,
            'nuevo_progreso': porcentaje > progreso.progreso  # Indica si hubo actualización
        })

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error DB: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': 'Error en base de datos'}), 500

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error inesperado: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': 'Error interno'}), 500


def calcular_progreso_curso(curso_id, usuario_id):
    curso = Curso.query.get_or_404(curso_id)
    secciones_ids = [s.id for s in curso.secciones]

    # Obtener todas las secciones del curso
    total_secciones = len(secciones_ids)
    if total_secciones == 0:
        return 0

    # Obtener progresos del usuario para este curso
    progresos = ProgresoUsuario.query.filter(
        ProgresoUsuario.usuario_id == usuario_id,
        ProgresoUsuario.seccion_id.in_(secciones_ids)
    ).all()

    # Calcular progreso ponderado
    suma_progresos = sum(p.progreso for p in progresos)
    progreso_curso = (suma_progresos / total_secciones)

    return min(100, round(progreso_curso, 2))


def verificar_curso_completado(curso_id, usuario_id):
    curso = Curso.query.get_or_404(curso_id)
    secciones_ids = [s.id for s in curso.secciones]

    progresos = ProgresoUsuario.query.filter(
        ProgresoUsuario.usuario_id == usuario_id,
        ProgresoUsuario.seccion_id.in_(secciones_ids)
    ).all()

    todas_completadas = all(p.completado for p in progresos)

    if todas_completadas:
        # Crear certificado si no existe
        certificado = Certificado.query.filter_by(
            usuario_id=usuario_id,
            curso_id=curso_id
        ).first()

        if not certificado:
            codigo = f"CERT-{curso_id}-{usuario_id}-{datetime.now().strftime('%Y%m%d')}"
            certificado = Certificado(
                usuario_id=usuario_id,
                curso_id=curso_id,
                codigo=codigo,
                fecha_emision=datetime.utcnow(),
                fecha_completado=datetime.utcnow(),
                valido=True
            )
            db.session.add(certificado)
            db.session.commit()


@app.route('/get_progreso_curso')
@login_required
def get_progreso_curso():
    curso_id = request.args.get('curso_id')
    if not curso_id:
        return jsonify({'success': False, 'error': 'curso_id requerido'}), 400

    try:
        # Obtener todas las secciones del curso con su progreso
        secciones = db.session.query(
            Seccion.id,
            func.coalesce(ProgresoUsuario.progreso, 0).label('progreso')
        ).outerjoin(
            ProgresoUsuario,
            (ProgresoUsuario.seccion_id == Seccion.id) &
            (ProgresoUsuario.usuario_id == current_user.id)
        ).filter(
            Seccion.curso_id == curso_id
        ).all()

        # Convertir a formato JSON
        secciones_data = [{
            'id': s.id,
            'progreso': float(s.progreso)
        } for s in secciones]

        # Calcular progreso general del curso
        total_secciones = len(secciones_data)
        if total_secciones == 0:
            return jsonify({
                'success': True,
                'progreso_curso': 0,
                'secciones': []
            })

        suma_progresos = sum(s['progreso'] for s in secciones_data)
        progreso_curso = round((suma_progresos / total_secciones), 2)

        return jsonify({
            'success': True,
            'progreso_curso': progreso_curso,
            'secciones': secciones_data
        })

    except Exception as e:
        app.logger.error(f"Error obteniendo progreso: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500
# error de pagina 404


@app.route('/comprar/<int:curso_id>', methods=['GET', 'POST'])
@login_required
def comprar_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    # Verificar si el usuario ya ha comprado el curso
    venta_existente = Venta.query.filter_by(
        usuario_id=current_user.id, curso_id=curso.id, estado_transferencia='confirmada').first()
    if venta_existente:
        flash('Ya has comprado este curso.')
        return redirect(url_for('ver_curso', curso_id=curso.id))

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
            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': curso.nombre,
                            },
                            'unit_amount': int(curso.precio * 100),
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=url_for('stripe_success', curso_id=curso.id,
                                        _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=url_for(
                        'stripe_cancel', curso_id=curso.id, _external=True),
                )
                return redirect(session.url, code=303)
            except stripe.error.StripeError as e:
                flash(f"Error en el pago con Stripe: {e.user_message}")
                return redirect(request.url)
        elif metodo_pago == "paypal":
            return_url = url_for(
                'confirmar_paypal', curso_id=curso.id, duracion=duracion, _external=True)
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
    return render_template('comprar_curso.html', curso=curso, stripe_publishable_key=stripe_publishable_key)


@app.route('/confirmar_pago/<int:curso_id>', methods=['POST'])
@login_required
def confirmar_pago(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    client_secret = request.form['client_secret']
    try:
        intent = stripe.PaymentIntent.confirm(
            client_secret,
            payment_method=request.form['payment_method_id']
        )
        if intent['status'] == 'succeeded':
            venta = Venta(
                usuario_id=current_user.id,
                curso_id=curso.id,
                metodo_pago='stripe',
                estado_transferencia='confirmada',
                # Ejemplo de duración de 1 año
                fecha_expiracion=datetime.utcnow() + timedelta(days=365)
            )
            db.session.add(venta)
            db.session.commit()
            flash('Pago realizado exitosamente.')
            return redirect(url_for('ver_curso', curso_id=curso.id))
        else:
            flash('Error en el pago con Stripe.')
    except stripe.error.StripeError as e:
        flash(f"Error en el pago con Stripe: {e.user_message}")
    return redirect(url_for('comprar_curso', curso_id=curso.id))


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


@app.route('/stripe_success/<int:curso_id>')
@login_required
def stripe_success(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    session_id = request.args.get('session_id')
    session = stripe.checkout.Session.retrieve(session_id)

    if session.payment_status == 'paid':
        venta = Venta(
            usuario_id=current_user.id,
            curso_id=curso_id,
            metodo_pago='stripe',
            estado_transferencia='confirmada',
            # Ejemplo de duración de 1 año
            fecha_expiracion=datetime.utcnow() + timedelta(days=365)
        )
        db.session.add(venta)
        db.session.commit()
        flash('Pago realizado exitosamente.')
        return redirect(url_for('ver_curso', curso_id=curso_id))
    else:
        flash('Error en el pago con Stripe.')
        return redirect(url_for('comprar_curso', curso_id=curso_id))


@app.route('/stripe_cancel/<int:curso_id>')
@login_required
def stripe_cancel(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    flash(f'Pago cancelado para el curso: {curso.nombre}')
    return redirect(url_for('comprar_curso', curso_id=curso_id))


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
    duracion = request.args.get('duracion')

    # Calcular la fecha de expiración
    if duracion == '1_mes':
        fecha_expiracion = datetime.utcnow() + timedelta(days=30)
    elif duracion == '6_meses':
        fecha_expiracion = datetime.utcnow() + timedelta(days=180)
    elif duracion == '1_ano':
        fecha_expiracion = datetime.utcnow() + timedelta(days=365)
    else:
        flash('Duración no válida.')
        return redirect(url_for('dashboard'))

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        venta = Venta.query.filter_by(
            usuario_id=current_user.id, curso_id=curso_id, metodo_pago='paypal').first()
        if venta:
            venta.estado_transferencia = 'confirmada'
            venta.fecha_expiracion = fecha_expiracion
            db.session.commit()
            flash('Pago con PayPal confirmado exitosamente.')
        else:
            # Crear una nueva venta si no se encuentra una existente
            nueva_venta = Venta(
                usuario_id=current_user.id,
                curso_id=curso_id,
                metodo_pago='paypal',
                estado_transferencia='confirmada',
                fecha_expiracion=fecha_expiracion
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


@app.route('/rechazar_transferencia/<int:venta_id>', methods=['POST'])
@login_required
def rechazar_transferencia(venta_id):
    if current_user.rol != 'admin':
        return redirect(url_for('dashboard'))
    venta = Venta.query.get_or_404(venta_id)
    venta.estado_transferencia = 'rechazada'
    db.session.commit()
    flash('Transferencia rechazada exitosamente.')
    return redirect(url_for('transferencias_pendientes'))


@app.route('/dashboard')
def dashboard():
    cursos = Curso.query.all()
    mis_ventas = []
    cursos_comprados_ids = []
    cursos_pendientes_ids = []
    current_time = datetime.utcnow()

    if current_user.is_authenticated:
        mis_ventas = Venta.query.filter_by(usuario_id=current_user.id).all()
        cursos_comprados_ids = [venta.curso_id for venta in mis_ventas if venta.estado_transferencia ==
                                'confirmada' and venta.fecha_expiracion > current_time]
        cursos_pendientes_ids = [
            venta.curso_id for venta in mis_ventas if venta.estado_transferencia == 'pendiente']

    return render_template('dashboard.html', cursos=cursos, mis_ventas=mis_ventas, cursos_comprados_ids=cursos_comprados_ids, cursos_pendientes_ids=cursos_pendientes_ids, current_time=current_time)


@app.route('/quitar_acceso/<int:venta_id>', methods=['POST'])
@login_required
def quitar_acceso(venta_id):
    if current_user.rol != 'admin':
        flash('No tienes permiso para realizar esta acción.')
        return redirect(url_for('dashboard'))

    venta = Venta.query.get_or_404(venta_id)
    venta.estado_transferencia = 'devuelta'
    db.session.commit()
    flash('Acceso al curso quitado exitosamente.')
    return redirect(url_for('admin_dashboard'))


@app.route('/activar_acceso/<int:venta_id>', methods=['POST'])
@login_required
def activar_acceso(venta_id):
    if current_user.rol != 'admin':
        flash('No tienes permiso para realizar esta acción.')
        return redirect(url_for('dashboard'))

    venta = Venta.query.get_or_404(venta_id)
    venta.estado_transferencia = 'confirmada'
    db.session.commit()
    flash('Acceso al curso activado exitosamente.')
    return redirect(url_for('admin_dashboard'))


@app.route('/health')
def health_check():
    """Health check endpoint for production monitoring"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')

        # Basic application health info
        health_info = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'database': 'connected',
            'environment': os.getenv('FLASK_ENV', 'development')
        }

        return jsonify(health_info), 200
    except Exception as e:
        error_info = {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e),
            'database': 'disconnected'
        }
        return jsonify(error_info), 500


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    init_app()
    # Toma PORT del .env o usa 5004 por defecto
    port = int(os.getenv("PORT", 5004))
    app.run(debug=True, host="0.0.0.0", port=port)
