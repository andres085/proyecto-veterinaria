<template>
  <div class="turno-list">
    <!-- Header con estadísticas -->
    <div class="turno-list__header">
      <div class="turno-list__stats">
        <div class="stat-item">
          <span class="stat-number">{{ totalTurnos }}</span>
          <span class="stat-label">Total Turnos</span>
        </div>
        <div v-if="filteredCount !== totalTurnos" class="stat-item">
          <span class="stat-number">{{ filteredCount }}</span>
          <span class="stat-label">Filtrados</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ turnosPendientes }}</span>
          <span class="stat-label">Pendientes</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ turnosHoy }}</span>
          <span class="stat-label">Hoy</span>
        </div>
      </div>
      
      <div class="turno-list__actions">
        <button 
          @click="refreshList"
          class="btn btn--secondary btn--small"
          :disabled="loading"
          title="Actualizar lista"
        >
          🔄 Actualizar
        </button>
      </div>
    </div>

    <!-- Filtros rápidos -->
    <div class="turno-list__filters">
      <div class="filter-chips">
        <button
          @click="setStateFilter('all')"
          class="filter-chip"
          :class="{ 'filter-chip--active': activeStateFilter === 'all' }"
        >
          📋 Todos ({{ totalTurnos }})
        </button>
        <button
          @click="setStateFilter('pendiente')"
          class="filter-chip"
          :class="{ 'filter-chip--active': activeStateFilter === 'pendiente' }"
        >
          ⏳ Pendientes ({{ getTurnosByEstado('pendiente').length }})
        </button>
        <button
          @click="setStateFilter('confirmado')"
          class="filter-chip"
          :class="{ 'filter-chip--active': activeStateFilter === 'confirmado' }"
        >
          ✅ Confirmados ({{ getTurnosByEstado('confirmado').length }})
        </button>
        <button
          @click="setStateFilter('completado')"
          class="filter-chip"
          :class="{ 'filter-chip--active': activeStateFilter === 'completado' }"
        >
          🏁 Completados ({{ getTurnosByEstado('completado').length }})
        </button>
        <button
          @click="setStateFilter('cancelado')"
          class="filter-chip"
          :class="{ 'filter-chip--active': activeStateFilter === 'cancelado' }"
        >
          ❌ Cancelados ({{ getTurnosByEstado('cancelado').length }})
        </button>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="turno-list__loading">
      <LoadingSpinner size="large" text="Cargando turnos..." />
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="turno-list__error">
      <div class="error-content">
        <div class="error-icon">❌</div>
        <h3>Error al cargar turnos</h3>
        <p>{{ error }}</p>
        <button @click="refreshList" class="btn btn--primary">
          🔄 Reintentar
        </button>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="filteredTurnos.length === 0" class="turno-list__empty">
      <div class="empty-content">
        <div class="empty-icon">📅</div>
        <h3 v-if="activeStateFilter === 'all'">No hay turnos registrados</h3>
        <h3 v-else>No hay turnos {{ getEstadoLabel(activeStateFilter) }}</h3>
        <p v-if="activeStateFilter === 'all'">Comienza agendando el primer turno</p>
        <p v-else>Cambia el filtro para ver otros turnos</p>
        <button 
          v-if="activeStateFilter === 'all'"
          @click="$emit('create')" 
          class="btn btn--primary"
        >
          📅 Agendar Primer Turno
        </button>
      </div>
    </div>

    <!-- Lista de turnos -->
    <div v-else class="turno-list__content">
      <!-- Vista de tabla (desktop) -->
      <div class="turno-table-wrapper">
        <table class="turno-table">
          <thead>
            <tr>
              <th 
                @click="setSortField('fecha_turno')"
                class="sortable"
                :class="{ 'sorted': sortField === 'fecha_turno' }"
              >
                📅 Fecha
                <span class="sort-indicator">
                  {{ getSortIcon('fecha_turno') }}
                </span>
              </th>
              <th 
                @click="setSortField('nombre_mascota')"
                class="sortable"
                :class="{ 'sorted': sortField === 'nombre_mascota' }"
              >
                🐕 Mascota
                <span class="sort-indicator">
                  {{ getSortIcon('nombre_mascota') }}
                </span>
              </th>
              <th>👤 Dueño</th>
              <th class="turno-table__tratamiento">🏥 Tratamiento</th>
              <th 
                @click="setSortField('estado')"
                class="sortable"
                :class="{ 'sorted': sortField === 'estado' }"
              >
                🔄 Estado
                <span class="sort-indicator">
                  {{ getSortIcon('estado') }}
                </span>
              </th>
              <th class="turno-table__actions">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="turno in sortedTurnos" 
              :key="turno.id"
              class="turno-row"
              :class="getTurnoRowClass(turno)"
              @click="$emit('view', turno)"
            >
              <td class="turno-table__fecha">
                <div class="fecha-cell">
                  <span class="fecha-main">{{ formatDateTime(turno.fecha_turno) }}</span>
                  <small class="fecha-relative">{{ getRelativeTime(turno.fecha_turno) }}</small>
                </div>
              </td>
              <td class="turno-table__mascota">
                <div class="mascota-cell">
                  <strong>{{ turno.nombre_mascota }}</strong>
                  <small v-if="turno.id" class="turno-id">ID: {{ turno.id }}</small>
                </div>
              </td>
              <td class="turno-table__duenio">
                <div class="duenio-cell">
                  <strong>{{ turno.duenio?.nombre_apellido || 'N/A' }}</strong>
                  <small v-if="turno.duenio?.telefono">{{ turno.duenio.telefono }}</small>
                </div>
              </td>
              <td class="turno-table__tratamiento">
                <div class="tratamiento-cell" :title="turno.tratamiento">
                  {{ truncateText(turno.tratamiento, 60) }}
                </div>
              </td>
              <td class="turno-table__estado">
                <span class="estado-badge" :class="`estado-badge--${turno.estado}`">
                  {{ getEstadoIcon(turno.estado) }} {{ getEstadoLabel(turno.estado) }}
                </span>
              </td>
              <td class="turno-table__actions" @click.stop>
                <div class="action-buttons">
                  <button
                    @click="$emit('view', turno)"
                    class="btn btn--ghost btn--small"
                    title="Ver detalles"
                  >
                    👁️
                  </button>
                  <button
                    @click="$emit('edit', turno)"
                    class="btn btn--secondary btn--small"
                    title="Editar turno"
                  >
                    ✏️
                  </button>
                  <button
                    v-if="turno.estado !== 'cancelado'"
                    @click="$emit('change-estado', turno)"
                    class="btn btn--primary btn--small"
                    title="Cambiar estado"
                  >
                    🔄
                  </button>
                  <button
                    @click="handleDelete(turno)"
                    class="btn btn--danger btn--small"
                    title="Eliminar turno"
                  >
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Vista de cards (mobile) -->
      <div class="turno-cards">
        <div
          v-for="turno in sortedTurnos"
          :key="turno.id"
          class="turno-card"
          :class="getTurnoCardClass(turno)"
          @click="$emit('view', turno)"
        >
          <div class="turno-card__header">
            <div class="turno-card__date">
              <h3>{{ formatDate(turno.fecha_turno) }}</h3>
              <small>{{ formatTime(turno.fecha_turno) }}</small>
            </div>
            <span class="estado-badge" :class="`estado-badge--${turno.estado}`">
              {{ getEstadoIcon(turno.estado) }} {{ getEstadoLabel(turno.estado) }}
            </span>
          </div>
          
          <div class="turno-card__body">
            <div class="turno-card__mascota">
              <h4>🐕 {{ turno.nombre_mascota }}</h4>
              <p>👤 {{ turno.duenio?.nombre_apellido || 'N/A' }}</p>
              <p v-if="turno.duenio?.telefono">📱 {{ turno.duenio.telefono }}</p>
            </div>
            
            <div class="turno-card__tratamiento">
              🏥 {{ turno.tratamiento }}
            </div>
            
            <div class="turno-card__meta">
              <small>ID: {{ turno.id }} • {{ getRelativeTime(turno.fecha_turno) }}</small>
            </div>
          </div>
          
          <div class="turno-card__actions" @click.stop>
            <button
              @click="$emit('view', turno)"
              class="btn btn--ghost btn--small"
            >
              👁️ Ver
            </button>
            <button
              @click="$emit('edit', turno)"
              class="btn btn--secondary btn--small"
            >
              ✏️ Editar
            </button>
            <button
              v-if="turno.estado !== 'cancelado'"
              @click="$emit('change-estado', turno)"
              class="btn btn--primary btn--small"
            >
              🔄 Estado
            </button>
            <button
              @click="handleDelete(turno)"
              class="btn btn--danger btn--small"
            >
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import type { EstadoTurno, Turno } from '@/types/models'
import { computed, ref } from 'vue'

// Types
export interface TurnoListProps {
  turnos: Turno[]
  loading?: boolean
  error?: string | null
}

export interface TurnoListEmits {
  (e: 'view', turno: Turno): void
  (e: 'edit', turno: Turno): void
  (e: 'delete', turno: Turno): void
  (e: 'change-estado', turno: Turno): void
  (e: 'create'): void
  (e: 'refresh'): void
}

// Props
const props = withDefaults(defineProps<TurnoListProps>(), {
  loading: false,
  error: null
})

// Emits
const emit = defineEmits<TurnoListEmits>()

// State
const sortField = ref<string>('fecha_turno')
const sortDirection = ref<'asc' | 'desc'>('asc')
const activeStateFilter = ref<string>('all')


// Computed
const totalTurnos = computed(() => props.turnos.length)

const filteredTurnos = computed(() => {
  if (activeStateFilter.value === 'all') {
    return props.turnos
  }
  return props.turnos.filter(turno => turno.estado === activeStateFilter.value)
})

const filteredCount = computed(() => filteredTurnos.value.length)

const turnosPendientes = computed(() => 
  props.turnos.filter(turno => turno.estado === 'pendiente').length
)

const turnosHoy = computed(() => {
  const today = new Date().toDateString()
  return props.turnos.filter(turno => {
    const turnoDate = new Date(turno.fecha_turno).toDateString()
    return turnoDate === today
  }).length
})

const sortedTurnos = computed(() => {
  if (!filteredTurnos.value.length) return []
  
  const sorted = [...filteredTurnos.value].sort((a, b) => {
    let aValue: any = a[sortField.value as keyof Turno]
    let bValue: any = b[sortField.value as keyof Turno]
    
    // Handle undefined values
    if (aValue === undefined) aValue = ''
    if (bValue === undefined) bValue = ''
    
    // Special handling for dates
    if (sortField.value === 'fecha_turno') {
      aValue = new Date(aValue).getTime()
      bValue = new Date(bValue).getTime()
    } else {
      // Convert to string for comparison
      aValue = String(aValue).toLowerCase()
      bValue = String(bValue).toLowerCase()
    }
    
    if (sortDirection.value === 'asc') {
      return aValue < bValue ? -1 : aValue > bValue ? 1 : 0
    } else {
      return aValue > bValue ? -1 : aValue < bValue ? 1 : 0
    }
  })
  
  return sorted
})

// Methods
const setSortField = (field: string) => {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDirection.value = 'asc'
  }
}

const getSortIcon = (field: string): string => {
  if (sortField.value !== field) return '↕️'
  return sortDirection.value === 'asc' ? '⬆️' : '⬇️'
}

const setStateFilter = (estado: string) => {
  activeStateFilter.value = estado
}

const getTurnosByEstado = (estado: EstadoTurno) => {
  return props.turnos.filter(turno => turno.estado === estado)
}

const formatDateTime = (dateString?: string): string => {
  if (!dateString) return 'N/A'
  
  try {
    const date = new Date(dateString)
    return date.toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return 'N/A'
  }
}

const formatDate = (dateString?: string): string => {
  if (!dateString) return 'N/A'
  
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch {
    return 'N/A'
  }
}

const formatTime = (dateString?: string): string => {
  if (!dateString) return 'N/A'
  
  try {
    const date = new Date(dateString)
    return date.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return 'N/A'
  }
}

const getRelativeTime = (dateString?: string): string => {
  if (!dateString) return 'Fecha desconocida'
  
  try {
    const date = new Date(dateString)
    const now = new Date()
    const diffInMs = date.getTime() - now.getTime()
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24))
    
    if (diffInDays === 0) return 'hoy'
    if (diffInDays === 1) return 'mañana'
    if (diffInDays === -1) return 'ayer'
    if (diffInDays > 0 && diffInDays < 7) return `en ${diffInDays} días`
    if (diffInDays < 0 && diffInDays > -7) return `hace ${Math.abs(diffInDays)} días`
    if (diffInDays >= 7) return `en ${Math.floor(diffInDays / 7)} semanas`
    if (diffInDays <= -7) return `hace ${Math.floor(Math.abs(diffInDays) / 7)} semanas`
    return formatDate(dateString)
  } catch {
    return 'Fecha inválida'
  }
}

const getEstadoIcon = (estado: EstadoTurno): string => {
  const icons = {
    pendiente: '⏳',
    confirmado: '✅',
    completado: '🏁',
    cancelado: '❌'
  }
  return icons[estado] || '❓'
}

const getEstadoLabel = (estado: EstadoTurno | string): string => {
  const labels = {
    pendiente: 'Pendiente',
    confirmado: 'Confirmado',
    completado: 'Completado',
    cancelado: 'Cancelado',
    all: 'Todos'
  }
  return labels[estado as keyof typeof labels] || estado
}

const getTurnoRowClass = (turno: Turno): string => {
  const classes = [`turno-row--${turno.estado}`]
  
  // Add urgency classes
  const now = new Date()
  const turnoDate = new Date(turno.fecha_turno)
  const diffInHours = (turnoDate.getTime() - now.getTime()) / (1000 * 60 * 60)
  
  if (diffInHours < 0 && turno.estado === 'pendiente') {
    classes.push('turno-row--overdue')
  } else if (diffInHours < 24 && turno.estado !== 'completado' && turno.estado !== 'cancelado') {
    classes.push('turno-row--upcoming')
  }
  
  return classes.join(' ')
}

const getTurnoCardClass = (turno: Turno): string => {
  return getTurnoRowClass(turno).replace('turno-row', 'turno-card')
}

const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const handleDelete = (turno: Turno) => {
  emit('delete', turno)
}


const refreshList = () => {
  emit('refresh')
}

console.log('🔧 Componente TurnoList cargado')
</script>

<style scoped>
.turno-list {
  background: white;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

/* Header */
.turno-list__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-light);
  background-color: var(--background-color);
}

.turno-list__stats {
  display: flex;
  gap: var(--spacing-lg);
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--primary-color);
}

.stat-label {
  display: block;
  font-size: var(--font-size-sm);
  color: var(--text-light);
}

/* Filters */
.turno-list__filters {
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--border-light);
  background-color: var(--background-color);
}

.filter-chips {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

.filter-chip {
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-full);
  background: white;
  color: var(--text-color);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.filter-chip:hover {
  border-color: var(--primary-color);
  background-color: var(--primary-light);
}

.filter-chip--active {
  border-color: var(--primary-color);
  background-color: var(--primary-color);
  color: white;
}

/* Loading, Error, Empty states */
.turno-list__loading,
.turno-list__error,
.turno-list__empty {
  padding: var(--spacing-3xl);
  text-align: center;
}

.error-content,
.empty-content {
  max-width: 400px;
  margin: 0 auto;
}

.error-icon,
.empty-icon {
  font-size: 4rem;
  margin-bottom: var(--spacing-lg);
}

/* Table */
.turno-table-wrapper {
  overflow-x: auto;
}

.turno-table {
  width: 100%;
  border-collapse: collapse;
}

.turno-table th {
  background-color: var(--background-color);
  padding: var(--spacing-md);
  text-align: left;
  font-weight: var(--font-weight-semibold);
  color: var(--text-color);
  border-bottom: 2px solid var(--border-color);
  white-space: nowrap;
}

.turno-table th.sortable {
  cursor: pointer;
  user-select: none;
  transition: background-color var(--transition-normal);
}

.turno-table th.sortable:hover {
  background-color: var(--primary-light);
}

.turno-table th.sorted {
  background-color: var(--primary-light);
  color: var(--primary-color);
}

.sort-indicator {
  margin-left: var(--spacing-xs);
  font-size: var(--font-size-sm);
}

.turno-table td {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--border-light);
  vertical-align: top;
}

.turno-row {
  cursor: pointer;
  transition: background-color var(--transition-normal);
}

.turno-row:hover {
  background-color: var(--background-color);
}

/* Row states */
.turno-row--pendiente {
  border-left: 4px solid var(--warning-color);
}

.turno-row--confirmado {
  border-left: 4px solid var(--success-color);
}

.turno-row--completado {
  border-left: 4px solid var(--info-color);
}

.turno-row--cancelado {
  border-left: 4px solid var(--danger-color);
  opacity: 0.7;
}

.turno-row--overdue {
  background-color: var(--danger-light);
}

.turno-row--upcoming {
  background-color: var(--warning-light);
}

/* Table cells */
.fecha-cell {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.fecha-relative {
  color: var(--text-muted);
  font-size: var(--font-size-xs);
}

.mascota-cell,
.duenio-cell {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.turno-id {
  color: var(--text-muted);
  font-size: var(--font-size-xs);
}

.tratamiento-cell {
  max-width: 250px;
  line-height: 1.4;
}

.estado-badge {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-full);
  font-size: var(--font-size-xs);
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

.action-buttons {
  display: flex;
  gap: var(--spacing-xs);
}

/* Cards (mobile) */
.turno-cards {
  display: none;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
}

.turno-card {
  background: white;
  border: 1px solid var(--border-light);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-md);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.turno-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.turno-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-md);
}

.turno-card__date h3 {
  margin: 0 0 var(--spacing-xs) 0;
  color: var(--primary-color);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
}

.turno-card__date small {
  color: var(--text-light);
  font-size: var(--font-size-sm);
}

.turno-card__body {
  margin-bottom: var(--spacing-md);
}

.turno-card__mascota {
  margin-bottom: var(--spacing-sm);
}

.turno-card__mascota h4 {
  margin: 0 0 var(--spacing-xs) 0;
  color: var(--text-color);
  font-size: var(--font-size-md);
}

.turno-card__mascota p {
  margin: 0 0 var(--spacing-xs) 0;
  color: var(--text-light);
  font-size: var(--font-size-sm);
}

.turno-card__tratamiento {
  color: var(--text-color);
  font-size: var(--font-size-sm);
  line-height: 1.4;
  margin-bottom: var(--spacing-sm);
}

.turno-card__meta {
  color: var(--text-muted);
}

.turno-card__actions {
  display: flex;
  gap: var(--spacing-xs);
  justify-content: flex-end;
  flex-wrap: wrap;
}

/* Card states */
.turno-card--pendiente {
  border-left: 4px solid var(--warning-color);
}

.turno-card--confirmado {
  border-left: 4px solid var(--success-color);
}

.turno-card--completado {
  border-left: 4px solid var(--info-color);
}

.turno-card--cancelado {
  border-left: 4px solid var(--danger-color);
  opacity: 0.7;
}

.turno-card--overdue {
  background-color: var(--danger-light);
}

.turno-card--upcoming {
  background-color: var(--warning-light);
}

/* Responsive */
@media (max-width: 768px) {
  .turno-list__header {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: stretch;
  }
  
  .turno-list__stats {
    justify-content: space-around;
    flex-wrap: wrap;
  }
  
  .turno-list__filters {
    padding: var(--spacing-md);
  }
  
  .filter-chips {
    justify-content: center;
  }
  
  .turno-table-wrapper {
    display: none;
  }
  
  .turno-cards {
    display: flex;
    flex-direction: column;
  }
  
  .turno-card__actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}

@media (max-width: 1024px) {
  .turno-table__tratamiento {
    display: none;
  }
}

@media (max-width: 900px) {
  .turno-table th,
  .turno-table td {
    padding: var(--spacing-sm);
    font-size: var(--font-size-sm);
  }
}
</style>