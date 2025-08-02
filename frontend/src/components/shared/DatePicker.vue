<template>
  <div class="date-picker" :class="{ 'date-picker--disabled': disabled }">
    <label
      v-if="label"
      :for="inputId"
      class="date-picker__label"
      :class="{ 'date-picker__label--required': required }"
    >
      {{ label }}
    </label>
    
    <div class="date-picker__wrapper">
      <input
        :id="inputId"
        ref="dateInput"
        type="date"
        class="date-picker__input"
        :class="{
          'date-picker__input--error': hasError,
          'date-picker__input--disabled': disabled
        }"
        :value="modelValue"
        :min="minDate"
        :max="maxDate"
        :required="required"
        :disabled="disabled"
        :placeholder="placeholder"
        @input="handleInput"
        @change="handleChange"
        @focus="handleFocus"
        @blur="handleBlur"
      />
      
      <div class="date-picker__icon">
        📅
      </div>
    </div>
    
    <!-- Error message -->
    <div
      v-if="errorMessage"
      class="date-picker__error"
      role="alert"
      :aria-live="hasError ? 'polite' : 'off'"
    >
      {{ errorMessage }}
    </div>
    
    <!-- Helper text -->
    <div
      v-if="helperText && !errorMessage"
      class="date-picker__helper"
    >
      {{ helperText }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

// Types
export interface DatePickerProps {
  modelValue: string
  label?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  minDate?: string
  maxDate?: string
  helperText?: string
  errorMessage?: string
  validateOnBlur?: boolean
  id?: string
}

export interface DatePickerEmits {
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
  (e: 'focus', event: FocusEvent): void
  (e: 'blur', event: FocusEvent): void
  (e: 'validation', isValid: boolean): void
}

// Props
const props = withDefaults(defineProps<DatePickerProps>(), {
  placeholder: '',
  required: false,
  disabled: false,
  validateOnBlur: true
})

// Emits
const emit = defineEmits<DatePickerEmits>()

// Refs
const dateInput = ref<HTMLInputElement>()
const internalError = ref<string>('')
const isFocused = ref(false)

// Computed
const inputId = computed(() => props.id || `date-picker-${Math.random().toString(36).substr(2, 9)}`)

const hasError = computed(() => !!(props.errorMessage || internalError.value))

const effectiveErrorMessage = computed(() => props.errorMessage || internalError.value)

// Methods
const validateDate = (value: string): string => {
  if (!value && props.required) {
    return 'Este campo es requerido'
  }
  
  if (value) {
    const date = new Date(value)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    // Validar fecha válida
    if (isNaN(date.getTime())) {
      return 'Fecha inválida'
    }
    
    // Validar fecha mínima
    if (props.minDate) {
      const minDate = new Date(props.minDate)
      if (date < minDate) {
        return `La fecha debe ser posterior a ${formatDate(props.minDate)}`
      }
    }
    
    // Validar fecha máxima
    if (props.maxDate) {
      const maxDate = new Date(props.maxDate)
      if (date > maxDate) {
        return `La fecha debe ser anterior a ${formatDate(props.maxDate)}`
      }
    }
    
    // Validar que no sea fecha pasada (solo si no hay minDate específica)
    if (!props.minDate && date < today) {
      return 'No se puede seleccionar una fecha pasada'
    }
  }
  
  return ''
}

const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  } catch {
    return dateString
  }
}

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  const value = target.value
  
  emit('update:modelValue', value)
  
  // Limpiar error interno al escribir
  if (internalError.value) {
    internalError.value = ''
  }
}

const handleChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const value = target.value
  
  emit('change', value)
  
  // Validar inmediatamente en change
  const error = validateDate(value)
  internalError.value = error
  emit('validation', !error)
}

const handleFocus = (event: FocusEvent) => {
  isFocused.value = true
  emit('focus', event)
}

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false
  emit('blur', event)
  
  // Validar en blur si está habilitado
  if (props.validateOnBlur) {
    const error = validateDate(props.modelValue)
    internalError.value = error
    emit('validation', !error)
  }
}

// Public methods
const focus = () => {
  dateInput.value?.focus()
}

const validate = (): boolean => {
  const error = validateDate(props.modelValue)
  internalError.value = error
  emit('validation', !error)
  return !error
}

// Watch for external validation
watch(() => props.modelValue, (newValue) => {
  if (props.validateOnBlur && !isFocused.value) {
    const error = validateDate(newValue)
    internalError.value = error
    emit('validation', !error)
  }
})

// Expose methods
defineExpose({
  focus,
  validate
})

console.log('🔧 Componente DatePicker cargado')
</script>

<style scoped>
.date-picker {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.date-picker--disabled {
  opacity: 0.6;
  pointer-events: none;
}

.date-picker__label {
  font-weight: 500;
  color: #333;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.date-picker__label--required::after {
  content: ' *';
  color: #dc3545;
}

.date-picker__wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.date-picker__input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 1rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  background-color: white;
  transition: all 0.2s ease;
  color: #333;
}

.date-picker__input:focus {
  outline: none;
  border-color: #2c5aa0;
  box-shadow: 0 0 0 3px rgba(44, 90, 160, 0.1);
}

.date-picker__input:hover:not(:disabled) {
  border-color: #999;
}

.date-picker__input--error {
  border-color: #dc3545;
}

.date-picker__input--error:focus {
  border-color: #dc3545;
  box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
}

.date-picker__input--disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.date-picker__icon {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: #666;
  font-size: 1.125rem;
}

.date-picker__error {
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.date-picker__error::before {
  content: '⚠️';
  font-size: 0.75rem;
}

.date-picker__helper {
  color: #666;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

/* Custom date input styling */
.date-picker__input::-webkit-calendar-picker-indicator {
  opacity: 0;
  position: absolute;
  right: 0;
  width: 2.5rem;
  height: 100%;
  cursor: pointer;
}

/* Firefox */
.date-picker__input::-moz-focus-inner {
  border: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .date-picker__input {
    padding: 1rem 2.5rem 1rem 1rem;
    font-size: 16px; /* Prevents zoom on iOS */
  }
}

/* Dark theme support */
@media (prefers-color-scheme: dark) {
  .date-picker__label {
    color: #e0e0e0;
  }
  
  .date-picker__input {
    background-color: #2d2d2d;
    border-color: #555;
    color: #e0e0e0;
  }
  
  .date-picker__input:focus {
    border-color: #4a90e2;
  }
  
  .date-picker__input--disabled {
    background-color: #1a1a1a;
  }
  
  .date-picker__icon {
    color: #ccc;
  }
  
  .date-picker__helper {
    color: #ccc;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .date-picker__input {
    border-width: 3px;
  }
  
  .date-picker__input:focus {
    box-shadow: 0 0 0 3px;
  }
}
</style>