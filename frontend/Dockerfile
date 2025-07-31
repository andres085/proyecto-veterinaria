# Usar imagen oficial de Node.js 18
FROM node:18-alpine

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración de dependencias
COPY package*.json ./

# Instalar dependencias con npm install legacy para evitar conflictos
RUN npm install --legacy-peer-deps

# Copiar el código de la aplicación
COPY . .

# Exponer puerto 3000
EXPOSE 3000

# Configurar variables de entorno para desarrollo
ENV NODE_ENV=development
ENV VITE_HOST=0.0.0.0
ENV VITE_PORT=3000

# Comando para ejecutar la aplicación en modo desarrollo
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]