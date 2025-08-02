<template>
  <form @submit.prevent="handleSubmit" class="turno-form">
    <div class="turno-form__header">
      <h2 class="turno-form__title">
        {{ mode === 'create' ? '📅 Nuevo Turno' : '✏️ Editar Turno' }}
      </h2>
      
      <p class="turno-form__subtitle">
        {{ mode === 'create' 
          ? 'Agenda una nueva cita para una mascota' 
          : 'Modifica los datos del turno seleccionado' 
        }}
      </p>
    </div>

    <div class="turno-form__body">
      <!-- Selección de Dueño -->
      <div class="form-group">
        <label for="id_duenio" class="form-label form-label--required">
          👤 Dueño de la Mascota
        </label>
        
        <!-- Dueño seleccionado (vista compacta) -->
        <div v-if="selectedDuenio && !showDuenioSelector" class="selected-duenio">
          <div class="selected-duenio__info">
            <h4>{{ selectedDuenio.nombre_apellido }}</h4>
            <p>📧 {{ selectedDuenio.email }} | 📱 {{ selectedDuenio.telefono }}</p>
          </div>
          <button
            type="button"
            @click="showDuenioSelector = true"
            class="btn btn--ghost btn--small"
          >
            🔄 Cambiar
          </button>
        </div>

        <!-- Selector de dueño -->
        <div v-else class="duenio-selector">
          <div class="duenio-search">
            <input
              v-model="duenioSearchQuery"
              type="text"
              class="form-input"
              placeholder="Buscar dueño por nombre o email..."
              @input="searchDuenios"
            />
            <div v-if="duenioSearchResults.length" class="search-results">
              <div
                v-for="duenio in duenioSearchResults"
                :key="duenio.id"
                class="search-result"
                @click="selectDuenio(duenio)"
              >
                <div class="result-info">
                  <strong>{{ duenio.nombre_apellido }}</strong>
                  <small>{{ duenio.email }}</small>
                </div>
              </div>
            </div>
            <div v-else-if="duenioSearchQuery && !loadingDuenios" class="no-results">
              ❌ No se encontraron dueños
            </div>
          </div>
          
          <button
            v-if="selectedDuenio"
            type="button"
            @click="clearDuenioSelection"
            class="btn btn--secondary btn--small"
          >
            ❌ Limpiar Selección
          </button>
        </div>
        
        <span v-if="errors.id_duenio" class="form-error">
          {{ errors.id_duenio }}
        </span>
        <span v-else class="form-help">
          Busca y selecciona el propietario de la mascota
        </span>
      </div>

      <!-- Nombre de la Mascota -->
      <div class="form-group">
        <label for="nombre_mascota" class="form-label form-label--required">
          🐕 Nombre de la Mascota
        </label>
        <input
          id="nombre_mascota"
          ref="mascotaInput"
          v-model="formData.nombre_mascota"
          type="text"
          class="form-input"
          :class="{ 'form-input--error': errors.nombre_mascota }"
          placeholder="Ej: Max, Luna, Bobby"
          :disabled="loading"
          required
          minlength="1"
          maxlength="80"
          @blur="validateField('nombre_mascota')"
          @input="clearFieldError('nombre_mascota')"
        />
        <span v-if="errors.nombre_mascota" class="form-error">
          {{ errors.nombre_mascota }}
        </span>
        <span v-else class="form-help">
          Nombre de la mascota para identificar el turno
        </span>
      </div>

      <!-- Fecha y Hora del Turno -->
      <div class="form-group">
        <label for="fecha_turno" class="form-label form-label--required">
          📅 Fecha y Hora del Turno
        </label>
        
        <div class="datetime-container">
          <DatePicker
            v-model="formData.fecha_turno"
            :disabled="loading"
            :min="minDate"
            :max="maxDate"
            :error="errors.fecha_turno"
            placeholder="Selecciona fecha y hora"
            show-time
            @change="validateField('fecha_turno')"
            @input="clearFieldError('fecha_turno')"
          />
        </div>
        
        <span v-if="errors.fecha_turno" class="form-error">
          {{ errors.fecha_turno }}
        </span>
        <span v-else class="form-help">
          Fecha y hora de la cita veterinaria
        </span>
      </div>

      <!-- Tratamiento -->
      <div class="form-group">
        <label for="tratamiento" class="form-label form-label--required">
          🏥 Tratamiento / Motivo de la Consulta
        </label>
        <textarea
          id="tratamiento"
          v-model="formData.tratamiento"
          class="form-input form-input--textarea"
          :class="{ 'form-input--error': errors.tratamiento }"
          placeholder="Ej: Consulta general, vacunación, control de rutina, problema específico..."
          :disabled="loading"
          required
          minlength="3"
          maxlength="500"
          rows="4"
          @blur="validateField('tratamiento')"
          @input="clearFieldError('tratamiento')"
        ></textarea>
        <span v-if="errors.tratamiento" class="form-error">
          {{ errors.tratamiento }}
        </span>
        <span v-else class="form-help">
          Describe el motivo de la consulta o tratamiento a realizar
        </span>
      </div>

      <!-- Estado (solo en modo edición) -->
      <div v-if="mode === 'edit'" class="form-group">
        <label for="estado" class="form-label">
          🔄 Estado del Turno
        </label>
        <select
          id="estado"
          v-model="formData.estado"
          class="form-input"
          :class="{ 'form-input--error': errors.estado }"
          :disabled="loading"
        >
          <option value="pendiente">⏳ Pendiente</option>
          <option value="confirmado">✅ Confirmado</option>
          <option value="completado">🏁 Completado</option>
          <option value="cancelado">❌ Cancelado</option>
        </select>
        <span v-if="errors.estado" class="form-error">
          {{ errors.estado }}
        </span>
        <span v-else class="form-help">
          Estado actual del turno
        </span>
      </div>
    </div>

    <!-- Actions -->
    <div class="turno-form__footer">
      <button
        type="button"
        class="btn btn--secondary"
        @click="handleCancel"
        :disabled="loading"
      >
        ❌ Cancelar
      </button>
      
      <button
        type="submit"
        class="btn btn--primary"
        :disabled="loading || !isFormValid"
      >
        <LoadingSpinner 
          v-if="loading" 
          size="small" 
          color="white"
        />
        <span v-else>
          {{ mode === 'create' ? '📅 Crear Turno' : '💾 Guardar Cambios' }}
        </span>
      </button>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="turno-form__success">
      ✅ {{ successMessage }}
    </div>

    <!-- Error Message -->
    <div v-if="generalError" class="turno-form__error">
      ❌ {{ generalError }}
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick, onMounted } from 'vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import DatePicker from '@/components/shared/DatePicker.vue'
import { useDuenioStore } from '@/stores/duenioStore'
import type { 
  Turno, 
  Duenio, 
  CreateTurnoPayload, 
  UpdateTurnoPayload,
  EstadoTurno 
} from '@/types/models'

// Types
export interface TurnoFormProps {
  turno?: Turno | null
  mode?: 'create' | 'edit'
  loading?: boolean
  duenios?: Duenio[]
}

export interface TurnoFormEmits {
  (e: 'submit', data: CreateTurnoPayload | UpdateTurnoPayload): void
  (e: 'cancel'): void
  (e: 'success', turno: Turno): void
}

// Props
const props = withDefaults(defineProps<TurnoFormProps>(), {
  turno: null,
  mode: 'create',
  loading: false,
  duenios: () => []
})

// Emits
const emit = defineEmits<TurnoFormEmits>()

// Stores
const duenioStore = useDuenioStore()

// Refs
const mascotaInput = ref<HTMLInputElement>()

// Reactive state
const formData = reactive<CreateTurnoPayload>({
  nombre_mascota: '',
  fecha_turno: '',
  tratamiento: '',
  id_duenio: 0,
  estado: 'pendiente' as EstadoTurno
})

const errors = reactive<Record<string, string>>({
  nombre_mascota: '',
  fecha_turno: '',
  tratamiento: '',
  id_duenio: '',
  estado: ''
})

const successMessage = ref<string>('')
const generalError = ref<string>('')
const showDuenioSelector = ref<boolean>(true)
const duenioSearchQuery = ref<string>('')
const duenioSearchResults = ref<Duenio[]>([])
const selectedDuenio = ref<Duenio | null>(null)
const loadingDuenios = ref<boolean>(false)

// Computed
const minDate = computed(() => {
  const today = new Date()
  return today.toISOString().slice(0, 16) // YYYY-MM-DDTHH:MM format
})

const maxDate = computed(() => {
  const futureDate = new Date()
  futureDate.setMonth(futureDate.getMonth() + 6) // 6 months from now
  return futureDate.toISOString().slice(0, 16)
})

const isFormValid = computed(() => {
  return formData.nombre_mascota.length >= 1 &&
         formData.fecha_turno.length > 0 &&
         formData.tratamiento.length >= 3 &&
         formData.id_duenio > 0 &&
         !Object.values(errors).some(error => error)
})

// Methods
const validateField = (field: keyof typeof formData): boolean => {
  errors[field] = ''
  
  switch (field) {
    case 'nombre_mascota':
      if (!formData.nombre_mascota.trim()) {
        errors[field] = 'El nombre de la mascota es requerido'
      } else if (formData.nombre_mascota.length > 80) {
        errors[field] = 'El nombre no puede exceder 80 caracteres'
      }
      break
      
    case 'fecha_turno':
      if (!formData.fecha_turno) {
        errors[field] = 'La fecha y hora son requeridas'
      } else {
        const selectedDate = new Date(formData.fecha_turno)
        const now = new Date()
        
        if (selectedDate <= now) {
          errors[field] = 'La fecha debe ser futura'
        }
      }
      break
      
    case 'tratamiento':
      if (!formData.tratamiento.trim()) {
        errors[field] = 'El tratamiento es requerido'
      } else if (formData.tratamiento.length < 3) {
        errors[field] = 'El tratamiento debe tener al menos 3 caracteres'
      } else if (formData.tratamiento.length > 500) {
        errors[field] = 'El tratamiento no puede exceder 500 caracteres'
      }
      break
      
    case 'id_duenio':
      if (!formData.id_duenio || formData.id_duenio <= 0) {
        errors[field] = 'Debe seleccionar un dueño'
      }
      break
  }
  
  return !errors[field]
}

const validateAllFields = (): boolean => {
  const fields: (keyof typeof formData)[] = ['nombre_mascota', 'fecha_turno', 'tratamiento', 'id_duenio']
  return fields.every(field => validateField(field))
}

const clearFieldError = (field: keyof typeof errors) => {
  if (errors[field]) {
    errors[field] = ''
  }
}

const searchDuenios = async () => {
  if (duenioSearchQuery.value.length < 2) {
    duenioSearchResults.value = []
    return
  }

  loadingDuenios.value = true
  
  try {
    // Use existing duenios from props or fetch from store
    const allDuenios = props.duenios.length > 0 ? props.duenios : duenioStore.duenios
    
    // Filter duenios based on search query
    duenioSearchResults.value = allDuenios.filter(duenio =>
      duenio.nombre_apellido.toLowerCase().includes(duenioSearchQuery.value.toLowerCase()) ||
      duenio.email.toLowerCase().includes(duenioSearchQuery.value.toLowerCase())
    ).slice(0, 5) // Limit to 5 results
    
  } catch (error) {
    console.error('Error searching duenios:', error)
    duenioSearchResults.value = []
  } finally {
    loadingDuenios.value = false
  }
}

const selectDuenio = (duenio: Duenio) => {
  selectedDuenio.value = duenio
  formData.id_duenio = duenio.id || 0
  showDuenioSelector.value = false
  duenioSearchQuery.value = ''
  duenioSearchResults.value = []
  clearFieldError('id_duenio')
}

const clearDuenioSelection = () => {
  selectedDuenio.value = null
  formData.id_duenio = 0
  duenioSearchQuery.value = ''
  duenioSearchResults.value = []
}

const resetForm = () => {
  formData.nombre_mascota = ''
  formData.fecha_turno = ''
  formData.tratamiento = ''
  formData.id_duenio = 0
  formData.estado = 'pendiente'
  
  Object.keys(errors).forEach(key => {
    errors[key as keyof typeof errors] = ''
  })
  
  selectedDuenio.value = null
  showDuenioSelector.value = true
  duenioSearchQuery.value = ''
  duenioSearchResults.value = []
  successMessage.value = ''
  generalError.value = ''
}

const loadTurnoData = () => {
  if (props.turno && props.mode === 'edit') {
    formData.nombre_mascota = props.turno.nombre_mascota
    formData.fecha_turno = props.turno.fecha_turno
    formData.tratamiento = props.turno.tratamiento
    formData.id_duenio = props.turno.id_duenio
    formData.estado = props.turno.estado
    
    // Find and set the selected duenio
    const duenio = props.duenios.find(d => d.id === props.turno?.id_duenio) ||
                   duenioStore.duenios.find(d => d.id === props.turno?.id_duenio)
    
    if (duenio) {
      selectedDuenio.value = duenio
      showDuenioSelector.value = false
    }
  }
}

const handleSubmit = () => {
  // Clear previous messages
  successMessage.value = ''
  generalError.value = ''
  
  // Validate form
  if (!validateAllFields()) {
    generalError.value = 'Por favor corrige los errores en el formulario'
    return
  }
  
  // Emit data
  const submitData = { ...formData }
  emit('submit', submitData)
  
  console.log(`📝 Formulario turno ${props.mode} enviado:`, submitData)
}

const handleCancel = () => {
  emit('cancel')
}

const showSuccess = (message: string) => {
  successMessage.value = message
  generalError.value = ''
  
  // Clear after 3 seconds
  setTimeout(() => {
    successMessage.value = ''
  }, 3000)
}

const showError = (message: string) => {
  generalError.value = message
  successMessage.value = ''
}

// Focus management
const focusFirstField = async () => {
  await nextTick()
  if (!selectedDuenio.value) {
    // Focus duenio search if no duenio selected
    const searchInput = document.querySelector('.duenio-search input') as HTMLInputElement
    searchInput?.focus()
  } else {
    // Focus mascota name input
    mascotaInput.value?.focus()
  }
}

// Watchers
watch(() => props.turno, () => {
  loadTurnoData()
}, { immediate: true })

watch(() => props.mode, () => {
  if (props.mode === 'create') {
    resetForm()
  }
}, { immediate: true })

// Load duenios on mount if not provided
onMounted(async () => {
  loadTurnoData()
  
  // Load duenios if not provided and store is empty
  if (props.duenios.length === 0 && duenioStore.duenios.length === 0) {
    try {
      await duenioStore.fetchAll()
    } catch (error) {
      console.error('Error loading duenios:', error)
    }
  }
  
  if (props.mode === 'create') {
    focusFirstField()
  }
})

// Expose methods
defineExpose({
  resetForm,
  validateAllFields,
  showSuccess,
  showError,
  focusFirstField
})

console.log('🔧 Componente TurnoForm cargado')
</script>

<style scoped>
.turno-form {
  background: white;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  max-width: 700px;
  margin: 0 auto;
}

.turno-form__header {
  padding: var(--spacing-xl) var(--spacing-xl) var(--spacing-lg);
  border-bottom: 1px solid var(--border-light);
  text-align: center;
}

.turno-form__title {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--primary-color);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
}

.turno-form__subtitle {
  margin: 0;
  color: var(--text-light);
  font-size: var(--font-size-sm);
}

.turno-form__body {
  padding: var(--spacing-xl);
}

.form-group {
  margin-bottom: var(--spacing-lg);
}

.form-input--textarea {
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
}

/* Dueño Selection */
.selected-duenio {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  background-color: var(--success-light);
  border: 1px solid var(--success-color);
  border-radius: var(--border-radius-md);
}

.selected-duenio__info h4 {
  margin: 0 0 var(--spacing-xs) 0;
  color: var(--success-color);
  font-size: var(--font-size-md);
}

.selected-duenio__info p {
  margin: 0;
  color: var(--text-light);
  font-size: var(--font-size-sm);
}

.duenio-selector {
  position: relative;
}

.duenio-search {
  position: relative;
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid var(--border-color);
  border-top: none;
  border-radius: 0 0 var(--border-radius-md) var(--border-radius-md);
  box-shadow: var(--shadow-md);
  z-index: 10;
  max-height: 200px;
  overflow-y: auto;
}

.search-result {
  padding: var(--spacing-md);
  cursor: pointer;
  border-bottom: 1px solid var(--border-light);
  transition: background-color var(--transition-normal);
}

.search-result:hover {
  background-color: var(--background-color);
}

.search-result:last-child {
  border-bottom: none;
}

.result-info strong {
  display: block;
  color: var(--text-color);
  font-size: var(--font-size-sm);
}

.result-info small {
  color: var(--text-light);
  font-size: var(--font-size-xs);
}

.no-results {
  padding: var(--spacing-md);
  text-align: center;
  color: var(--text-light);
  font-size: var(--font-size-sm);
  border: 1px solid var(--border-color);
  border-top: none;
  border-radius: 0 0 var(--border-radius-md) var(--border-radius-md);
  background: white;
}

/* DateTime Container */
.datetime-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

/* Footer */
.turno-form__footer {
  display: flex;
  gap: var(--spacing-md);
  padding: var(--spacing-lg) var(--spacing-xl) var(--spacing-xl);
  border-top: 1px solid var(--border-light);
  background-color: var(--background-color);
  justify-content: flex-end;
}

/* Messages */
.turno-form__success {
  margin: var(--spacing-md) var(--spacing-xl) 0;
  padding: var(--spacing-md);
  background-color: var(--success-light);
  color: var(--success-color);
  border-radius: var(--border-radius-md);
  font-weight: var(--font-weight-medium);
  text-align: center;
}

.turno-form__error {
  margin: var(--spacing-md) var(--spacing-xl) 0;
  padding: var(--spacing-md);
  background-color: var(--danger-light);
  color: var(--danger-color);
  border-radius: var(--border-radius-md);
  font-weight: var(--font-weight-medium);
  text-align: center;
}

/* Responsive */
@media (max-width: 768px) {
  .turno-form {
    margin: 0;
    border-radius: 0;
    box-shadow: none;
  }
  
  .turno-form__header,
  .turno-form__body,
  .turno-form__footer {
    padding-left: var(--spacing-md);
    padding-right: var(--spacing-md);
  }
  
  .turno-form__footer {
    flex-direction: column-reverse;
  }
  
  .btn {
    width: 100%;
  }
  
  .selected-duenio {
    flex-direction: column;
    gap: var(--spacing-sm);
    align-items: stretch;
  }
}

/* Form validation states */
.form-input:valid:not(:placeholder-shown) {
  border-color: var(--success-color);
}

.form-input:invalid:not(:placeholder-shown) {
  border-color: var(--warning-color);
}

/* Focus states */
.form-input:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

/* Animation for messages */
.turno-form__success,
.turno-form__error {
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
</style>