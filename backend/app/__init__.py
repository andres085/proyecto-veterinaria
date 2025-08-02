"""
Factory Flask para la aplicación de Veterinaria
Sistema de Gestión de Turnos con MySQL
"""

from flask import Flask
from flask_cors import CORS
from .database import get_db_info
from .error_handlers import register_error_handlers


def create_app():
    """Factory para crear la aplicación Flask"""
    
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = 'veterinaria_secret_development'
    
    # Configuración CORS para desarrollo
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"],
            "supports_credentials": False
        }
    })
    
    # Registrar manejadores de errores globales
    register_error_handlers(app)
    
    # Registrar Blueprints
    from .duenios._routes import duenios_bp
    from .turnos._routes import turnos_bp
    
    app.register_blueprint(duenios_bp, url_prefix='/api')
    app.register_blueprint(turnos_bp, url_prefix='/api')
    
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
                'duenios_stats': '/api/duenios/statistics',
                'turnos': '/api/turnos/',
                'turnos_por_duenio': '/api/turnos/duenio/:id_duenio',
                'turnos_por_fecha': '/api/turnos/fecha/:fecha',
                'cambiar_estado_turno': '/api/turnos/:id/estado',
                'turnos_stats': '/api/turnos/statistics'
            }
        }
    
    @app.route('/api/health')
    def health():
        db_info = get_db_info()
        return {
            'status': 'healthy',
            'service': 'backend',
            'database': db_info,
            'modules': ['duenios', 'turnos']
        }
    
    return app