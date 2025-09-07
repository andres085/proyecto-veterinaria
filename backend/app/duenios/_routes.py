import logging
from flask import Blueprint, request, jsonify

from ._controller import DuenioController
from ..error_handlers import (
    validate_json_request, 
    safe_int_conversion,
    create_error_response,
    log_request_info
)

logger = logging.getLogger(__name__)

duenios_bp = Blueprint('duenios', __name__)

duenios_controller = DuenioController()


@duenios_bp.before_request
def before_request():
    log_request_info()


@duenios_bp.route('/duenios/', methods=['GET'])
@duenios_bp.route('/duenios', methods=['GET'])
def get_all_duenios():
    try:
        limit_param = request.args.get('limit')
        offset_param = request.args.get('offset', '0')
        
        limit = None
        if limit_param:
            limit, error = safe_int_conversion(limit_param, 'limit')
            if error:
                return create_error_response(error, 400, "Parámetro inválido")
        
        offset, error = safe_int_conversion(offset_param, 'offset')
        if error:
            return create_error_response(error, 400, "Parámetro inválido")
        
        response_data, status_code = duenios_controller.get_all(limit=limit, offset=offset)
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error en get_all_duenios route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@duenios_bp.route('/duenios/<int:duenio_id>', methods=['GET'])
def get_duenio(duenio_id):
    try:
        response_data, status_code = duenios_controller.get_one(duenio_id)
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error en get_duenio route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@duenios_bp.route('/duenios/', methods=['POST'])
@duenios_bp.route('/duenios', methods=['POST'])
def create_duenio():
    try:
        json_data, error_response = validate_json_request()
        if error_response:
            return error_response
        
        response_data, status_code = duenios_controller.create(json_data)
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error en create_duenio route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@duenios_bp.route('/duenios/<int:duenio_id>', methods=['PUT'])
def update_duenio(duenio_id):
    try:
        json_data, error_response = validate_json_request()
        if error_response:
            return error_response
        
        response_data, status_code = duenios_controller.update(duenio_id, json_data)
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error en update_duenio route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@duenios_bp.route('/duenios/<int:duenio_id>', methods=['DELETE'])
def delete_duenio(duenio_id):
    try:
        response_data, status_code = duenios_controller.delete(duenio_id)
        
        if status_code == 204:
            return '', 204
        else:
            return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error en delete_duenio route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@duenios_bp.route('/duenios/search', methods=['GET'])
def search_duenios():
    try:
        query = request.args.get('q', '').strip()
        limit_param = request.args.get('limit', '50')
        
        if not query:
            return create_error_response(
                "El parámetro de búsqueda 'q' es requerido", 
                400, 
                "Parámetro faltante"
            )
        
        limit, error = safe_int_conversion(limit_param, 'limit')
        if error:
            limit = 50  # Valor por defecto si hay error
        
        response_data, status_code = duenios_controller.search(query, limit)
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error en search_duenios route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@duenios_bp.route('/duenios/statistics', methods=['GET'])
def get_duenios_statistics():
    try:
        response_data, status_code = duenios_controller.get_statistics()
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error en get_duenios_statistics route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@duenios_bp.errorhandler(404)
def handle_not_found_in_duenios(error):
    return create_error_response(
        "Endpoint no encontrado en el módulo de dueños", 
        404, 
        "Recurso no encontrado"
    )


@duenios_bp.errorhandler(405)
def handle_method_not_allowed_in_duenios(error):
    return create_error_response(
        f"Método {request.method} no permitido para este endpoint", 
        405, 
        "Método no permitido"
    )