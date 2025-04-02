# Configuración de la app

class Config:
    SECRET_KEY = 'supersecreto'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///contabilidad.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
