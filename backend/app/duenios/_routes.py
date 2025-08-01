"""
Rutas (endpoints) para el módulo de Dueños
Sistema de gestión de turnos veterinaria - API REST
"""

import logging
from flask import Blueprint, request, jsonify

from ._controller import DuenioController
from ..error_handlers import (
    validate_json_request, 
    safe_int_conversion,
    create_error_response,
    log_request_info
)

# Configurar logger
logger = logging.getLogger(__name__)

# Crear Blueprint para dueños
duenios_bp = Blueprint('duenios', __name__)

# Instanciar controlador
duenios_controller = DuenioController()


@duenios_bp.before_request
def before_request():
    """Log de información de la petición"""
    log_request_info()


@duenios_bp.route('/duenios/', methods=['GET'])
def get_all_duenios():
    """
    GET /api/duenios/
    Obtiene todos los dueños con paginación opcional
    
    Query Parameters:
        - limit (int, opcional): Número máximo de resultados (1-100)
        - offset (int, opcional): Número de registros a saltar (default: 0)
    
    Returns:
        JSON: Lista de dueños con metadata de paginación
    """
    try:
        # Obtener parámetros de query string
        limit_param = request.args.get('limit')
        offset_param = request.args.get('offset', '0')
        
        # Convertir parámetros de forma segura  
        limit = None
        if limit_param:
            limit, error = safe_int_conversion(limit_param, 'limit')
            if error:
                return create_error_response(error, 400, "Parámetro inválido")
        
        offset, error = safe_int_conversion(offset_param, 'offset')
        if error:
            return create_error_response(error, 400, "Parámetro inválido")
        
        # Llamar al controlador
        response_data, status_code = duenios_controller.get_all(limit=limit, offset=offset)
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error in get_all_duenios route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@duenios_bp.route('/duenios/<int:duenio_id>', methods=['GET'])
def get_duenio(duenio_id):
    """
    GET /api/duenios/:id
    Obtiene un dueño específico por ID
    
    Path Parameters:
        - duenio_id (int): ID del dueño
        
    Returns:
        JSON: Datos del dueño o error 404
    """
    try:
        # Flask ya valida que sea int por el <int:duenio_id>
        response_data, status_code = duenios_controller.get_one(duenio_id)
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error in get_duenio route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@duenios_bp.route('/duenios/', methods=['POST'])
def create_duenio():
    """
    POST /api/duenios/
    Crea un nuevo dueño
    
    Body (JSON):
        - nombre_apellido (string): Nombre completo del dueño
        - telefono (string): Número de teléfono
        - email (string): Email único
        - direccion (string): Dirección del dueño
        
    Returns:
        JSON: Dueño creado con status 201 o errores de validación
    """
    try:
        # Validar que sea JSON válido
        json_data, error_response = validate_json_request()
        if error_response:
            return error_response
        
        # Llamar al controlador
        response_data, status_code = duenios_controller.create(json_data)
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error in create_duenio route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@duenios_bp.route('/duenios/<int:duenio_id>', methods=['PUT'])
def update_duenio(duenio_id):
    """
    PUT /api/duenios/:id
    Actualiza un dueño existente
    
    Path Parameters:
        - duenio_id (int): ID del dueño a actualizar
        
    Body (JSON):
        - nombre_apellido (string, opcional): Nombre completo
        - telefono (string, opcional): Teléfono  
        - email (string, opcional): Email
        - direccion (string, opcional): Dirección
        
    Returns:
        JSON: Dueño actualizado o errores de validación
    """
    try:
        # Validar que sea JSON válido
        json_data, error_response = validate_json_request()
        if error_response:
            return error_response
        
        # Llamar al controlador
        response_data, status_code = duenios_controller.update(duenio_id, json_data)
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error in update_duenio route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@duenios_bp.route('/duenios/<int:duenio_id>', methods=['DELETE'])
def delete_duenio(duenio_id):
    """
    DELETE /api/duenios/:id
    Elimina un dueño y sus turnos asociados (CASCADE)
    
    Path Parameters:
        - duenio_id (int): ID del dueño a eliminar
        
    Returns:
        JSON: Confirmación de eliminación con status 204 o error 404
    """
    try:
        # Llamar al controlador
        response_data, status_code = duenios_controller.delete(duenio_id)
        
        # Para DELETE exitoso, devolver solo status code sin body
        if status_code == 204:
            return '', 204
        else:
            return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error in delete_duenio route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@duenios_bp.route('/duenios/search', methods=['GET'])
def search_duenios():
    """
    GET /api/duenios/search?q=<query>
    Busca dueños por nombre o email
    
    Query Parameters:
        - q (string, requerido): Término de búsqueda
        - limit (int, opcional): Límite de resultados (default: 50, max: 100)
        
    Returns:
        JSON: Lista de dueños que coinciden con la búsqueda
    """
    try:
        # Obtener parámetros de query
        query = request.args.get('q', '').strip()
        limit_param = request.args.get('limit', '50')
        
        # Validar query requerido
        if not query:
            return create_error_response(
                "El parámetro de búsqueda 'q' es requerido", 
                400, 
                "Parámetro faltante"
            )
        
        # Convertir límite de forma segura
        limit, error = safe_int_conversion(limit_param, 'limit')
        if error:
            limit = 50  # Valor por defecto si hay error
        
        # Llamar al controlador
        response_data, status_code = duenios_controller.search(query, limit)
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error in search_duenios route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@duenios_bp.route('/duenios/statistics', methods=['GET'])
def get_duenios_statistics():
    """
    GET /api/duenios/statistics
    Obtiene estadísticas básicas de dueños
    
    Returns:
        JSON: Estadísticas de dueños
    """
    try:
        response_data, status_code = duenios_controller.get_statistics()
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error in get_duenios_statistics route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


# Manejo de errores específicos del Blueprint
@duenios_bp.errorhandler(404)
def handle_not_found_in_duenios(error):
    """Maneja 404 específicos del módulo dueños"""
    return create_error_response(
        "Endpoint no encontrado en el módulo de dueños", 
        404, 
        "Recurso no encontrado"
    )


@duenios_bp.errorhandler(405)
def handle_method_not_allowed_in_duenios(error):
    """Maneja métodos no permitidos en dueños"""
    return create_error_response(
        f"Método {request.method} no permitido para este endpoint", 
        405, 
        "Método no permitido"
    )