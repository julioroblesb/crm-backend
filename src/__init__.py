from flask import Flask
from .routes.leads import leads_bp
from .routes.user import user_bp

def register_blueprints(app: Flask):
    """Registra todos los blueprints en la aplicación Flask"""
    
    # Registrar blueprint de leads con prefijo /api
    app.register_blueprint(leads_bp, url_prefix='/api')
    
    # Registrar blueprint de user con prefijo /api  
    app.register_blueprint(user_bp, url_prefix='/api')
    
    print("✅ Blueprints registrados exitosamente")
