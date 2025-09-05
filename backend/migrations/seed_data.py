import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Agregar el directorio padre al path para importar módulos de la app
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import execute_query, execute_transaction, get_db_info

# Cargar variables de entorno
load_dotenv()

def clear_existing_data():
    """
    Limpia datos existentes para reiniciar con datos frescos
    Basado en experiencia de db_rollback.py del proyecto anterior
    """
    try:
        print("🧹 Limpiando datos existentes...")
        
        # Eliminar en orden correcto (primero turnos por foreign key)
        turnos_deleted = execute_query("DELETE FROM turnos")
        duenios_deleted = execute_query("DELETE FROM duenios")
        
        # Reset AUTO_INCREMENT
        execute_query("ALTER TABLE turnos AUTO_INCREMENT = 1")
        execute_query("ALTER TABLE duenios AUTO_INCREMENT = 1")
        
        print(f"   - Turnos eliminados: {turnos_deleted}")
        print(f"   - Dueños eliminados: {duenios_deleted}")
        print("✅ Limpieza completada")
        
        return True
        
    except Exception as e:
        print(f"❌ Error limpiando datos: {e}")
        return False

def insert_duenios_data():
    """
    Inserta dueños de ejemplo con datos realistas
    Cubre diferentes casos de uso según especificaciones
    """
    duenios_data = [
        {
            'nombre_apellido': 'María González',
            'telefono': '+54-11-4567-8901',
            'email': 'maria.gonzalez@email.com',
            'direccion': 'Av. Corrientes 1234, CABA, Buenos Aires'
        },
        {
            'nombre_apellido': 'Carlos Rodríguez',
            'telefono': '+54-11-2345-6789',
            'email': 'carlos.rodriguez@gmail.com',
            'direccion': 'San Martín 567, Villa Crespo, CABA'
        },
        {
            'nombre_apellido': 'Ana Martínez',
            'telefono': '+54-11-8765-4321',
            'email': 'ana.martinez@hotmail.com',
            'direccion': 'Rivadavia 2890, Caballito, CABA'
        },
        {
            'nombre_apellido': 'Roberto Silva',
            'telefono': '+54-11-3456-7890',
            'email': 'roberto.silva@outlook.com',
            'direccion': 'Av. Santa Fe 1456, Recoleta, CABA'
        },
        {
            'nombre_apellido': 'Laura Fernández',
            'telefono': '+54-11-5678-9012',
            'email': 'laura.fernandez@yahoo.com',
            'direccion': 'Cabildo 3321, Belgrano, CABA'
        },
        {
            'nombre_apellido': 'Diego Pérez',
            'telefono': '+54-11-7890-1234',
            'email': 'diego.perez@veterinaria.com',
            'direccion': 'Av. Cabildo 1789, Núñez, CABA'
        },
        {
            'nombre_apellido': 'Sofía López',
            'telefono': '+54-11-9012-3456',
            'email': 'sofia.lopez@email.com',
            'direccion': 'Monroe 4567, Belgrano, CABA'
        },
        {
            'nombre_apellido': 'Alejandro Torres',
            'telefono': '+54-11-1357-2468',
            'email': 'alejandro.torres@gmail.com',
            'direccion': 'Av. Las Heras 2345, Recoleta, CABA'
        }
    ]
    
    try:
        print("👥 Insertando dueños de ejemplo...")
        
        duenios_inserted = []
        for duenio in duenios_data:
            duenio_id = execute_query("""
                INSERT INTO duenios (nombre_apellido, telefono, email, direccion) 
                VALUES (%(nombre_apellido)s, %(telefono)s, %(email)s, %(direccion)s)
            """, duenio)
            
            duenios_inserted.append({
                'id': duenio_id,
                'nombre': duenio['nombre_apellido']
            })
            
        print(f"✅ {len(duenios_inserted)} dueños insertados exitosamente")
        
        # Mostrar resumen
        for duenio in duenios_inserted:
            print(f"   - ID {duenio['id']}: {duenio['nombre']}")
            
        return duenios_inserted
        
    except Exception as e:
        print(f"❌ Error insertando dueños: {e}")
        return []

def insert_turnos_data(duenios_ids):
    """
    Inserta turnos de ejemplo con diferentes estados y escenarios
    Cubre todos los casos según especificaciones ENUM
    """
    if not duenios_ids:
        print("❌ No hay dueños para asignar turnos")
        return []
    
    # Fechas base para diferentes escenarios
    hoy = datetime.now()
    ayer = hoy - timedelta(days=1)
    hace_una_semana = hoy - timedelta(days=7)
    manana = hoy + timedelta(days=1)
    proxima_semana = hoy + timedelta(days=7)
    proximo_mes = hoy + timedelta(days=30)
    
    turnos_data = [
        # Turnos completados (históricos)
        {
            'nombre_mascota': 'Firulais',
            'fecha_turno': hace_una_semana.strftime('%Y-%m-%d 10:00:00'),
            'tratamiento': 'Consulta general y vacunación antirrábica',
            'id_duenio': duenios_ids[0],
            'estado': 'completado'
        },
        {
            'nombre_mascota': 'Misu',
            'fecha_turno': (hoy - timedelta(days=3)).strftime('%Y-%m-%d 14:30:00'),
            'tratamiento': 'Control de peso y desparasitación',
            'id_duenio': duenios_ids[1],
            'estado': 'completado'
        },
        {
            'nombre_mascota': 'Rocky',
            'fecha_turno': ayer.strftime('%Y-%m-%d 16:00:00'),
            'tratamiento': 'Curación de herida en pata trasera',
            'id_duenio': duenios_ids[2],
            'estado': 'completado'
        },
        
        # Turnos confirmados (próximos)
        {
            'nombre_mascota': 'Luna',
            'fecha_turno': manana.strftime('%Y-%m-%d 09:00:00'),
            'tratamiento': 'Consulta por pérdida de apetito',
            'id_duenio': duenios_ids[3],
            'estado': 'confirmado'
        },
        {
            'nombre_mascota': 'Max',
            'fecha_turno': (hoy + timedelta(days=2)).strftime('%Y-%m-%d 11:30:00'),
            'tratamiento': 'Revisión post-operatoria de esterilización',
            'id_duenio': duenios_ids[4],
            'estado': 'confirmado'
        },
        {
            'nombre_mascota': 'Bella',
            'fecha_turno': proxima_semana.strftime('%Y-%m-%d 15:00:00'),
            'tratamiento': 'Vacunación sextuple y control anual',
            'id_duenio': duenios_ids[5],
            'estado': 'confirmado'
        },
        
        # Turnos pendientes
        {
            'nombre_mascota': 'Coco',
            'fecha_turno': (hoy + timedelta(days=3)).strftime('%Y-%m-%d 10:30:00'),
            'tratamiento': 'Primera consulta - cachorro de 2 meses',
            'id_duenio': duenios_ids[6],
            'estado': 'pendiente'
        },
        {
            'nombre_mascota': 'Simba',
            'fecha_turno': (hoy + timedelta(days=5)).strftime('%Y-%m-%d 12:00:00'),
            'tratamiento': 'Consulta dermatológica por alergia',
            'id_duenio': duenios_ids[7],
            'estado': 'pendiente'
        },
        {
            'nombre_mascota': 'Nala',
            'fecha_turno': proximo_mes.strftime('%Y-%m-%d 14:00:00'),
            'tratamiento': 'Control geriátrico - perro de 12 años',
            'id_duenio': duenios_ids[0],  # María tiene 2 mascotas
            'estado': 'pendiente'
        },
        
        # Turnos cancelados
        {
            'nombre_mascota': 'Toby',
            'fecha_turno': (hoy + timedelta(days=1)).strftime('%Y-%m-%d 13:30:00'),
            'tratamiento': 'Consulta por vómitos - CANCELADO por cliente',
            'id_duenio': duenios_ids[1],  # Carlos tiene 2 mascotas
            'estado': 'cancelado'
        },
        {
            'nombre_mascota': 'Princesa',
            'fecha_turno': (hoy - timedelta(days=2)).strftime('%Y-%m-%d 16:30:00'),
            'tratamiento': 'Limpieza dental - CANCELADO por enfermedad veterinario',
            'id_duenio': duenios_ids[3],  # Roberto tiene 2 mascotas
            'estado': 'cancelado'
        },
        
        # Turnos adicionales para casos edge
        {
            'nombre_mascota': 'Chiquito',
            'fecha_turno': (hoy + timedelta(days=15)).strftime('%Y-%m-%d 08:30:00'),
            'tratamiento': 'Extracción dental programada',
            'id_duenio': duenios_ids[2],  # Ana tiene 2 mascotas
            'estado': 'pendiente'
        },
        {
            'nombre_mascota': 'Pelusa',
            'fecha_turno': (hoy + timedelta(days=10)).strftime('%Y-%m-%d 17:00:00'),
            'tratamiento': 'Control post-parto y revisión cachorros',
            'id_duenio': duenios_ids[4],  # Laura tiene 2 mascotas
            'estado': 'confirmado'
        }
    ]
    
    try:
        print("🐾 Insertando turnos de ejemplo...")
        
        turnos_inserted = []
        for turno in turnos_data:
            turno_id = execute_query("""
                INSERT INTO turnos (nombre_mascota, fecha_turno, tratamiento, id_duenio, estado) 
                VALUES (%(nombre_mascota)s, %(fecha_turno)s, %(tratamiento)s, %(id_duenio)s, %(estado)s)
            """, turno)
            
            turnos_inserted.append({
                'id': turno_id,
                'mascota': turno['nombre_mascota'],
                'estado': turno['estado'],
                'fecha': turno['fecha_turno']
            })
        
        print(f"✅ {len(turnos_inserted)} turnos insertados exitosamente")
        
        # Mostrar resumen por estado
        estados_count = {}
        for turno in turnos_inserted:
            estado = turno['estado']
            estados_count[estado] = estados_count.get(estado, 0) + 1
        
        print("📊 Resumen por estado:")
        for estado, count in estados_count.items():
            print(f"   - {estado.title()}: {count} turnos")
            
        return turnos_inserted
        
    except Exception as e:
        print(f"❌ Error insertando turnos: {e}")
        return []

def validate_referential_integrity():
    """
    Valida la integridad referencial y relaciones entre tablas
    Basado en experiencia de validaciones del proyecto anterior
    """
    try:
        print("🔍 Validando integridad referencial...")
        
        # Verificar relaciones duenios -> turnos
        result = execute_query("""
            SELECT 
                d.id,
                d.nombre_apellido,
                COUNT(t.id) as total_turnos,
                COUNT(CASE WHEN t.estado = 'pendiente' THEN 1 END) as pendientes,
                COUNT(CASE WHEN t.estado = 'confirmado' THEN 1 END) as confirmados,
                COUNT(CASE WHEN t.estado = 'completado' THEN 1 END) as completados,
                COUNT(CASE WHEN t.estado = 'cancelado' THEN 1 END) as cancelados
            FROM duenios d
            LEFT JOIN turnos t ON d.id = t.id_duenio
            GROUP BY d.id, d.nombre_apellido
            ORDER BY d.id
        """, fetch=True)
        
        print("👥 Relaciones Dueños -> Turnos:")
        total_turnos_sistema = 0
        for row in result:
            total_turnos_sistema += row['total_turnos']
            print(f"   - {row['nombre_apellido']} (ID: {row['id']}): {row['total_turnos']} turnos")
            if row['total_turnos'] > 0:
                print(f"     📋 Pendientes: {row['pendientes']}, Confirmados: {row['confirmados']}")
                print(f"     ✅ Completados: {row['completados']}, ❌ Cancelados: {row['cancelados']}")
        
        # Verificar totales
        total_duenios = execute_query("SELECT COUNT(*) as total FROM duenios", fetch_one=True)
        total_turnos = execute_query("SELECT COUNT(*) as total FROM turnos", fetch_one=True)
        
        print(f"\n📊 Totales del sistema:")
        print(f"   - Dueños: {total_duenios['total']}")
        print(f"   - Turnos: {total_turnos['total']}")
        print(f"   - Relaciones verificadas: {total_turnos_sistema}")
        
        # Verificar foreign keys
        turnos_huerfanos = execute_query("""
            SELECT COUNT(*) as count 
            FROM turnos t 
            LEFT JOIN duenios d ON t.id_duenio = d.id 
            WHERE d.id IS NULL
        """, fetch_one=True)
        
        if turnos_huerfanos['count'] > 0:
            print(f"⚠️  Turnos sin dueño válido: {turnos_huerfanos['count']}")
            return False
        else:
            print("✅ Foreign Keys: Válidas")
        
        print("✅ Validación de integridad referencial: EXITOSA")
        return True
        
    except Exception as e:
        print(f"❌ Error validando integridad referencial: {e}")
        return False

def show_sample_queries():
    """
    Muestra consultas de ejemplo para verificar los datos insertados
    """
    try:
        print("\n📋 Consultas de ejemplo:")
        
        # Turnos próximos
        print("\n🔜 Turnos próximos (siguientes 7 días):")
        proximos_turnos = execute_query("""
            SELECT 
                t.nombre_mascota,
                d.nombre_apellido as duenio,
                t.fecha_turno,
                t.estado,
                t.tratamiento
            FROM turnos t
            JOIN duenios d ON t.id_duenio = d.id
            WHERE t.fecha_turno BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 7 DAY)
            AND t.estado IN ('pendiente', 'confirmado')
            ORDER BY t.fecha_turno
        """, fetch=True)
        
        for turno in proximos_turnos:
            print(f"   - {turno['nombre_mascota']} ({turno['duenio']}) - {turno['fecha_turno']} [{turno['estado'].upper()}]")
        
        # Turnos por estado
        print("\n📊 Resumen por estado:")
        resumen_estados = execute_query("""
            SELECT estado, COUNT(*) as total
            FROM turnos
            GROUP BY estado
            ORDER BY total DESC
        """, fetch=True)
        
        for estado in resumen_estados:
            print(f"   - {estado['estado'].title()}: {estado['total']} turnos")
        
        print("✅ Datos de prueba listos para desarrollo")
        
    except Exception as e:
        print(f"❌ Error mostrando consultas de ejemplo: {e}")

def main():
    """Función principal del script de seeds"""
    print("🌱 Iniciando script de Seeds y Datos de Prueba...")
    print("=" * 60)
    
    # Verificar conexión a BD
    db_info = get_db_info()
    if db_info.get('status') != 'connected':
        print("❌ No hay conexión a la base de datos")
        sys.exit(1)
    
    print(f"🔌 Conectado a: {db_info.get('database')} (MySQL {db_info.get('mysql_version', 'N/A')})")
    
    # Paso 1: Limpiar datos existentes
    if not clear_existing_data():
        print("❌ Error en la limpieza de datos")
        sys.exit(1)
    
    # Paso 2: Insertar dueños
    duenios_insertados = insert_duenios_data()
    if not duenios_insertados:
        print("❌ Error insertando dueños")
        sys.exit(1)
    
    # Extraer IDs de dueños para turnos
    duenios_ids = [duenio['id'] for duenio in duenios_insertados]
    
    # Paso 3: Insertar turnos
    turnos_insertados = insert_turnos_data(duenios_ids)
    if not turnos_insertados:
        print("❌ Error insertando turnos")
        sys.exit(1)
    
    # Paso 4: Validar integridad referencial
    if not validate_referential_integrity():
        print("❌ Error en validación de integridad")
        sys.exit(1)
    
    # Paso 5: Mostrar consultas de ejemplo
    show_sample_queries()
    
    print("=" * 60)
    print("🎉 Script de Seeds completado exitosamente!")
    print("\n📊 Resumen final:")
    print(f"   - Dueños insertados: {len(duenios_insertados)}")
    print(f"   - Turnos insertados: {len(turnos_insertados)}")
    print("   - Integridad referencial: ✅ Válida")
    print("   - Estados cubiertos: pendiente, confirmado, completado, cancelado")
    print("   - Escenarios temporales: pasado, presente, futuro")
    print("\n✅ Datos de prueba listos para desarrollo y testing")

if __name__ == "__main__":
    main()