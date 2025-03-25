from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # admin, usuario
    compras = db.relationship('Venta', backref='usuario', lazy=True)


class Curso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(500))
    precio = db.Column(db.Float, nullable=False)
    ventas = db.relationship('Venta', backref='curso', lazy=True)


class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey(
        'usuario.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    metodo_pago = db.Column(db.String(50), nullable=False)
    fecha_venta = db.Column(db.DateTime, default=datetime.utcnow)


class HistoricoProgreso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    progreso_id = db.Column(db.Integer, db.ForeignKey(
        'progreso_usuario.id'), nullable=False)
    porcentaje = db.Column(db.Integer)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)


class ProgresoUsuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey(
        'usuario.id'), nullable=False)
    seccion_id = db.Column(db.Integer, db.ForeignKey(
        'seccion.id'), nullable=False)
    progreso = db.Column(db.Float, default=0.0)  # Porcentaje 0-100
    completado = db.Column(db.Boolean, default=False)
    ultima_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)


class Certificado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'))
    fecha_emision = db.Column(db.DateTime, default=datetime.utcnow)
    archivo_path = db.Column(db.String(255))
