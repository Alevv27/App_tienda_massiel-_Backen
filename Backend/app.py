from flask import Flask
from database import init_app, db
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp

app = Flask(__name__)

# Inicializar DB
init_app(app)

# Registrar rutas
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)

if __name__ == "__main__":
    with app.app_context():
        print("🔎 Rutas registradas:")
        print(app.url_map)
    app.run(debug=True)
