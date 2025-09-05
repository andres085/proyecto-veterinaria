<template>
  <div id="app">
    <header class="header">
      <h1>🐾 Sistema Veterinaria - Gestión de Turnos</h1>
      <nav class="nav">
        <router-link to="/" class="nav-link">🏠 Inicio</router-link>
        <router-link to="/duenios" class="nav-link">👥 Dueños</router-link>
        <router-link to="/turnos" class="nav-link">📋 Turnos</router-link>
        <router-link to="/calendario" class="nav-link">📅 Calendario</router-link>
      </nav>
    </header>
    
    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
console.log('📱 Componente App.vue cargado')
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  background-color: #2c5aa0;
  color: white;
  padding: 1rem;
  text-align: center;
}

.header h1 {
  margin: 0 0 1rem 0;
}

.nav {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-link.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
  font-weight: bold;
}

.main {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

@media (max-width: 768px) {
  .main {
    padding: 1rem;
  }
  
  .nav {
    flex-direction: column;
    align-items: center;
  }
  
  .nav-link {
    margin: 0.25rem 0;
  }
}
</style>