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

## 📡 API Endpoints (Planeados)

### Dueños (`/api/duenios`)
```
GET    /api/duenios/           # Listar todos
GET    /api/duenios/:id        # Obtener uno específico
POST   /api/duenios/           # Crear nuevo
PUT    /api/duenios/:id        # Actualizar
DELETE /api/duenios/:id        # Eliminar
GET    /api/duenios/search?q=  # Buscar por nombre/email
```

### Turnos (`/api/turnos`)
```
GET    /api/turnos/                    # Listar todos
GET    /api/turnos/:id                 # Obtener uno específico
POST   /api/turnos/                    # Crear nuevo
PUT    /api/turnos/:id                 # Actualizar
DELETE /api/turnos/:id                 # Eliminar
GET    /api/turnos/duenio/:id_duenio   # Turnos de un dueño
GET    /api/turnos/fecha/:fecha        # Turnos por fecha
PUT    /api/turnos/:id/estado          # Cambiar estado
```

## 🎯 Estado del Proyecto

### ✅ Completado
- [x] **Configuración Docker** - Servicios MySQL, Backend, Frontend
- [x] **Base de Datos** - Tablas, relaciones, constraints
- [x] **Pool de Conexiones** - MySQL con reconexión automática
- [x] **Datos de Prueba** - 8 dueños, 13 turnos con todos los estados
- [x] **Scripts de Migración** - Inicialización y seeds

### 🔄 En Desarrollo
- [ ] **Backend API** - Modelos, controladores, rutas
- [ ] **Frontend Vue** - Componentes, stores, vistas
- [ ] **Validaciones** - Backend y frontend
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

**Estado actual**: Base de datos y infraestructura completadas ✅  
**Siguiente paso**: Implementación de API REST Backend 🔄