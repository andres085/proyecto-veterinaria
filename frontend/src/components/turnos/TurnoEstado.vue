<template>
  <div class="turno-estado">
    <!-- Header with current state -->
    <div class="turno-estado__header">
      <h3 class="turno-estado__title">
        🔄 Cambiar Estado del Turno
      </h3>
      
      <div class="current-estado">
        <span class="current-estado__label">Estado actual:</span>
        <span class="estado-badge" :class="`estado-badge--${currentEstado}`">
          {{ getEstadoIcon(currentEstado) }} {{ getEstadoLabel(currentEstado) }}
        </span>
      </div>
    </div>

    <!-- Turno info -->
    <div v-if="turno" class="turno-estado__info">
      <div class="turno-info">
        <div class="info-item">
          <span class="info-label">🐕 Mascota:</span>
          <span class="info-value">{{ turno.nombre_mascota }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">👤 Dueño:</span>
          <span class="info-value">{{ turno.duenio?.nombre_apellido || 'N/A' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">📅 Fecha:</span>
          <span class="info-value">{{ formatDateTime(turno.fecha_turno) }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">🏥 Tratamiento:</span>
          <span class="info-value">{{ turno.tratamiento }}</span>
        </div>
      </div>
    </div>

    <!-- Estado transition options -->
    <div class="turno-estado__options">
      <h4 class="options-title">Seleccionar nuevo estado:</h4>
      
      <div class="estado-grid">
        <button
          v-for="estado in availableStates"
          :key="estado.value"
          @click="selectEstado(estado.value)"
          class="estado-option"
          :class="{ 
            'estado-option--selected': selectedEstado === estado.value,
            'estado-option--disabled': !estado.enabled 
          }"
          :disabled="!estado.enabled || loading"
          :title="estado.description"
        >
          <div class="estado-option__icon">
            {{ estado.icon }}
          </div>
          <div class="estado-option__content">
            <h5>{{ estado.label }}</h5>
            <p>{{ estado.description }}</p>
          </div>
          <div v-if="!estado.enabled" class="estado-option__disabled">
            ❌
          </div>
        </button>
      </div>
    </div>

    <!-- Transition info -->
    <div v-if="selectedEstado && selectedEstado !== currentEstado" class="turno-estado__transition">
      <div class="transition-info">
        <h4>📋 Información del cambio:</h4>
        <div class="transition-flow">
          <span class="estado-badge" :class="`estado-badge--${currentEstado}`">
            {{ getEstadoIcon(currentEstado) }} {{ getEstadoLabel(currentEstado) }}
          </span>
          <span class="transition-arrow">➡️</span>
          <span class="estado-badge" :class="`estado-badge--${selectedEstado}`">
            {{ getEstadoIcon(selectedEstado) }} {{ getEstadoLabel(selectedEstado) }}
          </span>
        </div>
        <p class="transition-description">
          {{ getTransitionDescription(currentEstado, selectedEstado) }}
        </p>
      </div>
    </div>

    <!-- Actions -->
    <div class="turno-estado__actions">
      <button
        @click="handleCancel"
        class="btn btn--secondary"
        :disabled="loading"
      >
        ❌ Cancelar
      </button>
      
      <button
        @click="handleConfirm"
        class="btn btn--primary"
        :disabled="loading || !selectedEstado || selectedEstado === currentEstado"
      >
        <LoadingSpinner 
          v-if="loading" 
          size="small" 
          color="white"
        />
        <span v-else>
          ✅ Confirmar Cambio
        </span>
      </button>
    </div>

    <!-- Error message -->
    <div v-if="error" class="turno-estado__error">
      ❌ {{ error }}
    </div>

    <!-- Success message -->
    <div v-if="success" class="turno-estado__success">
      ✅ {{ success }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import type { Turno, EstadoTurno } from '@/types/models'

// Types
interface EstadoOption {
  value: EstadoTurno
  label: string
  icon: string
  description: string
  enabled: boolean
}

export interface TurnoEstadoProps {
  turno?: Turno | null
  loading?: boolean
}

export interface TurnoEstadoEmits {
  (e: 'change', turno: Turno, newEstado: EstadoTurno): void
  (e: 'cancel'): void
  (e: 'success', turno: Turno, oldEstado: EstadoTurno, newEstado: EstadoTurno): void
}

// Props
const props = withDefaults(defineProps<TurnoEstadoProps>(), {
  turno: null,
  loading: false
})

// Emits
const emit = defineEmits<TurnoEstadoEmits>()

// State
const selectedEstado = ref<EstadoTurno | null>(null)
const error = ref<string>('')
const success = ref<string>('')

// Computed
const currentEstado = computed(() => props.turno?.estado || 'pendiente')

const availableStates = computed((): EstadoOption[] => {
  const current = currentEstado.value
  
  const states: EstadoOption[] = [
    {
      value: 'pendiente',
      label: 'Pendiente',
      icon: '⏳',
      description: 'En espera de confirmación',
      enabled: false // No se puede volver a pendiente - eliminar turno si es necesario
    },
    {
      value: 'confirmado',
      label: 'Confirmado',
      icon: '✅',
      description: 'Turno confirmado por el dueño',
      enabled: current === 'pendiente'
    },
    {
      value: 'completado',
      label: 'Completado',
      icon: '🏁',
      description: 'Consulta realizada exitosamente',
      enabled: current === 'confirmado' || current === 'pendiente'
    },
    {
      value: 'cancelado',
      label: 'Cancelado',
      icon: '❌',
      description: 'Turno cancelado (no se puede revertir)',
      enabled: current !== 'cancelado' && current !== 'completado'
    }
  ]
  
  return states
})

// Methods
const getEstadoIcon = (estado: EstadoTurno): string => {
  const icons = {
    pendiente: '⏳',
    confirmado: '✅',
    completado: '🏁',
    cancelado: '❌'
  }
  return icons[estado] || '❓'
}

const getEstadoLabel = (estado: EstadoTurno): string => {
  const labels = {
    pendiente: 'Pendiente',
    confirmado: 'Confirmado',
    completado: 'Completado',
    cancelado: 'Cancelado'
  }
  return labels[estado] || estado
}

const formatDateTime = (dateString?: string): string => {
  if (!dateString) return 'N/A'
  
  try {
    const date = new Date(dateString)
    return date.toLocaleString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return 'N/A'
  }
}

const getTransitionDescription = (from: EstadoTurno, to: EstadoTurno): string => {
  const transitions: Record<string, string> = {
    'pendiente->confirmado': 'El turno será marcado como confirmado. El dueño ha aceptado la cita.',
    'pendiente->completado': 'El turno será marcado como completado directamente. La consulta se realizó exitosamente.',
    'pendiente->cancelado': 'El turno será cancelado. Esta acción no se puede deshacer.',
    'confirmado->completado': 'El turno será marcado como completado. La consulta se realizó exitosamente.',
    'confirmado->cancelado': 'El turno confirmado será cancelado. Esta acción no se puede deshacer.',
  }
  
  const key = `${from}->${to}`
  return transitions[key] || `El estado cambiará de ${getEstadoLabel(from)} a ${getEstadoLabel(to)}.`
}

const selectEstado = (estado: EstadoTurno) => {
  if (estado === currentEstado.value) return
  
  selectedEstado.value = estado
  error.value = ''
  success.value = ''
}

const handleConfirm = () => {
  if (!props.turno || !selectedEstado.value || selectedEstado.value === currentEstado.value) {
    error.value = 'Por favor selecciona un estado válido'
    return
  }

  // Validate transition
  const isValidTransition = validateTransition(currentEstado.value, selectedEstado.value)
  if (!isValidTransition) {
    error.value = 'Transición de estado no válida'
    return
  }

  // Clear messages
  error.value = ''
  success.value = ''

  // Emit change
  emit('change', props.turno, selectedEstado.value)
  
  console.log(`🔄 Cambiando estado de turno ${props.turno.id}: ${currentEstado.value} -> ${selectedEstado.value}`)
}

const handleCancel = () => {
  emit('cancel')
}

const validateTransition = (from: EstadoTurno, to: EstadoTurno): boolean => {
  // Define valid transitions
  const validTransitions: Record<EstadoTurno, EstadoTurno[]> = {
    pendiente: ['confirmado', 'completado', 'cancelado'],
    confirmado: ['completado', 'cancelado'],
    completado: [], // Terminal state
    cancelado: []   // Terminal state
  }
  
  return validTransitions[from]?.includes(to) || false
}

const showSuccess = (message: string) => {
  success.value = message
  error.value = ''
  
  // Clear after 3 seconds
  setTimeout(() => {
    success.value = ''
  }, 3000)
}

const showError = (message: string) => {
  error.value = message
  success.value = ''
}

const reset = () => {
  selectedEstado.value = null
  error.value = ''
  success.value = ''
}

// Watchers
watch(() => props.turno, () => {
  reset()
}, { immediate: true })

// Lifecycle
onMounted(() => {
  reset()
})

// Expose methods
defineExpose({
  reset,
  showSuccess,
  showError
})

console.log('🔧 Componente TurnoEstado cargado')
</script>

<style scoped>
.turno-estado {
  background: white;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  max-width: 600px;
  margin: 0 auto;
}

/* Header */
.turno-estado__header {
  padding: var(--spacing-xl) var(--spacing-xl) var(--spacing-lg);
  border-bottom: 1px solid var(--border-light);
  text-align: center;
}

.turno-estado__title {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--primary-color);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
}

.current-estado {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
}

.current-estado__label {
  color: var(--text-light);
  font-size: var(--font-size-sm);
}

/* Turno Info */
.turno-estado__info {
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid var(--border-light);
  background-color: var(--background-color);
}

.turno-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-md);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.info-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--text-light);
}

.info-value {
  font-size: var(--font-size-sm);
  color: var(--text-color);
}

/* Estado Options */
.turno-estado__options {
  padding: var(--spacing-xl);
}

.options-title {
  margin: 0 0 var(--spacing-lg) 0;
  color: var(--text-color);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-medium);
}

.estado-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.estado-option {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius-md);
  background: white;
  cursor: pointer;
  transition: all var(--transition-normal);
  text-align: left;
}

.estado-option:hover:not(.estado-option--disabled) {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.estado-option--selected {
  border-color: var(--primary-color);
  background-color: var(--primary-light);
}

.estado-option--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.estado-option__icon {
  font-size: var(--font-size-xl);
  line-height: 1;
  flex-shrink: 0;
}

.estado-option__content {
  flex: 1;
}

.estado-option__content h5 {
  margin: 0 0 var(--spacing-xs) 0;
  color: var(--text-color);
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-medium);
}

.estado-option__content p {
  margin: 0;
  color: var(--text-light);
  font-size: var(--font-size-sm);
  line-height: 1.3;
}

.estado-option__disabled {
  position: absolute;
  top: var(--spacing-xs);
  right: var(--spacing-xs);
  font-size: var(--font-size-sm);
}

/* Estado Badge */
.estado-badge {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-full);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  text-align: center;
  white-space: nowrap;
}

.estado-badge--pendiente {
  background-color: var(--warning-light);
  color: var(--warning-color);
}

.estado-badge--confirmado {
  background-color: var(--success-light);
  color: var(--success-color);
}

.estado-badge--completado {
  background-color: var(--info-light);
  color: var(--info-color);
}

.estado-badge--cancelado {
  background-color: var(--danger-light);
  color: var(--danger-color);
}

/* Transition Info */
.turno-estado__transition {
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid var(--border-light);
  background-color: var(--info-light);
}

.transition-info h4 {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--info-color);
  font-size: var(--font-size-md);
}

.transition-flow {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.transition-arrow {
  font-size: var(--font-size-lg);
  color: var(--primary-color);
}

.transition-description {
  margin: 0;
  color: var(--info-color);
  font-size: var(--font-size-sm);
  text-align: center;
  line-height: 1.4;
}

/* Actions */
.turno-estado__actions {
  display: flex;
  gap: var(--spacing-md);
  padding: var(--spacing-lg) var(--spacing-xl) var(--spacing-xl);
  justify-content: flex-end;
}

/* Messages */
.turno-estado__error {
  margin: var(--spacing-md) var(--spacing-xl) 0;
  padding: var(--spacing-md);
  background-color: var(--danger-light);
  color: var(--danger-color);
  border-radius: var(--border-radius-md);
  font-weight: var(--font-weight-medium);
  text-align: center;
}

.turno-estado__success {
  margin: var(--spacing-md) var(--spacing-xl) 0;
  padding: var(--spacing-md);
  background-color: var(--success-light);
  color: var(--success-color);
  border-radius: var(--border-radius-md);
  font-weight: var(--font-weight-medium);
  text-align: center;
}

/* Responsive */
@media (max-width: 768px) {
  .turno-estado {
    margin: 0;
    border-radius: 0;
    box-shadow: none;
  }
  
  .turno-estado__header,
  .turno-estado__info,
  .turno-estado__options,
  .turno-estado__transition,
  .turno-estado__actions {
    padding-left: var(--spacing-md);
    padding-right: var(--spacing-md);
  }
  
  .turno-info {
    grid-template-columns: 1fr;
  }
  
  .estado-grid {
    grid-template-columns: 1fr;
  }
  
  .turno-estado__actions {
    flex-direction: column-reverse;
  }
  
  .btn {
    width: 100%;
  }
  
  .transition-flow {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
  
  .transition-arrow {
    transform: rotate(90deg);
  }
}

/* Animations */
.turno-estado__error,
.turno-estado__success {
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Focus states */
.estado-option:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}
</style>