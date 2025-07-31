#!/usr/bin/env python3
"""
Script de inicialización de base de datos para Sistema Veterinaria
Crea las tablas duenios y turnos con sus relaciones y constraints
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_db_config():
    """Obtiene la configuración de base de datos desde variables de entorno"""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'veterinaria_user'),
        'password': os.getenv('DB_PASSWORD', 'veterinaria_password_2024'),
        'database': os.getenv('DB_NAME', 'veterinaria_turnos'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }

def create_database_if_not_exists():
    """Crea la base de datos si no existe"""
    config = get_db_config()
    db_name = config.pop('database')
    
    try:
        # Conectar sin especificar database
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Crear database si no existe
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Base de datos '{db_name}' verificada/creada exitosamente")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"❌ Error al crear base de datos: {e}")
        return False
    
    return True

def create_tables():
    """Crea las tablas duenios y turnos con sus constraints"""
    
    # SQL para crear tabla duenios
    create_duenios_table = """
    CREATE TABLE IF NOT EXISTS duenios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre_apellido VARCHAR(100) NOT NULL,
        telefono VARCHAR(20) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        direccion TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
        -- Constraints y validaciones
        CONSTRAINT chk_nombre_length CHECK (CHAR_LENGTH(nombre_apellido) >= 2),
        CONSTRAINT chk_telefono_format CHECK (telefono REGEXP '^[0-9+\\-\\s\\(\\)]+$'),
        CONSTRAINT chk_email_format CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    # SQL para crear tabla turnos
    create_turnos_table = """
    CREATE TABLE IF NOT EXISTS turnos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre_mascota VARCHAR(80) NOT NULL,
        fecha_turno DATETIME NOT NULL,
        tratamiento TEXT NOT NULL,
        id_duenio INT NOT NULL,
        estado ENUM('pendiente', 'confirmado', 'completado', 'cancelado') DEFAULT 'pendiente',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
        -- Foreign Key con CASCADE
        FOREIGN KEY (id_duenio) REFERENCES duenios(id) ON DELETE CASCADE ON UPDATE CASCADE,
        
        -- Índices para performance
        INDEX idx_fecha_turno (fecha_turno),
        INDEX idx_duenio (id_duenio),
        INDEX idx_estado (estado),
        
        -- Constraints y validaciones
        CONSTRAINT chk_nombre_mascota_length CHECK (CHAR_LENGTH(nombre_mascota) >= 1),
        CONSTRAINT chk_tratamiento_length CHECK (CHAR_LENGTH(tratamiento) >= 5)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        config = get_db_config()
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("🔄 Creando tabla 'duenios'...")
        cursor.execute(create_duenios_table)
        print("✅ Tabla 'duenios' creada exitosamente")
        
        print("🔄 Creando tabla 'turnos'...")
        cursor.execute(create_turnos_table)
        print("✅ Tabla 'turnos' creada exitosamente")
        
        # Commit changes
        connection.commit()
        print("✅ Todas las tablas fueron creadas correctamente")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"❌ Error al crear tablas: {e}")
        return False
    
    return True

def verify_tables():
    """Verifica que las tablas fueron creadas correctamente"""
    try:
        config = get_db_config()
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Verificar tablas existentes
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        print("\n📋 Tablas encontradas en la base de datos:")
        for table in table_names:
            print(f"   - {table}")
        
        # Verificar estructura de duenios
        if 'duenios' in table_names:
            cursor.execute("DESCRIBE duenios")
            columns = cursor.fetchall()
            print("\n🏗️  Estructura tabla 'duenios':")
            for column in columns:
                print(f"   - {column[0]}: {column[1]} ({column[2]})")
        
        # Verificar estructura de turnos
        if 'turnos' in table_names:
            cursor.execute("DESCRIBE turnos")
            columns = cursor.fetchall()
            print("\n🏗️  Estructura tabla 'turnos':")
            for column in columns:
                print(f"   - {column[0]}: {column[1]} ({column[2]})")
        
        # Verificar foreign keys
        cursor.execute("""
            SELECT 
                CONSTRAINT_NAME,
                TABLE_NAME,
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = %s 
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """, (config['database'],))
        
        foreign_keys = cursor.fetchall()
        if foreign_keys:
            print("\n🔗 Foreign Keys configuradas:")
            for fk in foreign_keys:
                print(f"   - {fk[1]}.{fk[2]} -> {fk[3]}.{fk[4]}")
        
        cursor.close()
        connection.close()
        
        return len(table_names) >= 2
        
    except Error as e:
        print(f"❌ Error al verificar tablas: {e}")
        return False

def main():
    """Función principal de inicialización"""
    print("🚀 Iniciando configuración de base de datos...")
    print("=" * 50)
    
    # Paso 1: Crear base de datos si no existe
    if not create_database_if_not_exists():
        print("❌ No se pudo crear/verificar la base de datos")
        sys.exit(1)
    
    # Paso 2: Crear tablas
    if not create_tables():
        print("❌ No se pudieron crear las tablas")
        sys.exit(1)
    
    # Paso 3: Verificar configuración
    if not verify_tables():
        print("❌ Error en la verificación de tablas")
        sys.exit(1)
    
    print("=" * 50)
    print("🎉 Inicialización de base de datos completada exitosamente!")
    print("\n📊 Resumen:")
    print("   - Base de datos: veterinaria_turnos")
    print("   - Tablas creadas: duenios, turnos")
    print("   - Relaciones: duenios(1) -> turnos(N)")
    print("   - Constraints y validaciones aplicadas")
    print("\n✅ Sistema listo para recibir datos")

if __name__ == "__main__":
    main()