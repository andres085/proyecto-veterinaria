<template>
  <div class="calendario-view">
    <div class="page-header">
      <h1>📅 Calendario de Turnos</h1>
      <p>Vista general de citas programadas por fecha</p>
    </div>

    <div class="content-wrapper">
      <!-- Modal para ver detalles de turno -->
      <div
        v-if="showTurnoDetails"
        class="modal-overlay"
        @click="closeTurnoDetails"
      >
        <div class="modal-content" @click.stop>
          <div class="turno-details">
            <div class="details-header">
              <h2>🐕 {{ selectedTurno?.nombre_mascota }}</h2>
              <button
                @click="closeTurnoDetails"
                class="btn btn--ghost btn--small"
              >
                ❌ Cerrar
              </button>
            </div>

            <div v-if="selectedTurno" class="details-body">
              <div class="detail-item">
                <span class="detail-label">📅 Fecha y Hora:</span>
                <span class="detail-value">{{
                  formatDateTime(selectedTurno.fecha_turno)
                }}</span>
              </div>

              <div class="detail-item">
                <span class="detail-label">👤 Dueño:</span>
                <span class="detail-value">{{
                  selectedTurno.duenio?.nombre_apellido || "N/A"
                }}</span>
              </div>

              <div class="detail-item">
                <span class="detail-label">📱 Teléfono:</span>
                <span class="detail-value">{{
                  selectedTurno.duenio?.telefono || "N/A"
                }}</span>
              </div>

              <div class="detail-item">
                <span class="detail-label">📧 Email:</span>
                <span class="detail-value">{{
                  selectedTurno.duenio?.email || "N/A"
                }}</span>
              </div>

              <div class="detail-item">
                <span class="detail-label">🏥 Tratamiento:</span>
                <span class="detail-value">{{
                  selectedTurno.tratamiento
                }}</span>
              </div>

              <div class="detail-item">
                <span class="detail-label">🔄 Estado:</span>
                <span
                  class="estado-badge"
                  :class="`estado-badge--${selectedTurno.estado}`"
                >
                  {{ getEstadoIcon(selectedTurno.estado) }}
                  {{ getEstadoLabel(selectedTurno.estado) }}
                </span>
              </div>
            </div>

            <div class="details-actions">
              <button
                @click="editTurno(selectedTurno!)"
                class="btn btn--secondary"
              >
                ✏️ Editar
              </button>
              <button
                @click="changeEstado(selectedTurno!)"
                class="btn btn--primary"
              >
                🔄 Cambiar Estado
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal para editar turno -->
      <div v-if="showTurnoForm" class="modal-overlay" @click="closeTurnoForm">
        <div class="modal-content" @click.stop>
          <TurnoForm
            :turno="selectedTurno"
            :mode="'edit'"
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

      <!-- Calendario principal -->
      <TurnoCalendario
        :turnos="turnoStore.turnos"
        :loading="turnoStore.loading"
        :error="turnoStore.error"
        @refresh="refreshTurnos"
        @date-change="handleDateChange"
        @turno-click="viewTurnoDetails"
        @day-click="handleDayClick"
      />

      <!-- Resumen diario flotante -->
      <div v-if="selectedDayInfo" class="day-summary">
        <div class="summary-header">
          <h3>📋 {{ formatSelectedDate(selectedDayInfo.date) }}</h3>
          <button @click="clearDaySelection" class="btn btn--ghost btn--small">
            ❌
          </button>
        </div>

        <div v-if="selectedDayInfo.turnos.length > 0" class="summary-turnos">
          <div
            v-for="turno in selectedDayInfo.turnos"
            :key="turno.id"
            class="summary-turno"
            :class="`summary-turno--${turno.estado}`"
            @click="viewTurnoDetails(turno)"
          >
            <div class="summary-time">{{ formatTime(turno.fecha_turno) }}</div>
            <div class="summary-info">
              <strong>{{ turno.nombre_mascota }}</strong>
              <small>{{ turno.duenio?.nombre_apellido }}</small>
            </div>
            <div class="summary-estado">
              {{ getEstadoIcon(turno.estado) }}
            </div>
          </div>
        </div>

        <div v-else class="summary-empty">
          <p>No hay turnos programados para este día</p>
        </div>
      </div>
    </div>

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
import { ref, onMounted } from "vue";
import { useTurnoStore } from "@/stores/turnoStore";
import { useDuenioStore } from "@/stores/duenioStore";
import TurnoCalendario from "@/components/turnos/TurnoCalendario.vue";
import TurnoForm from "@/components/turnos/TurnoForm.vue";
import TurnoEstado from "@/components/turnos/TurnoEstado.vue";
import type { Turno, UpdateTurnoPayload, EstadoTurno } from "@/types/models";

// Stores
const turnoStore = useTurnoStore();
const duenioStore = useDuenioStore();

// State
const showTurnoDetails = ref(false);
const showTurnoForm = ref(false);
const showEstadoForm = ref(false);
const selectedTurno = ref<Turno | null>(null);
const selectedDayInfo = ref<{ date: Date; turnos: Turno[] } | null>(null);
const notification = ref<{ message: string; type: "success" | "error" } | null>(
  null
);

// Metodos
const viewTurnoDetails = (turno: Turno) => {
  selectedTurno.value = turno;
  showTurnoDetails.value = true;
};

const editTurno = (turno: Turno) => {
  selectedTurno.value = turno;
  showTurnoDetails.value = false;
  showTurnoForm.value = true;
};

const changeEstado = (turno: Turno) => {
  selectedTurno.value = turno;
  showTurnoDetails.value = false;
  showEstadoForm.value = true;
};

const closeTurnoDetails = () => {
  showTurnoDetails.value = false;
  selectedTurno.value = null;
};

const closeTurnoForm = () => {
  showTurnoForm.value = false;
  selectedTurno.value = null;
};

const closeEstadoForm = () => {
  showEstadoForm.value = false;
  selectedTurno.value = null;
};

const handleDayClick = (date: Date, turnos: Turno[]) => {
  selectedDayInfo.value = { date, turnos };
  console.log(
    `📅 Día seleccionado: ${date.toDateString()} con ${turnos.length} turnos`
  );
};

const clearDaySelection = () => {
  selectedDayInfo.value = null;
};

const handleDateChange = (date: Date) => {
  console.log(`📅 Navegación a: ${date.toDateString()}`);
  clearDaySelection();
};

const handleTurnoSubmit = async (data: UpdateTurnoPayload) => {
  try {
    const turnoId = selectedTurno.value?.id;
    if (turnoId) {
      await turnoStore.update(turnoId, data);
      showNotification("Turno actualizado exitosamente", "success");
    }
    closeTurnoForm();
  } catch (error) {
    console.error("Error al actualizar turno:", error);
    showNotification(
      error instanceof Error ? error.message : "Error al actualizar turno",
      "error"
    );
  }
};

const handleTurnoSuccess = () => {
  closeTurnoForm();
};

const handleEstadoChange = async (turno: Turno, newEstado: EstadoTurno) => {
  try {
    await turnoStore.updateEstado(turno.id!, newEstado);
    showNotification(`Estado cambiado a ${newEstado}`, "success");
    closeEstadoForm();
  } catch (error) {
    console.error("Error al cambiar estado:", error);
    showNotification(
      error instanceof Error ? error.message : "Error al cambiar estado",
      "error"
    );
  }
};

const handleEstadoSuccess = () => {
  closeEstadoForm();
};

const refreshTurnos = async () => {
  try {
    await turnoStore.fetchAll();
    showNotification("Calendario actualizado", "success");
  } catch (error) {
    console.error("Error al actualizar calendario:", error);
    showNotification(
      error instanceof Error ? error.message : "Error al actualizar calendario",
      "error"
    );
  }
};

const formatDateTime = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleString("es-ES", {
      weekday: "long",
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

const formatSelectedDate = (date: Date): string => {
  return date.toLocaleDateString("es-ES", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};

const formatTime = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleTimeString("es-ES", {
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "N/A";
  }
};

const getEstadoIcon = (estado: EstadoTurno): string => {
  const icons = {
    pendiente: "⏳",
    confirmado: "✅",
    completado: "🏁",
    cancelado: "❌",
  };
  return icons[estado] || "❓";
};

const getEstadoLabel = (estado: EstadoTurno): string => {
  const labels = {
    pendiente: "Pendiente",
    confirmado: "Confirmado",
    completado: "Completado",
    cancelado: "Cancelado",
  };
  return labels[estado] || estado;
};

const showNotification = (message: string, type: "success" | "error") => {
  notification.value = { message, type };

  setTimeout(() => {
    notification.value = null;
  }, 3000);
};

const loadInitialData = async () => {
  try {
    if (duenioStore.duenios.length === 0) {
      await duenioStore.fetchAll();
    }

    await turnoStore.fetchAll();

    console.log("✅ Datos del calendario cargados:", {
      turnos: turnoStore.turnos.length,
      duenios: duenioStore.duenios.length,
    });
  } catch (error) {
    console.error("❌ Error al cargar datos del calendario:", error);
    showNotification(
      error instanceof Error ? error.message : "Error al cargar datos",
      "error"
    );
  }
};

onMounted(() => {
  loadInitialData();
});

console.log("📱 Vista CalendarioView integrada con stores cargada");
</script>

<style scoped>
.calendario-view {
  max-width: 1600px;
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
  position: relative;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

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

.turno-details {
  padding: var(--spacing-xl);
  min-width: 400px;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--border-light);
}

.details-header h2 {
  margin: 0;
  color: var(--primary-color);
  font-size: var(--font-size-xl);
}

.details-body {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--border-light);
}

.detail-label {
  font-weight: var(--font-weight-medium);
  color: var(--text-light);
  font-size: var(--font-size-sm);
}

.detail-value {
  color: var(--text-color);
  font-size: var(--font-size-sm);
  text-align: right;
  max-width: 60%;
  word-wrap: break-word;
}

.details-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: flex-end;
}

.day-summary {
  position: fixed;
  bottom: var(--spacing-lg);
  right: var(--spacing-lg);
  background: white;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-xl);
  max-width: 350px;
  max-height: 400px;
  overflow: hidden;
  z-index: 100;
  animation: summarySlideIn 0.3s ease-out;
}

@keyframes summarySlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--border-light);
  background-color: var(--primary-light);
}

.summary-header h3 {
  margin: 0;
  color: var(--primary-color);
  font-size: var(--font-size-md);
}

.summary-turnos {
  padding: var(--spacing-md);
  max-height: 300px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.summary-turno {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-md);
  border-left: 3px solid var(--border-color);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.summary-turno:hover {
  background-color: var(--background-color);
  transform: translateX(2px);
}

.summary-turno--pendiente {
  border-left-color: var(--warning-color);
}

.summary-turno--confirmado {
  border-left-color: var(--success-color);
}

.summary-turno--completado {
  border-left-color: var(--info-color);
}

.summary-turno--cancelado {
  border-left-color: var(--danger-color);
  opacity: 0.7;
}

.summary-time {
  font-weight: var(--font-weight-bold);
  color: var(--primary-color);
  font-size: var(--font-size-sm);
}

.summary-info strong {
  display: block;
  color: var(--text-color);
  font-size: var(--font-size-sm);
}

.summary-info small {
  color: var(--text-light);
  font-size: var(--font-size-xs);
}

.summary-estado {
  display: flex;
  align-items: center;
  font-size: var(--font-size-sm);
}

.summary-empty {
  padding: var(--spacing-lg);
  text-align: center;
  color: var(--text-light);
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
  .calendario-view {
    padding: var(--spacing-md);
  }

  .page-header h1 {
    font-size: var(--font-size-xl);
  }

  .page-header p {
    font-size: var(--font-size-md);
  }

  .modal-overlay {
    padding: var(--spacing-sm);
  }

  .modal-content {
    max-width: 100%;
    margin: 0;
  }

  .turno-details {
    padding: var(--spacing-md);
    min-width: unset;
  }

  .detail-item {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-xs);
  }

  .detail-value {
    max-width: 100%;
    text-align: left;
  }

  .details-actions {
    flex-direction: column;
  }

  .day-summary {
    bottom: var(--spacing-sm);
    right: var(--spacing-sm);
    left: var(--spacing-sm);
    max-width: none;
  }

  .notification {
    top: var(--spacing-sm);
    right: var(--spacing-sm);
    left: var(--spacing-sm);
    max-width: none;
  }
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
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

.btn--secondary {
  background-color: var(--secondary-color);
  color: white;
}

.btn--ghost {
  background-color: transparent;
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.btn--small {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--font-size-xs);
}

.btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}
</style>
