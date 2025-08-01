"""
Rutas (endpoints) para el módulo de Turnos
Sistema de gestión de turnos veterinaria - API REST
"""

import logging
from flask import Blueprint, request, jsonify

from ._controller import TurnoController
from ..error_handlers import (
    validate_json_request, 
    safe_int_conversion,
    create_error_response,
    log_request_info
)

# Configurar logger
logger = logging.getLogger(__name__)

# Crear Blueprint para turnos
turnos_bp = Blueprint('turnos', __name__)

# Instanciar controlador
turnos_controller = TurnoController()


@turnos_bp.before_request
def before_request():
    """Log de información de la petición"""
    log_request_info()


@turnos_bp.route('/turnos/', methods=['GET'])
def get_all_turnos():
    """
    GET /api/turnos/
    Obtiene todos los turnos con filtros y paginación opcional
    
    Query Parameters:
        - limit (int, opcional): Número máximo de resultados (1-100)
        - offset (int, opcional): Número de registros a saltar (default: 0)
        - estado (string, opcional): Filtrar por estado ('pendiente', 'confirmado', 'completado', 'cancelado')
        - fecha_desde (string, opcional): Filtrar desde fecha (YYYY-MM-DD)
        - fecha_hasta (string, opcional): Filtrar hasta fecha (YYYY-MM-DD)
    
    Returns:
        JSON: Lista de turnos con datos del dueño y metadata de paginación
    """
    try:
        # Obtener parámetros de query string
        limit_param = request.args.get('limit')
        offset_param = request.args.get('offset', '0')
        estado = request.args.get('estado')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
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
        response_data, status_code = turnos_controller.get_all(
            limit=limit, 
            offset=offset, 
            estado=estado, 
            fecha_desde=fecha_desde, 
            fecha_hasta=fecha_hasta
        )
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error in get_all_turnos route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@turnos_bp.route('/turnos/<int:turno_id>', methods=['GET'])
def get_turno(turno_id):
    """
    GET /api/turnos/:id
    Obtiene un turno específico por ID con datos completos del dueño
    
    Path Parameters:
        - turno_id (int): ID del turno
        
    Returns:
        JSON: Datos del turno con información del dueño o error 404
    """
    try:
        # Flask ya valida que sea int por el <int:turno_id>
        response_data, status_code = turnos_controller.get_one(turno_id)
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error in get_turno route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@turnos_bp.route('/turnos/', methods=['POST'])
def create_turno():
    """
    POST /api/turnos/
    Crea un nuevo turno
    
    Body (JSON):
        - nombre_mascota (string): Nombre de la mascota
        - fecha_turno (string): Fecha y hora del turno (YYYY-MM-DD HH:MM:SS)
        - tratamiento (string): Descripción del tratamiento
        - id_duenio (int): ID del dueño de la mascota
        - estado (string, opcional): Estado inicial ('pendiente' por defecto)
        
    Returns:
        JSON: Turno creado con datos del dueño, status 201 o errores de validación
    """
    try:
        # Validar que sea JSON válido
        json_data, error_response = validate_json_request()
        if error_response:
            return error_response
        
        # Llamar al controlador
        response_data, status_code = turnos_controller.create(json_data)
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error in create_turno route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@turnos_bp.route('/turnos/<int:turno_id>', methods=['PUT'])
def update_turno(turno_id):
    """
    PUT /api/turnos/:id
    Actualiza un turno existente
    
    Path Parameters:
        - turno_id (int): ID del turno a actualizar
        
    Body (JSON):
        - nombre_mascota (string, opcional): Nombre de la mascota
        - fecha_turno (string, opcional): Nueva fecha y hora (solo si estado = 'pendiente')
        - tratamiento (string, opcional): Descripción del tratamiento  
        - id_duenio (int, opcional): Cambiar dueño
        - estado (string, opcional): Nuevo estado
        
    Returns:
        JSON: Turno actualizado o errores de validación
    """
    try:
        # Validar que sea JSON válido
        json_data, error_response = validate_json_request()
        if error_response:
            return error_response
        
        # Llamar al controlador
        response_data, status_code = turnos_controller.update(turno_id, json_data)
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error in update_turno route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@turnos_bp.route('/turnos/<int:turno_id>', methods=['DELETE'])
def delete_turno(turno_id):
    """
    DELETE /api/turnos/:id
    Elimina un turno
    
    Path Parameters:
        - turno_id (int): ID del turno a eliminar
        
    Returns:
        JSON: Confirmación de eliminación con status 204 o error 404
    """
    try:
        # Llamar al controlador
        response_data, status_code = turnos_controller.delete(turno_id)
        
        # Para DELETE exitoso, devolver solo status code sin body
        if status_code == 204:
            return '', 204
        else:
            return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error in delete_turno route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@turnos_bp.route('/turnos/duenio/<int:id_duenio>', methods=['GET'])
def get_turnos_by_duenio(id_duenio):
    """
    GET /api/turnos/duenio/:id_duenio
    Obtiene todos los turnos de un dueño específico
    
    Path Parameters:
        - id_duenio (int): ID del dueño
        
    Query Parameters:
        - limit (int, opcional): Límite de resultados (default: 50, max: 100)
        
    Returns:
        JSON: Lista de turnos del dueño especificado
    """
    try:
        # Obtener límite opcional
        limit_param = request.args.get('limit', '50')
        
        # Convertir límite de forma segura
        limit, error = safe_int_conversion(limit_param, 'limit')
        if error:
            limit = 50  # Valor por defecto si hay error
        
        # Llamar al controlador
        response_data, status_code = turnos_controller.get_by_duenio(id_duenio, limit)
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error in get_turnos_by_duenio route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@turnos_bp.route('/turnos/fecha/<fecha>', methods=['GET'])
def get_turnos_by_fecha(fecha):
    """
    GET /api/turnos/fecha/:fecha
    Obtiene todos los turnos de una fecha específica
    
    Path Parameters:
        - fecha (string): Fecha en formato YYYY-MM-DD
        
    Query Parameters:
        - limit (int, opcional): Límite de resultados (default: 100, max: 200)
        
    Returns:
        JSON: Lista de turnos de la fecha especificada
    """
    try:
        # Obtener límite opcional
        limit_param = request.args.get('limit', '100')
        
        # Convertir límite de forma segura
        limit, error = safe_int_conversion(limit_param, 'limit')
        if error:
            limit = 100  # Valor por defecto si hay error
        
        # Llamar al controlador
        response_data, status_code = turnos_controller.get_by_fecha(fecha, limit)
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error in get_turnos_by_fecha route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@turnos_bp.route('/turnos/<int:turno_id>/estado', methods=['PUT'])
def update_turno_estado(turno_id):
    """
    PUT /api/turnos/:id/estado
    Actualiza solo el estado de un turno con validaciones de transición
    
    Path Parameters:
        - turno_id (int): ID del turno
        
    Body (JSON):
        - estado (string): Nuevo estado ('pendiente', 'confirmado', 'completado', 'cancelado')
        
    Returns:
        JSON: Turno con estado actualizado o errores de validación de transición
    """
    try:
        # Validar que sea JSON válido
        json_data, error_response = validate_json_request()
        if error_response:
            return error_response
        
        # Extraer estado del JSON
        nuevo_estado = json_data.get('estado')
        
        if not nuevo_estado:
            return create_error_response(
                "El campo 'estado' es requerido", 
                400, 
                "Datos faltantes"
            )
        
        # Llamar al controlador
        response_data, status_code = turnos_controller.update_estado(turno_id, nuevo_estado)
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error in update_turno_estado route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@turnos_bp.route('/turnos/statistics', methods=['GET'])
def get_turnos_statistics():
    """
    GET /api/turnos/statistics
    Obtiene estadísticas básicas de turnos
    
    Returns:
        JSON: Estadísticas de turnos (total, por estado, turnos de hoy)
    """
    try:
        response_data, status_code = turnos_controller.get_statistics()
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error in get_turnos_statistics route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


# Manejo de errores específicos del Blueprint
@turnos_bp.errorhandler(404)
def handle_not_found_in_turnos(error):
    """Maneja 404 específicos del módulo turnos"""
    return create_error_response(
        "Endpoint no encontrado en el módulo de turnos", 
        404, 
        "Recurso no encontrado"
    )


@turnos_bp.errorhandler(405)
def handle_method_not_allowed_in_turnos(error):
    """Maneja métodos no permitidos en turnos"""
    return create_error_response(
        f"Método {request.method} no permitido para este endpoint", 
        405, 
        "Método no permitido"
    )