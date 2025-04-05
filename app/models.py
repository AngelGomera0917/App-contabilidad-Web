# Define los modelos (Usuario, Transaccion)

from . import db
from flask_login import UserMixin
from datetime import datetime


# Modelo de Usuario
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Agrega el campo email
    is_admin = db.Column(db.Boolean, default=False)  # Agregar el atributo is_admin
    # def __repr__(self):
    #     return f'<Usuario {self.username}>'


class Transaccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'Ingreso' o 'Gasto'
    monto = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.String(200))
    # fecha = db.Column(db.DateTime, default=datetime.utcnow)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Se actualizará con hora local
    
    # # 🔥 Esta línea es la que falta
    # usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
        # Aquí especificamos la clave foránea correcta
    usuario = db.relationship('Usuario', backref='transacciones', foreign_keys=[usuario_id])

    #usuario = db.relationship('Usuario', backref=db.backref('transacciones', lazy=True))