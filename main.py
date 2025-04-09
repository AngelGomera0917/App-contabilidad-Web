# pagina principal de la aplicacion

# app/main.py

from app import create_app, db
from app.models import Usuario, Transaccion
import os  # ✅ necesario para leer el puerto de Railway

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        print("✅ Creando tablas en la base de datos...")
        db.create_all()  # Crea las tablas si no existen

    # ✅ Railway usará su propio puerto, lo leemos desde variables de entorno
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)