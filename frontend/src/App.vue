<template>
  <div id="app">
    <header class="header">
      <h1>🐾 Sistema Veterinaria - Gestión de Turnos</h1>
    </header>
    
    <main class="main">
      <div class="welcome">
        <h2>Bienvenido al Sistema de Turnos</h2>
        <p>Frontend Vue.js funcionando correctamente</p>
        <div class="status">
          <span class="status-badge">Estado: Activo</span>
        </div>
      </div>
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

.main {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.welcome {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.status-badge {
  background-color: #4caf50;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
}
</style>