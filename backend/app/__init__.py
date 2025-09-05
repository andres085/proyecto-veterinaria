from flask import Flask
from flask_cors import CORS
from .database import get_db_info
from .error_handlers import register_error_handlers


def create_app():
    
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'veterinaria_secret_development'
    
    CORS(app)
    
    register_error_handlers(app)
    
    from .duenios._routes import duenios_bp
    from .turnos._routes import turnos_bp
    
    app.register_blueprint(duenios_bp, url_prefix='/api')
    app.register_blueprint(turnos_bp, url_prefix='/api')
    
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