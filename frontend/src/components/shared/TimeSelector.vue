<template>
  <div class="time-selector" :class="{ 'time-selector--disabled': disabled }">
    <label
      v-if="label"
      :for="inputId"
      class="time-selector__label"
      :class="{ 'time-selector__label--required': required }"
    >
      {{ label }}
    </label>
    
    <div class="time-selector__wrapper">
      <select
        :id="inputId"
        ref="timeSelect"
        class="time-selector__input"
        :class="{
          'time-selector__input--error': hasError,
          'time-selector__input--disabled': disabled
        }"
        :value="modelValue"
        :required="required"
        :disabled="disabled"
        @input="handleInput"
        @change="handleChange"
        @focus="handleFocus"
        @blur="handleBlur"
      >
        <option value="" disabled>{{ placeholder }}</option>
        <optgroup label="🌅 Turno Mañana (9:00 - 13:00)">
          <option value="09:00">09:00</option>
          <option value="09:30">09:30</option>
          <option value="10:00">10:00</option>
          <option value="10:30">10:30</option>
          <option value="11:00">11:00</option>
          <option value="11:30">11:30</option>
          <option value="12:00">12:00</option>
          <option value="12:30">12:30</option>
          <option value="13:00">13:00</option>
        </optgroup>
        <optgroup label="🌆 Turno Tarde (17:00 - 20:00)">
          <option value="17:00">17:00</option>
          <option value="17:30">17:30</option>
          <option value="18:00">18:00</option>
          <option value="18:30">18:30</option>
          <option value="19:00">19:00</option>
          <option value="19:30">19:30</option>
          <option value="20:00">20:00</option>
        </optgroup>
      </select>
      
      <div class="time-selector__icon">
        🕐
      </div>
    </div>
    
    <!-- Error message -->
    <div
      v-if="errorMessage"
      class="time-selector__error"
      role="alert"
      :aria-live="hasError ? 'polite' : 'off'"
    >
      {{ errorMessage }}
    </div>
    
    <!-- Helper text -->
    <div
      v-if="helperText && !errorMessage"
      class="time-selector__helper"
    >
      {{ helperText }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// Types
export interface TimeSelectorProps {
  modelValue: string
  label?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  helperText?: string
  errorMessage?: string
  validateOnBlur?: boolean
  id?: string
}

export interface TimeSelectorEmits {
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
  (e: 'focus', event: FocusEvent): void
  (e: 'blur', event: FocusEvent): void
  (e: 'validation', isValid: boolean): void
}

// Props
const props = withDefaults(defineProps<TimeSelectorProps>(), {
  placeholder: 'Selecciona una hora',
  required: false,
  disabled: false,
  validateOnBlur: true
})

// Emits
const emit = defineEmits<TimeSelectorEmits>()

// Refs
const timeSelect = ref<HTMLSelectElement>()
const internalError = ref<string>('')
const isFocused = ref(false)

// Computed
const inputId = computed(() => props.id || `time-selector-${Math.random().toString(36).substr(2, 9)}`)

const hasError = computed(() => !!(props.errorMessage || internalError.value))

// Methods
const validateTime = (value: string): string => {
  if (!value && props.required) {
    return 'Debe seleccionar una hora'
  }
  
  return ''
}

const handleInput = (event: Event) => {
  const target = event.target as HTMLSelectElement
  const value = target.value
  
  emit('update:modelValue', value)
  
  // Limpiar error interno al seleccionar
  if (internalError.value) {
    internalError.value = ''
  }
}

const handleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  const value = target.value
  
  emit('change', value)
  
  // Validar inmediatamente en change
  const error = validateTime(value)
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
    const error = validateTime(props.modelValue)
    internalError.value = error
    emit('validation', !error)
  }
}

// Public methods
const focus = () => {
  timeSelect.value?.focus()
}

const validate = (): boolean => {
  const error = validateTime(props.modelValue)
  internalError.value = error
  emit('validation', !error)
  return !error
}

// Expose methods
defineExpose({
  focus,
  validate
})

console.log('🔧 Componente TimeSelector cargado')
</script>

<style scoped>
.time-selector {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.time-selector--disabled {
  opacity: 0.6;
  pointer-events: none;
}

.time-selector__label {
  font-weight: 500;
  color: #333;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.time-selector__label--required::after {
  content: ' *';
  color: #dc3545;
}

.time-selector__wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.time-selector__input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 1rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  background-color: white;
  transition: all 0.2s ease;
  color: #333;
  cursor: pointer;
}

.time-selector__input:focus {
  outline: none;
  border-color: #2c5aa0;
  box-shadow: 0 0 0 3px rgba(44, 90, 160, 0.1);
}

.time-selector__input:hover:not(:disabled) {
  border-color: #999;
}

.time-selector__input--error {
  border-color: #dc3545;
}

.time-selector__input--error:focus {
  border-color: #dc3545;
  box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
}

.time-selector__input--disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.time-selector__icon {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: #666;
  font-size: 1.125rem;
}

.time-selector__error {
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.time-selector__error::before {
  content: '⚠️';
  font-size: 0.75rem;
}

.time-selector__helper {
  color: #666;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

/* Custom select styling */
.time-selector__input option {
  padding: 0.5rem;
  background-color: white;
  color: #333;
}

.time-selector__input optgroup {
  font-weight: 600;
  color: #2c5aa0;
  background-color: #f8f9fa;
}

.time-selector__input option:checked {
  background-color: #2c5aa0;
  color: white;
}

/* Responsive */
@media (max-width: 768px) {
  .time-selector__input {
    padding: 1rem 2.5rem 1rem 1rem;
    font-size: 16px; /* Prevents zoom on iOS */
  }
}

/* Dark theme support */
@media (prefers-color-scheme: dark) {
  .time-selector__label {
    color: #e0e0e0;
  }
  
  .time-selector__input {
    background-color: #2d2d2d;
    border-color: #555;
    color: #e0e0e0;
  }
  
  .time-selector__input:focus {
    border-color: #4a90e2;
  }
  
  .time-selector__input--disabled {
    background-color: #1a1a1a;
  }
  
  .time-selector__icon {
    color: #ccc;
  }
  
  .time-selector__helper {
    color: #ccc;
  }
  
  .time-selector__input option {
    background-color: #2d2d2d;
    color: #e0e0e0;
  }
  
  .time-selector__input optgroup {
    background-color: #1a1a1a;
    color: #4a90e2;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .time-selector__input {
    border-width: 3px;
  }
  
  .time-selector__input:focus {
    box-shadow: 0 0 0 3px;
  }
}
</style>