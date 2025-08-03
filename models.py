from datetime import datetime
from flask_login import UserMixin
from extensions import db


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.String(250), nullable=False)
    rol = db.Column(db.String(20), nullable=False)

    # Relaciones
    certificados = db.relationship('Certificado', backref='usuario', lazy=True)
    progresos = db.relationship(
        'ProgresoUsuario', backref='usuario', lazy=True)
    ventas = db.relationship('Venta', backref='usuario', lazy=True)


class Curso(db.Model):
    __tablename__ = 'curso'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(500))
    precio = db.Column(db.Float, nullable=False)

    # Relaciones
    secciones = db.relationship('Seccion', backref='curso', lazy=True)
    certificados = db.relationship('Certificado', backref='curso', lazy=True)
    progresos = db.relationship('ProgresoUsuario', backref='curso', lazy=True)
    ventas = db.relationship('Venta', backref='curso', lazy=True)


class Seccion(db.Model):
    __tablename__ = 'seccion'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(500))
    video_url = db.Column(db.String(200))
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    es_gratis = db.Column(db.Boolean, default=False)
    video_file = db.Column(db.String(200))

    # Relaciones
    progresos = db.relationship(
        'ProgresoUsuario', backref='seccion', lazy=True)


class ProgresoUsuario(db.Model):
    __tablename__ = 'progreso_usuario'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey(
        'usuario.id'), nullable=False)
    seccion_id = db.Column(db.Integer, db.ForeignKey(
        'seccion.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    progreso = db.Column(db.Numeric(5, 2), default=0)  # 0.00 a 100.00
    completado = db.Column(db.Boolean, default=False)
    ultima_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_completado = db.Column(db.DateTime)
    tiempo_total_visto = db.Column(db.Integer, default=0)  # en segundos

    # Relación con histórico
    historicos = db.relationship(
        'HistoricoProgreso', backref='progreso', lazy=True)


class HistoricoProgreso(db.Model):
    __tablename__ = 'historico_progreso'

    id = db.Column(db.Integer, primary_key=True)
    progreso_id = db.Column(db.Integer, db.ForeignKey(
        'progreso_usuario.id'), nullable=False)
    progreso_anterior = db.Column(db.Numeric(5, 2))
    progreso_nuevo = db.Column(db.Numeric(5, 2))
    fecha_cambio = db.Column(db.DateTime, default=datetime.utcnow)
    tipo_cambio = db.Column(db.String(20))


class Certificado(db.Model):
    __tablename__ = 'certificado'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey(
        'usuario.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    fecha_emision = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_completado = db.Column(db.DateTime)
    archivo_path = db.Column(db.String(255))
    horas_curso = db.Column(db.Numeric(4, 1))  # 999.9 horas máximo
    url_verificacion = db.Column(db.String(255))
    valido = db.Column(db.Boolean, default=True)


class Venta(db.Model):
    __tablename__ = 'venta'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey(
        'usuario.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    metodo_pago = db.Column(db.String(50), nullable=False)
    fecha_venta = db.Column(db.DateTime, default=datetime.utcnow)
    estado_transferencia = db.Column(db.String(20))
    fecha_expiracion = db.Column(db.DateTime)
