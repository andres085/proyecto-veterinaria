<template>
  <Transition name="modal" appear>
    <div
      v-if="isVisible"
      class="confirm-dialog-overlay"
      @click="handleBackdropClick"
      @keydown.esc="handleCancel"
      tabindex="-1"
    >
      <div
        class="confirm-dialog"
        :class="[`confirm-dialog--${type}`]"
        @click.stop
        role="dialog"
        :aria-labelledby="titleId"
        :aria-describedby="messageId"
        aria-modal="true"
      >
        <!-- Header -->
        <div class="confirm-dialog__header">
          <div class="confirm-dialog__icon">
            <span v-if="type === 'danger'">⚠️</span>
            <span v-else-if="type === 'warning'">⚡</span>
            <span v-else-if="type === 'info'">ℹ️</span>
            <span v-else>❓</span>
          </div>
          
          <h3 :id="titleId" class="confirm-dialog__title">
            {{ title }}
          </h3>
        </div>

        <!-- Body -->
        <div class="confirm-dialog__body">
          <p :id="messageId" class="confirm-dialog__message">
            {{ message }}
          </p>
          
          <!-- Slot para contenido adicional -->
          <div v-if="$slots.default" class="confirm-dialog__content">
            <slot />
          </div>
        </div>

        <!-- Footer -->
        <div class="confirm-dialog__footer">
          <button
            type="button"
            class="btn btn--secondary"
            @click="handleCancel"
            :disabled="loading"
          >
            {{ cancelText }}
          </button>
          
          <button
            type="button"
            class="btn"
            :class="[`btn--${type}`]"
            @click="handleConfirm"
            :disabled="loading"
            ref="confirmButton"
          >
            <span v-if="loading" class="btn__spinner"></span>
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, computed } from 'vue'

// Types
export interface ConfirmDialogProps {
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  type?: 'danger' | 'warning' | 'info' | 'default'
  isVisible: boolean
  loading?: boolean
  closeOnBackdrop?: boolean
}

export interface ConfirmDialogEmits {
  (e: 'confirm'): void
  (e: 'cancel'): void
  (e: 'update:isVisible', value: boolean): void
}

// Props
const props = withDefaults(defineProps<ConfirmDialogProps>(), {
  confirmText: 'Confirmar',
  cancelText: 'Cancelar',
  type: 'default',
  loading: false,
  closeOnBackdrop: true
})

// Emits
const emit = defineEmits<ConfirmDialogEmits>()

// Refs
const confirmButton = ref<HTMLButtonElement>()

// Computed
const titleId = computed(() => `confirm-title-${Math.random().toString(36).substr(2, 9)}`)
const messageId = computed(() => `confirm-message-${Math.random().toString(36).substr(2, 9)}`)

// Methods
const handleConfirm = () => {
  if (!props.loading) {
    emit('confirm')
  }
}

const handleCancel = () => {
  if (!props.loading) {
    emit('cancel')
    emit('update:isVisible', false)
  }
}

const handleBackdropClick = () => {
  if (props.closeOnBackdrop && !props.loading) {
    handleCancel()
  }
}

// Focus management
watch(() => props.isVisible, async (newValue) => {
  if (newValue) {
    await nextTick()
    confirmButton.value?.focus()
  }
}, { immediate: true })

console.log('🔧 Componente ConfirmDialog cargado')
</script>

<style scoped>
.confirm-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.confirm-dialog {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideIn 0.3s ease-out;
}

.confirm-dialog__header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 1px solid #eee;
}

.confirm-dialog__icon {
  font-size: 2rem;
  line-height: 1;
}

.confirm-dialog__title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
  flex: 1;
}

.confirm-dialog__body {
  padding: 1rem 1.5rem;
}

.confirm-dialog__message {
  margin: 0 0 1rem 0;
  color: #666;
  line-height: 1.5;
}

.confirm-dialog__content {
  margin-top: 1rem;
}

.confirm-dialog__footer {
  display: flex;
  gap: 0.75rem;
  padding: 1rem 1.5rem 1.5rem;
  justify-content: flex-end;
  border-top: 1px solid #eee;
}

/* Button styles */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-width: 100px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn--secondary {
  background-color: #6c757d;
  color: white;
}

.btn--secondary:hover:not(:disabled) {
  background-color: #545b62;
}

.btn--danger {
  background-color: #dc3545;
  color: white;
}

.btn--danger:hover:not(:disabled) {
  background-color: #c82333;
}

.btn--warning {
  background-color: #ffc107;
  color: #212529;
}

.btn--warning:hover:not(:disabled) {
  background-color: #e0a800;
}

.btn--info {
  background-color: #17a2b8;
  color: white;
}

.btn--info:hover:not(:disabled) {
  background-color: #138496;
}

.btn--default {
  background-color: #2c5aa0;
  color: white;
}

.btn--default:hover:not(:disabled) {
  background-color: #1e3f73;
}

.btn__spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Dialog type styles */
.confirm-dialog--danger .confirm-dialog__header {
  border-bottom-color: #dc3545;
}

.confirm-dialog--warning .confirm-dialog__header {
  border-bottom-color: #ffc107;
}

.confirm-dialog--info .confirm-dialog__header {
  border-bottom-color: #17a2b8;
}

/* Animations */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Transition classes */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .confirm-dialog,
.modal-leave-active .confirm-dialog {
  transition: transform 0.3s ease;
}

.modal-enter-from .confirm-dialog,
.modal-leave-to .confirm-dialog {
  transform: scale(0.9) translateY(-20px);
}

/* Responsive */
@media (max-width: 768px) {
  .confirm-dialog {
    margin: 1rem;
    max-width: none;
  }
  
  .confirm-dialog__header,
  .confirm-dialog__body,
  .confirm-dialog__footer {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .confirm-dialog__footer {
    flex-direction: column-reverse;
  }
  
  .btn {
    width: 100%;
  }
}
</style>