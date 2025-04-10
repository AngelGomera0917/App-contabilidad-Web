from app import create_app, db
from app.models import Usuario, Transaccion

# Creamos la app
app = create_app()

# Usamos el contexto de la app para crear las tablas
with app.app_context():
    db.create_all()
    print("✅ Tablas creadas correctamente en la base de datos.")
