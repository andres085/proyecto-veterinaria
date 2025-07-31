"""
Modelo de Dueños para el sistema de gestión de turnos veterinaria
Basado en el patrón MVC del proyecto anterior con mejoras
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from mysql.connector import Error as MySQLError

from ..database import get_db_connection, execute_query, execute_transaction
from ..validators import validate_duenio_data

# Configurar logger
logger = logging.getLogger(__name__)


class DuenioModel:
    """
    Modelo para gestionar dueños de mascotas
    Basado en tabla: duenios (id, nombre_apellido, telefono, email, direccion, timestamps)
    """
    
    def __init__(self):
        """Inicializar el modelo"""
        self.table_name = "duenios"
        logger.debug("DuenioModel inicializado")
    
    
    def get_all(self, limit: int = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Obtiene todos los dueños con paginación opcional
        
        Args:
            limit: Límite de registros (None = todos)
            offset: Número de registros a saltar
            
        Returns:
            List[Dict]: Lista de dueños
        """
        try:
            query = f"""
                SELECT id, nombre_apellido, telefono, email, direccion, 
                       created_at, updated_at
                FROM {self.table_name}
                ORDER BY nombre_apellido ASC
            """
            
            params = ()
            
            # Agregar paginación si se especifica
            if limit is not None:
                query += " LIMIT %s OFFSET %s"
                params = (limit, offset)
            
            result = execute_query(query, params, fetch=True)
            
            # Serializar resultados
            duenios = [self._serialize_duenio(row) for row in result] if result else []
            
            logger.info(f"Retrieved {len(duenios)} dueños from database")
            return duenios
            
        except MySQLError as e:
            logger.error(f"MySQL error in get_all: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_all: {e}")
            raise
    
    
    def get_one(self, duenio_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un dueño específico por ID
        
        Args:
            duenio_id: ID del dueño
            
        Returns:
            Dict: Datos del dueño o None si no existe
        """
        try:
            if not isinstance(duenio_id, int) or duenio_id <= 0:
                logger.warning(f"Invalid duenio_id: {duenio_id}")
                return None
            
            query = f"""
                SELECT id, nombre_apellido, telefono, email, direccion,
                       created_at, updated_at
                FROM {self.table_name}
                WHERE id = %s
            """
            
            result = execute_query(query, (duenio_id,), fetch_one=True)
            
            if result:
                duenio = self._serialize_duenio(result)
                logger.debug(f"Found dueño with ID {duenio_id}")
                return duenio
            else:
                logger.debug(f"No dueño found with ID {duenio_id}")
                return None
                
        except MySQLError as e:
            logger.error(f"MySQL error in get_one: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_one: {e}")
            raise
    
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un nuevo dueño
        
        Args:
            data: Datos del dueño (nombre_apellido, telefono, email, direccion)
            
        Returns:
            Dict: Resultado con 'success', 'data'/'errors', 'duenio_id'
        """
        try:
            # Validar datos usando validaciones manuales
            validation_result = validate_duenio_data(data)
            
            if not validation_result['is_valid']:
                logger.warning(f"Validation failed for create: {validation_result['errors']}")
                return {
                    'success': False,
                    'errors': validation_result['errors']
                }
            
            # Preparar query INSERT
            query = f"""
                INSERT INTO {self.table_name} 
                (nombre_apellido, telefono, email, direccion)
                VALUES (%s, %s, %s, %s)
            """
            
            params = (
                data['nombre_apellido'].strip(),
                data['telefono'].strip(),
                data['email'].strip().lower(),
                data['direccion'].strip()
            )
            
            # Ejecutar inserción
            duenio_id = execute_query(query, params)
            
            if duenio_id:
                logger.info(f"Created new dueño with ID: {duenio_id}")
                
                # Obtener el registro creado
                new_duenio = self.get_one(duenio_id)
                
                return {
                    'success': True,
                    'data': new_duenio,
                    'duenio_id': duenio_id
                }
            else:
                logger.error("Failed to create dueño - no ID returned")
                return {
                    'success': False,
                    'errors': ['Error al crear el dueño']
                }
                
        except MySQLError as e:
            logger.error(f"MySQL error in create: {e}")
            
            # Manejar errores específicos de MySQL
            if e.errno == 1062:  # Duplicate entry
                return {
                    'success': False, 
                    'errors': ['El email ya está registrado']
                }
            else:
                raise
                
        except Exception as e:
            logger.error(f"Unexpected error in create: {e}")
            raise
    
    
    def update(self, duenio_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza un dueño existente
        
        Args:
            duenio_id: ID del dueño a actualizar
            data: Datos a actualizar (campos opcionales)
            
        Returns:
            Dict: Resultado con 'success', 'data'/'errors'
        """
        try:
            # Verificar que el dueño existe
            existing_duenio = self.get_one(duenio_id)
            if not existing_duenio:
                return {
                    'success': False,
                    'errors': [f'No existe un dueño con ID: {duenio_id}']
                }
            
            # Validar datos (solo los campos presentes)
            if data:
                validation_result = validate_duenio_data(data)
                if not validation_result['is_valid']:
                    logger.warning(f"Validation failed for update: {validation_result['errors']}")
                    return {
                        'success': False,
                        'errors': validation_result['errors']
                    }
            
            # Construir query UPDATE dinámicamente
            update_fields = []
            params = []
            
            allowed_fields = ['nombre_apellido', 'telefono', 'email', 'direccion']
            
            for field in allowed_fields:
                if field in data:
                    update_fields.append(f"{field} = %s")
                    value = data[field].strip()
                    if field == 'email':
                        value = value.lower()
                    params.append(value)
            
            if not update_fields:
                return {
                    'success': False,
                    'errors': ['No hay campos para actualizar']
                }
            
            # Agregar ID al final de los parámetros
            params.append(duenio_id)
            
            query = f"""
                UPDATE {self.table_name}
                SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            # Ejecutar actualización
            rows_affected = execute_query(query, tuple(params))
            
            if rows_affected > 0:
                logger.info(f"Updated dueño ID: {duenio_id}")
                
                # Obtener el registro actualizado
                updated_duenio = self.get_one(duenio_id)
                
                return {
                    'success': True,
                    'data': updated_duenio
                }
            else:
                return {
                    'success': False,
                    'errors': ['No se pudo actualizar el dueño']
                }
                
        except MySQLError as e:
            logger.error(f"MySQL error in update: {e}")
            
            if e.errno == 1062:  # Duplicate entry
                return {
                    'success': False,
                    'errors': ['El email ya está registrado por otro dueño']
                }
            else:
                raise
                
        except Exception as e:
            logger.error(f"Unexpected error in update: {e}")
            raise
    
    
    def delete(self, duenio_id: int) -> Dict[str, Any]:
        """
        Elimina un dueño (CASCADE eliminará turnos asociados)
        
        Args:
            duenio_id: ID del dueño a eliminar
            
        Returns:
            Dict: Resultado con 'success', 'message'/'errors'
        """
        try:
            # Verificar que el dueño existe
            existing_duenio = self.get_one(duenio_id)
            if not existing_duenio:
                return {
                    'success': False,
                    'errors': [f'No existe un dueño con ID: {duenio_id}']
                }
            
            # Eliminar dueño (CASCADE eliminará turnos automáticamente)
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            rows_affected = execute_query(query, (duenio_id,))
            
            if rows_affected > 0:
                logger.info(f"Deleted dueño ID: {duenio_id} and associated turnos")
                return {
                    'success': True,
                    'message': f'Dueño eliminado correctamente (y sus turnos asociados)'
                }
            else:
                return {
                    'success': False,
                    'errors': ['No se pudo eliminar el dueño']
                }
                
        except MySQLError as e:
            logger.error(f"MySQL error in delete: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in delete: {e}")
            raise
    
    
    def search(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Busca dueños por nombre o email
        
        Args:
            query: Término de búsqueda
            limit: Límite de resultados
            
        Returns:
            List[Dict]: Lista de dueños que coinciden
        """
        try:
            if not query or not query.strip():
                logger.warning("Empty search query provided")
                return []
            
            search_term = f"%{query.strip()}%"
            
            sql_query = f"""
                SELECT id, nombre_apellido, telefono, email, direccion,
                       created_at, updated_at
                FROM {self.table_name}
                WHERE nombre_apellido LIKE %s 
                   OR email LIKE %s
                ORDER BY nombre_apellido ASC
                LIMIT %s
            """
            
            result = execute_query(sql_query, (search_term, search_term, limit), fetch=True)
            
            # Serializar resultados
            duenios = [self._serialize_duenio(row) for row in result] if result else []
            
            logger.info(f"Search '{query}' returned {len(duenios)} results")
            return duenios
            
        except MySQLError as e:
            logger.error(f"MySQL error in search: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in search: {e}")
            raise
    
    
    def exists(self, duenio_id: int) -> bool:
        """
        Verifica si existe un dueño con el ID especificado
        
        Args:
            duenio_id: ID del dueño
            
        Returns:
            bool: True si existe, False si no
        """
        try:
            query = f"SELECT 1 FROM {self.table_name} WHERE id = %s LIMIT 1"
            result = execute_query(query, (duenio_id,), fetch_one=True)
            return result is not None
            
        except MySQLError as e:
            logger.error(f"MySQL error in exists: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in exists: {e}")
            raise
    
    
    def get_count(self) -> int:
        """
        Obtiene el número total de dueños
        
        Returns:
            int: Número total de dueños
        """
        try:
            query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            result = execute_query(query, fetch_one=True)
            return result['total'] if result else 0
            
        except MySQLError as e:
            logger.error(f"MySQL error in get_count: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_count: {e}")
            raise
    
    
    def _serialize_duenio(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serializa un registro de dueño para respuesta JSON
        
        Args:
            row: Fila de la base de datos
            
        Returns:
            Dict: Dueño serializado
        """
        if not row:
            return {}
        
        return {
            'id': row['id'],
            'nombre_apellido': row['nombre_apellido'], 
            'telefono': row['telefono'],
            'email': row['email'],
            'direccion': row['direccion'],
            'created_at': row['created_at'].isoformat() if row.get('created_at') else None,
            'updated_at': row['updated_at'].isoformat() if row.get('updated_at') else None
        }