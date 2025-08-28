import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from mysql.connector import Error as MySQLError

from ..database import get_db_connection, execute_query, execute_transaction
from ..validators import validate_turno_data, validate_turno_update_data
from ..duenios._model import DuenioModel

logger = logging.getLogger(__name__)


class TurnoModel:
    
    def __init__(self):
        self.table_name = "turnos"
        self.duenio_model = DuenioModel()
        logger.debug("TurnoModel inicializado")
    
    
    def get_all(self, limit: int = None, offset: int = 0, estado: str = None, fecha_desde: str = None, fecha_hasta: str = None) -> List[Dict[str, Any]]:
        try:
            query = f"""
                SELECT 
                    t.id, t.nombre_mascota, t.fecha_turno, t.tratamiento, 
                    t.id_duenio, t.estado, t.created_at, t.updated_at,
                    d.nombre_apellido, d.telefono, d.email, d.direccion
                FROM {self.table_name} t
                JOIN duenios d ON t.id_duenio = d.id
                WHERE 1=1
            """
            
            params = []
            
            # Agregar filtros dinámicamente
            if estado:
                query += " AND t.estado = %s"
                params.append(estado)
            
            if fecha_desde:
                query += " AND DATE(t.fecha_turno) >= %s"
                params.append(fecha_desde)
            
            if fecha_hasta:
                query += " AND DATE(t.fecha_turno) <= %s"
                params.append(fecha_hasta)
            
            # Ordenar por fecha más reciente primero
            query += " ORDER BY t.fecha_turno DESC"
            
            # Agregar paginación si se especifica
            if limit is not None:
                query += " LIMIT %s OFFSET %s"
                params.extend([limit, offset])
            
            result = execute_query(query, tuple(params), fetch=True)
            
            # Serializar resultados
            turnos = [self._serialize_turno_with_duenio(row) for row in result] if result else []
            
            logger.info(f"Retrieved {len(turnos)} turnos from database")
            return turnos
            
        except MySQLError as e:
            logger.error(f"MySQL error in get_all: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_all: {e}")
            raise
    
    
    def get_one(self, turno_id: int) -> Optional[Dict[str, Any]]:
        try:
            if not isinstance(turno_id, int) or turno_id <= 0:
                logger.warning(f"Invalid turno_id: {turno_id}")
                return None
            
            query = f"""
                SELECT 
                    t.id, t.nombre_mascota, t.fecha_turno, t.tratamiento,
                    t.id_duenio, t.estado, t.created_at, t.updated_at,
                    d.nombre_apellido, d.telefono, d.email, d.direccion
                FROM {self.table_name} t
                JOIN duenios d ON t.id_duenio = d.id
                WHERE t.id = %s
            """
            
            result = execute_query(query, (turno_id,), fetch_one=True)
            
            if not result:
                logger.debug(f"No turno found with ID {turno_id}")
                return None

            turno = self._serialize_turno_with_duenio(result)
            logger.debug(f"Found turno with ID {turno_id}")
            return turno
                
        except MySQLError as e:
            logger.error(f"MySQL error in get_one: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_one: {e}")
            raise
    
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            validation_result = validate_turno_data(data, self.duenio_model.exists)
            
            if not validation_result['is_valid']:
                logger.warning(f"Validation failed for create: {validation_result['errors']}")
                return {
                    'success': False,
                    'errors': validation_result['errors']
                }
            
            estado = data.get('estado', 'pendiente')
            
            query = f"""
                INSERT INTO {self.table_name} 
                (nombre_mascota, fecha_turno, tratamiento, id_duenio, estado)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            params = (
                data['nombre_mascota'].strip(),
                data['fecha_turno'],
                data['tratamiento'].strip(),
                int(data['id_duenio']),
                estado
            )
            
            # Ejecutar inserción
            turno_id = execute_query(query, params)
            
            if not turno_id:
                logger.error("Failed to create turno - no ID returned")
                return {
                    'success': False,
                    'errors': ['Error al crear el turno']
                }

            logger.info(f"Created new turno with ID: {turno_id}")
            
            new_turno = self.get_one(turno_id)
            
            return {
                'success': True,
                'data': new_turno,
                'turno_id': turno_id
            }
                
        except MySQLError as e:
            logger.error(f"MySQL error in create: {e}")
            
            # Manejar errores específicos de MySQL
            if e.errno == 1452:  # Foreign key constraint fails
                return {
                    'success': False, 
                    'errors': ['El dueño especificado no existe']
                }
            else:
                raise
                
        except Exception as e:
            logger.error(f"Unexpected error in create: {e}")
            raise
    
    
    def update(self, turno_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Verificar que el turno existe
            existing_turno = self.get_one(turno_id)
            if not existing_turno:
                return {
                    'success': False,
                    'errors': [f'No existe un turno con ID: {turno_id}']
                }
            
            # Validar datos (solo los campos presentes)
            if data:
                validation_result = validate_turno_update_data(data, self.duenio_model.exists)
                if not validation_result['is_valid']:
                    logger.warning(f"Validation failed for update: {validation_result['errors']}")
                    return {
                        'success': False,
                        'errors': validation_result['errors']
                    }
            
            # Validación de lógica de negocio: solo permitir cambios de fecha si estado es 'pendiente'
            if 'fecha_turno' in data and existing_turno['estado'] not in ['pendiente']:
                return {
                    'success': False,
                    'errors': ['Solo se puede cambiar la fecha de turnos pendientes']
                }
            
            # Construir query UPDATE dinámicamente
            update_fields = []
            params = []
            
            allowed_fields = ['nombre_mascota', 'fecha_turno', 'tratamiento', 'id_duenio', 'estado']
            
            for field in allowed_fields:
                if field in data:
                    update_fields.append(f"{field} = %s")
                    
                    # Procesamiento especial por campo
                    if field in ['nombre_mascota', 'tratamiento']:
                        params.append(data[field].strip())
                    elif field == 'id_duenio':
                        params.append(int(data[field]))
                    else:
                        params.append(data[field])
            
            if not update_fields:
                return {
                    'success': False,
                    'errors': ['No hay campos para actualizar']
                }
            
            # Agregar ID al final de los parámetros
            params.append(turno_id)
            
            query = f"""
                UPDATE {self.table_name}
                SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            # Ejecutar actualización
            rows_affected = execute_query(query, tuple(params))
            
            if rows_affected > 0:
                logger.info(f"Updated turno ID: {turno_id}")
                
                # Obtener el registro actualizado
                updated_turno = self.get_one(turno_id)
                
                return {
                    'success': True,
                    'data': updated_turno
                }
            else:
                return {
                    'success': False,
                    'errors': ['No se pudo actualizar el turno']
                }
                
        except MySQLError as e:
            logger.error(f"MySQL error in update: {e}")
            
            if e.errno == 1452:  # Foreign key constraint fails
                return {
                    'success': False,
                    'errors': ['El dueño especificado no existe']
                }
            else:
                raise
                
        except Exception as e:
            logger.error(f"Unexpected error in update: {e}")
            raise
    
    
    def delete(self, turno_id: int) -> Dict[str, Any]:
        try:
            # Verificar que el turno existe
            existing_turno = self.get_one(turno_id)
            if not existing_turno:
                return {
                    'success': False,
                    'errors': [f'No existe un turno con ID: {turno_id}']
                }
            
            # Eliminar turno
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            rows_affected = execute_query(query, (turno_id,))
            
            if rows_affected > 0:
                logger.info(f"Deleted turno ID: {turno_id}")
                return {
                    'success': True,
                    'message': f'Turno eliminado correctamente'
                }
            else:
                return {
                    'success': False,
                    'errors': ['No se pudo eliminar el turno']
                }
                
        except MySQLError as e:
            logger.error(f"MySQL error in delete: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in delete: {e}")
            raise
    
    
    def get_by_duenio(self, id_duenio: int, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            # Verificar que el dueño existe
            if not self.duenio_model.exists(id_duenio):
                logger.warning(f"Duenio with ID {id_duenio} does not exist")
                return []
            
            query = f"""
                SELECT 
                    t.id, t.nombre_mascota, t.fecha_turno, t.tratamiento,
                    t.id_duenio, t.estado, t.created_at, t.updated_at,
                    d.nombre_apellido, d.telefono, d.email, d.direccion
                FROM {self.table_name} t
                JOIN duenios d ON t.id_duenio = d.id
                WHERE t.id_duenio = %s
                ORDER BY t.fecha_turno DESC
                LIMIT %s
            """
            
            result = execute_query(query, (id_duenio, limit), fetch=True)
            
            # Serializar resultados
            turnos = [self._serialize_turno_with_duenio(row) for row in result] if result else []
            
            logger.info(f"Retrieved {len(turnos)} turnos for duenio ID: {id_duenio}")
            return turnos
            
        except MySQLError as e:
            logger.error(f"MySQL error in get_by_duenio: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_by_duenio: {e}")
            raise
    
    
    def get_by_fecha(self, fecha: str, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            # Validar formato de fecha
            try:
                datetime.strptime(fecha, '%Y-%m-%d')
            except ValueError:
                logger.warning(f"Invalid date format: {fecha}")
                return []
            
            query = f"""
                SELECT 
                    t.id, t.nombre_mascota, t.fecha_turno, t.tratamiento,
                    t.id_duenio, t.estado, t.created_at, t.updated_at,
                    d.nombre_apellido, d.telefono, d.email, d.direccion
                FROM {self.table_name} t
                JOIN duenios d ON t.id_duenio = d.id
                WHERE DATE(t.fecha_turno) = %s
                ORDER BY t.fecha_turno ASC
                LIMIT %s
            """
            
            result = execute_query(query, (fecha, limit), fetch=True)
            
            # Serializar resultados
            turnos = [self._serialize_turno_with_duenio(row) for row in result] if result else []
            
            logger.info(f"Retrieved {len(turnos)} turnos for date: {fecha}")
            return turnos
            
        except MySQLError as e:
            logger.error(f"MySQL error in get_by_fecha: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_by_fecha: {e}")
            raise
    
    
    def update_estado(self, turno_id: int, nuevo_estado: str) -> Dict[str, Any]:
        try:
            # Verificar que el turno existe
            existing_turno = self.get_one(turno_id)
            if not existing_turno:
                return {
                    'success': False,
                    'errors': [f'No existe un turno con ID: {turno_id}']
                }
            
            # Validar estado válido
            estados_validos = ['pendiente', 'confirmado', 'completado', 'cancelado']
            if nuevo_estado not in estados_validos:
                return {
                    'success': False,
                    'errors': [f'Estado inválido. Debe ser uno de: {", ".join(estados_validos)}']
                }
            
            # Validar transiciones de estado (lógica de negocio)
            estado_actual = existing_turno['estado']
            
            # Transiciones válidas
            transiciones_validas = {
                'pendiente': ['confirmado', 'cancelado'],
                'confirmado': ['completado', 'cancelado'],  
                'completado': [],  # No se puede cambiar desde completado
                'cancelado': ['pendiente']  # Se puede reagendar
            }
            
            if nuevo_estado != estado_actual and nuevo_estado not in transiciones_validas.get(estado_actual, []):
                return {
                    'success': False,
                    'errors': [f'No se puede cambiar de "{estado_actual}" a "{nuevo_estado}"']
                }
            
            # Si es el mismo estado, no hacer nada
            if nuevo_estado == estado_actual:
                return {
                    'success': True,
                    'data': existing_turno,
                    'message': f'El turno ya está en estado "{nuevo_estado}"'
                }
            
            # Actualizar estado
            query = f"""
                UPDATE {self.table_name}
                SET estado = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            rows_affected = execute_query(query, (nuevo_estado, turno_id))
            
            if rows_affected > 0:
                logger.info(f"Updated turno ID: {turno_id} from '{estado_actual}' to '{nuevo_estado}'")
                
                # Obtener el registro actualizado
                updated_turno = self.get_one(turno_id)
                
                return {
                    'success': True,
                    'data': updated_turno,
                    'message': f'Estado cambiado de "{estado_actual}" a "{nuevo_estado}"'
                }
            else:
                return {
                    'success': False,
                    'errors': ['No se pudo actualizar el estado del turno']
                }
                
        except MySQLError as e:
            logger.error(f"MySQL error in update_estado: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in update_estado: {e}")
            raise
    
    
    def get_count(self, estado: str = None, fecha_desde: str = None, fecha_hasta: str = None) -> int:
        try:
            query = f"SELECT COUNT(*) as total FROM {self.table_name} WHERE 1=1"
            params = []
            
            if estado:
                query += " AND estado = %s"
                params.append(estado)
            
            if fecha_desde:
                query += " AND DATE(fecha_turno) >= %s"
                params.append(fecha_desde)
            
            if fecha_hasta:
                query += " AND DATE(fecha_turno) <= %s"
                params.append(fecha_hasta)
            
            result = execute_query(query, tuple(params), fetch_one=True)
            return result['total'] if result else 0
            
        except MySQLError as e:
            logger.error(f"MySQL error in get_count: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_count: {e}")
            raise
    
    
    def _serialize_turno_with_duenio(self, row: Dict[str, Any]) -> Dict[str, Any]:
        if not row:
            return {}
        
        # Calcular días hasta el turno
        dias_hasta_turno = None
        if row.get('fecha_turno'):
            fecha_turno = row['fecha_turno']
            if isinstance(fecha_turno, str):
                fecha_turno = datetime.fromisoformat(fecha_turno.replace('Z', '+00:00'))
            
            dias_hasta_turno = (fecha_turno.date() - date.today()).days
        
        return {
            'id': row['id'],
            'nombre_mascota': row['nombre_mascota'],
            'fecha_turno': row['fecha_turno'].isoformat() if row.get('fecha_turno') else None,
            'tratamiento': row['tratamiento'],
            'estado': row['estado'],
            'dias_hasta_turno': dias_hasta_turno,
            'created_at': row['created_at'].isoformat() if row.get('created_at') else None,
            'updated_at': row['updated_at'].isoformat() if row.get('updated_at') else None,
            'duenio': {
                'id': row['id_duenio'],
                'nombre_apellido': row['nombre_apellido'],
                'telefono': row['telefono'],
                'email': row['email'],
                'direccion': row['direccion']
            }
        }