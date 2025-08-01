"""
Factory Flask para la aplicación de Veterinaria
Sistema de Gestión de Turnos con MySQL
"""

from flask import Flask
from .database import get_db_info
from .error_handlers import register_error_handlers


def create_app():
    """Factory para crear la aplicación Flask"""
    
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = 'veterinaria_secret_development'
    
    # Registrar manejadores de errores globales
    register_error_handlers(app)
    
    # Registrar Blueprints
    from .duenios._routes import duenios_bp
    app.register_blueprint(duenios_bp, url_prefix='/api')
    
    # Ruta de prueba básica
    @app.route('/')
    def home():
        return {
            'message': '🐾 API Veterinaria Turnos',
            'status': 'running',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'duenios': '/api/duenios/',
                'search_duenios': '/api/duenios/search?q=',
                'duenios_stats': '/api/duenios/statistics'
            }
        }
    
    @app.route('/api/health')
    def health():
        db_info = get_db_info()
        return {
            'status': 'healthy',
            'service': 'backend',
            'database': db_info,
            'modules': ['duenios']
        }
    
    return app