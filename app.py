from flask import Flask, render_template, request, redirect, jsonify, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
#from app import db 
import pytz
#from models import Transaccion  # Importa el modelo de transacción


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecreto'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contabilidad.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelo de Usuario
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Transaccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'Ingreso' o 'Gasto'
    monto = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.String(200))
    # fecha = db.Column(db.DateTime, default=datetime.utcnow)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Se actualizará con hora local

    usuario = db.relationship('Usuario', backref=db.backref('transacciones', lazy=True))




@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Ruta de inicio
@app.route('/')
def index():
    return "Bienvenido a la App de Contabilidad"

# Ruta de registro de usuario
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = Usuario(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

# 📌 Ruta para registrar transacciones
@app.route('/transaccion', methods=['GET', 'POST'])
@login_required
def transaccion():
    print("Usuario actual:", current_user)
    if request.method == 'POST':
        tipo = request.form['tipo']
        monto = float(request.form['monto'])
        descripcion = request.form['descripcion']
        
        # 📌 Obtener la hora local en la zona horaria correcta
        zona_horaria = pytz.timezone("America/Santo_Domingo")  # Cambia según tu ubicación
        hora_actual = datetime.now(zona_horaria) 

        # 📌 Guardar la transacción con la fecha y hora correctas
        nueva_transaccion = Transaccion(user_id=current_user.id, tipo=tipo, monto=monto, descripcion=descripcion, fecha=hora_actual)
        db.session.add(nueva_transaccion)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('transaccion.html')


# Ruta para eliminar una transacción
@app.route('/transaccion/<int:id>', methods=['GET', 'POST', 'DELETE'])
@login_required  # Solo usuarios logueados pueden eliminar
def eliminar_transaccion(id):
    transaccion = Transaccion.query.get(id)  # Busca la transacción por ID
    
    if not transaccion:
        return jsonify({"error": "Transacción no encontrada"}), 404  # Error si no existe
    
    db.session.delete(transaccion)  # Elimina la transacción
    db.session.commit()  # Guarda los cambios
    
    return jsonify({"mensaje": "Transacción eliminada correctamente"}), 200  # Respuesta JSON


# Ruta protegida del dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return f"""
    <h1> Bienvenid@, {current_user.username} </h1>
    <a href='{url_for("logout")}' class='btn btn-danger'> Cerrar Sesión </a>
    """


# Ruta de cierre de sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Ejecutar la app en modo debug
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
