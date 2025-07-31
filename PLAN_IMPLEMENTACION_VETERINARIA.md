# Plan de Implementación - Sistema Veterinaria Turnos

## 📋 TODO List - Orden de Implementación

### 🚀 FASE 1: Setup y Configuración Inicial

#### 1.1 Estructura del Proyecto

- [x] **1.1.1** Crear estructura de directorios del proyecto
- [x] **1.1.2** Inicializar repositorio Git
- [x] **1.1.3** Crear .gitignore para Python y Node.js
- [x] **1.1.4** Configurar archivo README.md principal

#### 1.2 Configuración Docker

- [x] **1.2.1** Crear docker-compose.yml con servicios MySQL, Backend, Frontend
- [x] **1.2.2** Configurar variables de entorno (.env)
- [x] **1.2.3** Crear Dockerfile para backend (Python Flask)
- [x] **1.2.4** Crear Dockerfile para frontend (Node.js/Vue)
- [x] **1.2.5** Configurar redes y volúmenes Docker
- [x] **1.2.6** Levantar docker-compose up para verificar servicios

### 🗄️ FASE 2: Base de Datos

#### 2.1 Configuración MySQL

- [x] **2.1.1** Crear script de inicialización de base de datos (init_db.py)
- [x] **2.1.2** Definir schema de tabla `duenios`
- [x] **2.1.3** Definir schema de tabla `turnos` con foreign keys
- [x] **2.1.5** Configurar constraints y validaciones a nivel BD

#### 2.2 Seeds y Datos de Prueba

- [x] **2.2.1** Crear script seed_data.py con datos de prueba
- [x] **2.2.2** Insertar dueños de ejemplo (5-10 registros)
- [x] **2.2.3** Insertar turnos de ejemplo con diferentes estados
- [x] **2.2.4** Validar integridad referencial

### ⚙️ FASE 3: Backend Flask - Infraestructura

#### 3.1 Configuración Base Flask

- [x] **3.1.1** Crear app/**init**.py con factory pattern
- [x] **3.1.2** Configurar Flask-CORS para comunicación frontend
- [x] **3.1.3** Implementar database.py con connection pooling MySQL
- [x] **3.1.4** Configurar manejo de variables de entorno
- [x] **3.1.5** Crear run.py como punto de entrada

#### 3.2 Configuración de Validaciones

- [ ] **3.2.1** Instalar y configurar Marshmallow
- [ ] **3.2.2** Crear schemas base para validación
- [ ] **3.2.3** Configurar manejo de errores global

### 🏗️ FASE 4: Backend - Módulo Dueños

#### 4.1 Modelo Dueño

- [ ] **4.1.1** Crear app/duenios/\_model.py
- [ ] **4.1.2** Implementar clase DuenioModel con métodos CRUD
- [ ] **4.1.3** Implementar método get_all() para listar dueños
- [ ] **4.1.4** Implementar método get_one(id) para obtener dueño específico
- [ ] **4.1.5** Implementar método create() para crear nuevo dueño
- [ ] **4.1.6** Implementar método update() para actualizar dueño
- [ ] **4.1.7** Implementar método delete() para eliminar dueño
- [ ] **4.1.8** Implementar método search(query) para búsqueda
- [ ] **4.1.9** Implementar serialización/deserialización

#### 4.2 Controlador Dueño

- [ ] **4.2.1** Crear app/duenios/\_controller.py
- [ ] **4.2.2** Implementar DuenioController.get_all()
- [ ] **4.2.3** Implementar DuenioController.get_one(id)
- [ ] **4.2.4** Implementar DuenioController.create(data) con validaciones
- [ ] **4.2.5** Implementar DuenioController.update(id, data)
- [ ] **4.2.6** Implementar DuenioController.delete(id)
- [ ] **4.2.7** Implementar DuenioController.search(query)
- [ ] **4.2.8** Agregar manejo de errores y validaciones Marshmallow

#### 4.3 Rutas Dueño

- [ ] **4.3.1** Crear app/duenios/\_routes.py con Blueprint
- [ ] **4.3.2** Implementar GET /api/duenios/ (listar todos)
- [ ] **4.3.3** Implementar GET /api/duenios/:id (obtener uno)
- [ ] **4.3.4** Implementar POST /api/duenios/ (crear)
- [ ] **4.3.5** Implementar PUT /api/duenios/:id (actualizar)
- [ ] **4.3.6** Implementar DELETE /api/duenios/:id (eliminar)
- [ ] **4.3.7** Implementar GET /api/duenios/search?q= (buscar)
- [ ] **4.3.8** Registrar Blueprint en app/**init**.py

### 🏗️ FASE 5: Backend - Módulo Turnos

#### 5.1 Modelo Turno

- [ ] **5.1.1** Crear app/turnos/\_model.py
- [ ] **5.1.2** Implementar clase TurnoModel con métodos CRUD
- [ ] **5.1.3** Implementar método get_all() con join a dueños
- [ ] **5.1.4** Implementar método get_one(id) con datos completos
- [ ] **5.1.5** Implementar método create() con validación de dueño
- [ ] **5.1.6** Implementar método update() para modificar turno
- [ ] **5.1.7** Implementar método delete() para cancelar turno
- [ ] **5.1.8** Implementar método get_by_duenio(id_duenio)
- [ ] **5.1.9** Implementar método get_by_fecha(fecha)
- [ ] **5.1.10** Implementar método update_estado(id, estado)
- [ ] **5.1.11** Implementar serialización con datos de dueño

#### 5.2 Controlador Turno

- [ ] **5.2.1** Crear app/turnos/\_controller.py
- [ ] **5.2.2** Implementar TurnoController.get_all()
- [ ] **5.2.3** Implementar TurnoController.get_one(id)
- [ ] **5.2.4** Implementar TurnoController.create(data) con validaciones
- [ ] **5.2.5** Implementar TurnoController.update(id, data)
- [ ] **5.2.6** Implementar TurnoController.delete(id)
- [ ] **5.2.7** Implementar TurnoController.get_by_duenio(id_duenio)
- [ ] **5.2.8** Implementar TurnoController.get_by_fecha(fecha)
- [ ] **5.2.9** Implementar TurnoController.update_estado(id, estado)
- [ ] **5.2.10** Agregar validaciones de fecha y disponibilidad

#### 5.3 Rutas Turno

- [ ] **5.3.1** Crear app/turnos/\_routes.py con Blueprint
- [ ] **5.3.2** Implementar GET /api/turnos/ (listar todos)
- [ ] **5.3.3** Implementar GET /api/turnos/:id (obtener uno)
- [ ] **5.3.4** Implementar POST /api/turnos/ (crear)
- [ ] **5.3.5** Implementar PUT /api/turnos/:id (actualizar)
- [ ] **5.3.6** Implementar DELETE /api/turnos/:id (eliminar)
- [ ] **5.3.7** Implementar GET /api/turnos/duenio/:id_duenio
- [ ] **5.3.8** Implementar GET /api/turnos/fecha/:fecha
- [ ] **5.3.9** Implementar PUT /api/turnos/:id/estado
- [ ] **5.3.10** Registrar Blueprint en app/**init**.py

### 🎨 FASE 6: Frontend Vue - Configuración Base

#### 6.1 Setup Inicial Frontend

- [ ] **6.1.1** Crear proyecto Vue 3 con TypeScript
- [ ] **6.1.2** Configurar Vite (vite.config.ts)
- [ ] **6.1.3** Configurar TypeScript (tsconfig.json)
- [ ] **6.1.4** Instalar dependencias (Vue Router, Pinia, Axios)
- [ ] **6.1.5** Configurar estructura de directorios src/

#### 6.2 Configuración Base

- [ ] **6.2.1** Crear src/main.ts con configuración base
- [ ] **6.2.2** Crear src/App.vue como componente raíz
- [ ] **6.2.3** Configurar src/router/index.ts con rutas principales
- [ ] **6.2.4** Crear src/services/ApiService.ts para comunicación HTTP
- [ ] **6.2.5** Configurar variables de entorno para API base URL

#### 6.3 Tipos TypeScript

- [ ] **6.3.1** Crear src/types/models.ts con interfaces
- [ ] **6.3.2** Definir interface Duenio
- [ ] **6.3.3** Definir interface Turno
- [ ] **6.3.4** Definir types para payloads y responses
- [ ] **6.3.5** Definir enums para estados de turno

### 🏬 FASE 7: Frontend - Stores Pinia

#### 7.1 Store Dueños

- [ ] **7.1.1** Crear src/stores/duenioStore.ts
- [ ] **7.1.2** Implementar estado reactivo (dueños, loading, error)
- [ ] **7.1.3** Implementar acción fetchAll() para listar dueños
- [ ] **7.1.4** Implementar acción create(data) para crear dueño
- [ ] **7.1.5** Implementar acción update(id, data) para actualizar
- [ ] **7.1.6** Implementar acción remove(id) para eliminar
- [ ] **7.1.7** Implementar acción search(query) para búsqueda
- [ ] **7.1.8** Agregar manejo de errores y loading states

#### 7.2 Store Turnos

- [ ] **7.2.1** Crear src/stores/turnoStore.ts
- [ ] **7.2.2** Implementar estado reactivo (turnos, loading, error)
- [ ] **7.2.3** Implementar acción fetchAll() para listar turnos
- [ ] **7.2.4** Implementar acción create(data) para crear turno
- [ ] **7.2.5** Implementar acción update(id, data) para actualizar
- [ ] **7.2.6** Implementar acción remove(id) para eliminar
- [ ] **7.2.7** Implementar acción fetchByDuenio(id) para turnos por dueño
- [ ] **7.2.8** Implementar acción fetchByFecha(fecha) para turnos por fecha
- [ ] **7.2.9** Implementar acción updateEstado(id, estado)
- [ ] **7.2.10** Agregar getters para filtros y computadas

### 🧩 FASE 8: Frontend - Componentes Base

#### 8.1 Componentes Compartidos

- [ ] **8.1.1** Crear src/components/shared/ConfirmDialog.vue
- [ ] **8.1.2** Crear src/components/shared/LoadingSpinner.vue
- [ ] **8.1.3** Crear src/components/shared/DatePicker.vue
- [ ] **8.1.4** Crear src/components/shared/SearchInput.vue
- [ ] **8.1.5** Agregar estilos CSS globales básicos

#### 8.2 Componentes Dueños

- [ ] **8.2.1** Crear src/components/duenios/DuenioForm.vue
- [ ] **8.2.2** Implementar formulario con validaciones (nombre, teléfono, email, dirección)
- [ ] **8.2.3** Crear src/components/duenios/DuenioList.vue
- [ ] **8.2.4** Implementar tabla con acciones (ver, editar, eliminar)
- [ ] **8.2.5** Crear src/components/duenios/DuenioBuscar.vue
- [ ] **8.2.6** Implementar búsqueda en tiempo real
- [ ] **8.2.7** Agregar paginación y filtros

#### 8.3 Componentes Turnos

- [ ] **8.3.1** Crear src/components/turnos/TurnoForm.vue
- [ ] **8.3.2** Implementar formulario con selección de dueño y fecha
- [ ] **8.3.3** Crear src/components/turnos/TurnoList.vue
- [ ] **8.3.4** Implementar tabla con información completa
- [ ] **8.3.5** Crear src/components/turnos/TurnoEstado.vue
- [ ] **8.3.6** Implementar componente para cambio de estado
- [ ] **8.3.7** Crear src/components/turnos/TurnoCalendario.vue
- [ ] **8.3.8** Implementar vista de calendario básica

### 📱 FASE 9: Frontend - Vistas Principales

#### 9.1 Vistas Base

- [ ] **9.1.1** Crear src/views/HomeView.vue con dashboard
- [ ] **9.1.2** Crear src/views/DueniosView.vue
- [ ] **9.1.3** Integrar DuenioList, DuenioForm y DuenioBuscar
- [ ] **9.1.4** Crear src/views/TurnosView.vue
- [ ] **9.1.5** Integrar TurnoList, TurnoForm y filtros
- [ ] **9.1.6** Crear src/views/CalendarioView.vue
- [ ] **9.1.7** Integrar TurnoCalendario con navegación de fechas

#### 9.2 Navegación y Layout

- [ ] **9.2.1** Implementar menú de navegación en App.vue
- [ ] **9.2.2** Configurar rutas en router/index.ts
- [ ] **9.2.3** Agregar breadcrumbs y navegación activa
- [ ] **9.2.4** Implementar layout responsive

### 🎯 FASE 10: Integración y Funcionalidades Avanzadas

#### 10.1 Integración Completa

- [ ] **10.1.1** Conectar todos los componentes con stores
- [ ] **10.1.2** Implementar flujo completo: crear dueño → agendar turno
- [ ] **10.1.3** Implementar búsqueda global
- [ ] **10.1.4** Agregar filtros avanzados por estado y fecha

#### 10.2 Validaciones Frontend

- [ ] **10.2.1** Instalar Vee-Validate + Yup
- [ ] **10.2.2** Implementar validaciones en DuenioForm
- [ ] **10.2.3** Implementar validaciones en TurnoForm
- [ ] **10.2.4** Agregar feedback visual de errores

#### 10.3 UX/UI Mejoras

- [ ] **10.3.1** Implementar confirmaciones para eliminaciones
- [ ] **10.3.2** Agregar loading states en todas las acciones
- [ ] **10.3.3** Implementar notificaciones toast
- [ ] **10.3.4** Mejorar estilos CSS y responsiveness

### 🚀 FASE 11: Documentación y Preparación MVP

#### 11.1 Documentación del Proyecto

- [ ] **11.1.1** Completar README.md con instrucciones de desarrollo
- [ ] **11.1.2** Documentar API endpoints con ejemplos
- [ ] **11.1.3** Crear guía de instalación y uso
- [ ] **11.1.4** Documentar comandos Docker para desarrollo

#### 11.2 Preparación para Presentación

- [ ] **11.2.1** Verificar que todos los casos de uso funcionen
- [ ] **11.2.2** Preparar datos de demostración
- [ ] **11.2.3** Crear scripts de inicialización con datos de ejemplo
- [ ] **11.2.4** Validar flujo completo de la aplicación

#### 11.3 Refinamiento MVP

- [ ] **11.3.1** Pulir interfaz de usuario para presentación
- [ ] **11.3.2** Agregar mensajes de éxito/error claros
- [ ] **11.3.3** Verificar responsiveness básico
- [ ] **11.3.4** Revisión final de funcionalidades core

---

## 📊 Resumen por Fases

| Fase | Descripción             | Tareas    | Tiempo Estimado |
| ---- | ----------------------- | --------- | --------------- |
| 1    | Setup y Configuración   | 10 tareas | 1-2 días        |
| 2    | Base de Datos           | 9 tareas  | 1 día           |
| 3    | Backend Infraestructura | 8 tareas  | 1 día           |
| 4    | Backend Dueños          | 24 tareas | 2-3 días        |
| 5    | Backend Turnos          | 30 tareas | 3-4 días        |
| 6    | Frontend Base           | 13 tareas | 1-2 días        |
| 7    | Stores Pinia            | 18 tareas | 2 días          |
| 8    | Componentes Frontend    | 21 tareas | 3-4 días        |
| 9    | Vistas Principales      | 14 tareas | 2-3 días        |
| 10   | Integración Avanzada    | 12 tareas | 2-3 días        |
| 11   | Documentación y MVP     | 12 tareas | 1-2 días        |

**TOTAL: 171 tareas - Tiempo estimado: 16-20 días**

---

## 🔧 Comandos Útiles Durante Desarrollo

```bash
# Levantar servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f backend
docker-compose logs -f frontend

# Acceder a contenedor MySQL
docker-compose exec mysql mysql -u root -p

# Reiniciar servicio específico
docker-compose restart backend

# Ejecutar comando en contenedor
docker-compose exec backend python migrations/init_db.py

# Detener todos los servicios
docker-compose down

# Eliminar volúmenes (CUIDADO: elimina datos)
docker-compose down -v

# Build y rebuild de imágenes
docker-compose build
docker-compose up --build
```
