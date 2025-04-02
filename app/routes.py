# Define las rutas y vistas

from flask import render_template, request, redirect, url_for, jsonify, Blueprint
from flask_login import login_user, login_required, logout_user, current_user
#from app import db
from app.models import Usuario, Transaccion
from werkzeug.security import generate_password_hash, check_password_hash
import pytz
from datetime import datetime

routes = Blueprint('routes', __name__)
app = routes  # Esto permite que las rutas se registren correctamente

# # Aquí importas la función create_app desde __init__.py
# from . import create_app

# # Aquí obtienes la instancia de la aplicación
# app = create_app()

# Ruta de inicio
@routes.route('/')
def index():
    return "Bienvenido a la App de Contabilidad"


# Ruta de registro de usuario
@routes.route('/register', methods=['GET', 'POST'])
def register():
    
    from app import db  # ✅ Importa `db` dentro de la función (evita circular import)
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = Usuario(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('routes.login'))
    return render_template('register.html')


# Ruta de inicio de sesión
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('routes.dashboard'))
    return render_template('login.html')


# 📌 Ruta para registrar transacciones
@routes.route('/transaccion', methods=['GET', 'POST'])
@login_required
def transaccion():
    
    from app import db  # ✅ Importa `db` dentro de la función (evita circular import)
    print("Usuario actual:", current_user)
    
    if request.method == 'POST':
        tipo = request.form['Tipo']
        monto = float(request.form['Monto'])
        descripcion = request.form['Descripcion']
        
        # 📌 Obtener la hora local en la zona horaria correcta
        zona_horaria = pytz.timezone("America/Santo_Domingo")  # Cambia según tu ubicación
        hora_actual = datetime.now(zona_horaria) 

        # 📌 Guardar la transacción con la fecha y hora correctas
        nueva_transaccion = Transaccion(user_id=current_user.id, tipo=tipo, monto=monto, descripcion=descripcion, fecha=hora_actual)
        db.session.add(nueva_transaccion)
        db.session.commit()

        return redirect(url_for('routes.dashboard')) # Usa 'routes.dashboard' para referenciar el dashboard

    return render_template('transaccion.html')


# Ruta para eliminar una transacción
@routes.route('/transaccion/<int:id>', methods=['GET', 'POST', 'DELETE'])
@login_required  # Solo usuarios logueados pueden eliminar
def eliminar_transaccion(id):
    
    from app import db  # ✅ Importa `db` dentro de la función (evita circular import)
    
    transaccion = Transaccion.query.get(id)  # Busca la transacción por ID
    
    if not transaccion:
        return jsonify({"error": "Transacción no encontrada"}), 404  # Error si no existe
    
    db.session.delete(transaccion)  # Elimina la transacción
    db.session.commit()  # Guarda los cambios
    
    return jsonify({"mensaje": "Transacción eliminada correctamente"}), 200  # Respuesta JSON


# Ruta protegida del dashboard
@routes.route('/dashboard')
@login_required
def dashboard():
    return f"""
    <h1> Bienvenid@, {current_user.username} </h1>
    <a href='{url_for("routes.logout")}' class='btn btn-danger'> Cerrar Sesión </a>
    """


# Ruta de cierre de sesión
@routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.login'))  # Usa 'routes.login' para referenciar la ruta de login
# Al usar url_for, cambié login y dashboard por routes.login y routes.dashboard respectivamente, porque ahora las rutas están dentro del blueprint routes.