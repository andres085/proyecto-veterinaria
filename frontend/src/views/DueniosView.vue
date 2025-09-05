<template>
  <div class="duenios-view">
    <div class="page-header">
      <h1>👥 Gestión de Dueños</h1>
      <p>Administra la información de los propietarios de mascotas</p>
    </div>

    <div class="content-wrapper">
      <!-- Modal para crear/editar dueño -->
      <div v-if="showDuenioForm" class="modal-overlay" @click="closeDuenioForm">
        <div class="modal-content" @click.stop>
          <DuenioForm
            :duenio="selectedDuenio"
            :mode="duenioFormMode"
            :loading="duenioStore.loading"
            @submit="handleDuenioSubmit"
            @cancel="closeDuenioForm"
            @success="handleDuenioSuccess"
          />
        </div>
      </div>

      <!-- Modal para ver dueño (solo lectura) -->
      <div v-if="showViewModal" class="modal-overlay" @click="closeViewModal">
        <div class="modal-content" @click.stop>
          <div class="view-modal">
            <div class="view-modal__header">
              <h2>👤 Información del Dueño</h2>
              <button @click="closeViewModal" class="close-btn">✕</button>
            </div>
            
            <div class="view-modal__content" v-if="viewedDuenio">
              <div class="info-grid">
                <div class="info-item">
                  <label>ID:</label>
                  <span>{{ viewedDuenio.id }}</span>
                </div>
                
                <div class="info-item">
                  <label>Nombre y Apellido:</label>
                  <span>{{ viewedDuenio.nombre_apellido }}</span>
                </div>
                
                <div class="info-item">
                  <label>Teléfono:</label>
                  <a :href="`tel:${viewedDuenio.telefono}`" class="contact-link">
                    📱 {{ viewedDuenio.telefono }}
                  </a>
                </div>
                
                <div class="info-item">
                  <label>Email:</label>
                  <a :href="`mailto:${viewedDuenio.email}`" class="contact-link">
                    📧 {{ viewedDuenio.email }}
                  </a>
                </div>
                
                <div class="info-item">
                  <label>Dirección:</label>
                  <span>📍 {{ viewedDuenio.direccion }}</span>
                </div>
                
                <div class="info-item">
                  <label>Fecha de Registro:</label>
                  <span>📅 {{ formatDate(viewedDuenio.created_at) }}</span>
                </div>
                
                <div class="info-item" v-if="viewedDuenio.updated_at">
                  <label>Última Actualización:</label>
                  <span>🔄 {{ formatDate(viewedDuenio.updated_at) }}</span>
                </div>
              </div>
              
              <div class="view-modal__actions">
                <button @click="editFromView" class="btn btn--primary">
                  ✏️ Editar
                </button>
                <button @click="closeViewModal" class="btn btn--secondary">
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Sección de búsqueda -->
      <DuenioBuscar
        :loading="duenioStore.loading"
        :results-count="searchResults.length"
        :total-duenios="duenioStore.duenios.length"
        @search="handleSearch"
        @clear="handleClearSearch"
        @refresh="refreshDuenios"
        @create="createDuenio"
        @view-all="viewAllDuenios"
      />

      <!-- Botón de crear dueño -->
      <div class="actions-section">
        <button
          @click="createDuenio"
          class="btn btn--primary"
          :disabled="duenioStore.loading"
        >
          ➕ Nuevo Dueño
        </button>
      </div>

      <!-- Lista de dueños -->
      <DuenioList
        :duenios="displayedDuenios"
        :loading="duenioStore.loading"
        :error="duenioStore.error"
        @view="viewDuenio"
        @edit="editDuenio"
        @delete="deleteDuenio"
        @create="createDuenio"
        @refresh="refreshDuenios"
      />
    </div>

    <!-- Confirm Dialog para eliminación -->
    <ConfirmDialog
      :is-visible="showDeleteDialog"
      :title="'Eliminar Dueño'"
      :message="`¿Estás seguro que deseas eliminar al dueño ${duenioToDelete?.nombre_apellido}? Esta acción también eliminará todos sus turnos asociados.`"
      :confirm-text="'Sí, Eliminar'"
      :cancel-text="'Cancelar'"
      type="danger"
      :loading="deletingDuenio"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />

    <!-- Toast notifications -->
    <div
      v-if="notification"
      class="notification"
      :class="`notification--${notification.type}`"
    >
      {{ notification.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useDuenioStore } from "@/stores/duenioStore";
import DuenioForm from "@/components/duenios/DuenioForm.vue";
import DuenioList from "@/components/duenios/DuenioList.vue";
import DuenioBuscar from "@/components/duenios/DuenioBuscar.vue";
import ConfirmDialog from "@/components/shared/ConfirmDialog.vue";
import type {
  Duenio,
  CreateDuenioPayload,
  UpdateDuenioPayload,
} from "@/types/models";

// Store
const duenioStore = useDuenioStore();

// State
const showDuenioForm = ref(false);
const showViewModal = ref(false);
const showDeleteDialog = ref(false);
const selectedDuenio = ref<Duenio | null>(null);
const viewedDuenio = ref<Duenio | null>(null);
const duenioFormMode = ref<"create" | "edit">("create");
const duenioToDelete = ref<Duenio | null>(null);
const deletingDuenio = ref(false);
const searchQuery = ref("");
let searchResults = ref<Duenio[]>([]);
const isSearching = ref(false);
const notification = ref<{ message: string; type: "success" | "error" } | null>(
  null
);

// Computed
const displayedDuenios = computed(() => {
  return isSearching.value ? searchResults.value : duenioStore.duenios;
});

// Methods
const createDuenio = () => {
  selectedDuenio.value = null;
  duenioFormMode.value = "create";
  showDuenioForm.value = true;
};

const editDuenio = (duenio: Duenio) => {
  selectedDuenio.value = duenio;
  duenioFormMode.value = "edit";
  showDuenioForm.value = true;
};

const viewDuenio = (duenio: Duenio) => {
  viewedDuenio.value = duenio;
  showViewModal.value = true;
};

const deleteDuenio = (duenio: Duenio) => {
  duenioToDelete.value = duenio;
  showDeleteDialog.value = true;
};

const closeDuenioForm = () => {
  showDuenioForm.value = false;
  selectedDuenio.value = null;
};

const closeViewModal = () => {
  showViewModal.value = false;
  viewedDuenio.value = null;
};

const editFromView = () => {
  if (viewedDuenio.value) {
    selectedDuenio.value = viewedDuenio.value;
    duenioFormMode.value = "edit";
    showViewModal.value = false;
    showDuenioForm.value = true;
  }
};

const handleDuenioSubmit = async (
  data: CreateDuenioPayload | UpdateDuenioPayload
) => {
  try {
    if (duenioFormMode.value === "create") {
      await duenioStore.create(data as CreateDuenioPayload);
      showNotification("Dueño creado exitosamente", "success");
    } else {
      const duenioId = selectedDuenio.value?.id;
      if (duenioId) {
        await duenioStore.update(duenioId, data as UpdateDuenioPayload);
        showNotification("Dueño actualizado exitosamente", "success");
      }
    }
    closeDuenioForm();
  } catch (error) {
    console.error("Error al guardar dueño:", error);
    showNotification(
      error instanceof Error ? error.message : "Error al guardar dueño",
      "error"
    );
  }
};

const handleDuenioSuccess = () => {
  closeDuenioForm();
};

const confirmDelete = async () => {
  if (!duenioToDelete.value?.id) return;

  deletingDuenio.value = true;

  try {
    await duenioStore.remove(duenioToDelete.value.id);
    showNotification("Dueño eliminado exitosamente", "success");
    showDeleteDialog.value = false;
  } catch (error) {
    console.error("Error al eliminar dueño:", error);
    showNotification(
      error instanceof Error ? error.message : "Error al eliminar dueño",
      "error"
    );
  } finally {
    deletingDuenio.value = false;
    duenioToDelete.value = null;
  }
};

const cancelDelete = () => {
  showDeleteDialog.value = false;
  duenioToDelete.value = null;
};

const handleSearch = async (query: string, filters: any) => {
  searchQuery.value = query;

  if (!query.trim()) {
    handleClearSearch();
    return;
  }

  try {
    isSearching.value = true;
    searchResults = await duenioStore.search(query);
    console.log(
      `🔍 Búsqueda: "${query}" - ${searchResults.value.length} resultados`
    );
  } catch (error) {
    console.error("Error en búsqueda:", error);
    showNotification(
      error instanceof Error ? error.message : "Error en la búsqueda",
      "error"
    );
    searchResults.value = [];
  }
};

const handleClearSearch = () => {
  searchQuery.value = "";
  searchResults.value = [];
  isSearching.value = false;
};

const viewAllDuenios = () => {
  handleClearSearch();
};

const refreshDuenios = async () => {
  try {
    await duenioStore.fetchAll();
    showNotification("Dueños actualizados", "success");

    // Refresh search results if searching
    if (isSearching.value && searchQuery.value) {
      await handleSearch(searchQuery.value, {});
    }
  } catch (error) {
    console.error("Error al actualizar dueños:", error);
    showNotification(
      error instanceof Error ? error.message : "Error al actualizar dueños",
      "error"
    );
  }
};

const showNotification = (message: string, type: "success" | "error") => {
  notification.value = { message, type };

  // Auto-hide after 3 seconds
  setTimeout(() => {
    notification.value = null;
  }, 3000);
};

const formatDate = (dateString?: string): string => {
  if (!dateString) return "N/A";
  
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString("es-ES", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "N/A";
  }
};

const loadInitialData = async () => {
  try {
    await duenioStore.fetchAll();
    console.log("✅ Datos iniciales cargados:", {
      duenios: duenioStore.duenios.length,
    });
  } catch (error) {
    console.error("❌ Error al cargar datos iniciales:", error);
    showNotification(
      error instanceof Error ? error.message : "Error al cargar datos",
      "error"
    );
  }
};

// Lifecycle
onMounted(() => {
  loadInitialData();
});

console.log("📱 Vista DueniosView integrada con stores cargada");
</script>

<style scoped>
.duenios-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--spacing-lg);
}

.page-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.page-header h1 {
  color: var(--primary-color);
  margin: 0 0 var(--spacing-sm) 0;
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
}

.page-header p {
  color: var(--text-light);
  margin: 0;
  font-size: var(--font-size-lg);
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.actions-section {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding: var(--spacing-lg);
  background: white;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--spacing-md);
}

.modal-content {
  background: white;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-xl);
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Notifications */
.notification {
  position: fixed;
  top: var(--spacing-lg);
  right: var(--spacing-lg);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--border-radius-md);
  font-weight: var(--font-weight-medium);
  z-index: 1100;
  animation: notificationSlideIn 0.3s ease-out;
  max-width: 400px;
  box-shadow: var(--shadow-lg);
}

.notification--success {
  background-color: var(--success-light);
  color: var(--success-color);
  border: 1px solid var(--success-color);
}

.notification--error {
  background-color: var(--danger-light);
  color: var(--danger-color);
  border: 1px solid var(--danger-color);
}

@keyframes notificationSlideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* View Modal Styles */
.view-modal {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.view-modal__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-light);
}

.view-modal__header h2 {
  margin: 0;
  color: var(--primary-color);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
}

.close-btn {
  background: none;
  border: none;
  font-size: var(--font-size-lg);
  color: var(--text-light);
  cursor: pointer;
  padding: var(--spacing-xs);
  border-radius: var(--border-radius-md);
  transition: all var(--transition-normal);
}

.close-btn:hover {
  background-color: var(--danger-light);
  color: var(--danger-color);
}

.view-modal__content {
  padding: var(--spacing-lg);
}

.info-grid {
  display: grid;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.info-item label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-item span {
  font-size: var(--font-size-md);
  color: var(--text-color);
  padding: var(--spacing-sm);
  background-color: var(--background-color);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--border-light);
}

.contact-link {
  color: var(--primary-color);
  text-decoration: none;
  padding: var(--spacing-sm);
  background-color: var(--primary-light);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--primary-color);
  transition: all var(--transition-normal);
  display: inline-block;
}

.contact-link:hover {
  background-color: var(--primary-color);
  color: white;
}

.view-modal__actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: flex-end;
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--border-light);
}

.btn--secondary {
  background-color: var(--background-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.btn--secondary:hover:not(:disabled) {
  background-color: var(--border-color);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

/* Responsive */
@media (max-width: 768px) {
  .duenios-view {
    padding: var(--spacing-md);
  }

  .page-header h1 {
    font-size: var(--font-size-xl);
  }

  .page-header p {
    font-size: var(--font-size-md);
  }

  .actions-section {
    padding: var(--spacing-md);
    justify-content: center;
  }

  .modal-overlay {
    padding: var(--spacing-sm);
  }

  .modal-content {
    max-width: 100%;
    margin: 0;
  }

  .notification {
    top: var(--spacing-sm);
    right: var(--spacing-sm);
    left: var(--spacing-sm);
    max-width: none;
  }
}

/* Button overrides for consistency */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-md) var(--spacing-lg);
  border: none;
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-normal);
  text-decoration: none;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn--primary {
  background-color: var(--primary-color);
  color: white;
}

.btn--primary:hover:not(:disabled) {
  background-color: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
</style>
