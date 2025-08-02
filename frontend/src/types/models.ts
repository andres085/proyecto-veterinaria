// Interfaces para el sistema de gestión de turnos veterinaria

export interface Duenio {
  id?: number
  nombre_apellido: string
  telefono: string
  email: string
  direccion: string
  created_at?: string
  updated_at?: string
}

export interface Turno {
  id?: number
  nombre_mascota: string
  fecha_turno: string
  tratamiento: string
  id_duenio: number
  estado: TurnoEstado
  created_at?: string
  updated_at?: string
  duenio?: Duenio // Información del dueño cuando se hace join
}

export type TurnoEstado = 'pendiente' | 'confirmado' | 'completado' | 'cancelado'

// Payloads para requests
export interface CreateDuenioPayload {
  nombre_apellido: string
  telefono: string
  email: string
  direccion: string
}

export interface UpdateDuenioPayload extends Partial<CreateDuenioPayload> {}

export interface CreateTurnoPayload {
  nombre_mascota: string
  fecha_turno: string
  tratamiento: string
  id_duenio: number
  estado?: TurnoEstado
}

export interface UpdateTurnoPayload extends Partial<CreateTurnoPayload> {}

export interface UpdateTurnoEstadoPayload {
  estado: TurnoEstado
}

// Responses del API
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

// Store states
export interface DuenioStoreState {
  duenios: Duenio[]
  currentDuenio: Duenio | null
  loading: boolean
  error: string | null
}

export interface TurnoStoreState {
  turnos: Turno[]
  currentTurno: Turno | null
  loading: boolean
  error: string | null
}

// Form validation interfaces
export interface ValidationError {
  field: string
  message: string
}

export interface FormErrors {
  [key: string]: string[]
}