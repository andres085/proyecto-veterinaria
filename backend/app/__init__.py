"""
Factory Flask para la aplicación de Veterinaria
Configuración inicial básica para verificar Docker
"""

from flask import Flask
from flask_cors import CORS


def create_app():
    """Factory para crear la aplicación Flask"""
    
    app = Flask(__name__)
    
    # Configurar CORS para permitir comunicación con frontend
    CORS(app, origins=['http://localhost:3000'])
    
    # Configuración básica
    app.config['SECRET_KEY'] = 'veterinaria_secret_development'
    
    # Ruta de prueba básica
    @app.route('/')
    def home():
        return {
            'message': '🐾 API Veterinaria Turnos',
            'status': 'running',
            'version': '1.0.0'
        }
    
    @app.route('/api/health')
    def health():
        return {
            'status': 'healthy',
            'service': 'backend',
            'database': 'pending_connection'
        }
    
    return app