import os
from app import create_app

if __name__ == '__main__':
    app = create_app()
    
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    
    print("Iniciando servidor Flask...")
    print(f"Puerto: {port}")
    print(f"Debug: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )