# Sistema de Gestión de Turnos - Veterinaria

Sistema web para gestión de turnos en una clínica veterinaria que permite administrar citas de mascotas y datos de sus dueños.

## Tecnologías

### Backend

- Framework: Flask (Python)
- Base de Datos: MySQL 8.0
- Containerización: Docker Compose

### Frontend

- Framework: Vue.js 3
- Gestor de Estado: Pinia
- Cliente HTTP: Axios
- Build Tool: Vite
- Lenguaje: TypeScript

## Requisitos Previos

- Docker y Docker Compose instalados
- Git
- Puertos disponibles: 3000 (Frontend), 5000 (Backend), 3306 (MySQL)

## Instalación

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd proyecto-veterinaria
```

### 2. Variables de Entorno

El archivo `.env.example` ya está configurado con los valores por defecto copiarlo como `.env`.

```bash
cp .env.example .env
```

### 3. Levantar Servicios

```bash
# Construir e iniciar todos los servicios
docker compose up --build -d

# Verificar que todos los servicios estén corriendo
docker compose ps
```

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

## Verificación

### Backend

```bash
curl http://localhost:5000/
curl http://localhost:5000/api/health
```

### Frontend

Abrir http://localhost:3000 en el navegador

### Base de Datos

```bash
docker compose exec mysql mysql -u veterinaria_user -p veterinaria_turnos
```

## Comandos Útiles

### Gestión de Servicios

```bash
# Iniciar servicios
docker compose up -d

# Ver logs
docker compose logs -f backend
docker compose logs -f frontend

# Reiniciar servicio específico
docker compose restart backend

# Detener servicios
docker compose down
```

### Base de Datos

```bash
# Reinicializar BD
docker compose exec backend python migrations/init_db.py

# Recargar datos de prueba
docker compose exec backend python migrations/seed_data.py

# Acceso directo a MySQL
docker compose exec mysql mysql -u veterinaria_user -p
```

## API Endpoints

### Sistema

- `GET /` - Información general de la API
- `GET /api/health` - Estado de salud del sistema

### Dueños

- `GET /api/duenios/` - Listar todos los dueños
- `GET /api/duenios/{id}` - Obtener dueño específico
- `POST /api/duenios/` - Crear nuevo dueño
- `PUT /api/duenios/{id}` - Actualizar dueño
- `DELETE /api/duenios/{id}` - Eliminar dueño
- `GET /api/duenios/search?q={query}` - Buscar dueños

### Turnos

- `GET /api/turnos/` - Listar todos los turnos
- `GET /api/turnos/{id}` - Obtener turno específico
- `POST /api/turnos/` - Crear nuevo turno
- `PUT /api/turnos/{id}` - Actualizar turno
- `DELETE /api/turnos/{id}` - Eliminar turno
- `PUT /api/turnos/{id}/estado` - Cambiar estado del turno
- `GET /api/turnos/duenio/{id}` - Turnos por dueño
- `GET /api/turnos/fecha/{fecha}` - Turnos por fecha

## Estructura de Base de Datos

### Tabla: duenios

- id (INT, AUTO_INCREMENT, PRIMARY KEY)
- nombre_apellido (VARCHAR(100), NOT NULL)
- telefono (VARCHAR(20), NOT NULL)
- email (VARCHAR(100), UNIQUE, NOT NULL)
- direccion (TEXT, NOT NULL)
- created_at, updated_at (TIMESTAMP)

### Tabla: turnos

- id (INT, AUTO_INCREMENT, PRIMARY KEY)
- nombre_mascota (VARCHAR(80), NOT NULL)
- fecha_turno (DATETIME, NOT NULL)
- tratamiento (TEXT, NOT NULL)
- id_duenio (INT, FOREIGN KEY)
- estado (ENUM: 'pendiente', 'confirmado', 'completado', 'cancelado')
- created_at, updated_at (TIMESTAMP)

## Datos de Prueba

El sistema incluye:

- 8 dueños de ejemplo
- 13 turnos con diferentes estados
- Datos históricos, actuales y futuros

## Troubleshooting

### Los servicios no inician

```bash
# Verificar puertos
netstat -tulpn | grep -E ':(3000|5000|3306)'

# Reconstruir imágenes
docker compose build --no-cache
docker compose up -d
```

### Error de conexión a MySQL

```bash
# Verificar MySQL
docker compose exec mysql mysqladmin ping -h localhost
docker compose logs mysql
docker compose restart mysql
```

### Resetear Completamente

```bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
docker compose exec backend python migrations/init_db.py
docker compose exec backend python migrations/seed_data.py
```

## Estados del Proyecto

### Completado

- Configuración Docker
- Base de Datos con tablas y relaciones
- API REST completa para Dueños y Turnos
- Validaciones y manejo de errores
- Datos de prueba

### En Desarrollo

- Frontend Vue.js
- Interfaz de Usuario

### Por Implementar

- Sistema de autenticación
- Reportes y estadísticas
- Notificaciones
- Búsqueda avanzada

## Ejemplo de Uso Rápido

```bash
# 1. Listar dueños
curl http://localhost:5000/api/duenios/

# 2. Crear nuevo dueño
curl -X POST http://localhost:5000/api/duenios/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_apellido": "Juan Pérez",
    "telefono": "1122334455",
    "email": "juan@example.com",
    "direccion": "Av. Corrientes 1234"
  }'

# 3. Crear turno para el dueño
curl -X POST http://localhost:5000/api/turnos/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_mascota": "Firulais",
    "fecha_turno": "2024-02-20 14:30:00",
    "tratamiento": "Vacunación",
    "id_duenio": 1
  }'

# 4. Listar turnos
curl http://localhost:5000/api/turnos/
```

## Contacto y Desarrollo

Backend API REST completamente funcional.
Siguiente paso: Implementación Frontend Vue.js.
