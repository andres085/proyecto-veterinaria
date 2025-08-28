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
const showDeleteDialog = ref(false);
const selectedDuenio = ref<Duenio | null>(null);
const duenioFormMode = ref<"create" | "edit">("create");
const duenioToDelete = ref<Duenio | null>(null);
const deletingDuenio = ref(false);
const searchQuery = ref("");
const searchResults = ref<Duenio[]>([]);
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
  // For now, just edit the duenio when viewed
  editDuenio(duenio);
};

const deleteDuenio = (duenio: Duenio) => {
  duenioToDelete.value = duenio;
  showDeleteDialog.value = true;
};

const closeDuenioForm = () => {
  showDuenioForm.value = false;
  selectedDuenio.value = null;
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
