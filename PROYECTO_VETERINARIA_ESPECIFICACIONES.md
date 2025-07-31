# Sistema de Gestión de Turnos - Veterinaria

## 📋 Descripción del Proyecto

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
    FOREIGN KEY (id_duenio) REFERENCES duenios(id) ON DELETE CASCADE,
    INDEX idx_fecha_turno (fecha_turno),
    INDEX idx_duenio (id_duenio)
);
```

### Relaciones
- **duenios** 1:N **turnos** (Un dueño puede tener múltiples turnos)
- Relación con Foreign Key y CASCADE para mantener integridad referencial

## 🎯 Funcionalidades Principales

### Gestión de Dueños
- ✅ Crear nuevo dueño
- ✅ Listar todos los dueños
- ✅ Buscar dueño por nombre/email
- ✅ Actualizar datos del dueño
- ✅ Eliminar dueño (y sus turnos asociados)
- ✅ Validar email único

### Gestión de Turnos
- ✅ Agendar nuevo turno
- ✅ Listar turnos (todos/por fecha/por dueño)
- ✅ Modificar turno existente
- ✅ Cancelar turno
- ✅ Cambiar estado del turno
- ✅ Filtrar por estado y fecha
- ✅ Validar disponibilidad horaria

## 🔌 API REST Endpoints

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

## 📂 Estructura del Proyecto

```
veterinaria-turnos/
├── docker-compose.yml           # Servicios Docker
├── .env                        # Variables de entorno
├── requirements.txt            # Dependencias Python
├── README.md                   # Documentación
├── backend/
│   ├── app/
│   │   ├── __init__.py        # Factory Flask
│   │   ├── database.py        # Conexión MySQL
│   │   ├── duenios/
│   │   │   ├── _model.py      # Modelo Dueño
│   │   │   ├── _controller.py # Controlador Dueño
│   │   │   └── _routes.py     # Rutas Dueño
│   │   └── turnos/
│   │       ├── _model.py      # Modelo Turno
│   │       ├── _controller.py # Controlador Turno
│   │       └── _routes.py     # Rutas Turno
│   ├── migrations/
│   │   ├── init_db.py         # Inicialización BD
│   │   └── seed_data.py       # Datos de prueba
│   ├── run.py                 # Punto de entrada
│   └── Dockerfile             # Imagen backend
└── frontend/
    ├── package.json           # Dependencias Node
    ├── vite.config.ts         # Configuración Vite
    ├── tsconfig.json          # Configuración TypeScript
    ├── src/
    │   ├── main.ts           # Punto de entrada
    │   ├── App.vue           # Componente raíz
    │   ├── router/
    │   │   └── index.ts      # Configuración rutas
    │   ├── stores/
    │   │   ├── duenioStore.ts    # Store dueños
    │   │   └── turnoStore.ts     # Store turnos
    │   ├── types/
    │   │   └── models.ts     # Interfaces TypeScript
    │   ├── services/
    │   │   └── ApiService.ts # Cliente HTTP
    │   ├── components/
    │   │   ├── duenios/
    │   │   │   ├── DuenioForm.vue
    │   │   │   ├── DuenioList.vue
    │   │   │   └── DuenioBuscar.vue
    │   │   ├── turnos/
    │   │   │   ├── TurnoForm.vue
    │   │   │   ├── TurnoList.vue
    │   │   │   ├── TurnoCalendario.vue
    │   │   │   └── TurnoEstado.vue
    │   │   └── shared/
    │   │       ├── ConfirmDialog.vue
    │   │       ├── DatePicker.vue
    │   │       └── LoadingSpinner.vue
    │   └── views/
    │       ├── HomeView.vue
    │       ├── DueniosView.vue
    │       ├── TurnosView.vue
    │       └── CalendarioView.vue
    └── Dockerfile             # Imagen frontend
```

## 🐳 Docker Compose Services

### docker-compose.yml
```yaml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - veterinaria_network

  backend:
    build: ./backend
    environment:
      DB_HOST: mysql
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
      DB_NAME: ${DB_NAME}
      DB_PORT: 3306
    ports:
      - "5000:5000"
    depends_on:
      - mysql
    networks:
      - veterinaria_network

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      VITE_API_BASE_URL: http://localhost:5000/api
    depends_on:
      - backend
    networks:
      - veterinaria_network

volumes:
  mysql_data:

networks:
  veterinaria_network:
    driver: bridge
```

## 🔧 Stack Tecnológico Detallado

### Backend Dependencies (requirements.txt)
```
Flask==3.1.0
Flask-CORS==4.0.0
mysql-connector-python==9.3.0
python-dotenv==1.1.0
marshmallow==3.22.0
flask-marshmallow==0.15.0
```

### Frontend Dependencies (package.json)
```json
{
  "dependencies": {
    "vue": "^3.4.21",
    "vue-router": "^4.5.1",
    "pinia": "^2.3.1",
    "axios": "^1.10.0",
    "@vueuse/core": "^10.5.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.2.1",
    "typescript": "~5.7.2",
    "vite": "^6.2.0",
    "vue-tsc": "^2.2.4"
  }
}
```

## 🚀 Comandos de Desarrollo

### Desarrollo Local
```bash
# Levantar servicios
docker-compose up -d

# Inicializar base de datos (primera vez)
docker-compose exec backend python migrations/init_db.py

# Logs de servicios
docker-compose logs -f backend
docker-compose logs -f frontend

# Detener servicios
docker-compose down
```

### Desarrollo sin Docker
```bash
# Backend
cd backend
pip install -r requirements.txt
python migrations/init_db.py
python run.py

# Frontend
cd frontend
npm install
npm run dev
```

## 📊 Características Técnicas

### Validaciones
- **Backend**: Marshmallow para validación de esquemas
- **Frontend**: Vee-Validate + Yup para formularios
- **Base de Datos**: Constraints y foreign keys

### Seguridad
- CORS configurado correctamente
- Validación de entrada en ambos extremos
- Sanitización de datos SQL

### UX/UI
- Interfaz responsive
- Loading states
- Confirmaciones para acciones destructivas
- Feedback visual de errores
- Calendario visual para turnos

## 🎯 Casos de Uso Principales

1. **Registrar nuevo dueño y agendar turno**
2. **Buscar turnos por fecha específica**
3. **Modificar estado de turno (pendiente → confirmado → completado)**
4. **Consultar historial de turnos de una mascota/dueño**
5. **Cancelar turno y reprogramar**
6. **Ver agenda diaria/semanal de la veterinaria**