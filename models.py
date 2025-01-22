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
