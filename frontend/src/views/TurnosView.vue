<template>
  <div class="turnos-view">
    <div class="page-header">
      <h1>📅 Gestión de Turnos</h1>
      <p>Administra las citas y consultas veterinarias</p>
    </div>

    <div class="content-wrapper">
      <!-- Modal para crear/editar turno -->
      <div v-if="showTurnoForm" class="modal-overlay" @click="closeTurnoForm">
        <div class="modal-content" @click.stop>
          <TurnoForm
            :turno="selectedTurno"
            :mode="turnoFormMode"
            :loading="turnoStore.loading"
            :duenios="duenioStore.duenios"
            @submit="handleTurnoSubmit"
            @cancel="closeTurnoForm"
            @success="handleTurnoSuccess"
          />
        </div>
      </div>

      <!-- Modal para cambiar estado -->
      <div v-if="showEstadoForm" class="modal-overlay" @click="closeEstadoForm">
        <div class="modal-content" @click.stop>
          <TurnoEstado
            :turno="selectedTurno"
            :loading="turnoStore.loading"
            @change="handleEstadoChange"
            @cancel="closeEstadoForm"
            @success="handleEstadoSuccess"
          />
        </div>
      </div>

      <!-- Botón de crear turno -->
      <div class="actions-section">
        <button 
          @click="createTurno" 
          class="btn btn--primary"
          :disabled="turnoStore.loading"
        >
          ➕ Nuevo Turno
        </button>
      </div>

      <!-- Lista de turnos -->
      <TurnoList
        :turnos="turnoStore.turnos"
        :loading="turnoStore.loading"
        :error="turnoStore.error"
        @view="viewTurno"
        @edit="editTurno"
        @delete="deleteTurno"
        @change-estado="changeEstado"
        @create="createTurno"
        @refresh="refreshTurnos"
      />
    </div>

    <!-- Confirm Dialog para eliminación -->
    <ConfirmDialog
      :is-visible="showDeleteDialog"
      :title="'Eliminar Turno'"
      :message="`¿Estás seguro que deseas eliminar el turno de ${turnoToDelete?.nombre_mascota}?`"
      :confirm-text="'Sí, Eliminar'"
      :cancel-text="'Cancelar'"
      type="danger"
      :loading="deletingTurno"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />

    <!-- Toast notifications -->
    <div v-if="notification" class="notification" :class="`notification--${notification.type}`">
      {{ notification.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTurnoStore } from '@/stores/turnoStore'
import { useDuenioStore } from '@/stores/duenioStore'
import TurnoForm from '@/components/turnos/TurnoForm.vue'
import TurnoList from '@/components/turnos/TurnoList.vue'
import TurnoEstado from '@/components/turnos/TurnoEstado.vue'
import ConfirmDialog from '@/components/shared/ConfirmDialog.vue'
import type { Turno, CreateTurnoPayload, UpdateTurnoPayload, EstadoTurno } from '@/types/models'

// Stores
const turnoStore = useTurnoStore()
const duenioStore = useDuenioStore()

// State
const showTurnoForm = ref(false)
const showEstadoForm = ref(false)
const showDeleteDialog = ref(false)
const selectedTurno = ref<Turno | null>(null)
const turnoFormMode = ref<'create' | 'edit'>('create')
const turnoToDelete = ref<Turno | null>(null)
const deletingTurno = ref(false)
const notification = ref<{ message: string; type: 'success' | 'error' } | null>(null)

// Methods
const createTurno = () => {
  selectedTurno.value = null
  turnoFormMode.value = 'create'
  showTurnoForm.value = true
}

const editTurno = (turno: Turno) => {
  selectedTurno.value = turno
  turnoFormMode.value = 'edit'
  showTurnoForm.value = true
}

const viewTurno = (turno: Turno) => {
  // For now, just edit the turno when viewed
  editTurno(turno)
}

const changeEstado = (turno: Turno) => {
  selectedTurno.value = turno
  showEstadoForm.value = true
}

const deleteTurno = (turno: Turno) => {
  turnoToDelete.value = turno
  showDeleteDialog.value = true
}

const closeTurnoForm = () => {
  showTurnoForm.value = false
  selectedTurno.value = null
}

const closeEstadoForm = () => {
  showEstadoForm.value = false
  selectedTurno.value = null
}

const handleTurnoSubmit = async (data: CreateTurnoPayload | UpdateTurnoPayload) => {
  try {
    if (turnoFormMode.value === 'create') {
      await turnoStore.create(data as CreateTurnoPayload)
      showNotification('Turno creado exitosamente', 'success')
    } else {
      const turnoId = selectedTurno.value?.id
      if (turnoId) {
        await turnoStore.update(turnoId, data as UpdateTurnoPayload)
        showNotification('Turno actualizado exitosamente', 'success')
      }
    }
    closeTurnoForm()
  } catch (error) {
    console.error('Error al guardar turno:', error)
    showNotification(
      error instanceof Error ? error.message : 'Error al guardar turno',
      'error'
    )
  }
}

const handleTurnoSuccess = () => {
  closeTurnoForm()
}

const handleEstadoChange = async (turno: Turno, newEstado: EstadoTurno) => {
  try {
    await turnoStore.updateEstado(turno.id!, newEstado)
    showNotification(`Estado cambiado a ${newEstado}`, 'success')
    closeEstadoForm()
  } catch (error) {
    console.error('Error al cambiar estado:', error)
    showNotification(
      error instanceof Error ? error.message : 'Error al cambiar estado',
      'error'
    )
  }
}

const handleEstadoSuccess = () => {
  closeEstadoForm()
}

const confirmDelete = async () => {
  if (!turnoToDelete.value?.id) return
  
  deletingTurno.value = true
  
  try {
    await turnoStore.remove(turnoToDelete.value.id)
    showNotification('Turno eliminado exitosamente', 'success')
    showDeleteDialog.value = false
  } catch (error) {
    console.error('Error al eliminar turno:', error)
    showNotification(
      error instanceof Error ? error.message : 'Error al eliminar turno',
      'error'
    )
  } finally {
    deletingTurno.value = false
    turnoToDelete.value = null
  }
}

const cancelDelete = () => {
  showDeleteDialog.value = false
  turnoToDelete.value = null
}

const refreshTurnos = async () => {
  try {
    await turnoStore.fetchAll()
    showNotification('Turnos actualizados', 'success')
  } catch (error) {
    console.error('Error al actualizar turnos:', error)
    showNotification(
      error instanceof Error ? error.message : 'Error al actualizar turnos',
      'error'
    )
  }
}

const showNotification = (message: string, type: 'success' | 'error') => {
  notification.value = { message, type }
  
  // Auto-hide after 3 seconds
  setTimeout(() => {
    notification.value = null
  }, 3000)
}

const loadInitialData = async () => {
  try {
    // Load duenios first (needed for turno form)
    if (duenioStore.duenios.length === 0) {
      await duenioStore.fetchAll()
    }
    
    // Then load turnos
    await turnoStore.fetchAll()
    
    console.log('✅ Datos iniciales cargados:', {
      turnos: turnoStore.turnos.length,
      duenios: duenioStore.duenios.length
    })
  } catch (error) {
    console.error('❌ Error al cargar datos iniciales:', error)
    showNotification(
      error instanceof Error ? error.message : 'Error al cargar datos',
      'error'
    )
  }
}

// Lifecycle
onMounted(() => {
  loadInitialData()
})

console.log('📱 Vista TurnosView integrada con stores cargada')
</script>

<style scoped>
.turnos-view {
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
  .turnos-view {
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

/* Loading state for modal */
.modal-content:has(.loading-spinner) {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>