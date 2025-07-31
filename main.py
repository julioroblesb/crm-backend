import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from models.user import db
from routes.user import user_bp
from routes.leads import leads_bp

# Crear la app y configurar la carpeta de archivos estáticos
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Configurar CORS para permitir requests desde distintos orígenes
CORS(app, origins=[
    'http://localhost:5173', 
    'http://127.0.0.1:5173',
    'https://*.vercel.app',
    'https://*.netlify.app',
    'https://*.railway.app',
    'https://*.render.com'
])

# Crear la carpeta de base de datos si no existe
os.makedirs(os.path.join(os.path.dirname(__file__), 'database'), exist_ok=True)

# Configuración de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# Registrar los blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(leads_bp, url_prefix='/api')

# Endpoint de health check para Railway
@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy", "message": "CRM Backend is running"})

# Servir archivos estáticos o index.html
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    file_path = os.path.join(static_folder_path, path)
    index_path = os.path.join(static_folder_path, 'index.html')

    if path != "" and os.path.exists(file_path):
        return send_from_directory(static_folder_path, path)
    elif os.path.exists(index_path):
        return send_from_directory(static_folder_path, 'index.html')
    else:
        return "index.html not found", 404

# Run app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
