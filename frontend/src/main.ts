import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/globals.css'

console.log('🚀 Iniciando aplicación Vue.js - Veterinaria Turnos')

const app = createApp(App)
const pinia = createPinia()

// Configurar plugins
app.use(pinia)
app.use(router)

// Configuración global
app.config.globalProperties.$appName = import.meta.env.VITE_APP_TITLE || 'Sistema Veterinaria'
app.config.globalProperties.$version = import.meta.env.VITE_APP_VERSION || '1.0.0'

app.mount('#app')