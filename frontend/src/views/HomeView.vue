<template>
  <div class="home">
    <div class="welcome-card">
      <h2>🐾 Bienvenido al Sistema de Turnos</h2>
      <p>Sistema de gestión de turnos para clínica veterinaria</p>
      
      <div class="status-info">
        <div class="status-item">
          <span class="status-label">Frontend:</span>
          <span class="status-badge success">Vue.js 3 + TypeScript</span>
        </div>
        <div class="status-item">
          <span class="status-label">Estado:</span>
          <span class="status-badge success">Configuración Base Completada</span>
        </div>
        <div class="status-item">
          <span class="status-label">API:</span>
          <span class="status-badge pending">{{ apiUrl }}</span>
        </div>
      </div>
    </div>

    <div class="features-grid">
      <div class="feature-card">
        <h3>👥 Gestión de Dueños</h3>
        <p>Administra la información de los propietarios de mascotas</p>
        <router-link to="/duenios" class="feature-link">Ir a Dueños →</router-link>
      </div>

      <div class="feature-card">
        <h3>📋 Gestión de Turnos</h3>
        <p>Agenda y gestiona las citas veterinarias</p>
        <router-link to="/turnos" class="feature-link">Ir a Turnos →</router-link>
      </div>

      <div class="feature-card">
        <h3>📅 Calendario</h3>
        <p>Vista de calendario para organizar las citas</p>
        <router-link to="/calendario" class="feature-link">Ver Calendario →</router-link>
      </div>
    </div>

    <div class="tech-info">
      <h3>🔧 Tecnologías Implementadas</h3>
      <div class="tech-list">
        <span class="tech-badge">Vue.js 3</span>
        <span class="tech-badge">TypeScript</span>
        <span class="tech-badge">Vue Router</span>
        <span class="tech-badge">Pinia</span>
        <span class="tech-badge">Axios</span>
        <span class="tech-badge">Vite</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const apiUrl = import.meta.env.VITE_API_BASE_URL || 'No configurada'

console.log('🏠 Vista Home cargada')
console.log('🌐 API URL configurada:', apiUrl)
</script>

<style scoped>
.home {
  max-width: 1000px;
  margin: 0 auto;
}

.welcome-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  margin-bottom: 2rem;
}

.welcome-card h2 {
  color: #2c5aa0;
  margin-bottom: 1rem;
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
}

.status-label {
  font-weight: bold;
  color: #666;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: bold;
}

.status-badge.success {
  background-color: #4caf50;
  color: white;
}

.status-badge.pending {
  background-color: #ff9800;
  color: white;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.feature-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.2s;
}

.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.feature-card h3 {
  color: #2c5aa0;
  margin-bottom: 1rem;
}

.feature-link {
  display: inline-block;
  margin-top: 1rem;
  color: #2c5aa0;
  text-decoration: none;
  font-weight: bold;
  transition: color 0.2s;
}

.feature-link:hover {
  color: #1e3f73;
}

.tech-info {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.tech-info h3 {
  color: #2c5aa0;
  margin-bottom: 1rem;
}

.tech-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}

.tech-badge {
  background-color: #e3f2fd;
  color: #1976d2;
  padding: 0.25rem 0.75rem;
  border-radius: 16px;
  font-size: 0.9rem;
  font-weight: bold;
}

@media (max-width: 768px) {
  .status-item {
    flex-direction: column;
    gap: 0.25rem;
    text-align: center;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>