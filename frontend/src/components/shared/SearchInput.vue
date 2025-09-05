<template>
  <div class="search-input" :class="{ 'search-input--disabled': disabled }">
    <label
      v-if="label"
      :for="inputId"
      class="search-input__label"
    >
      {{ label }}
    </label>
    
    <div class="search-input__wrapper">
      <!-- Search icon -->
      <div class="search-input__icon search-input__icon--search">
        🔍
      </div>
      
      <!-- Input field -->
      <input
        :id="inputId"
        ref="searchInput"
        type="text"
        class="search-input__input"
        :class="{
          'search-input__input--loading': loading,
          'search-input__input--disabled': disabled,
          'search-input__input--clearable': clearable && modelValue
        }"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :autocomplete="autocomplete"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        @keydown.enter="handleEnter"
        @keydown.escape="handleEscape"
      />
      
      <!-- Loading spinner -->
      <div
        v-if="loading"
        class="search-input__icon search-input__icon--loading"
        role="status"
        aria-label="Buscando..."
      >
        <div class="search-input__spinner"></div>
      </div>
      
      <!-- Clear button -->
      <button
        v-else-if="clearable && modelValue && !disabled"
        type="button"
        class="search-input__clear"
        title="Limpiar búsqueda"
        @click="handleClear"
        @mousedown.prevent
      >
        ❌
      </button>
    </div>
    
    <!-- Results count -->
    <div
      v-if="showResultsCount && resultsCount !== undefined"
      class="search-input__results"
    >
      {{ formatResultsCount(resultsCount) }}
    </div>
    
    <!-- Helper text -->
    <div
      v-if="helperText"
      class="search-input__helper"
    >
      {{ helperText }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'

// Types
export interface SearchInputProps {
  modelValue: string
  label?: string
  placeholder?: string
  disabled?: boolean
  loading?: boolean
  clearable?: boolean
  debounce?: number
  minLength?: number
  maxLength?: number
  autocomplete?: string
  helperText?: string
  showResultsCount?: boolean
  resultsCount?: number
  id?: string
}

export interface SearchInputEmits {
  (e: 'update:modelValue', value: string): void
  (e: 'search', query: string): void
  (e: 'clear'): void
  (e: 'focus', event: FocusEvent): void
  (e: 'blur', event: FocusEvent): void
  (e: 'enter', query: string): void
}

// Props
const props = withDefaults(defineProps<SearchInputProps>(), {
  placeholder: 'Buscar...',
  disabled: false,
  loading: false,
  clearable: true,
  debounce: 300,
  minLength: 0,
  autocomplete: 'off',
  showResultsCount: false
})

// Emits
const emit = defineEmits<SearchInputEmits>()

// Refs
const searchInput = ref<HTMLInputElement>()
const debounceTimer = ref<number | null>(null)
const isFocused = ref(false)

// Computed
const inputId = computed(() => props.id || `search-input-${Math.random().toString(36).substr(2, 9)}`)

// Methods
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  const value = target.value
  
  // Aplicar límite de caracteres
  if (props.maxLength && value.length > props.maxLength) {
    return
  }
  
  emit('update:modelValue', value)
  
  // Debounced search
  if (debounceTimer.value) {
    clearTimeout(debounceTimer.value)
  }
  
  debounceTimer.value = window.setTimeout(() => {
    if (value.length >= props.minLength) {
      emit('search', value)
    } else if (value.length === 0) {
      emit('search', '')
    }
  }, props.debounce)
}

const handleFocus = (event: FocusEvent) => {
  isFocused.value = true
  emit('focus', event)
}

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false
  emit('blur', event)
}

const handleEnter = (event: KeyboardEvent) => {
  event.preventDefault()
  
  // Cancelar debounce y buscar inmediatamente
  if (debounceTimer.value) {
    clearTimeout(debounceTimer.value)
    debounceTimer.value = null
  }
  
  emit('search', props.modelValue)
  emit('enter', props.modelValue)
}

const handleEscape = () => {
  if (props.modelValue) {
    handleClear()
  } else {
    searchInput.value?.blur()
  }
}

const handleClear = () => {
  emit('update:modelValue', '')
  emit('clear')
  emit('search', '')
  
  // Cancelar búsqueda pendiente
  if (debounceTimer.value) {
    clearTimeout(debounceTimer.value)
    debounceTimer.value = null
  }
  
  // Mantener el foco
  searchInput.value?.focus()
}

const formatResultsCount = (count: number): string => {
  if (count === 0) {
    return 'No se encontraron resultados'
  } else if (count === 1) {
    return '1 resultado encontrado'
  } else {
    return `${count} resultados encontrados`
  }
}

// Public methods
const focus = () => {
  searchInput.value?.focus()
}

const clear = () => {
  handleClear()
}

// Cleanup
onUnmounted(() => {
  if (debounceTimer.value) {
    clearTimeout(debounceTimer.value)
  }
})

// Watch for external model changes
watch(() => props.modelValue, (newValue, oldValue) => {
  // Si el valor se limpia externamente, cancelar búsqueda pendiente
  if (!newValue && oldValue && debounceTimer.value) {
    clearTimeout(debounceTimer.value)
    debounceTimer.value = null
  }
})

// Expose methods
defineExpose({
  focus,
  clear
})

console.log('🔧 Componente SearchInput cargado')
</script>

<style scoped>
.search-input {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.search-input--disabled {
  opacity: 0.6;
  pointer-events: none;
}

.search-input__label {
  font-weight: 500;
  color: #333;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.search-input__wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input__input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 2.5rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  background-color: white;
  transition: all 0.2s ease;
  color: #333;
}

.search-input__input:focus {
  outline: none;
  border-color: #2c5aa0;
  box-shadow: 0 0 0 3px rgba(44, 90, 160, 0.1);
}

.search-input__input:hover:not(:disabled) {
  border-color: #999;
}

.search-input__input--loading {
  padding-right: 3rem;
}

.search-input__input--clearable {
  padding-right: 3rem;
}

.search-input__input--disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.search-input__icon {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  color: #666;
  font-size: 1rem;
}

.search-input__icon--search {
  left: 0.875rem;
}

.search-input__icon--loading {
  right: 0.875rem;
}

.search-input__spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #2c5aa0;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.search-input__clear {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  color: #666;
}

.search-input__clear:hover {
  background-color: #f8f9fa;
  color: #333;
}

.search-input__clear:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(44, 90, 160, 0.2);
}

.search-input__results {
  font-size: 0.875rem;
  color: #666;
  margin-top: 0.25rem;
}

.search-input__helper {
  font-size: 0.875rem;
  color: #666;
  margin-top: 0.25rem;
}

/* Animations */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .search-input__input {
    padding: 1rem 3rem 1rem 2.5rem;
    font-size: 16px; /* Prevents zoom on iOS */
  }
}

/* Dark theme support */
@media (prefers-color-scheme: dark) {
  .search-input__label {
    color: #e0e0e0;
  }
  
  .search-input__input {
    background-color: #2d2d2d;
    border-color: #555;
    color: #e0e0e0;
  }
  
  .search-input__input:focus {
    border-color: #4a90e2;
  }
  
  .search-input__input--disabled {
    background-color: #1a1a1a;
  }
  
  .search-input__icon {
    color: #ccc;
  }
  
  .search-input__clear {
    color: #ccc;
  }
  
  .search-input__clear:hover {
    background-color: #444;
    color: #e0e0e0;
  }
  
  .search-input__results,
  .search-input__helper {
    color: #ccc;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .search-input__input {
    border-width: 3px;
  }
  
  .search-input__input:focus {
    box-shadow: 0 0 0 3px;
  }
}

/* Accessibility - reduce motion */
@media (prefers-reduced-motion: reduce) {
  .search-input__spinner {
    animation: spin 2s linear infinite;
  }
  
  .search-input__input,
  .search-input__clear {
    transition: none;
  }
}
</style>