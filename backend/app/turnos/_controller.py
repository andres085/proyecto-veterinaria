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
            logger.error(f"Error in get_all: {e}")
            return create_error_response(
                "Error al obtener los turnos", 
                500, 
                "Error interno"
            )
    
    
    def get_one(self, turno_id: int) -> tuple:
        """
        Obtiene un turno específico por ID
        
        Args:
            turno_id: ID del turno
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Validar ID
            if not isinstance(turno_id, int) or turno_id <= 0:
                return create_error_response(
                    "ID de turno debe ser un número entero positivo", 
                    400, 
                    "Parámetro inválido"
                )
            
            # Obtener turno del modelo
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
            logger.error(f"Error in get_one: {e}")
            return create_error_response(
                "Error al obtener el turno", 
                500, 
                "Error interno"
            )
    
    
    def create(self, data: Dict[str, Any]) -> tuple:
        """
        Crea un nuevo turno
        
        Args:
            data: Datos del turno a crear
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # El modelo ya maneja las validaciones manuales
            result = self.turno_model.create(data)
            
            if result['success']:
                logger.info(f"Created turno ID: {result['turno_id']}")
                
                return create_success_response(
                    data={'turno': result['data']},
                    message="Turno creado correctamente",
                    status_code=201
                )
            else:
                # Errores de validación o FK constraint
                return create_validation_error_response(
                    result['errors'], 
                    400
                )
                
        except Exception as e:
            logger.error(f"Error in create: {e}")
            return create_error_response(
                "Error al crear el turno", 
                500, 
                "Error interno"
            )
    
    
    def update(self, turno_id: int, data: Dict[str, Any]) -> tuple:
        """
        Actualiza un turno existente
        
        Args:
            turno_id: ID del turno a actualizar
            data: Datos a actualizar
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Validar ID
            if not isinstance(turno_id, int) or turno_id <= 0:
                return create_error_response(
                    "ID de turno debe ser un número entero positivo", 
                    400, 
                    "Parámetro inválido"
                )
            
            # Validar que hay datos para actualizar
            if not data:
                return create_error_response(
                    "No se proporcionaron datos para actualizar", 
                    400, 
                    "Datos faltantes"
                )
            
            # El modelo maneja validaciones y verificación de existencia
            result = self.turno_model.update(turno_id, data)
            
            if result['success']:
                logger.info(f"Updated turno ID: {turno_id}")
                
                return create_success_response(
                    data={'turno': result['data']},
                    message="Turno actualizado correctamente"
                )
            else:
                # Errores de validación o turno no encontrado
                return create_validation_error_response(
                    result['errors'], 
                    400
                )
                
        except Exception as e:
            logger.error(f"Error in update: {e}")
            return create_error_response(
                "Error al actualizar el turno", 
                500, 
                "Error interno"
            )
    
    
    def delete(self, turno_id: int) -> tuple:
        """
        Elimina un turno
        
        Args:
            turno_id: ID del turno a eliminar
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Validar ID
            if not isinstance(turno_id, int) or turno_id <= 0:
                return create_error_response(
                    "ID de turno debe ser un número entero positivo", 
                    400, 
                    "Parámetro inválido"
                )
            
            # El modelo maneja la verificación de existencia
            result = self.turno_model.delete(turno_id)
            
            if result['success']:
                logger.info(f"Deleted turno ID: {turno_id}")
                
                return create_success_response(
                    data=None,
                    message=result['message'],
                    status_code=204
                )
            else:
                # Turno no encontrado
                return create_error_response(
                    result['errors'][0] if result['errors'] else "Error al eliminar", 
                    404, 
                    "Recurso no encontrado"
                )
                
        except Exception as e:
            logger.error(f"Error in delete: {e}")
            return create_error_response(
                "Error al eliminar el turno", 
                500, 
                "Error interno"
            )
    
    
    def get_by_duenio(self, id_duenio: int, limit: int = 50) -> tuple:
        """
        Obtiene turnos de un dueño específico
        
        Args:
            id_duenio: ID del dueño
            limit: Límite de resultados
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Validar ID de dueño
            if not isinstance(id_duenio, int) or id_duenio <= 0:
                return create_error_response(
                    "ID de dueño debe ser un número entero positivo", 
                    400, 
                    "Parámetro inválido"
                )
            
            # Validar límite
            if limit <= 0 or limit > 100:
                limit = 50  # Valor por defecto
            
            # Obtener turnos del modelo
            turnos = self.turno_model.get_by_duenio(id_duenio, limit)
            
            # Si la lista está vacía, podría ser que el dueño no existe o no tiene turnos
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
            logger.error(f"Error in get_by_duenio: {e}")
            return create_error_response(
                "Error al obtener turnos del dueño", 
                500, 
                "Error interno"
            )
    
    
    def get_by_fecha(self, fecha: str, limit: int = 100) -> tuple:
        """
        Obtiene turnos por fecha específica
        
        Args:
            fecha: Fecha en formato YYYY-MM-DD
            limit: Límite de resultados
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Validar formato de fecha
            try:
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
            except ValueError:
                return create_error_response(
                    "Fecha debe tener formato YYYY-MM-DD", 
                    400, 
                    "Formato de fecha inválido"
                )
            
            # Validar límite
            if limit <= 0 or limit > 200:
                limit = 100  # Valor por defecto
            
            # Obtener turnos del modelo
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
            logger.error(f"Error in get_by_fecha: {e}")
            return create_error_response(
                "Error al obtener turnos por fecha", 
                500, 
                "Error interno"
            )
    
    
    def update_estado(self, turno_id: int, nuevo_estado: str) -> tuple:
        """
        Actualiza el estado de un turno con validaciones de transición
        
        Args:
            turno_id: ID del turno
            nuevo_estado: Nuevo estado del turno
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Validar ID
            if not isinstance(turno_id, int) or turno_id <= 0:
                return create_error_response(
                    "ID de turno debe ser un número entero positivo", 
                    400, 
                    "Parámetro inválido"
                )
            
            # Validar que se proporciona el estado
            if not nuevo_estado or not nuevo_estado.strip():
                return create_error_response(
                    "El estado es requerido", 
                    400, 
                    "Datos faltantes"
                )
            
            nuevo_estado = nuevo_estado.strip().lower()
            
            # El modelo maneja las validaciones de estado y transiciones
            result = self.turno_model.update_estado(turno_id, nuevo_estado)
            
            if result['success']:
                logger.info(f"Updated estado for turno ID: {turno_id} to: {nuevo_estado}")
                
                return create_success_response(
                    data={'turno': result['data']},
                    message=result.get('message', 'Estado actualizado correctamente')
                )
            else:
                # Errores de validación o turno no encontrado
                return create_validation_error_response(
                    result['errors'], 
                    400
                )
                
        except Exception as e:
            logger.error(f"Error in update_estado: {e}")
            return create_error_response(
                "Error al actualizar el estado del turno", 
                500, 
                "Error interno"
            )
    
    
    def get_statistics(self) -> tuple:
        """
        Obtiene estadísticas básicas de turnos
        
        Returns:
            tuple: (response_data, status_code)  
        """
        try:
            total_turnos = self.turno_model.get_count()
            
            # Estadísticas por estado
            estados = ['pendiente', 'confirmado', 'completado', 'cancelado']
            stats_por_estado = {}
            
            for estado in estados:
                count = self.turno_model.get_count(estado=estado)
                stats_por_estado[estado] = count
            
            # Fecha de hoy para turnos de hoy
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