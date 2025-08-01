# 🐾 Sistema de Gestión de Turnos - Veterinaria

Sistema web para gestión de turnos en una clínica veterinaria que permite administrar citas de mascotas y datos de sus dueños.

## 🏗️ Arquitectura Tecnológica

### Backend
- **Framework**: Flask (Python)
- **Patrón**: MVC (Model-View-Controller)
- **Base de Datos**: MySQL 8.0
- **Containerización**: Docker Compose

### Frontend
- **Framework**: Vue.js 3
- **Gestor de Estado**: Pinia
- **Cliente HTTP**: Axios
- **Build Tool**: Vite
- **Lenguaje**: TypeScript

### Infraestructura
- **Contenedores**: Docker Compose
- **Base de Datos**: MySQL como servicio
- **Variables de Entorno**: .env para configuración

## 📦 Requisitos Previos

- Docker y Docker Compose instalados
- Git
- Puertos disponibles: 3000 (Frontend), 5000 (Backend), 3306 (MySQL)

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd proyecto-veterinaria
```

### 2. Variables de Entorno
El archivo `.env` ya está configurado con los valores por defecto:

```bash
# Las variables ya están configuradas en .env
cat .env
```

### 3. Construir y Levantar Servicios
```bash
# Construir e iniciar todos los servicios
docker compose up --build -d

# Verificar que todos los servicios estén corriendo
docker compose ps
```

**Servicios disponibles después del inicio:**
- 🟢 **MySQL**: Puerto 3306 (Base de datos)
- 🟢 **Backend Flask**: Puerto 5000 (API REST)
- 🟢 **Frontend Vue**: Puerto 3000 (Aplicación web)

### 4. Inicializar Base de Datos
```bash
# Crear tablas y estructura de BD
docker compose exec backend python migrations/init_db.py
```

### 5. Cargar Datos de Prueba
```bash
# Insertar datos de ejemplo para desarrollo
docker compose exec backend python migrations/seed_data.py
```

## 🔍 Verificación de Instalación

### Verificar Backend
```bash
# Endpoint básico
curl http://localhost:5000/

# Endpoint de salud con info de BD
curl http://localhost:5000/api/health
```

### Verificar Frontend
```bash
# Abrir en navegador
open http://localhost:3000
```

### Verificar Base de Datos
```bash
# Conectar a MySQL
docker compose exec mysql mysql -u veterinaria_user -p veterinaria_turnos

# Ver tablas creadas
SHOW TABLES;

# Ver datos de prueba
SELECT COUNT(*) FROM duenios;
SELECT COUNT(*) FROM turnos;
```

## 📊 Datos de Prueba

El sistema incluye datos de ejemplo listos para desarrollo:

### Dueños (8 registros)
- María González, Carlos Rodríguez, Ana Martínez, Roberto Silva
- Laura Fernández, Diego Pérez, Sofía López, Alejandro Torres

### Turnos (13 registros)
- **Estados**: pendiente (4), confirmado (4), completado (3), cancelado (2)
- **Escenarios**: históricos, actuales, futuros
- **Mascotas**: Firulais, Luna, Max, Bella, Coco, Simba, Rocky, etc.

### Consultas de Ejemplo
```bash
# Ver próximos turnos
docker compose exec backend python -c "
from app.database import execute_query
turnos = execute_query('''
    SELECT t.nombre_mascota, d.nombre_apellido, t.fecha_turno, t.estado
    FROM turnos t JOIN duenios d ON t.id_duenio = d.id
    WHERE t.fecha_turno >= NOW() AND t.estado IN ('pendiente', 'confirmado')
    ORDER BY t.fecha_turno LIMIT 5
''', fetch=True)
for t in turnos:
    print(f'{t[\"nombre_mascota\"]} - {t[\"nombre_apellido\"]} - {t[\"fecha_turno\"]} [{t[\"estado\"].upper()}]')
"
```

## 🛠️ Comandos de Desarrollo

### Gestión de Servicios
```bash
# Iniciar servicios
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f backend
docker compose logs -f frontend

# Reiniciar servicio específico
docker compose restart backend
docker compose restart frontend

# Detener servicios
docker compose down

# Eliminar volúmenes (CUIDADO: elimina datos)
docker compose down -v
```

### Base de Datos
```bash
# Reinicializar BD (elimina y recrea tablas)
docker compose exec backend python migrations/init_db.py

# Recargar datos de prueba
docker compose exec backend python migrations/seed_data.py

# Limpiar solo datos (mantiene estructura)
docker compose exec backend python -c "
from migrations.seed_data import clear_existing_data
clear_existing_data()
"

# Acceso directo a MySQL
docker compose exec mysql mysql -u veterinaria_user -p
```

### Backend
```bash
# Acceder al contenedor backend
docker compose exec backend bash

# Ejecutar scripts Python
docker compose exec backend python -c "
from app.database import get_db_info
print(get_db_info())
"

# Ver logs específicos
docker compose logs backend
```

### Frontend
```bash
# Acceder al contenedor frontend
docker compose exec frontend sh

# Instalar dependencias (si es necesario)
docker compose exec frontend npm install

# Ver logs específicos
docker compose logs frontend
```

## 🗄️ Estructura de Base de Datos

### Tabla: `duenios`
```sql
CREATE TABLE duenios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    direccion TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Tabla: `turnos`
```sql
CREATE TABLE turnos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_mascota VARCHAR(80) NOT NULL,
    fecha_turno DATETIME NOT NULL,
    tratamiento TEXT NOT NULL,
    id_duenio INT NOT NULL,
    estado ENUM('pendiente', 'confirmado', 'completado', 'cancelado') DEFAULT 'pendiente',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_duenio) REFERENCES duenios(id) ON DELETE CASCADE
);
```

### Relaciones
- **duenios** 1:N **turnos** (Un dueño puede tener múltiples turnos)
- Relación con Foreign Key y CASCADE para mantener integridad referencial

## 🔧 Troubleshooting

### Problemas Comunes

#### Los servicios no inician
```bash
# Verificar puertos disponibles
netstat -tulpn | grep -E ':(3000|5000|3306)'

# Reconstruir imágenes
docker compose build --no-cache
docker compose up -d
```

#### Error de conexión a MySQL
```bash
# Verificar salud de MySQL
docker compose exec mysql mysqladmin ping -h localhost

# Ver logs de MySQL
docker compose logs mysql

# Reiniciar MySQL
docker compose restart mysql
```

#### Frontend no carga
```bash
# Verificar logs
docker compose logs frontend

# Acceder al contenedor y verificar
docker compose exec frontend sh
npm run dev
```

#### Base de datos no responde
```bash
# Verificar pool de conexiones
docker compose exec backend python -c "
from app.database import get_db_info
print(get_db_info())
"
```

### Resetear Completamente
```bash
# Eliminar todo y empezar de cero
docker compose down -v
docker compose build --no-cache
docker compose up -d
docker compose exec backend python migrations/init_db.py
docker compose exec backend python migrations/seed_data.py
```

## 📡 API Endpoints

### 🔍 Endpoints de Sistema
```bash
# Información general de la API
GET    http://localhost:5000/

# Estado de salud del sistema
GET    http://localhost:5000/api/health
```

### 🐾 Dueños (`/api/duenios`) - ✅ IMPLEMENTADO

#### Listar Dueños
```bash
# Obtener todos los dueños
GET    http://localhost:5000/api/duenios/

# Con paginación
GET    http://localhost:5000/api/duenios/?limit=10&offset=0

# Ejemplo con curl
curl "http://localhost:5000/api/duenios/?limit=5"
```

#### Dueño Específico
```bash
# Obtener dueño por ID
GET    http://localhost:5000/api/duenios/1

# Ejemplo con curl
curl http://localhost:5000/api/duenios/1
```

#### Crear Dueño
```bash
# Crear nuevo dueño
POST   http://localhost:5000/api/duenios/
Content-Type: application/json

{
    "nombre_apellido": "Juan Pérez",
    "telefono": "+54911234567",
    "email": "juan.perez@email.com",
    "direccion": "Av. Corrientes 1234, CABA"
}

# Ejemplo con curl
curl -X POST http://localhost:5000/api/duenios/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_apellido": "Juan Pérez",
    "telefono": "+54911234567", 
    "email": "juan.perez@email.com",
    "direccion": "Av. Corrientes 1234, CABA"
  }'
```

#### Actualizar Dueño
```bash
# Actualizar dueño existente (campos opcionales)
PUT    http://localhost:5000/api/duenios/1
Content-Type: application/json

{
    "telefono": "+54911111111",
    "direccion": "Nueva dirección 456"
}

# Ejemplo con curl
curl -X PUT http://localhost:5000/api/duenios/1 \
  -H "Content-Type: application/json" \
  -d '{
    "telefono": "+54911111111",
    "direccion": "Nueva dirección 456"
  }'
```

#### Eliminar Dueño
```bash
# Eliminar dueño (elimina turnos asociados por CASCADE)
DELETE http://localhost:5000/api/duenios/1

# Ejemplo con curl
curl -X DELETE http://localhost:5000/api/duenios/1
```

#### Buscar Dueños
```bash
# Buscar por nombre o email
GET    http://localhost:5000/api/duenios/search?q=maria
GET    http://localhost:5000/api/duenios/search?q=gmail.com&limit=20

# Ejemplo con curl
curl "http://localhost:5000/api/duenios/search?q=maria"
```

#### Estadísticas de Dueños
```bash
# Obtener estadísticas básicas
GET    http://localhost:5000/api/duenios/statistics

# Ejemplo con curl
curl http://localhost:5000/api/duenios/statistics
```

### 📋 Turnos (`/api/turnos`) - ✅ IMPLEMENTADO

#### Listar Turnos
```bash
# Obtener todos los turnos
GET    http://localhost:5000/api/turnos/

# Con filtros y paginación
GET    http://localhost:5000/api/turnos/?limit=10&offset=0&estado=pendiente
GET    http://localhost:5000/api/turnos/?fecha_desde=2024-01-15&fecha_hasta=2024-01-31

# Ejemplo con curl
curl "http://localhost:5000/api/turnos/?estado=pendiente&limit=5"
```

#### Turno Específico
```bash
# Obtener turno por ID (incluye datos del dueño)
GET    http://localhost:5000/api/turnos/1

# Ejemplo con curl
curl http://localhost:5000/api/turnos/1
```

#### Crear Turno
```bash
# Crear nuevo turno
POST   http://localhost:5000/api/turnos/
Content-Type: application/json

{
    "nombre_mascota": "Firulais",
    "fecha_turno": "2024-01-20 14:30:00",
    "tratamiento": "Vacunación antirrábica",
    "id_duenio": 1,
    "estado": "pendiente"
}

# Ejemplo con curl
curl -X POST http://localhost:5000/api/turnos/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_mascota": "Firulais",
    "fecha_turno": "2024-01-20 14:30:00",
    "tratamiento": "Vacunación antirrábica",
    "id_duenio": 1
  }'
```

#### Actualizar Turno
```bash
# Actualizar turno existente (campos opcionales)
PUT    http://localhost:5000/api/turnos/1
Content-Type: application/json

{
    "fecha_turno": "2024-01-21 15:00:00",
    "tratamiento": "Vacunación antirrábica + desparasitación"
}

# Ejemplo con curl
curl -X PUT http://localhost:5000/api/turnos/1 \
  -H "Content-Type: application/json" \
  -d '{
    "fecha_turno": "2024-01-21 15:00:00",
    "tratamiento": "Vacunación antirrábica + desparasitación"
  }'
```

#### Eliminar Turno
```bash
# Eliminar turno
DELETE http://localhost:5000/api/turnos/1

# Ejemplo con curl
curl -X DELETE http://localhost:5000/api/turnos/1
```

#### Turnos por Dueño
```bash
# Obtener todos los turnos de un dueño
GET    http://localhost:5000/api/turnos/duenio/1
GET    http://localhost:5000/api/turnos/duenio/1?limit=20

# Ejemplo con curl
curl http://localhost:5000/api/turnos/duenio/1
```

#### Turnos por Fecha
```bash
# Obtener turnos de una fecha específica
GET    http://localhost:5000/api/turnos/fecha/2024-01-20
GET    http://localhost:5000/api/turnos/fecha/2024-01-20?limit=50

# Ejemplo con curl
curl http://localhost:5000/api/turnos/fecha/2024-01-20
```

#### Cambiar Estado del Turno
```bash
# Cambiar estado con validaciones de transición
PUT    http://localhost:5000/api/turnos/1/estado
Content-Type: application/json

{
    "estado": "confirmado"
}

# Ejemplo con curl - Confirmar turno
curl -X PUT http://localhost:5000/api/turnos/1/estado \
  -H "Content-Type: application/json" \
  -d '{"estado": "confirmado"}'

# Completar turno
curl -X PUT http://localhost:5000/api/turnos/1/estado \
  -H "Content-Type: application/json" \
  -d '{"estado": "completado"}'

# Cancelar turno
curl -X PUT http://localhost:5000/api/turnos/1/estado \
  -H "Content-Type: application/json" \
  -d '{"estado": "cancelado"}'
```

#### Estadísticas de Turnos
```bash
# Obtener estadísticas básicas
GET    http://localhost:5000/api/turnos/statistics

# Ejemplo con curl
curl http://localhost:5000/api/turnos/statistics
```

### 📝 Ejemplos de Respuestas

#### Éxito - Lista de Turnos
```json
{
  "success": true,
  "message": "Turnos obtenidos correctamente",
  "timestamp": "2024-01-15T10:30:00",
  "data": {
    "turnos": [
      {
        "id": 1,
        "nombre_mascota": "Firulais",
        "fecha_turno": "2024-01-20T14:30:00",
        "tratamiento": "Vacunación antirrábica",
        "estado": "pendiente",
        "dias_hasta_turno": 5,
        "created_at": "2024-01-15T09:00:00",
        "updated_at": "2024-01-15T09:00:00",
        "duenio": {
          "id": 1,
          "nombre_apellido": "María González",
          "telefono": "+54911234567",
          "email": "maria.gonzalez@email.com",
          "direccion": "Av. Santa Fe 1234, CABA"
        }
      }
    ],
    "metadata": {
      "total": 13,
      "count": 1,
      "offset": 0,
      "limit": 10,
      "has_more": true,
      "filters": {
        "estado": "pendiente",
        "fecha_desde": null,
        "fecha_hasta": null
      }
    }
  }
}
```

#### Éxito - Cambio de Estado
```json
{
  "success": true,
  "message": "Estado cambiado de \"pendiente\" a \"confirmado\"",
  "timestamp": "2024-01-15T10:30:00",
  "data": {
    "turno": {
      "id": 1,
      "nombre_mascota": "Firulais",
      "fecha_turno": "2024-01-20T14:30:00",
      "tratamiento": "Vacunación antirrábica",
      "estado": "confirmado",
      "dias_hasta_turno": 5,
      "duenio": {
        "id": 1,
        "nombre_apellido": "María González",
        "telefono": "+54911234567",
        "email": "maria.gonzalez@email.com",
        "direccion": "Av. Santa Fe 1234, CABA"
      }
    }
  }
}
```

#### Error - Transición de Estado Inválida
```json
{
  "error": "Error de validación",
  "message": "Los datos enviados no son válidos",
  "validation_errors": [
    "No se puede cambiar de \"completado\" a \"pendiente\""
  ],
  "code": 400,
  "timestamp": "2024-01-15T10:30:00"
}
```

#### Éxito - Lista de Dueños
```json
{
  "success": true,
  "message": "Dueños obtenidos correctamente",
  "timestamp": "2024-01-15T10:30:00",
  "data": {
    "duenios": [
      {
        "id": 1,
        "nombre_apellido": "María González",
        "telefono": "+54911234567",
        "email": "maria.gonzalez@email.com",
        "direccion": "Av. Santa Fe 1234, CABA",
        "created_at": "2024-01-15T09:00:00",
        "updated_at": "2024-01-15T09:00:00"
      }
    ],
    "metadata": {
      "total": 8,
      "count": 1,
      "offset": 0,
      "limit": 10,
      "has_more": true
    }
  }
}
```

#### Error - Validación
```json
{
  "error": "Error de validación",
  "message": "Los datos enviados no son válidos",
  "validation_errors": [
    "El campo 'email' es requerido",
    "Formato de teléfono inválido (8-15 dígitos)"
  ],
  "code": 400,
  "timestamp": "2024-01-15T10:30:00"
}
```

### 🧪 Pruebas Rápidas

#### Probar todas las operaciones CRUD
```bash
# 1. Listar dueños existentes
curl http://localhost:5000/api/duenios/

# 2. Crear nuevo dueño
curl -X POST http://localhost:5000/api/duenios/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_apellido": "Test Usuario",
    "telefono": "1122334455",
    "email": "test@example.com",
    "direccion": "Dirección de prueba 123"
  }'

# 3. Buscar el dueño creado
curl "http://localhost:5000/api/duenios/search?q=Test"

# 4. Actualizar el dueño (usar ID obtenido del paso 2)
curl -X PUT http://localhost:5000/api/duenios/ID_AQUI \
  -H "Content-Type: application/json" \
  -d '{"telefono": "9988776655"}'

# 5. Obtener dueño específico
curl http://localhost:5000/api/duenios/ID_AQUI

# 6. Eliminar dueño de prueba
curl -X DELETE http://localhost:5000/api/duenios/ID_AQUI
```

#### Probar operaciones completas con Turnos
```bash
# 1. Crear un dueño para los turnos
curl -X POST http://localhost:5000/api/duenios/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_apellido": "Test Veterinario",
    "telefono": "1122334455",
    "email": "test.vet@example.com",
    "direccion": "Dirección veterinaria 123"
  }'

# 2. Crear un turno (usar ID del dueño obtenido del paso 1)
curl -X POST http://localhost:5000/api/turnos/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_mascota": "Mascota Test",
    "fecha_turno": "2024-02-20 14:30:00",
    "tratamiento": "Consulta de prueba",
    "id_duenio": ID_DUENIO_AQUI
  }'

# 3. Listar turnos con filtros
curl "http://localhost:5000/api/turnos/?estado=pendiente&limit=5"

# 4. Obtener turnos del dueño
curl http://localhost:5000/api/turnos/duenio/ID_DUENIO_AQUI

# 5. Confirmar el turno (usar ID del turno obtenido del paso 2)
curl -X PUT http://localhost:5000/api/turnos/ID_TURNO_AQUI/estado \
  -H "Content-Type: application/json" \
  -d '{"estado": "confirmado"}'

# 6. Completar el turno
curl -X PUT http://localhost:5000/api/turnos/ID_TURNO_AQUI/estado \
  -H "Content-Type: application/json" \
  -d '{"estado": "completado"}'

# 7. Ver estadísticas
curl http://localhost:5000/api/turnos/statistics

# 8. Obtener turnos por fecha
curl http://localhost:5000/api/turnos/fecha/2024-02-20

# 9. Limpiar - eliminar turno y dueño
curl -X DELETE http://localhost:5000/api/turnos/ID_TURNO_AQUI
curl -X DELETE http://localhost:5000/api/duenios/ID_DUENIO_AQUI
```

## 🎯 Estado del Proyecto

### ✅ Completado
- [x] **Configuración Docker** - Servicios MySQL, Backend, Frontend
- [x] **Base de Datos** - Tablas, relaciones, constraints
- [x] **Pool de Conexiones** - MySQL con reconexión automática
- [x] **Datos de Prueba** - 8 dueños, 13 turnos con todos los estados
- [x] **Scripts de Migración** - Inicialización y seeds
- [x] **Validaciones Manuales** - Sistema de validación backend sin librerías externas
- [x] **API Dueños** - CRUD completo con paginación, búsqueda y estadísticas
- [x] **API Turnos** - CRUD completo con filtros, JOIN a dueños, transiciones de estado
- [x] **Error Handling** - Manejo global de errores con responses JSON consistentes
- [x] **Casos de Uso** - Todos los casos del sistema veterinaria implementados

### 🔄 En Desarrollo
- [ ] **Frontend Vue** - Componentes, stores, vistas
- [ ] **Interfaz de Usuario** - Formularios, tablas, navegación

### 📋 Por Implementar
- [ ] **Autenticación** - Sistema de usuarios
- [ ] **Reportes** - Estadísticas y reportes
- [ ] **Notificaciones** - Recordatorios de turnos
- [ ] **Búsqueda Avanzada** - Filtros complejos

## 📝 Notas de Desarrollo

- El sistema usa **connection pooling** para optimizar las conexiones a MySQL
- Los **constraints de BD** validan formatos de email y teléfono
- Las **relaciones CASCADE** mantienen integridad referencial
- Los **datos de prueba** cubren todos los casos de uso del sistema
- La **configuración Docker** permite desarrollo sin instalación local

## 🤝 Contribución

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE.md](LICENSE.md) para detalles.

---

**Estado actual**: Backend API REST completamente funcional ✅  
**Siguiente paso**: Implementación Frontend Vue.js 🔄