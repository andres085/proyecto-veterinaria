<template>
  <div class="turno-calendario">
    <div class="calendario__header">
      <div class="calendario__navigation">
        <button
          @click="previousMonth"
          class="btn btn--ghost btn--small"
          :disabled="loading"
        >
          ◀️ Anterior
        </button>

        <h2 class="calendario__title">📅 {{ formatMonthYear(currentDate) }}</h2>

        <button
          @click="nextMonth"
          class="btn btn--ghost btn--small"
          :disabled="loading"
        >
          Siguiente ▶️
        </button>
      </div>

      <div class="calendario__actions">
        <button
          @click="goToToday"
          class="btn btn--secondary btn--small"
          :disabled="loading || isCurrentMonth"
        >
          🏠 Hoy
        </button>

        <button
          @click="refreshCalendar"
          class="btn btn--ghost btn--small"
          :disabled="loading"
        >
          🔄 Actualizar
        </button>
      </div>
    </div>

    <div class="calendario__legend">
      <div class="legend-item">
        <span class="legend-color legend-color--pendiente"></span>
        <span>⏳ Pendiente</span>
      </div>
      <div class="legend-item">
        <span class="legend-color legend-color--confirmado"></span>
        <span>✅ Confirmado</span>
      </div>
      <div class="legend-item">
        <span class="legend-color legend-color--completado"></span>
        <span>🏁 Completado</span>
      </div>
      <div class="legend-item">
        <span class="legend-color legend-color--cancelado"></span>
        <span>❌ Cancelado</span>
      </div>
      <div class="legend-item">
        <span class="legend-color legend-color--multiple"></span>
        <span>📅 Múltiples</span>
      </div>
    </div>

    <div v-if="loading" class="calendario__loading">
      <LoadingSpinner size="large" text="Cargando calendario..." />
    </div>

    <div v-else-if="error" class="calendario__error">
      <div class="error-content">
        <div class="error-icon">❌</div>
        <h3>Error al cargar calendario</h3>
        <p>{{ error }}</p>
        <button @click="refreshCalendar" class="btn btn--primary">
          🔄 Reintentar
        </button>
      </div>
    </div>

    <div v-else class="calendario__grid">
      <div class="calendario__weekdays">
        <div v-for="day in weekdays" :key="day" class="weekday">
          {{ day }}
        </div>
      </div>

      <div class="calendario__days">
        <div
          v-for="day in calendarDays"
          :key="`${day.date}-${day.isCurrentMonth}`"
          class="calendar-day"
          :class="getDayClass(day)"
          @click="selectDay(day)"
        >
          <div class="day-number">
            {{ day.dayNumber }}
          </div>

          <div v-if="day.turnos.length > 0" class="day-turnos">
            <div
              v-for="turno in day.turnos.slice(0, 3)"
              :key="turno.id"
              class="turno-indicator"
              :class="`turno-indicator--${turno.estado}`"
              :title="getTurnoTooltip(turno)"
            >
              <span class="turno-time">{{
                formatTime(turno.fecha_turno)
              }}</span>
              <span class="turno-pet">{{
                truncatePetName(turno.nombre_mascota)
              }}</span>
            </div>

            <div v-if="day.turnos.length > 3" class="more-turnos">
              +{{ day.turnos.length - 3 }} más
            </div>
          </div>
        </div>
      </div>
    </div>

    <div
      v-if="selectedDay && selectedDayTurnos.length > 0"
      class="calendario__details"
    >
      <div class="details-header">
        <h3>📋 Turnos del {{ formatSelectedDate(selectedDay.date) }}</h3>
        <button @click="selectedDay = null" class="btn btn--ghost btn--small">
          ❌ Cerrar
        </button>
      </div>

      <div class="details-turnos">
        <div
          v-for="turno in selectedDayTurnos"
          :key="turno.id"
          class="turno-detail"
          :class="`turno-detail--${turno.estado}`"
          @click="$emit('turno-click', turno)"
        >
          <div class="turno-detail__time">
            {{ formatTime(turno.fecha_turno) }}
          </div>
          <div class="turno-detail__info">
            <h4>🐕 {{ turno.nombre_mascota }}</h4>
            <p>👤 {{ turno.duenio?.nombre_apellido || "N/A" }}</p>
            <p>🏥 {{ turno.tratamiento }}</p>
          </div>
          <div class="turno-detail__estado">
            <span class="estado-badge" :class="`estado-badge--${turno.estado}`">
              {{ getEstadoIcon(turno.estado) }}
              {{ getEstadoLabel(turno.estado) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="calendario__stats">
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-number">{{ monthStats.total }}</span>
          <span class="stat-label">Total del mes</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ monthStats.pendientes }}</span>
          <span class="stat-label">Pendientes</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ monthStats.confirmados }}</span>
          <span class="stat-label">Confirmados</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ monthStats.completados }}</span>
          <span class="stat-label">Completados</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import LoadingSpinner from "@/components/shared/LoadingSpinner.vue";
import type { Turno, EstadoTurno } from "@/types/models";

interface CalendarDay {
  date: Date;
  dayNumber: number;
  isCurrentMonth: boolean;
  isToday: boolean;
  turnos: Turno[];
}

export interface TurnoCalendarioProps {
  turnos: Turno[];
  loading?: boolean;
  error?: string | null;
}

export interface TurnoCalendarioEmits {
  (e: "refresh"): void;
  (e: "date-change", date: Date): void;
  (e: "turno-click", turno: Turno): void;
  (e: "day-click", date: Date, turnos: Turno[]): void;
}

const props = withDefaults(defineProps<TurnoCalendarioProps>(), {
  loading: false,
  error: null,
});

const emit = defineEmits<TurnoCalendarioEmits>();

const currentDate = ref<Date>(new Date());
const selectedDay = ref<CalendarDay | null>(null);

const weekdays = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];

const isCurrentMonth = computed(() => {
  const today = new Date();
  return (
    currentDate.value.getMonth() === today.getMonth() &&
    currentDate.value.getFullYear() === today.getFullYear()
  );
});

const calendarDays = computed((): CalendarDay[] => {
  const year = currentDate.value.getFullYear();
  const month = currentDate.value.getMonth();

  // Primer día del mes
  const firstDay = new Date(year, month, 1);
  // Último día del mes
  const lastDay = new Date(year, month + 1, 0);

  // Días a mostrar antes del primer día del mes
  const startDate = new Date(firstDay);
  startDate.setDate(startDate.getDate() - firstDay.getDay());

  // Días a mostrar después del último día del mes
  const endDate = new Date(lastDay);
  const remainingDays = 6 - lastDay.getDay();
  endDate.setDate(endDate.getDate() + remainingDays);

  const days: CalendarDay[] = [];
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  for (
    let date = new Date(startDate);
    date <= endDate;
    date.setDate(date.getDate() + 1)
  ) {
    const dayDate = new Date(date);
    const isCurrentMonth = dayDate.getMonth() === month;
    const isToday = dayDate.getTime() === today.getTime();

    // Filtrar turnos para este día
    const dayTurnos = props.turnos
      .filter((turno) => {
        const turnoDate = new Date(turno.fecha_turno);
        return turnoDate.toDateString() === dayDate.toDateString();
      })
      .sort(
        (a, b) =>
          new Date(a.fecha_turno).getTime() - new Date(b.fecha_turno).getTime()
      );

    days.push({
      date: new Date(dayDate),
      dayNumber: dayDate.getDate(),
      isCurrentMonth,
      isToday,
      turnos: dayTurnos,
    });
  }

  return days;
});

const selectedDayTurnos = computed(() => {
  return selectedDay.value?.turnos || [];
});

const monthStats = computed(() => {
  const monthTurnos = props.turnos.filter((turno) => {
    const turnoDate = new Date(turno.fecha_turno);
    return (
      turnoDate.getMonth() === currentDate.value.getMonth() &&
      turnoDate.getFullYear() === currentDate.value.getFullYear()
    );
  });

  return {
    total: monthTurnos.length,
    pendientes: monthTurnos.filter((t) => t.estado === "pendiente").length,
    confirmados: monthTurnos.filter((t) => t.estado === "confirmado").length,
    completados: monthTurnos.filter((t) => t.estado === "completado").length,
    cancelados: monthTurnos.filter((t) => t.estado === "cancelado").length,
  };
});

const previousMonth = () => {
  const newDate = new Date(currentDate.value);
  newDate.setMonth(newDate.getMonth() - 1);
  currentDate.value = newDate;
  selectedDay.value = null;
  emit("date-change", newDate);
};

const nextMonth = () => {
  const newDate = new Date(currentDate.value);
  newDate.setMonth(newDate.getMonth() + 1);
  currentDate.value = newDate;
  selectedDay.value = null;
  emit("date-change", newDate);
};

const goToToday = () => {
  currentDate.value = new Date();
  selectedDay.value = null;
  emit("date-change", new Date());
};

const refreshCalendar = () => {
  emit("refresh");
};

const selectDay = (day: CalendarDay) => {
  if (!day.isCurrentMonth) {
    // Si es un día de otro mes, navegar a ese mes
    currentDate.value = new Date(day.date);
    emit("date-change", new Date(day.date));
    return;
  }

  selectedDay.value =
    selectedDay.value?.date.getTime() === day.date.getTime() ? null : day;
  emit("day-click", day.date, day.turnos);
};

const formatMonthYear = (date: Date): string => {
  return date.toLocaleDateString("es-ES", {
    year: "numeric",
    month: "long",
  });
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

const truncatePetName = (name: string): string => {
  return name.length > 8 ? name.substring(0, 8) + "..." : name;
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

const getTurnoTooltip = (turno: Turno): string => {
  return `${formatTime(turno.fecha_turno)} - ${turno.nombre_mascota} (${
    turno.duenio?.nombre_apellido || "N/A"
  }) - ${getEstadoLabel(turno.estado)}`;
};

const getDayClass = (day: CalendarDay): string => {
  const classes = [];

  if (!day.isCurrentMonth) classes.push("calendar-day--other-month");
  if (day.isToday) classes.push("calendar-day--today");
  if (selectedDay.value?.date.getTime() === day.date.getTime())
    classes.push("calendar-day--selected");
  if (day.turnos.length > 0) classes.push("calendar-day--has-turnos");

  if (day.turnos.length > 0) {
    const estados = [...new Set(day.turnos.map((t) => t.estado))];
    if (estados.length === 1) {
      classes.push(`calendar-day--${estados[0]}`);
    } else {
      classes.push("calendar-day--multiple");
    }
  }

  return classes.join(" ");
};

watch(
  () => props.turnos,
  () => {
    if (selectedDay.value && selectedDay.value.turnos.length === 0) {
      selectedDay.value = null;
    }
  }
);

onMounted(() => {
  emit("refresh");
});

console.log("🔧 Componente TurnoCalendario cargado");
</script>

<style scoped>
.turno-calendario {
  background: white;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.calendario__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-light);
  background-color: var(--background-color);
}

.calendario__navigation {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.calendario__title {
  margin: 0;
  color: var(--primary-color);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  min-width: 200px;
  text-align: center;
}

.calendario__actions {
  display: flex;
  gap: var(--spacing-sm);
}

/* Legend */
.calendario__legend {
  display: flex;
  justify-content: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--border-light);
  background-color: var(--background-color);
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid var(--border-color);
}

.legend-color--pendiente {
  background-color: var(--warning-color);
}

.legend-color--confirmado {
  background-color: var(--success-color);
}

.legend-color--completado {
  background-color: var(--info-color);
}

.legend-color--cancelado {
  background-color: var(--danger-color);
}

.legend-color--multiple {
  background: linear-gradient(
    45deg,
    var(--warning-color) 25%,
    var(--success-color) 25%,
    var(--success-color) 50%,
    var(--info-color) 50%,
    var(--info-color) 75%,
    var(--danger-color) 75%
  );
}

/* Loading, Error states */
.calendario__loading,
.calendario__error {
  padding: var(--spacing-3xl);
  text-align: center;
}

.error-content {
  max-width: 400px;
  margin: 0 auto;
}

.error-icon {
  font-size: 4rem;
  margin-bottom: var(--spacing-lg);
}

/* Calendar Grid */
.calendario__grid {
  padding: var(--spacing-lg);
}

.calendario__weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  margin-bottom: var(--spacing-sm);
}

.weekday {
  padding: var(--spacing-sm);
  text-align: center;
  font-weight: var(--font-weight-semibold);
  color: var(--text-light);
  font-size: var(--font-size-sm);
}

.calendario__days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background-color: var(--border-light);
}

.calendar-day {
  background: white;
  min-height: 120px;
  padding: var(--spacing-xs);
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
}

.calendar-day:hover {
  background-color: var(--background-color);
}

.calendar-day--other-month {
  background-color: var(--background-color);
  opacity: 0.5;
}

.calendar-day--today {
  background-color: var(--primary-light);
}

.calendar-day--selected {
  background-color: var(--primary-color);
  color: white;
}

.calendar-day--has-turnos {
  border-left: 4px solid var(--primary-color);
}

.calendar-day--pendiente {
  border-left-color: var(--warning-color);
}

.calendar-day--confirmado {
  border-left-color: var(--success-color);
}

.calendar-day--completado {
  border-left-color: var(--info-color);
}

.calendar-day--cancelado {
  border-left-color: var(--danger-color);
}

.calendar-day--multiple {
  border-left: 4px solid;
  border-image: linear-gradient(
      to bottom,
      var(--warning-color),
      var(--success-color),
      var(--info-color)
    )
    1;
}

.day-number {
  font-weight: var(--font-weight-semibold);
  color: var(--text-color);
  margin-bottom: var(--spacing-xs);
}

.calendar-day--selected .day-number {
  color: white;
}

.day-turnos {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.turno-indicator {
  padding: 1px var(--spacing-xs);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  line-height: 1.2;
  overflow: hidden;
}

.turno-indicator--pendiente {
  background-color: var(--warning-light);
  color: var(--warning-color);
}

.turno-indicator--confirmado {
  background-color: var(--success-light);
  color: var(--success-color);
}

.turno-indicator--completado {
  background-color: var(--info-light);
  color: var(--info-color);
}

.turno-indicator--cancelado {
  background-color: var(--danger-light);
  color: var(--danger-color);
}

.turno-time {
  font-weight: var(--font-weight-semibold);
}

.turno-pet {
  display: block;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.more-turnos {
  font-size: var(--font-size-xs);
  color: var(--text-light);
  font-style: italic;
  text-align: center;
  padding: 1px var(--spacing-xs);
}

/* Details */
.calendario__details {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--border-light);
  background-color: var(--background-color);
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.details-header h3 {
  margin: 0;
  color: var(--primary-color);
  font-size: var(--font-size-lg);
}

.details-turnos {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.turno-detail {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: white;
  border-radius: var(--border-radius-md);
  border-left: 4px solid var(--border-color);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.turno-detail:hover {
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.turno-detail--pendiente {
  border-left-color: var(--warning-color);
}

.turno-detail--confirmado {
  border-left-color: var(--success-color);
}

.turno-detail--completado {
  border-left-color: var(--info-color);
}

.turno-detail--cancelado {
  border-left-color: var(--danger-color);
  opacity: 0.7;
}

.turno-detail__time {
  font-weight: var(--font-weight-bold);
  color: var(--primary-color);
  font-size: var(--font-size-lg);
}

.turno-detail__info h4 {
  margin: 0 0 var(--spacing-xs) 0;
  color: var(--text-color);
  font-size: var(--font-size-md);
}

.turno-detail__info p {
  margin: 0 0 var(--spacing-xs) 0;
  color: var(--text-light);
  font-size: var(--font-size-sm);
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

/* Stats */
.calendario__stats {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--border-light);
  background-color: var(--background-color);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
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

/* Responsive */
@media (max-width: 768px) {
  .calendario__header {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: stretch;
  }

  .calendario__navigation {
    justify-content: center;
  }

  .calendario__actions {
    justify-content: center;
  }

  .calendario__legend {
    gap: var(--spacing-md);
  }

  .calendario__grid,
  .calendario__details,
  .calendario__stats {
    padding: var(--spacing-md);
  }

  .calendar-day {
    min-height: 80px;
  }

  .turno-detail {
    grid-template-columns: 1fr;
    gap: var(--spacing-sm);
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .calendar-day {
    min-height: 60px;
    padding: 2px;
  }

  .turno-indicator {
    padding: 1px 2px;
  }

  .turno-time,
  .turno-pet {
    font-size: 10px;
  }
}
</style>
