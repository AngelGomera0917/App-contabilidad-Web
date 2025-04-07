# Define las rutas y vistas

from flask import render_template, request, redirect, url_for, flash, jsonify, Blueprint
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


# # Ruta para hacer admin a un usuario
# # Esta ruta es solo para propósitos de prueba y no debería estar en producción sin una verificación adecuada

# @routes.route('/hacer_admin')
# @login_required
# def hacer_admin():
#     from app import db
#     current_user.is_admin = True
#     db.session.commit()
#     return "Ahora eres admin"


# Ruta de registro de usuario
@routes.route('/register', methods=['GET', 'POST'])
def register():
    
    from app import db  # ✅ Importa `db` dentro de la función (evita circular import)
    
    # Verificar si ya existe un administrador en la base de datos
    administrador_existente = Usuario.query.filter_by(is_admin=True).first()  # Busca el primer admin
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Imprimir los datos capturados para ver qué valores llegan
        print(f"Username: {username}, Email: {email}, Password: {password}")

        # 📌 Validación: Las contraseñas deben coincidir
        if password != confirm_password:
            flash("⚠️ Las contraseñas no coinciden. Inténtalo de nuevo.", "danger")
            return redirect(url_for('routes.register'))  # Vuelve a la página de registro
        
        # # Si no hay administradores, permitir que el primer usuario sea admin
        if administrador_existente:
            is_admin = False  # Si ya hay un admin, todos los nuevos usuarios serán regulares
        else:
            is_admin = True if request.form.get('is_admin') == 'on' else False  # El primer usuario puede ser admin
        
        # # Validar si el checkbox fue marcado
        # is_admin = True if request.form.get('is_admin') == 'on' else False
        
        

        # 📌 Si las contraseñas coinciden, guardar usuario en la base de datos
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        nuevo_usuario = Usuario(
            username=username, 
            email=email, 
            password=hashed_password,
            is_admin=is_admin
            )
        
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash("✅ Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for('routes.login'))  # Redirige a login

    return render_template('register.html', administrador_existente=administrador_existente) #, administrador_existente=administrador_existente

"""     if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = Usuario(username=username, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('routes.login'))
    return render_template('register.html')""" 



# Ruta de inicio de sesión

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']  # Asegúrate de que el formulario tiene este nombre
        password = request.form['password']  # Lo mismo con el campo de la contraseña
        
        # Consulta al usuario por el nombre de usuario
        user = Usuario.query.filter_by(username=username).first()
        
        # Verifica la contraseña con la función `check_password_hash`
        if user and check_password_hash(user.password, password):
            login_user(user)  # Inicia la sesión del usuario
            return redirect(url_for('routes.dashboard'))  # Redirige al dashboard del usuario
    return render_template('login.html')  # Si no es un POST, renderiza el formulario de login

"""@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('routes.dashboard'))
    return render_template('login.html')"""


# necesito una ruta para listar los usuarios, y otra para eliminar un usuario.

# Ruta para listar usuarios
@routes.route('/usuarios', methods=['GET'])
@login_required  # Solo usuarios logueados pueden ver la lista de usuarios

def listar_usuarios():
    from app import db
    usuarios = Usuario.query.all()  # Obtiene todos los usuarios de la base de datos
    return render_template('usuarios.html', usuarios=usuarios)  # Renderiza la plantilla con la lista de usuarios



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
        
        nueva_transaccion = Transaccion(
            tipo=tipo,
            monto=float(monto),
            descripcion=descripcion,
            usuario_id=current_user.id # Aquí conectas la transacción con el usuario logueado
        )
        
        # 📌 Obtener la hora local en la zona horaria correcta
        zona_horaria = pytz.timezone("America/Santo_Domingo")  # Cambia según tu ubicación
        hora_actual = datetime.now(zona_horaria) 

        # 📌 Guardar la transacción con la fecha y hora correctas
        nueva_transaccion = Transaccion(usuario_id=current_user.id, tipo=tipo, monto=monto, descripcion=descripcion, fecha=hora_actual)
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
    if transaccion.usuario_id != current_user.id:
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
        transacciones = Transaccion.query.filter_by(usuario_id=current_user.id, tipo='Ingreso').all()
    elif filtro == 'gastos':
        transacciones = Transaccion.query.filter_by(usuario_id=current_user.id, tipo='Gasto').all()
    else:
        transacciones = Transaccion.query.filter_by(usuario_id=current_user.id).all()  # Mostrar todos si no hay filtro
        
    usuarios = Usuario.query.all()  # Obtiene todos los usuarios de la base de datos
    
    
    # Calcular los ingresos, gastos y el balance total
    ingresos = sum(t.monto for t in transacciones if t.tipo == 'Ingreso')
    gastos = sum(t.monto for t in transacciones if t.tipo == 'Gasto')
    
    # Si el filtro es 'gastos', no restamos el total de los gastos para que no aparezca negativo
    if filtro == 'gastos':
        balance = gastos  # Solo mostramos los ingresos cuando el filtro es 'gastos'
    else:
        balance = ingresos + gastos  # Calculamos el balance total si el filtro no es 'gastos'
    
    # Retornar la plantilla con las transacciones y el resumen financiero
    return render_template('dashboard.html', 
                            usuarios=usuarios,
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



# Ruta para Eliminar un usuario
@routes.route('/eliminar_usuario/<int:id>', methods=['POST'])  # Usa el método POST
@login_required
def eliminar_usuario(id):
    from app import db  # Importar db dentro de la función para evitar circular imports

    # Buscar el usuario
    usuario = Usuario.query.get(id)

    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for('routes.dashboard'))

    # Asegurarse de que solo un administrador pueda eliminar usuarios
    if not current_user.is_admin:
        flash("No tienes permisos para eliminar usuarios.", "danger")
        return redirect(url_for('routes.dashboard'))

    try:
        # Primero, eliminar las transacciones asociadas al usuario
        if usuario.transacciones:
            print(f"Eliminando transacciones para el usuario: {usuario.username}")
            for transaccion in usuario.transacciones:
                db.session.delete(transaccion)
                
                # Agregar mensaje después de eliminar cada transacción
                print(f"Transacción con ID {transaccion.id} eliminada.")
            flash(f"Transacción con ID {transaccion.id} eliminada correctamente.", "info")
                

        # Luego eliminar el usuario
        print(f"Eliminando usuario: {usuario.username}")
        db.session.delete(usuario)
        db.session.commit()  # Confirmar los cambios

        flash("Usuario eliminado correctamente.", "success")
    except Exception as e:
        db.session.rollback()  # Revertir los cambios en caso de error
        flash(f"Hubo un error al eliminar el usuario: {str(e)}", "danger")

    return redirect(url_for('routes.dashboard'))



# @routes.route('/eliminar_usuario/<int:id>', methods=['POST'])  # Cambiado a 'POST' en lugar de 'GET'
# @login_required
# def eliminar_usuario(id):
#     from app import db  # Importar db dentro de la función (evitar circular import)

#     # Buscar el usuario en la base de datos
#     usuario = Usuario.query.get(id)

#     if not usuario:
#         flash("Usuario no encontrado.", "danger")
#         return redirect(url_for('routes.dashboard'))

#     # Asegurarse de que solo un administrador pueda eliminar usuarios
#     if not current_user.is_admin:
#         flash("No tienes permisos para eliminar usuarios.", "danger")
#         return redirect(url_for('routes.dashboard'))

#     try:
#         # Eliminar todas las transacciones asociadas al usuario
#         for transaccion in usuario.transacciones:
#             db.session.delete(transaccion)

#         # Eliminar el usuario
#         db.session.delete(usuario)
#         db.session.commit()  # Confirmar los cambios en la base de datos

#         flash("Usuario eliminado correctamente.", "success")

#     except Exception as e:
#         db.session.rollback()  # Si ocurre un error, revertir los cambios
#         flash(f"Ocurrió un error al eliminar el usuario: {str(e)}", "danger")

#     return redirect(url_for('routes.dashboard'))



# @routes.route('/eliminar_usuario/<int:id>', methods=['POST'])
# @login_required
# def eliminar_usuario(id):
#     from app import db  # Importa `db` dentro de la función (evita circular import)
    
#     # Busca el usuario en la base de datos
#     usuario = Usuario.query.get(id)

#     if not usuario:
#         flash("Usuario no encontrado.", "danger")
#         return redirect(url_for('routes.dashboard'))

#     # Asegurarse de que solo un administrador pueda eliminar usuarios
#     if not current_user.is_admin:
#         flash("No tienes permisos para eliminar usuarios.", "danger")
#         return redirect(url_for('routes.dashboard'))

#     try:
#         db.session.delete(usuario)
#         db.session.commit()

#         # Verificar cuántas filas fueron afectadas por el commit
#         if db.session.is_active:
#             flash("Usuario eliminado correctamente.", "success")
#         else:
#             flash("Hubo un problema al eliminar el usuario. Intenta nuevamente.", "danger")

#     except Exception as e:
#         db.session.rollback()  # Deshace la transacción en caso de error
#         flash(f"Ocurrió un error al eliminar el usuario: {str(e)}", "danger")

#     return redirect(url_for('routes.dashboard'))



# # Ruta para Eliminar un usuario
# @routes.route('/eliminar_usuario/<int:id>', methods=['POST'])
# @login_required
# def eliminar_usuario(id):
    
#     from app import db  # ✅ Importa `db` dentro de la función (evita circular import)
    
#     # Busca el usuario en la base de datos
#     usuario = Usuario.query.get(id)
    
#     if not usuario:
#         flash("Usuario no encontrado.", "danger")
#         return redirect(url_for('routes.dashboard'))

#     # Asegurarse de que solo un administrador pueda eliminar usuarios
#     if not current_user.is_admin:
#         flash("No tienes permisos para eliminar usuarios.", "danger")
#         return redirect(url_for('routes.dashboard'))
    
#     db.session.delete(usuario)
#     db.session.commit()
    
#     flash("Usuario eliminado correctamente.", "success")
#     return redirect(url_for('routes.dashboard'))





