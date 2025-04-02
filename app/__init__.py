# Inicializa la app y la base de datos

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager



# Inicialización de la base de datos
db = SQLAlchemy()

# Inicialización de Flask-Login
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecreto'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contabilidad.db'
    
    # Inicializamos la base de datos con la app
    db.init_app(app)
    
    # Inicializamos Flask-Login con la app, Inicializamos el LoginManager con la app
    login_manager.init_app(app)
    login_manager.login_view = 'routes.login'  # Define la vista de login
    
    from .routes import routes  # ✅ Importa después de inicializar `db`
    app.register_blueprint(routes, url_prefix='/')  # 🔹 Registrar Blueprint con prefijo base

    # Importar rutas aquí para evitar dependencias circulares

    return app

# Cargar al usuario desde la base de datos usando su ID
@login_manager.user_loader
def load_user(user_id):
    from .models import Usuario  # Importamos Usuario aquí para evitar el ciclo de importación, # IMPORTAR EL MODELO Usuario El punto (.) hace referencia al directorio actual o al paquete actual. Esto es útil cuando tienes una estructura de proyecto con subcarpetas, y quieres importar un módulo dentro de la misma carpeta o paquete sin tener que especificar toda la ruta.
    
    return Usuario.query.get(int(user_id))

