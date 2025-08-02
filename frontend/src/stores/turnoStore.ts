import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import ApiService from '@/services/ApiService'
import type { 
  Turno, 
  TurnoEstado,
  CreateTurnoPayload, 
  UpdateTurnoPayload,
  UpdateTurnoEstadoPayload,
  TurnoStoreState 
} from '@/types/models'

export const useTurnoStore = defineStore('turno', () => {
  // 🏪 Estado reactivo
  const turnos = ref<Turno[]>([])
  const currentTurno = ref<Turno | null>(null)
  const turnosByDuenio = ref<Turno[]>([])
  const turnosByFecha = ref<Turno[]>([])
  const loading = ref<boolean>(false)
  const error = ref<string | null>(null)

  // 📊 Getters computados
  const totalTurnos = computed(() => turnos.value.length)
  const hasError = computed(() => error.value !== null)
  const isLoading = computed(() => loading.value)

  // Filtros por estado
  const turnosPendientes = computed(() => 
    turnos.value.filter(t => t.estado === 'pendiente')
  )
  
  const turnosConfirmados = computed(() => 
    turnos.value.filter(t => t.estado === 'confirmado')
  )
  
  const turnosCompletados = computed(() => 
    turnos.value.filter(t => t.estado === 'completado')
  )
  
  const turnosCancelados = computed(() => 
    turnos.value.filter(t => t.estado === 'cancelado')
  )

  // Estadísticas
  const estadisticas = computed(() => ({
    total: turnos.value.length,
    pendientes: turnosPendientes.value.length,
    confirmados: turnosConfirmados.value.length,
    completados: turnosCompletados.value.length,
    cancelados: turnosCancelados.value.length
  }))

  // Turnos de hoy
  const turnosHoy = computed(() => {
    const today = new Date().toISOString().split('T')[0]
    return turnos.value.filter(turno => 
      turno.fecha_turno.startsWith(today)
    ).sort((a, b) => a.fecha_turno.localeCompare(b.fecha_turno))
  })

  // Próximos turnos (siguientes 7 días)
  const proximosTurnos = computed(() => {
    const now = new Date()
    const nextWeek = new Date()
    nextWeek.setDate(now.getDate() + 7)
    
    return turnos.value.filter(turno => {
      const turnoDate = new Date(turno.fecha_turno)
      return turnoDate >= now && turnoDate <= nextWeek && turno.estado !== 'cancelado'
    }).sort((a, b) => a.fecha_turno.localeCompare(b.fecha_turno))
  })

  // 🔄 Acciones

  /**
   * 7.2.3 - Obtener todos los turnos
   */
  const fetchAll = async (): Promise<void> => {
    try {
      loading.value = true
      error.value = null
      
      console.log('🔍 Obteniendo lista de turnos...')
      const response = await ApiService.getTurnos()
      
      turnos.value = response.data || response || []
      console.log(`✅ ${turnos.value.length} turnos cargados`)
      
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Error al cargar turnos'
      console.error('❌ Error al obtener turnos:', error.value)
      turnos.value = []
    } finally {
      loading.value = false
    }
  }

  /**
   * Obtener un turno específico por ID
   */
  const fetchOne = async (id: number): Promise<Turno | null> => {
    try {
      loading.value = true
      error.value = null
      
      console.log(`🔍 Obteniendo turno ID: ${id}`)
      const response = await ApiService.getTurno(id)
      
      currentTurno.value = response.data || response
      console.log('✅ Turno obtenido:', currentTurno.value?.nombre_mascota)
      
      return currentTurno.value
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Error al cargar turno'
      console.error('❌ Error al obtener turno:', error.value)
      currentTurno.value = null
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 7.2.4 - Crear nuevo turno
   */
  const create = async (data: CreateTurnoPayload): Promise<Turno | null> => {
    try {
      loading.value = true
      error.value = null
      
      // Validar fecha
      const turnoDate = new Date(data.fecha_turno)
      const now = new Date()
      
      if (turnoDate < now) {
        error.value = 'No se puede agendar un turno en fecha pasada'
        return null
      }
      
      console.log('➕ Creando nuevo turno:', data.nombre_mascota)
      const response = await ApiService.createTurno(data)
      
      const newTurno = response.data || response
      turnos.value.push(newTurno)
      currentTurno.value = newTurno
      
      console.log('✅ Turno creado exitosamente:', newTurno.nombre_mascota)
      return newTurno
      
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Error al crear turno'
      console.error('❌ Error al crear turno:', error.value)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 7.2.5 - Actualizar turno existente
   */
  const update = async (id: number, data: UpdateTurnoPayload): Promise<Turno | null> => {
    try {
      loading.value = true
      error.value = null
      
      console.log(`✏️ Actualizando turno ID: ${id}`)
      const response = await ApiService.updateTurno(id, data)
      
      const updatedTurno = response.data || response
      
      // Actualizar en la lista
      const index = turnos.value.findIndex(t => t.id === id)
      if (index !== -1) {
        turnos.value[index] = updatedTurno
      }
      
      // Actualizar turno actual si corresponde
      if (currentTurno.value?.id === id) {
        currentTurno.value = updatedTurno
      }
      
      console.log('✅ Turno actualizado:', updatedTurno.nombre_mascota)
      return updatedTurno
      
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Error al actualizar turno'
      console.error('❌ Error al actualizar turno:', error.value)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 7.2.6 - Eliminar turno
   */
  const remove = async (id: number): Promise<boolean> => {
    try {
      loading.value = true
      error.value = null
      
      console.log(`🗑️ Eliminando turno ID: ${id}`)
      await ApiService.deleteTurno(id)
      
      // Remover de la lista
      turnos.value = turnos.value.filter(t => t.id !== id)
      
      // Limpiar turno actual si era el eliminado
      if (currentTurno.value?.id === id) {
        currentTurno.value = null
      }
      
      console.log('✅ Turno eliminado exitosamente')
      return true
      
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Error al eliminar turno'
      console.error('❌ Error al eliminar turno:', error.value)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 7.2.7 - Obtener turnos por dueño
   */
  const fetchByDuenio = async (idDuenio: number): Promise<void> => {
    try {
      loading.value = true
      error.value = null
      
      console.log(`🔍 Obteniendo turnos del dueño ID: ${idDuenio}`)
      const response = await ApiService.getTurnosByDuenio(idDuenio)
      
      turnosByDuenio.value = response.data || response || []
      console.log(`✅ ${turnosByDuenio.value.length} turnos encontrados para el dueño`)
      
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Error al cargar turnos del dueño'
      console.error('❌ Error al obtener turnos por dueño:', error.value)
      turnosByDuenio.value = []
    } finally {
      loading.value = false
    }
  }

  /**
   * 7.2.8 - Obtener turnos por fecha
   */
  const fetchByFecha = async (fecha: string): Promise<void> => {
    try {
      loading.value = true
      error.value = null
      
      console.log(`🔍 Obteniendo turnos de la fecha: ${fecha}`)
      const response = await ApiService.getTurnosByFecha(fecha)
      
      turnosByFecha.value = response.data || response || []
      console.log(`✅ ${turnosByFecha.value.length} turnos encontrados para la fecha`)
      
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Error al cargar turnos de la fecha'
      console.error('❌ Error al obtener turnos por fecha:', error.value)
      turnosByFecha.value = []
    } finally {
      loading.value = false
    }
  }

  /**
   * 7.2.9 - Cambiar estado del turno
   */
  const updateEstado = async (id: number, estado: TurnoEstado): Promise<Turno | null> => {
    try {
      loading.value = true
      error.value = null
      
      console.log(`🔄 Cambiando estado del turno ID ${id} a: ${estado}`)
      const response = await ApiService.updateTurnoEstado(id, estado)
      
      const updatedTurno = response.data || response
      
      // Actualizar en la lista principal
      const index = turnos.value.findIndex(t => t.id === id)
      if (index !== -1) {
        turnos.value[index] = updatedTurno
      }
      
      // Actualizar en turno actual si corresponde
      if (currentTurno.value?.id === id) {
        currentTurno.value = updatedTurno
      }
      
      console.log('✅ Estado actualizado exitosamente')
      return updatedTurno
      
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Error al cambiar estado'
      console.error('❌ Error al cambiar estado:', error.value)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Filtrar turnos por estado
   */
  const filterByEstado = (estado: TurnoEstado): Turno[] => {
    return turnos.value.filter(turno => turno.estado === estado)
  }

  /**
   * Filtrar turnos por rango de fechas
   */
  const filterByDateRange = (startDate: string, endDate: string): Turno[] => {
    return turnos.value.filter(turno => {
      const turnoDate = turno.fecha_turno.split('T')[0]
      return turnoDate >= startDate && turnoDate <= endDate
    })
  }

  /**
   * Buscar turnos por texto (mascota, dueño, tratamiento)
   */
  const searchTurnos = (query: string): Turno[] => {
    if (!query.trim()) return turnos.value
    
    const searchTerm = query.toLowerCase().trim()
    return turnos.value.filter(turno => 
      turno.nombre_mascota.toLowerCase().includes(searchTerm) ||
      turno.tratamiento.toLowerCase().includes(searchTerm) ||
      turno.duenio?.nombre_apellido.toLowerCase().includes(searchTerm) ||
      turno.duenio?.telefono.includes(searchTerm)
    )
  }

  /**
   * Verificar conflictos de horario
   */
  const checkConflicts = (fecha: string, excludeId?: number): Turno[] => {
    const targetDateTime = new Date(fecha)
    const marginMinutes = 30 // Margen de 30 minutos entre turnos
    
    return turnos.value.filter(turno => {
      if (excludeId && turno.id === excludeId) return false
      if (turno.estado === 'cancelado') return false
      
      const turnoDateTime = new Date(turno.fecha_turno)
      const diffMinutes = Math.abs(targetDateTime.getTime() - turnoDateTime.getTime()) / (1000 * 60)
      
      return diffMinutes < marginMinutes
    })
  }

  /**
   * Limpiar filtros
   */
  const clearFilters = (): void => {
    turnosByDuenio.value = []
    turnosByFecha.value = []
    error.value = null
  }

  /**
   * Limpiar errores
   */
  const clearError = (): void => {
    error.value = null
  }

  /**
   * Limpiar turno actual
   */
  const clearCurrent = (): void => {
    currentTurno.value = null
  }

  /**
   * Encontrar turno por ID en la lista cargada
   */
  const findById = (id: number): Turno | undefined => {
    return turnos.value.find(t => t.id === id)
  }

  // 🔄 Retornar estado y acciones
  return {
    // Estado
    turnos,
    currentTurno,
    turnosByDuenio,
    turnosByFecha,
    loading,
    error,
    
    // Getters computados
    totalTurnos,
    hasError,
    isLoading,
    turnosPendientes,
    turnosConfirmados,
    turnosCompletados,
    turnosCancelados,
    estadisticas,
    turnosHoy,
    proximosTurnos,
    
    // Acciones principales
    fetchAll,
    fetchOne,
    create,
    update,
    remove,
    fetchByDuenio,
    fetchByFecha,
    updateEstado,
    
    // Utilidades
    filterByEstado,
    filterByDateRange,
    searchTurnos,
    checkConflicts,
    clearFilters,
    clearError,
    clearCurrent,
    findById
  }
})