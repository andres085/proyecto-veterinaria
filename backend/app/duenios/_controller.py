import logging
from typing import Dict, Any, Optional, List
from flask import request

from ._model import DuenioModel
from ..error_handlers import (
    create_success_response, 
    create_error_response, 
    create_validation_error_response,
    safe_int_conversion
)

logger = logging.getLogger(__name__)


class DuenioController:
    
    def __init__(self):
        self.duenio_model = DuenioModel()
        logger.debug("DuenioController inicializado")
    
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> tuple:
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
            
            duenios = self.duenio_model.get_all(limit=limit, offset=offset)
            
            total_count = self.duenio_model.get_count()
            
            metadata = {
                'total': total_count,
                'count': len(duenios),
                'offset': offset
            }
            
            if limit:
                metadata['limit'] = limit
                metadata['has_more'] = (offset + limit) < total_count
            
            logger.info(f"Retrieved {len(duenios)} dueños (offset: {offset}, limit: {limit})")
            
            return create_success_response(
                data={
                    'duenios': duenios,
                    'metadata': metadata
                },
                message="Dueños obtenidos correctamente"
            )
            
        except Exception as e:
            logger.error(f"Error in get_all: {e}")
            return create_error_response(
                "Error al obtener los dueños", 
                500, 
                "Error interno"
            )
    
    
    def get_one(self, duenio_id: int) -> tuple:
        try:
            if not isinstance(duenio_id, int) or duenio_id <= 0:
                return create_error_response(
                    "ID de dueño debe ser un número entero positivo", 
                    400, 
                    "Parámetro inválido"
                )
            
            duenio = self.duenio_model.get_one(duenio_id)
            
            if not duenio:
                return create_error_response(
                    f"No se encontró un dueño con ID: {duenio_id}", 
                    404, 
                    "Recurso no encontrado"
                )
            
            logger.info(f"Retrieved dueño ID: {duenio_id}")
            
            return create_success_response(
                data={'duenio': duenio},
                message="Dueño obtenido correctamente"
            )
            
        except Exception as e:
            logger.error(f"Error in get_one: {e}")
            return create_error_response(
                "Error al obtener el dueño", 
                500, 
                "Error interno"
            )
    
    
    def create(self, data: Dict[str, Any]) -> tuple:
        try:
            result = self.duenio_model.create(data)
            
            if result['success']:
                logger.info(f"Created dueño ID: {result['duenio_id']}")
                
                return create_success_response(
                    data={'duenio': result['data']},
                    message="Dueño creado correctamente",
                    status_code=201
                )
            else:
                # Errores de validación o duplicados
                return create_validation_error_response(
                    result['errors'], 
                    400
                )
                
        except Exception as e:
            logger.error(f"Error in create: {e}")
            return create_error_response(
                "Error al crear el dueño", 
                500, 
                "Error interno"
            )
    
    
    def update(self, duenio_id: int, data: Dict[str, Any]) -> tuple:
        """
        Actualiza un dueño existente
        
        Args:
            duenio_id: ID del dueño a actualizar
            data: Datos a actualizar
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Validar ID
            if not isinstance(duenio_id, int) or duenio_id <= 0:
                return create_error_response(
                    "ID de dueño debe ser un número entero positivo", 
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
            result = self.duenio_model.update(duenio_id, data)
            
            if result['success']:
                logger.info(f"Updated dueño ID: {duenio_id}")
                
                return create_success_response(
                    data={'duenio': result['data']},
                    message="Dueño actualizado correctamente"
                )
            else:
                # Errores de validación o dueño no encontrado
                return create_validation_error_response(
                    result['errors'], 
                    400
                )
                
        except Exception as e:
            logger.error(f"Error in update: {e}")
            return create_error_response(
                "Error al actualizar el dueño", 
                500, 
                "Error interno"
            )
    
    
    def delete(self, duenio_id: int) -> tuple:
        try:
            if not isinstance(duenio_id, int) or duenio_id <= 0:
                return create_error_response(
                    "ID de dueño debe ser un número entero positivo", 
                    400, 
                    "Parámetro inválido"
                )
            
            result = self.duenio_model.delete(duenio_id)
            
            if result['success']:
                logger.info(f"Deleted dueño ID: {duenio_id}")
                
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
            logger.error(f"Error in delete: {e}")
            return create_error_response(
                "Error al eliminar el dueño", 
                500, 
                "Error interno"
            )
    
    
    def search(self, query: str, limit: int = 50) -> tuple:
        try:
            if not query or not query.strip():
                return create_error_response(
                    "El parámetro de búsqueda 'q' es requerido", 
                    400, 
                    "Parámetro faltante"
                )
            
            query = query.strip()
            
            if len(query) < 2:
                return create_error_response(
                    "El término de búsqueda debe tener al menos 2 caracteres", 
                    400, 
                    "Parámetro inválido"
                )
            
            if limit <= 0 or limit > 100:
                limit = 50  # Valor por defecto
            
            duenios = self.duenio_model.search(query, limit)
            
            logger.info(f"Search '{query}' returned {len(duenios)} results")
            
            return create_success_response(
                data={
                    'duenios': duenios,
                    'query': query,
                    'count': len(duenios),
                    'limit': limit
                },
                message=f"Búsqueda completada: {len(duenios)} resultados"
            )
            
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return create_error_response(
                "Error al realizar la búsqueda", 
                500, 
                "Error interno"
            )
    
    
    def get_statistics(self) -> tuple:
        try:
            total_duenios = self.duenio_model.get_count()
            
            stats = {
                'total_duenios': total_duenios
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