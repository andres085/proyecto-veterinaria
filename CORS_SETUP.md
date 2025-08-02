# 🔧 Configuración CORS - Resolución de Problemas

## 🚫 Problema Original:
```
Cross-Origin Request Blocked: The Same Origin Policy disallows reading from http://localhost:5000/api/duenios. 
(Reason: CORS header 'Access-Control-Allow-Origin' missing). Status code: 308.
```

## ✅ Solución Implementada:

### 1. Backend Flask - Configuración CORS

**📁 `backend/requirements.txt`**
```txt
Flask==3.1.0
mysql-connector-python==9.3.0
python-dotenv==1.1.0
Flask-CORS==4.0.0  ← Agregado
```

**📁 `backend/app/__init__.py`**
```python
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # Configuración CORS para desarrollo
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"],
            "supports_credentials": False
        }
    })
```

### 2. Frontend Vite - Configuración Proxy

**📁 `frontend/vite.config.ts`**
```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
```

**📁 `frontend/src/services/ApiService.ts`**
```typescript
const baseURL = import.meta.env.DEV 
  ? '/api'  // Use Vite proxy in development
  : import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'
```

## 🚀 Pasos para Resolver CORS:

### Paso 1: Instalar Flask-CORS en el Backend
```bash
cd backend
pip install Flask-CORS==4.0.0
```

### Paso 2: Reiniciar el Backend
```bash
# Si usas Docker
docker-compose restart backend

# Si usas directamente Python
cd backend
python run.py
```

### Paso 3: Reiniciar el Frontend
```bash
cd frontend
npm run dev
```

## 🔍 Verificación:

### 1. Verificar que el Backend está ejecutándose:
```bash
curl http://localhost:5000/
# Debería devolver JSON con información de la API
```

### 2. Verificar headers CORS:
```bash
curl -I -X OPTIONS http://localhost:5000/api/duenios
# Debería mostrar headers CORS en la respuesta
```

### 3. Verificar en el navegador:
- Abrir DevTools → Network
- Las solicitudes a `/api/*` deberían resolverse exitosamente
- No deberían aparecer errores CORS en la consola

## 🌐 Configuración por Entorno:

### Desarrollo Local:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:5000`
- CORS: Configurado para permitir localhost:3000

### Producción:
- Actualizar `origins` en CORS con la URL de producción
- Configurar variables de entorno apropiadas

## 🐛 Troubleshooting:

### Si aún tienes problemas CORS:

1. **Verificar puertos:**
   - Frontend debe estar en puerto 3000
   - Backend debe estar en puerto 5000

2. **Limpiar caché:**
   ```bash
   # Limpiar caché del navegador
   Ctrl + Shift + R (Chrome/Firefox)
   ```

3. **Verificar que Flask-CORS esté instalado:**
   ```bash
   cd backend
   pip list | grep Flask-CORS
   ```

4. **Verificar logs del backend:**
   ```bash
   docker-compose logs backend
   ```

5. **Usar proxy de Vite:**
   - El proxy está configurado para redirigir `/api` a `http://localhost:5000`
   - Esto evita problemas CORS en desarrollo

## 📋 Checklist de Resolución CORS:

- [x] Flask-CORS agregado a requirements.txt
- [x] CORS configurado en backend/__init__.py
- [x] Vite proxy configurado en vite.config.ts
- [x] ApiService actualizado para usar proxy
- [x] Headers apropiados configurados
- [x] Métodos HTTP permitidos: GET, POST, PUT, DELETE, OPTIONS
- [x] Origins permitidos: localhost:3000, 127.0.0.1:3000

## 🔄 Próximos Pasos:

1. Reiniciar ambos servicios (backend y frontend)
2. Verificar que no hay errores CORS en la consola del navegador
3. Probar las operaciones CRUD (crear, leer, actualizar, eliminar)
4. Verificar que todas las vistas funcionan correctamente

---

**✅ Con esta configuración, el problema CORS debería estar completamente resuelto.**