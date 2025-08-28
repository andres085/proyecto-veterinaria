"""
Módulo de conexión a base de datos MySQL con Connection Pooling
Sistema de Gestión de Turnos - Veterinaria
"""

import os
import mysql.connector
from mysql.connector import pooling, Error
from dotenv import load_dotenv
import logging

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración del pool de conexiones
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql'),
    'user': os.getenv('DB_USER', 'veterinaria_user'),
    'password': os.getenv('DB_PASSWORD', 'veterinaria_password_2024'),
    'database': os.getenv('DB_NAME', 'veterinaria_turnos'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'autocommit': True,
    'raise_on_warnings': True
}

# Pool de conexiones global
connection_pool = None

def init_connection_pool():
    """
    Inicializa el pool de conexiones MySQL
    Basado en la experiencia del proyecto anterior (database.py:11-21)
    """
    global connection_pool
    
    try:
        connection_pool = pooling.MySQLConnectionPool(
            pool_name="veterinaria_pool",
            pool_size=10,
            pool_reset_session=True,
            **DB_CONFIG
        )
        
        logger.info("✅ Pool de conexiones MySQL inicializado correctamente")
        logger.info(f"📊 Pool configurado: {connection_pool.pool_name} (tamaño: {connection_pool.pool_size})")
        
        # Probar una conexión del pool
        test_connection = connection_pool.get_connection()
        if test_connection.is_connected():
            cursor = test_connection.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            cursor.close()
            test_connection.close()
            
            if result and result[0] == 1:
                logger.info("🔍 Test de conectividad: EXITOSO")
                return True
                
    except Error as e:
        logger.error(f"❌ Error al inicializar pool de conexiones: {e}")
        return False
    
    return True

def get_db_connection():
    """
    Obtiene una conexión del pool
    Implementa reconexión automática como en el proyecto anterior
    
    Returns:
        mysql.connector.connection: Conexión de base de datos
    """
    global connection_pool
    
    # Inicializar pool si no existe
    if connection_pool is None:
        if not init_connection_pool():
            raise Exception("No se pudo inicializar el pool de conexiones")
    
    try:
        connection = connection_pool.get_connection()
        
        # Verificar que la conexión esté activa
        if not connection.is_connected():
            connection.reconnect(attempts=3, delay=1)
            
        return connection
        
    except Error as e:
        logger.error(f"❌ Error al obtener conexión del pool: {e}")
        
        # Intentar reinicializar el pool
        logger.info("🔄 Intentando reinicializar pool de conexiones...")
        if init_connection_pool():
            try:
                return connection_pool.get_connection()
            except Error as retry_error:
                logger.error(f"❌ Error en reintento de conexión: {retry_error}")
                raise
        else:
            raise

def execute_query(query, params=None, fetch=False, fetch_one=False):
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute(query, params or ())
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch:
            result = cursor.fetchall()
        else:
            # Para INSERT/UPDATE/DELETE, devolver lastrowid o rowcount
            connection.commit()
            result = cursor.lastrowid if cursor.lastrowid else cursor.rowcount
            
        logger.debug(f"✅ Query ejecutada: {query[:50]}...")
        return result
        
    except Error as e:
        if connection:
            connection.rollback()
        logger.error(f"❌ Error ejecutando query: {e}")
        logger.error(f"Query: {query}")
        raise
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def execute_transaction(queries_with_params):
    """
    Ejecuta múltiples consultas en una transacción
    
    Args:
        queries_with_params (list): Lista de tuplas (query, params)
        
    Returns:
        bool: True si la transacción fue exitosa
    """
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        connection.autocommit = False  # Desactivar autocommit para transacción
        cursor = connection.cursor(dictionary=True)
        
        results = []
        for query, params in queries_with_params:
            cursor.execute(query, params or ())
            # Guardar lastrowid para INSERTs
            if cursor.lastrowid:
                results.append(cursor.lastrowid)
            else:
                results.append(cursor.rowcount)
        
        connection.commit()
        logger.info(f"✅ Transacción completada: {len(queries_with_params)} queries")
        return results
        
    except Error as e:
        if connection:
            connection.rollback()
        logger.error(f"❌ Error en transacción: {e}")
        raise
        
    finally:
        if connection:
            connection.autocommit = True  # Restaurar autocommit
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_db_info():
    """
    Obtiene información sobre la base de datos y el pool de conexiones
    
    Returns:
        dict: Información de la base de datos
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Información de la BD
        cursor.execute("SELECT DATABASE() as current_db, VERSION() as mysql_version")
        db_info = cursor.fetchone()
        
        # Información del pool
        pool_info = {
            'pool_name': connection_pool.pool_name if connection_pool else None,
            'pool_size': connection_pool.pool_size if connection_pool else None,
            'connections_available': connection_pool._cnx_queue.qsize() if connection_pool else 0
        }
        
        cursor.close()
        connection.close()
        
        return {
            'database': db_info['current_db'],
            'mysql_version': db_info['mysql_version'],
            'pool_info': pool_info,
            'status': 'connected'
        }
        
    except Error as e:
        logger.error(f"❌ Error obteniendo info de BD: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

def close_pool():
    """Cierra el pool de conexiones"""
    global connection_pool
    
    if connection_pool:
        connection_pool._remove_connections()
        connection_pool = None
        logger.info("🔒 Pool de conexiones cerrado")

# Inicializar pool al importar el módulo
if __name__ != "__main__":
    init_connection_pool()