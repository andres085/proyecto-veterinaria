<template>
  <div class="duenio-buscar">
    <!-- Search Header -->
    <div class="duenio-buscar__header">
      <h3 class="duenio-buscar__title">🔍 Buscar Dueños</h3>
      <p class="duenio-buscar__subtitle">
        Encuentra dueños por nombre, email o teléfono
      </p>
    </div>

    <!-- Search Controls -->
    <div class="duenio-buscar__controls">
      <!-- Main search input -->
      <div class="search-main">
        <SearchInput
          v-model="searchQuery"
          placeholder="Buscar por nombre, email o teléfono..."
          :loading="loading"
          :clearable="true"
          :debounce="300"
          :min-length="1"
          :show-results-count="true"
          :results-count="resultsCount"
          helper-text="Mínimo 1 carácter para buscar"
          @search="handleSearch"
          @clear="handleClear"
          @enter="handleEnter"
        />
      </div>

      <!-- Advanced filters -->
      <div class="search-filters" :class="{ 'filters-expanded': showAdvancedFilters }">
        <button
          @click="toggleAdvancedFilters"
          class="btn btn--ghost btn--small filters-toggle"
        >
          ⚙️ Filtros Avanzados
          <span class="toggle-icon">
            {{ showAdvancedFilters ? '▲' : '▼' }}
          </span>
        </button>

        <Transition name="filters-slide">
          <div v-if="showAdvancedFilters" class="advanced-filters">
            <!-- Search type filter -->
            <div class="filter-group">
              <label class="filter-label">Buscar en:</label>
              <div class="filter-options">
                <label class="filter-option">
                  <input
                    v-model="searchFilters.searchInName"
                    type="checkbox"
                    @change="applyFilters"
                  />
                  <span>👤 Nombre</span>
                </label>
                <label class="filter-option">
                  <input
                    v-model="searchFilters.searchInEmail"
                    type="checkbox"
                    @change="applyFilters"
                  />
                  <span>📧 Email</span>
                </label>
                <label class="filter-option">
                  <input
                    v-model="searchFilters.searchInPhone"
                    type="checkbox"
                    @change="applyFilters"
                  />
                  <span>📱 Teléfono</span>
                </label>
              </div>
            </div>

            <!-- Date filter -->
            <div class="filter-group">
              <label class="filter-label">Registrado desde:</label>
              <input
                v-model="searchFilters.dateFrom"
                type="date"
                class="filter-input"
                @change="applyFilters"
              />
            </div>

            <!-- Sort options -->
            <div class="filter-group">
              <label class="filter-label">Ordenar por:</label>
              <select
                v-model="searchFilters.sortBy"
                class="filter-input"
                @change="applyFilters"
              >
                <option value="nombre_apellido">Nombre A-Z</option>
                <option value="nombre_apellido_desc">Nombre Z-A</option>
                <option value="email">Email A-Z</option>
                <option value="created_at">Más recientes</option>
                <option value="created_at_desc">Más antiguos</option>
              </select>
            </div>

            <!-- Filter actions -->
            <div class="filter-actions">
              <button
                @click="clearAllFilters"
                class="btn btn--secondary btn--small"
              >
                🧹 Limpiar Filtros
              </button>
              <button
                @click="applyFilters"
                class="btn btn--primary btn--small"
              >
                ✅ Aplicar
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </div>

    <!-- Search Results Summary -->
    <div v-if="hasSearched" class="duenio-buscar__results">
      <div class="results-summary">
        <div class="results-info">
          <span v-if="loading" class="results-text">
            🔍 Buscando...
          </span>
          <span v-else-if="searchQuery && resultsCount === 0" class="results-text results-empty">
            ❌ No se encontraron dueños que coincidan con "{{ searchQuery }}"
          </span>
          <span v-else-if="searchQuery && resultsCount > 0" class="results-text results-found">
            ✅ {{ formatResultsText(resultsCount) }} que coinciden con "{{ searchQuery }}"
          </span>
          <span v-else class="results-text">
            📋 Mostrando todos los dueños ({{ totalDuenios }})
          </span>
        </div>

        <div class="results-actions">
          <button
            v-if="searchQuery"
            @click="handleClear"
            class="btn btn--ghost btn--small"
            title="Limpiar búsqueda"
          >
            ❌ Limpiar
          </button>
          
          <button
            @click="handleRefresh"
            class="btn btn--ghost btn--small"
            :disabled="loading"
            title="Actualizar resultados"
          >
            🔄 Actualizar
          </button>
        </div>
      </div>

      <!-- Search suggestions -->
      <div v-if="searchQuery && resultsCount === 0 && !loading" class="search-suggestions">
        <h4>💡 Sugerencias:</h4>
        <ul>
          <li>Verifica la ortografía</li>
          <li>Usa términos más generales</li>
          <li>Busca por apellido únicamente</li>
          <li>Intenta con el email o teléfono</li>
        </ul>
      </div>
    </div>

    <!-- Quick Actions -->
    <div v-if="!hasSearched || (searchQuery && resultsCount === 0)" class="duenio-buscar__quick-actions">
      <h4>🚀 Acciones Rápidas:</h4>
      <div class="quick-actions-grid">
        <button
          @click="$emit('create')"
          class="quick-action-btn"
        >
          <div class="quick-action-icon">➕</div>
          <div class="quick-action-text">
            <strong>Nuevo Dueño</strong>
            <small>Registrar propietario</small>
          </div>
        </button>
        
        <button
          @click="$emit('view-all')"
          class="quick-action-btn"
        >
          <div class="quick-action-icon">📋</div>
          <div class="quick-action-text">
            <strong>Ver Todos</strong>
            <small>Lista completa</small>
          </div>
        </button>
        
        <button
          @click="handleRefresh"
          class="quick-action-btn"
          :disabled="loading"
        >
          <div class="quick-action-icon">🔄</div>
          <div class="quick-action-text">
            <strong>Actualizar</strong>
            <small>Refrescar datos</small>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import SearchInput from '@/components/shared/SearchInput.vue'

// Types
export interface DuenioBuscarProps {
  loading?: boolean
  resultsCount?: number
  totalDuenios?: number
}

export interface DuenioBuscarEmits {
  (e: 'search', query: string, filters: SearchFilters): void
  (e: 'clear'): void
  (e: 'refresh'): void
  (e: 'create'): void
  (e: 'view-all'): void
}

export interface SearchFilters {
  searchInName: boolean
  searchInEmail: boolean
  searchInPhone: boolean
  dateFrom: string
  sortBy: string
}

// Props
const props = withDefaults(defineProps<DuenioBuscarProps>(), {
  loading: false,
  resultsCount: 0,
  totalDuenios: 0
})

// Emits
const emit = defineEmits<DuenioBuscarEmits>()

// State
const searchQuery = ref<string>('')
const hasSearched = ref<boolean>(false)
const showAdvancedFilters = ref<boolean>(false)

const searchFilters = reactive<SearchFilters>({
  searchInName: true,
  searchInEmail: true,
  searchInPhone: true,
  dateFrom: '',
  sortBy: 'nombre_apellido'
})

// Computed
const activeFiltersCount = computed(() => {
  let count = 0
  if (!searchFilters.searchInName) count++
  if (!searchFilters.searchInEmail) count++
  if (!searchFilters.searchInPhone) count++
  if (searchFilters.dateFrom) count++
  if (searchFilters.sortBy !== 'nombre_apellido') count++
  return count
})

// Methods
const handleSearch = (query: string) => {
  hasSearched.value = true
  emit('search', query, { ...searchFilters })
  console.log('🔍 Búsqueda:', query, searchFilters)
}

const handleClear = () => {
  searchQuery.value = ''
  hasSearched.value = false
  emit('clear')
  console.log('🧹 Búsqueda limpiada')
}

const handleEnter = (query: string) => {
  handleSearch(query)
}

const handleRefresh = () => {
  emit('refresh')
  console.log('🔄 Actualizando resultados')
}

const toggleAdvancedFilters = () => {
  showAdvancedFilters.value = !showAdvancedFilters.value
}

const applyFilters = () => {
  if (searchQuery.value || hasSearched.value) {
    handleSearch(searchQuery.value)
  }
}

const clearAllFilters = () => {
  searchFilters.searchInName = true
  searchFilters.searchInEmail = true
  searchFilters.searchInPhone = true
  searchFilters.dateFrom = ''
  searchFilters.sortBy = 'nombre_apellido'
  
  if (hasSearched.value) {
    applyFilters()
  }
}

const formatResultsText = (count: number): string => {
  if (count === 0) return 'No se encontraron dueños'
  if (count === 1) return '1 dueño encontrado'
  return `${count} dueños encontrados`
}

// Watch for external changes
watch(() => props.resultsCount, (newValue) => {
  if (newValue !== undefined && hasSearched.value) {
    console.log(`📊 Resultados actualizados: ${newValue}`)
  }
})

console.log('🔧 Componente DuenioBuscar cargado')
</script>

<style scoped>
.duenio-buscar {
  background: white;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

/* Header */
.duenio-buscar__header {
  padding: var(--spacing-lg) var(--spacing-lg) var(--spacing-md);
  border-bottom: 1px solid var(--border-light);
  text-align: center;
}

.duenio-buscar__title {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--primary-color);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
}

.duenio-buscar__subtitle {
  margin: 0;
  color: var(--text-light);
  font-size: var(--font-size-sm);
}

/* Controls */
.duenio-buscar__controls {
  padding: var(--spacing-lg);
}

.search-main {
  margin-bottom: var(--spacing-md);
}

.search-filters {
  border-top: 1px solid var(--border-light);
  padding-top: var(--spacing-md);
}

.filters-toggle {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.toggle-icon {
  font-size: var(--font-size-sm);
}

/* Advanced Filters */
.advanced-filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background-color: var(--background-color);
  border-radius: var(--border-radius-md);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.filter-label {
  font-weight: var(--font-weight-medium);
  color: var(--text-color);
  font-size: var(--font-size-sm);
}

.filter-options {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.filter-option {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
  cursor: pointer;
}

.filter-option input[type="checkbox"] {
  margin: 0;
}

.filter-input {
  padding: var(--spacing-sm);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
}

.filter-actions {
  grid-column: 1 / -1;
  display: flex;
  gap: var(--spacing-sm);
  justify-content: flex-end;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--border-light);
}

/* Results */
.duenio-buscar__results {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--border-light);
  background-color: var(--background-color);
}

.results-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.results-text {
  font-weight: var(--font-weight-medium);
  color: var(--text-color);
}

.results-found {
  color: var(--success-color);
}

.results-empty {
  color: var(--warning-color);
}

.results-actions {
  display: flex;
  gap: var(--spacing-sm);
}

/* Search Suggestions */
.search-suggestions {
  background: white;
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--warning-color);
  background-color: var(--warning-light);
}

.search-suggestions h4 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--warning-color);
  font-size: var(--font-size-md);
}

.search-suggestions ul {
  margin: 0;
  padding-left: var(--spacing-lg);
  color: var(--text-color);
}

.search-suggestions li {
  margin-bottom: var(--spacing-xs);
  font-size: var(--font-size-sm);
}

/* Quick Actions */
.duenio-buscar__quick-actions {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--border-light);
}

.duenio-buscar__quick-actions h4 {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--text-color);
  font-size: var(--font-size-md);
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.quick-action-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: white;
  border: 2px solid var(--border-light);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
  text-align: left;
}

.quick-action-btn:hover:not(:disabled) {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.quick-action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.quick-action-icon {
  font-size: var(--font-size-xl);
  line-height: 1;
}

.quick-action-text {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.quick-action-text strong {
  color: var(--text-color);
  font-size: var(--font-size-md);
}

.quick-action-text small {
  color: var(--text-light);
  font-size: var(--font-size-sm);
}

/* Transitions */
.filters-slide-enter-active,
.filters-slide-leave-active {
  transition: all 0.3s ease;
}

.filters-slide-enter-from,
.filters-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Responsive */
@media (max-width: 768px) {
  .duenio-buscar__header,
  .duenio-buscar__controls,
  .duenio-buscar__results,
  .duenio-buscar__quick-actions {
    padding: var(--spacing-md);
  }
  
  .advanced-filters {
    grid-template-columns: 1fr;
  }
  
  .results-summary {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: stretch;
  }
  
  .results-actions {
    justify-content: center;
  }
  
  .quick-actions-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-actions {
    flex-direction: column;
  }
}
</style>