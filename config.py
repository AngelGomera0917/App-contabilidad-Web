# Configuración de la app

# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate

# # Configuración de la aplicación
# class Config:
#     SECRET_KEY = 'supersecreto'
#     SQLALCHEMY_DATABASE_URI = 'sqlite:///contabilidad.db'
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

# # Inicialización de Flask
# app = Flask(__name__)
# app.config.from_object(Config)

# # Inicialización de SQLAlchemy y Flask-Migrate
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)

# # Tu modelo de datos y rutas aquí...

# if __name__ == '__main__':
#     app.run(debug=True)


import os

class Config:
    SECRET_KEY = 'supersecreto'
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

