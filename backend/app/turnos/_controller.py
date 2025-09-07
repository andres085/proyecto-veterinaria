import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ._model import TurnoModel
from ..error_handlers import (
    create_success_response, 
    create_error_response, 
    create_validation_error_response,
    safe_int_conversion
)

logger = logging.getLogger(__name__)


class TurnoController:
    
    def __init__(self):
        self.turno_model = TurnoModel()
        logger.debug("TurnoController inicializado")
    
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0, estado: str = None, fecha_desde: str = None, fecha_hasta: str = None) -> tuple:
        try:
            if limit is not None:
                if limit <= 0 or limit > 100:
                    return create_error_response(
                        "El límite debe estar entre 1 y 100", 
                        400, 
                        "Parámetro inválido"
                    )
            
            if offset < 0:
                return create_error_response(
                    "El offset debe ser mayor o igual a 0", 
                    400, 
                    "Parámetro inválido"
                )
            
            if estado:
                estados_validos = ['pendiente', 'confirmado', 'completado', 'cancelado']
                if estado not in estados_validos:
                    return create_error_response(
                        f"Estado inválido. Debe ser uno de: {', '.join(estados_validos)}", 
                        400, 
                        "Parámetro inválido"
                    )
            
            if fecha_desde:
                try:
                    datetime.strptime(fecha_desde, '%Y-%m-%d')
                except ValueError:
                    return create_error_response(
                        "fecha_desde debe tener formato YYYY-MM-DD", 
                        400, 
                        "Formato de fecha inválido"
                    )
            
            if fecha_hasta:
                try:
                    datetime.strptime(fecha_hasta, '%Y-%m-%d')
                except ValueError:
                    return create_error_response(
                        "fecha_hasta debe tener formato YYYY-MM-DD", 
                        400, 
                        "Formato de fecha inválido"
                    )
            
            turnos = self.turno_model.get_all(
                limit=limit, 
                offset=offset, 
                estado=estado, 
                fecha_desde=fecha_desde, 
                fecha_hasta=fecha_hasta
            )
            
            total_count = self.turno_model.get_count(
                estado=estado, 
                fecha_desde=fecha_desde, 
                fecha_hasta=fecha_hasta
            )
            
            metadata = {
                'total': total_count,
                'count': len(turnos),
                'offset': offset,
                'filters': {
                    'estado': estado,
                    'fecha_desde': fecha_desde,
                    'fecha_hasta': fecha_hasta
                }
            }
            
            if limit:
                metadata['limit'] = limit
                metadata['has_more'] = (offset + limit) < total_count
            
            logger.info(f"Recuperado {len(turnos)} turnos (offset: {offset}, limit: {limit}, filters: {estado})")
            
            return create_success_response(
                data={
                    'turnos': turnos,
                    'metadata': metadata
                },
                message="Turnos obtenidos correctamente"
            )
            
        except Exception as e:
            logger.error(f"Error en get_all: {e}")
            return create_error_response(
                "Error al obtener los turnos", 
                500, 
                "Error interno"
            )
    
    
    def get_one(self, turno_id: int) -> tuple:
        try:
            if not isinstance(turno_id, int) or turno_id <= 0:
                return create_error_response(
                    "ID de turno debe ser un número entero positivo", 
                    400, 
                    "Parámetro inválido"
                )
            
            turno = self.turno_model.get_one(turno_id)
            
            if not turno:
                return create_error_response(
                    f"No se encontró un turno con ID: {turno_id}", 
                    404, 
                    "Recurso no encontrado"
                )
            
            logger.info(f"Retrieved turno ID: {turno_id}")
            
            return create_success_response(
                data={'turno': turno},
                message="Turno obtenido correctamente"
            )
            
        except Exception as e:
            logger.error(f"Error en get_one: {e}")
            return create_error_response(
                "Error al obtener el turno", 
                500, 
                "Error interno"
            )
    
    
    def create(self, data: Dict[str, Any]) -> tuple:
        try:
            result = self.turno_model.create(data)
            
            if result['success']:
                logger.info(f"Created turno ID: {result['turno_id']}")
                
                return create_success_response(
                    data={'turno': result['data']},
                    message="Turno creado correctamente",
                    status_code=201
                )
            else:
                return create_validation_error_response(
                    result['errors'], 
                    400
                )
                
        except Exception as e:
            logger.error(f"Error en create: {e}")
            return create_error_response(
                "Error al crear el turno", 
                500, 
                "Error interno"
            )
    
    
    def update(self, turno_id: int, data: Dict[str, Any]) -> tuple:
        try:
            if not isinstance(turno_id, int) or turno_id <= 0:
                return create_error_response(
                    "ID de turno debe ser un número entero positivo", 
                    400, 
                    "Parámetro inválido"
                )
            
            if not data:
                return create_error_response(
                    "No se proporcionaron datos para actualizar", 
                    400, 
                    "Datos faltantes"
                )
            
            result = self.turno_model.update(turno_id, data)
            
            if result['success']:
                logger.info(f"Updated turno ID: {turno_id}")
                
                return create_success_response(
                    data={'turno': result['data']},
                    message="Turno actualizado correctamente"
                )
            else:
                return create_validation_error_response(
                    result['errors'], 
                    400
                )
                
        except Exception as e:
            logger.error(f"Error en update: {e}")
            return create_error_response(
                "Error al actualizar el turno", 
                500, 
                "Error interno"
            )
    
    
    def delete(self, turno_id: int) -> tuple:
        try:
            if not isinstance(turno_id, int) or turno_id <= 0:
                return create_error_response(
                    "ID de turno debe ser un número entero positivo", 
                    400, 
                    "Parámetro inválido"
                )
            
            result = self.turno_model.delete(turno_id)
            
            if result['success']:
                logger.info(f"Deleted turno ID: {turno_id}")
                
                return create_success_response(
                    data=None,
                    message=result['message'],
                    status_code=204
                )
            else:
                return create_error_response(
                    result['errors'][0] if result['errors'] else "Error al eliminar", 
                    404, 
                    "Recurso no encontrado"
                )
                
        except Exception as e:
            logger.error(f"Error en delete: {e}")
            return create_error_response(
                "Error al eliminar el turno", 
                500, 
                "Error interno"
            )
    
    
    def get_by_duenio(self, id_duenio: int, limit: int = 50) -> tuple:
        try:
            if not isinstance(id_duenio, int) or id_duenio <= 0:
                return create_error_response(
                    "ID de dueño debe ser un número entero positivo", 
                    400, 
                    "Parámetro inválido"
                )
            
            if limit <= 0 or limit > 100:
                limit = 50  # Valor por defecto
            
            turnos = self.turno_model.get_by_duenio(id_duenio, limit)
            
            logger.info(f"Retrieved {len(turnos)} turnos for duenio ID: {id_duenio}")
            
            return create_success_response(
                data={
                    'turnos': turnos,
                    'id_duenio': id_duenio,
                    'count': len(turnos),
                    'limit': limit
                },
                message=f"Turnos del dueño obtenidos correctamente: {len(turnos)} encontrados"
            )
            
        except Exception as e:
            logger.error(f"Error en get_by_duenio: {e}")
            return create_error_response(
                "Error al obtener turnos del dueño", 
                500, 
                "Error interno"
            )
    
    
    def get_by_fecha(self, fecha: str, limit: int = 100) -> tuple:
        try:
            try:
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
            except ValueError:
                return create_error_response(
                    "Fecha debe tener formato YYYY-MM-DD", 
                    400, 
                    "Formato de fecha inválido"
                )
            
            if limit <= 0 or limit > 200:
                limit = 100  # Valor por defecto
            
            turnos = self.turno_model.get_by_fecha(fecha, limit)
            
            logger.info(f"Retrieved {len(turnos)} turnos for date: {fecha}")
            
            return create_success_response(
                data={
                    'turnos': turnos,
                    'fecha': fecha,
                    'fecha_formateada': fecha_obj.strftime('%d/%m/%Y'),
                    'dia_semana': fecha_obj.strftime('%A'),
                    'count': len(turnos),
                    'limit': limit
                },
                message=f"Turnos de la fecha obtenidos correctamente: {len(turnos)} encontrados"
            )
            
        except Exception as e:
            logger.error(f"Error en get_by_fecha: {e}")
            return create_error_response(
                "Error al obtener turnos por fecha", 
                500, 
                "Error interno"
            )
    
    
    def update_estado(self, turno_id: int, nuevo_estado: str) -> tuple:
        try:
            if not isinstance(turno_id, int) or turno_id <= 0:
                return create_error_response(
                    "ID de turno debe ser un número entero positivo", 
                    400, 
                    "Parámetro inválido"
                )
            
            if not nuevo_estado or not nuevo_estado.strip():
                return create_error_response(
                    "El estado es requerido", 
                    400, 
                    "Datos faltantes"
                )
            
            nuevo_estado = nuevo_estado.strip().lower()
            
            result = self.turno_model.update_estado(turno_id, nuevo_estado)
            
            if result['success']:
                logger.info(f"Updated estado for turno ID: {turno_id} to: {nuevo_estado}")
                
                return create_success_response(
                    data={'turno': result['data']},
                    message=result.get('message', 'Estado actualizado correctamente')
                )
            else:
                return create_validation_error_response(
                    result['errors'], 
                    400
                )
                
        except Exception as e:
            logger.error(f"Error en update_estado: {e}")
            return create_error_response(
                "Error al actualizar el estado del turno", 
                500, 
                "Error interno"
            )
    
    
    def get_statistics(self) -> tuple:
        try:
            total_turnos = self.turno_model.get_count()
            
            estados = ['pendiente', 'confirmado', 'completado', 'cancelado']
            stats_por_estado = {}
            
            for estado in estados:
                count = self.turno_model.get_count(estado=estado)
                stats_por_estado[estado] = count
            
            fecha_hoy = datetime.now().strftime('%Y-%m-%d')
            turnos_hoy = self.turno_model.get_count(fecha_desde=fecha_hoy, fecha_hasta=fecha_hoy)
            
            stats = {
                'total_turnos': total_turnos,
                'por_estado': stats_por_estado,
                'turnos_hoy': turnos_hoy
            }
            
            return create_success_response(
                data={'statistics': stats},
                message="Estadísticas obtenidas correctamente"
            )
            
        except Exception as e:
            logger.error(f"Error in get_statistics: {e}")
            return create_error_response(
                "Error al obtener estadísticas", 
                500, 
                "Error interno"
            )