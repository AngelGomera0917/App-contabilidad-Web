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
@routes.route('/transaccion/<int:id>/eliminar', methods=['POST'])
@login_required  # Solo usuarios logueados pueden eliminar
def eliminar_transaccion(id):
    from app import db  # ✅ Importa `db` dentro de la función (evita import circular)

    transaccion = Transaccion.query.get(id)  # Busca la transacción por ID
    
    if not transaccion:
        return jsonify({"error": "Transacción no encontrada"}), 404  # Error si no existe

    # Verificar que la transacción pertenece al usuario actual
    if transaccion.user_id != current_user.id:
        return jsonify({"error": "No tienes permiso para eliminar esta transacción"}), 403  # Prohibido

    db.session.delete(transaccion)  # Elimina la transacción
    db.session.commit()  # Guarda los cambios

    return redirect(url_for('routes.dashboard'))  # ✅ Redirigir al dashboard después de eliminar

# Ruta protegida del dashboard
@routes.route('/dashboard')
@login_required
def dashboard():
    # Obtener el parámetro 'filtro' de la URL, por defecto 'todos'
    filtro = request.args.get('filtro', 'todos')
    
    # Filtrar las transacciones según el parámetro 'filtro'
    if filtro == 'ingresos':
        transacciones = Transaccion.query.filter_by(user_id=current_user.id, tipo='Ingreso').all()
    elif filtro == 'gastos':
        transacciones = Transaccion.query.filter_by(user_id=current_user.id, tipo='Gasto').all()
    else:
        transacciones = Transaccion.query.filter_by(user_id=current_user.id).all()  # Mostrar todos si no hay filtro
    
    # Calcular los ingresos, gastos y el balance total
    ingresos = sum(t.monto for t in transacciones if t.tipo == 'Ingreso')
    gastos = sum(t.monto for t in transacciones if t.tipo == 'Gasto')
    
    # Si el filtro es 'gastos', no restamos el total de los gastos para que no aparezca negativo
    if filtro == 'gastos':
        balance = gastos  # Solo mostramos los ingresos cuando el filtro es 'gastos'
    else:
        balance = ingresos - gastos  # Calculamos el balance total si el filtro no es 'gastos'
    
    # Retornar la plantilla con las transacciones y el resumen financiero
    return render_template('dashboard.html', 
                           transacciones=transacciones, 
                           ingresos=ingresos, 
                           gastos=gastos, 
                           balance=balance)



# Ruta de cierre de sesión
@routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.login'))  # Usa 'routes.login' para referenciar la ruta de login
# Al usar url_for, cambié login y dashboard por routes.login y routes.dashboard respectivamente, porque ahora las rutas están dentro del blueprint routes.