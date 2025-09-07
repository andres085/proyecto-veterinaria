import logging
from flask import Blueprint, request, jsonify

from ._controller import TurnoController
from ..error_handlers import (
    validate_json_request, 
    safe_int_conversion,
    create_error_response,
    log_request_info
)

logger = logging.getLogger(__name__)

turnos_bp = Blueprint('turnos', __name__)

turnos_controller = TurnoController()


@turnos_bp.before_request
def before_request():
    log_request_info()


@turnos_bp.route('/turnos', methods=['GET'])
def get_all_turnos():
    try:
        limit_param = request.args.get('limit')
        offset_param = request.args.get('offset', '0')
        estado = request.args.get('estado')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        limit = None
        if limit_param:
            limit, error = safe_int_conversion(limit_param, 'limit')
            if error:
                return create_error_response(error, 400, "Parámetro inválido")
        
        offset, error = safe_int_conversion(offset_param, 'offset')
        if error:
            return create_error_response(error, 400, "Parámetro inválido")
        
        response_data, status_code = turnos_controller.get_all(
            limit=limit, 
            offset=offset, 
            estado=estado, 
            fecha_desde=fecha_desde, 
            fecha_hasta=fecha_hasta
        )
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error en get_all_turnos route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@turnos_bp.route('/turnos/<int:turno_id>', methods=['GET'])
def get_turno(turno_id):
    try:
        response_data, status_code = turnos_controller.get_one(turno_id)
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error en get_turno route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@turnos_bp.route('/turnos', methods=['POST'])
def create_turno():
    try:
        json_data, error_response = validate_json_request()
        if error_response:
            return error_response
        
        response_data, status_code = turnos_controller.create(json_data)
        return response_data, status_code
        
    except Exception as e:
        logger.error(f"Error en create_turno route: {e}")
        return create_error_response(
            "Error interno del servidor", 
            500, 
            "Error interno"
        )


@turnos_bp.route('/turnos/<int:turno_id>', methods=['PUT'])
def update_turno(turno_id):
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
    try:
        response_data, status_code = turnos_controller.delete(turno_id)
        
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
    try:
        limit_param = request.args.get('limit', '50')
        
        limit, error = safe_int_conversion(limit_param, 'limit')
        if error:
            limit = 50  # Valor por defecto si hay error
        
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
    try:
        limit_param = request.args.get('limit', '100')
        
        limit, error = safe_int_conversion(limit_param, 'limit')
        if error:
            limit = 100  # Valor por defecto si hay error
        
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
    try:
        json_data, error_response = validate_json_request()
        if error_response:
            return error_response
        
        nuevo_estado = json_data.get('estado')
        
        if not nuevo_estado:
            return create_error_response(
                "El campo 'estado' es requerido", 
                400, 
                "Datos faltantes"
            )
        
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


@turnos_bp.errorhandler(404)
def handle_not_found_in_turnos(error):
    return create_error_response(
        "Endpoint no encontrado en el módulo de turnos", 
        404, 
        "Recurso no encontrado"
    )


@turnos_bp.errorhandler(405)
def handle_method_not_allowed_in_turnos(error):
    return create_error_response(
        f"Método {request.method} no permitido para este endpoint", 
        405, 
        "Método no permitido"
    )