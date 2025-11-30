from flask import Flask
from database import init_app
from api import register_blueprints

app = Flask(__name__)

# Inicializar DB
init_app(app)

# Registrar rutas (capa API)
register_blueprints(app)

if __name__ == "__main__":
    with app.app_context():
        print("🔎 Rutas registradas:")
        print(app.url_map)
    app.run(debug=True)
