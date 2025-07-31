"""
Manejadores de errores globales para la aplicación Flask
Sistema de Gestión de Turnos - Veterinaria
"""

import logging
from flask import jsonify, request
from mysql.connector import Error as MySQLError
from datetime import datetime

# Configurar logger
logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """
    Registra los manejadores de errores globales en la aplicación Flask
    
    Args:
        app: Instancia de Flask
    """
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Maneja errores de petición inválida (400)"""
        logger.warning(f"Bad Request 400: {error} - URL: {request.url}")
        
        return jsonify({
            'error': 'Petición inválida',
            'message': str(error.description) if hasattr(error, 'description') else 'Datos enviados no válidos',
            'code': 400,
            'timestamp': datetime.now().isoformat()
        }), 400
    
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Maneja errores de recurso no encontrado (404)"""
        logger.warning(f"Not Found 404: {error} - URL: {request.url}")
        
        return jsonify({
            'error': 'Recurso no encontrado',
            'message': 'El recurso solicitado no existe',
            'code': 404,
            'timestamp': datetime.now().isoformat()
        }), 404
    
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Maneja errores de método no permitido (405)"""
        logger.warning(f"Method Not Allowed 405: {error} - URL: {request.url}")
        
        return jsonify({
            'error': 'Método no permitido',
            'message': f'El método {request.method} no está permitido para esta URL',
            'code': 405,
            'timestamp': datetime.now().isoformat()
        }), 405
    
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Maneja errores internos del servidor (500)"""
        logger.error(f"Internal Server Error 500: {error} - URL: {request.url}")
        
        return jsonify({
            'error': 'Error interno del servidor',
            'message': 'Ha ocurrido un error inesperado',
            'code': 500,
            'timestamp': datetime.now().isoformat()
        }), 500
    
    
    @app.errorhandler(MySQLError)
    def handle_mysql_error(error):
        """Maneja errores específicos de MySQL"""
        logger.error(f"MySQL Error: {error} - URL: {request.url}")
        
        # Diferentes tipos de errores MySQL
        error_code = getattr(error, 'errno', None)
        error_msg = str(error)
        
        # Errores comunes de MySQL
        if error_code == 1062:  # Duplicate entry
            return jsonify({
                'error': 'Valor duplicado',
                'message': 'El registro ya existe (email duplicado)',
                'code': 400,
                'timestamp': datetime.now().isoformat()
            }), 400
        
        elif error_code == 1452:  # Foreign key constraint fails
            return jsonify({
                'error': 'Referencia inválida',
                'message': 'El ID de dueño especificado no existe',
                'code': 400,
                'timestamp': datetime.now().isoformat()
            }), 400
        
        elif error_code == 1146:  # Table doesn't exist
            logger.critical(f"Table doesn't exist: {error_msg}")
            return jsonify({
                'error': 'Error de configuración',
                'message': 'Base de datos no configurada correctamente',
                'code': 500,
                'timestamp': datetime.now().isoformat()
            }), 500
        
        else:
            # Error genérico de base de datos
            return jsonify({
                'error': 'Error de base de datos',
                'message': 'Error al procesar la operación en la base de datos',
                'code': 500,
                'timestamp': datetime.now().isoformat()
            }), 500
    
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Maneja errores no esperados"""
        logger.exception(f"Unexpected Error: {error} - URL: {request.url}")
        
        return jsonify({
            'error': 'Error inesperado',
            'message': 'Ha ocurrido un error no esperado',
            'code': 500,
            'timestamp': datetime.now().isoformat()
        }), 500


def create_validation_error_response(errors, status_code=400):
    """
    Crea una respuesta JSON estándar para errores de validación
    
    Args:
        errors: Lista de errores de validación o string único
        status_code: Código de estado HTTP (por defecto 400)
        
    Returns:
        Response: Respuesta JSON con formato estándar
    """
    if isinstance(errors, str):
        errors = [errors]
    
    return jsonify({
        'error': 'Error de validación',
        'message': 'Los datos enviados no son válidos',
        'validation_errors': errors,
        'code': status_code,
        'timestamp': datetime.now().isoformat()
    }), status_code


def create_success_response(data=None, message="Operación exitosa", status_code=200):
    """
    Crea una respuesta JSON estándar para operaciones exitosas
    
    Args:
        data: Datos a incluir en la respuesta
        message: Mensaje de éxito
        status_code: Código de estado HTTP (por defecto 200)
        
    Returns:
        Response: Respuesta JSON con formato estándar
    """
    response = {
        'success': True,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code


def create_error_response(error_message, status_code=400, error_type="Error"):
    """
    Crea una respuesta JSON estándar para errores
    
    Args:
        error_message: Mensaje de error
        status_code: Código de estado HTTP
        error_type: Tipo de error
        
    Returns:
        Response: Respuesta JSON con formato estándar
    """
    return jsonify({
        'error': error_type,
        'message': error_message,
        'code': status_code,
        'timestamp': datetime.now().isoformat()
    }), status_code


def log_request_info():
    """
    Registra información de la petición para debugging
    """
    if request.method in ['POST', 'PUT', 'PATCH']:
        logger.info(f"{request.method} {request.url} - Content-Type: {request.content_type}")
        if request.is_json:
            logger.debug(f"Request JSON: {request.get_json()}")
    else:
        logger.info(f"{request.method} {request.url}")


def safe_int_conversion(value, field_name):
    """
    Convierte un valor a entero de forma segura
    
    Args:
        value: Valor a convertir
        field_name: Nombre del campo para el error
        
    Returns:
        tuple: (int_value, error_message)
    """
    try:
        return int(value), None
    except (ValueError, TypeError):
        return None, f"El campo '{field_name}' debe ser un número entero válido"


def validate_json_request():
    """
    Valida que la petición tenga JSON válido
    
    Returns:
        tuple: (json_data, error_response)
    """
    if not request.is_json:
        error_response = create_error_response(
            "Content-Type debe ser application/json", 
            400, 
            "Formato inválido"
        )
        return None, error_response
    
    try:
        json_data = request.get_json()
        if json_data is None:
            error_response = create_error_response(
                "JSON inválido o vacío", 
                400, 
                "Formato inválido"
            )
            return None, error_response
        
        return json_data, None
    
    except Exception as e:
        logger.error(f"Error parsing JSON: {e}")
        error_response = create_error_response(
            "JSON malformado", 
            400, 
            "Formato inválido"
        )
        return None, error_response