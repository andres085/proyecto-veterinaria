<template>
  <div class="duenio-list">
    <!-- Header con estadísticas -->
    <div class="duenio-list__header">
      <div class="duenio-list__stats">
        <div class="stat-item">
          <span class="stat-number">{{ totalDuenios }}</span>
          <span class="stat-label">Total Dueños</span>
        </div>
        <div v-if="filteredCount !== totalDuenios" class="stat-item">
          <span class="stat-number">{{ filteredCount }}</span>
          <span class="stat-label">Filtrados</span>
        </div>
      </div>

      <div class="duenio-list__actions">
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

    <!-- Loading state -->
    <div v-if="loading" class="duenio-list__loading">
      <LoadingSpinner size="large" text="Cargando dueños..." />
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="duenio-list__error">
      <div class="error-content">
        <div class="error-icon">❌</div>
        <h3>Error al cargar dueños</h3>
        <p>{{ error }}</p>
        <button @click="refreshList" class="btn btn--primary">
          🔄 Reintentar
        </button>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="duenios.length === 0" class="duenio-list__empty">
      <div class="empty-content">
        <div class="empty-icon">👥</div>
        <h3>No hay dueños registrados</h3>
        <p>Comienza agregando el primer dueño al sistema</p>
        <button @click="$emit('create')" class="btn btn--primary">
          ➕ Agregar Primer Dueño
        </button>
      </div>
    </div>

    <!-- Lista de dueños -->
    <div v-else class="duenio-list__content">
      <!-- Vista de tabla (desktop) -->
      <div class="duenio-table-wrapper">
        <table class="duenio-table">
          <thead>
            <tr>
              <th
                @click="setSortField('nombre_apellido')"
                class="sortable"
                :class="{ sorted: sortField === 'nombre_apellido' }"
              >
                👤 Nombre
                <span class="sort-indicator">
                  {{ getSortIcon("nombre_apellido") }}
                </span>
              </th>
              <th>📱 Teléfono</th>
              <th
                @click="setSortField('email')"
                class="sortable"
                :class="{ sorted: sortField === 'email' }"
              >
                📧 Email
                <span class="sort-indicator">
                  {{ getSortIcon("email") }}
                </span>
              </th>
              <th class="duenio-table__direccion">📍 Dirección</th>
              <th
                @click="setSortField('created_at')"
                class="sortable"
                :class="{ sorted: sortField === 'created_at' }"
              >
                📅 Registro
                <span class="sort-indicator">
                  {{ getSortIcon("created_at") }}
                </span>
              </th>
              <th class="duenio-table__actions">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="duenio in sortedDuenios"
              :key="duenio.id"
              class="duenio-row"
              @click="$emit('view', duenio)"
            >
              <td class="duenio-table__nombre">
                <div class="nombre-cell">
                  <strong>{{ duenio.nombre_apellido }}</strong>
                  <small v-if="duenio.id" class="duenio-id"
                    >ID: {{ duenio.id }}</small
                  >
                </div>
              </td>
              <td class="duenio-table__telefono">
                <a :href="`tel:${duenio.telefono}`" class="phone-link">
                  {{ duenio.telefono }}
                </a>
              </td>
              <td class="duenio-table__email">
                <a :href="`mailto:${duenio.email}`" class="email-link">
                  {{ duenio.email }}
                </a>
              </td>
              <td class="duenio-table__direccion">
                <div class="direccion-cell" :title="duenio.direccion">
                  {{ truncateText(duenio.direccion, 50) }}
                </div>
              </td>
              <td class="duenio-table__fecha">
                <div class="fecha-cell">
                  <span class="fecha-main">{{
                    formatDate(duenio.created_at)
                  }}</span>
                  <small class="fecha-relative">{{
                    getRelativeTime(duenio.created_at)
                  }}</small>
                </div>
              </td>
              <td class="duenio-table__actions" @click.stop>
                <div class="action-buttons">
                  <button
                    @click="$emit('view', duenio)"
                    class="btn btn--ghost btn--small"
                    title="Ver detalles"
                  >
                    👁️
                  </button>
                  <button
                    @click="$emit('edit', duenio)"
                    class="btn btn--secondary btn--small"
                    title="Editar dueño"
                  >
                    ✏️
                  </button>
                  <button
                    @click="handleDelete(duenio)"
                    class="btn btn--danger btn--small"
                    title="Eliminar dueño"
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
      <div class="duenio-cards">
        <div
          v-for="duenio in sortedDuenios"
          :key="duenio.id"
          class="duenio-card"
          @click="$emit('view', duenio)"
        >
          <div class="duenio-card__header">
            <h3 class="duenio-card__name">{{ duenio.nombre_apellido }}</h3>
            <small class="duenio-card__id">ID: {{ duenio.id }}</small>
          </div>

          <div class="duenio-card__body">
            <div class="duenio-card__contact">
              <a :href="`tel:${duenio.telefono}`" class="contact-item">
                📱 {{ duenio.telefono }}
              </a>
              <a :href="`mailto:${duenio.email}`" class="contact-item">
                📧 {{ duenio.email }}
              </a>
            </div>

            <div class="duenio-card__address">📍 {{ duenio.direccion }}</div>

            <div class="duenio-card__date">
              📅 Registrado {{ getRelativeTime(duenio.created_at) }}
            </div>
          </div>

          <div class="duenio-card__actions" @click.stop>
            <button
              @click="$emit('view', duenio)"
              class="btn btn--ghost btn--small"
            >
              👁️ Ver
            </button>
            <button
              @click="$emit('edit', duenio)"
              class="btn btn--secondary btn--small"
            >
              ✏️ Editar
            </button>
            <button
              @click="handleDelete(duenio)"
              class="btn btn--danger btn--small"
            >
              🗑️ Eliminar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirm Dialog -->
    <ConfirmDialog
      :is-visible="showDeleteDialog"
      :title="deleteDialog.title"
      :message="deleteDialog.message"
      :confirm-text="deleteDialog.confirmText"
      :cancel-text="deleteDialog.cancelText"
      type="danger"
      :loading="deletingDuenio"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import LoadingSpinner from "@/components/shared/LoadingSpinner.vue";
import ConfirmDialog from "@/components/shared/ConfirmDialog.vue";
import type { Duenio } from "@/types/models";

// Types
export interface DuenioListProps {
  duenios: Duenio[];
  loading?: boolean;
  error?: string | null;
}

export interface DuenioListEmits {
  (e: "view", duenio: Duenio): void;
  (e: "edit", duenio: Duenio): void;
  (e: "delete", duenio: Duenio): void;
  (e: "create"): void;
  (e: "refresh"): void;
}

// Props
const props = withDefaults(defineProps<DuenioListProps>(), {
  loading: false,
  error: null,
});

// Emits
const emit = defineEmits<DuenioListEmits>();

// State
const sortField = ref<string>("nombre_apellido");
const sortDirection = ref<"asc" | "desc">("asc");
const showDeleteDialog = ref(false);
const duenioToDelete = ref<Duenio | null>(null);
const deletingDuenio = ref(false);

// Delete dialog state
const deleteDialog = computed(() => ({
  title: "Eliminar Dueño",
  message: `¿Estás seguro que deseas eliminar al dueño "${duenioToDelete.value?.nombre_apellido}"? Esta acción también eliminará todos los turnos asociados.`,
  confirmText: "Sí, Eliminar",
  cancelText: "Cancelar",
}));

// Computed
const totalDuenios = computed(() => props.duenios.length);
const filteredCount = computed(() => props.duenios.length); // Para filtros futuros

const sortedDuenios = computed(() => {
  if (!props.duenios.length) return [];

  const sorted = [...props.duenios].sort((a, b) => {
    let aValue: any = a[sortField.value as keyof Duenio];
    let bValue: any = b[sortField.value as keyof Duenio];

    if (aValue === undefined) aValue = "";
    if (bValue === undefined) bValue = "";

    aValue = String(aValue).toLowerCase();
    bValue = String(bValue).toLowerCase();

    if (sortDirection.value === "asc") {
      return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
    } else {
      return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
    }
  });

  return sorted;
});

// Methods
const setSortField = (field: string) => {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === "asc" ? "desc" : "asc";
  } else {
    sortField.value = field;
    sortDirection.value = "asc";
  }
};

const getSortIcon = (field: string): string => {
  if (sortField.value !== field) return "↕️";
  return sortDirection.value === "asc" ? "⬆️" : "⬇️";
};

const formatDate = (dateString?: string): string => {
  if (!dateString) return "N/A";

  try {
    const date = new Date(dateString);
    return date.toLocaleDateString("es-ES", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return "N/A";
  }
};

const getRelativeTime = (dateString?: string): string => {
  if (!dateString) return "Fecha desconocida";

  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

    if (diffInDays === 0) return "hoy";
    if (diffInDays === 1) return "ayer";
    if (diffInDays < 7) return `hace ${diffInDays} días`;
    if (diffInDays < 30) return `hace ${Math.floor(diffInDays / 7)} semanas`;
    if (diffInDays < 365) return `hace ${Math.floor(diffInDays / 30)} meses`;
    return `hace ${Math.floor(diffInDays / 365)} años`;
  } catch {
    return "Fecha inválida";
  }
};

const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + "...";
};

const handleDelete = (duenio: Duenio) => {
  duenioToDelete.value = duenio;
  showDeleteDialog.value = true;
};

const confirmDelete = async () => {
  if (!duenioToDelete.value) return;

  deletingDuenio.value = true;

  try {
    emit("delete", duenioToDelete.value);
    showDeleteDialog.value = false;
  } finally {
    deletingDuenio.value = false;
    duenioToDelete.value = null;
  }
};

const cancelDelete = () => {
  showDeleteDialog.value = false;
  duenioToDelete.value = null;
};

const refreshList = () => {
  emit("refresh");
};

console.log("🔧 Componente DuenioList cargado");
</script>

<style scoped>
.duenio-list {
  background: white;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

/* Header */
.duenio-list__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-light);
  background-color: var(--background-color);
}

.duenio-list__stats {
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

/* Loading, Error, Empty states */
.duenio-list__loading,
.duenio-list__error,
.duenio-list__empty {
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
.duenio-table-wrapper {
  overflow-x: auto;
}

.duenio-table {
  width: 100%;
  border-collapse: collapse;
}

.duenio-table th {
  background-color: var(--background-color);
  padding: var(--spacing-md);
  text-align: left;
  font-weight: var(--font-weight-semibold);
  color: var(--text-color);
  border-bottom: 2px solid var(--border-color);
  white-space: nowrap;
}

.duenio-table th.sortable {
  cursor: pointer;
  user-select: none;
  transition: background-color var(--transition-normal);
}

.duenio-table th.sortable:hover {
  background-color: var(--primary-light);
}

.duenio-table th.sorted {
  background-color: var(--primary-light);
  color: var(--primary-color);
}

.sort-indicator {
  margin-left: var(--spacing-xs);
  font-size: var(--font-size-sm);
}

.duenio-table td {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--border-light);
  vertical-align: top;
}

.duenio-row {
  cursor: pointer;
  transition: background-color var(--transition-normal);
}

.duenio-row:hover {
  background-color: var(--background-color);
}

/* Table cells */
.nombre-cell {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.duenio-id {
  color: var(--text-muted);
  font-size: var(--font-size-xs);
}

.phone-link,
.email-link {
  color: var(--primary-color);
  text-decoration: none;
}

.phone-link:hover,
.email-link:hover {
  text-decoration: underline;
}

.direccion-cell {
  max-width: 200px;
  line-height: 1.4;
}

.fecha-cell {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.fecha-relative {
  color: var(--text-muted);
  font-size: var(--font-size-xs);
}

.action-buttons {
  display: flex;
  gap: var(--spacing-xs);
}

/* Cards (mobile) */
.duenio-cards {
  display: none;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
}

.duenio-card {
  background: white;
  border: 1px solid var(--border-light);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-md);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.duenio-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.duenio-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-md);
}

.duenio-card__name {
  margin: 0;
  color: var(--primary-color);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
}

.duenio-card__id {
  color: var(--text-muted);
  font-size: var(--font-size-xs);
}

.duenio-card__body {
  margin-bottom: var(--spacing-md);
}

.duenio-card__contact {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-sm);
}

.contact-item {
  color: var(--primary-color);
  text-decoration: none;
  font-size: var(--font-size-sm);
}

.duenio-card__address,
.duenio-card__date {
  font-size: var(--font-size-sm);
  color: var(--text-light);
  margin-bottom: var(--spacing-xs);
}

.duenio-card__actions {
  display: flex;
  gap: var(--spacing-xs);
  justify-content: flex-end;
}

/* Responsive */
@media (max-width: 768px) {
  .duenio-list__header {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: stretch;
  }

  .duenio-list__stats {
    justify-content: space-around;
  }

  .duenio-table-wrapper {
    display: none;
  }

  .duenio-cards {
    display: flex;
    flex-direction: column;
  }
}

@media (max-width: 1024px) {
  .duenio-table__direccion {
    display: none;
  }
}

@media (max-width: 900px) {
  .duenio-table th,
  .duenio-table td {
    padding: var(--spacing-sm);
    font-size: var(--font-size-sm);
  }
}
</style>
