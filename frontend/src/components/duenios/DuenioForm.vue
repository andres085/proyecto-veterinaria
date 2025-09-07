<template>
  <form @submit.prevent="handleSubmit" class="duenio-form">
    <div class="duenio-form__header">
      <h2 class="duenio-form__title">
        {{ mode === "create" ? "➕ Nuevo Dueño" : "✏️ Editar Dueño" }}
      </h2>

      <p class="duenio-form__subtitle">
        {{
          mode === "create"
            ? "Ingresa los datos del propietario de la mascota"
            : "Modifica los datos del dueño seleccionado"
        }}
      </p>
    </div>

    <div class="duenio-form__body">
      <div class="form-group">
        <label for="nombre_apellido" class="form-label form-label--required">
          👤 Nombre y Apellido
        </label>
        <input
          id="nombre_apellido"
          ref="nombreInput"
          v-model="formData.nombre_apellido"
          type="text"
          class="form-input"
          :class="{ 'form-input--error': errors.nombre_apellido }"
          placeholder="Ej: Juan Carlos Pérez"
          :disabled="loading"
          required
          minlength="2"
          maxlength="100"
          @blur="validateField('nombre_apellido')"
          @input="clearFieldError('nombre_apellido')"
        />
        <span v-if="errors.nombre_apellido" class="form-error">
          {{ errors.nombre_apellido }}
        </span>
        <span v-else class="form-help">
          Nombre completo del propietario de la mascota
        </span>
      </div>

      <div class="form-group">
        <label for="telefono" class="form-label form-label--required">
          📱 Teléfono
        </label>
        <input
          id="telefono"
          v-model="formData.telefono"
          type="tel"
          class="form-input"
          :class="{ 'form-input--error': errors.telefono }"
          placeholder="Ej: +54 11 1234-5678"
          :disabled="loading"
          required
          maxlength="20"
          @blur="validateField('telefono')"
          @input="clearFieldError('telefono')"
        />
        <span v-if="errors.telefono" class="form-error">
          {{ errors.telefono }}
        </span>
        <span v-else class="form-help"> Número de contacto principal </span>
      </div>

      <div class="form-group">
        <label for="email" class="form-label form-label--required">
          📧 Email
        </label>
        <input
          id="email"
          v-model="formData.email"
          type="email"
          class="form-input"
          :class="{ 'form-input--error': errors.email }"
          placeholder="Ej: juan.perez@email.com"
          :disabled="loading"
          required
          maxlength="100"
          @blur="validateField('email')"
          @input="clearFieldError('email')"
        />
        <span v-if="errors.email" class="form-error">
          {{ errors.email }}
        </span>
        <span v-else class="form-help">
          Dirección de correo electrónico (debe ser única)
        </span>
      </div>

      <div class="form-group">
        <label for="direccion" class="form-label form-label--required">
          📍 Dirección
        </label>
        <textarea
          id="direccion"
          v-model="formData.direccion"
          class="form-input form-input--textarea"
          :class="{ 'form-input--error': errors.direccion }"
          placeholder="Ej: Av. Corrientes 1234, CABA, Buenos Aires"
          :disabled="loading"
          required
          minlength="5"
          maxlength="500"
          rows="3"
          @blur="validateField('direccion')"
          @input="clearFieldError('direccion')"
        ></textarea>
        <span v-if="errors.direccion" class="form-error">
          {{ errors.direccion }}
        </span>
        <span v-else class="form-help">
          Dirección completa para contacto y visitas
        </span>
      </div>
    </div>

    <div class="duenio-form__footer">
      <button
        type="button"
        class="btn btn--secondary"
        @click="handleCancel"
        :disabled="loading"
      >
        ❌ Cancelar
      </button>

      <button
        type="submit"
        class="btn btn--primary"
        :disabled="loading || !isFormValid"
      >
        <LoadingSpinner v-if="loading" size="small" color="white" />
        <span v-else>
          {{ mode === "create" ? "💾 Crear Dueño" : "💾 Guardar Cambios" }}
        </span>
      </button>
    </div>

    <div v-if="successMessage" class="duenio-form__success">
      ✅ {{ successMessage }}
    </div>

    <div v-if="generalError" class="duenio-form__error">
      ❌ {{ generalError }}
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick, onMounted } from "vue";
import LoadingSpinner from "@/components/shared/LoadingSpinner.vue";
import type {
  Duenio,
  CreateDuenioPayload,
  UpdateDuenioPayload,
} from "@/types/models";

export interface DuenioFormProps {
  duenio?: Duenio | null;
  mode?: "create" | "edit";
  loading?: boolean;
}

export interface DuenioFormEmits {
  (e: "submit", data: CreateDuenioPayload | UpdateDuenioPayload): void;
  (e: "cancel"): void;
  (e: "success", duenio: Duenio): void;
}

const props = withDefaults(defineProps<DuenioFormProps>(), {
  duenio: null,
  mode: "create",
  loading: false,
});

const emit = defineEmits<DuenioFormEmits>();

const nombreInput = ref<HTMLInputElement>();

const formData = reactive<CreateDuenioPayload>({
  nombre_apellido: "",
  telefono: "",
  email: "",
  direccion: "",
});

const errors = reactive<Record<string, string>>({
  nombre_apellido: "",
  telefono: "",
  email: "",
  direccion: "",
});

const successMessage = ref<string>("");
const generalError = ref<string>("");

const isFormValid = computed(() => {
  return (
    formData.nombre_apellido.length >= 2 &&
    formData.telefono.length >= 8 &&
    isValidEmail(formData.email) &&
    formData.direccion.length >= 5 &&
    !Object.values(errors).some((error) => error)
  );
});

const validateField = (field: keyof typeof formData): boolean => {
  errors[field] = "";

  switch (field) {
    case "nombre_apellido":
      if (!formData.nombre_apellido.trim()) {
        errors[field] = "El nombre es requerido";
      } else if (formData.nombre_apellido.length < 2) {
        errors[field] = "El nombre debe tener al menos 2 caracteres";
      } else if (formData.nombre_apellido.length > 100) {
        errors[field] = "El nombre no puede exceder 100 caracteres";
      } else if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(formData.nombre_apellido)) {
        errors[field] = "El nombre solo puede contener letras y espacios";
      }
      break;

    case "telefono":
      if (!formData.telefono.trim()) {
        errors[field] = "El teléfono es requerido";
      } else if (formData.telefono.length < 8) {
        errors[field] = "El teléfono debe tener al menos 8 caracteres";
      } else if (!/^[\d\s\-\+\(\)]+$/.test(formData.telefono)) {
        errors[field] = "Formato de teléfono inválido";
      }
      break;

    case "email":
      if (!formData.email.trim()) {
        errors[field] = "El email es requerido";
      } else if (!isValidEmail(formData.email)) {
        errors[field] = "Formato de email inválido";
      }
      break;

    case "direccion":
      if (!formData.direccion.trim()) {
        errors[field] = "La dirección es requerida";
      } else if (formData.direccion.length < 5) {
        errors[field] = "La dirección debe tener al menos 5 caracteres";
      } else if (formData.direccion.length > 500) {
        errors[field] = "La dirección no puede exceder 500 caracteres";
      }
      break;
  }

  return !errors[field];
};

const validateAllFields = (): boolean => {
  const fields: (keyof typeof formData)[] = [
    "nombre_apellido",
    "telefono",
    "email",
    "direccion",
  ];
  return fields.every((field) => validateField(field));
};

const clearFieldError = (field: keyof typeof errors) => {
  if (errors[field]) {
    errors[field] = "";
  }
};

const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

const resetForm = () => {
  formData.nombre_apellido = "";
  formData.telefono = "";
  formData.email = "";
  formData.direccion = "";

  Object.keys(errors).forEach((key) => {
    errors[key as keyof typeof errors] = "";
  });

  successMessage.value = "";
  generalError.value = "";
};

const loadDuenioData = () => {
  if (props.duenio && props.mode === "edit") {
    formData.nombre_apellido = props.duenio.nombre_apellido;
    formData.telefono = props.duenio.telefono;
    formData.email = props.duenio.email;
    formData.direccion = props.duenio.direccion;
  }
};

const handleSubmit = () => {
  successMessage.value = "";
  generalError.value = "";

  if (!validateAllFields()) {
    generalError.value = "Por favor corrige los errores en el formulario";
    return;
  }

  const submitData = { ...formData };
  emit("submit", submitData);

  console.log(`📝 Formulario ${props.mode} enviado:`, submitData);
};

const handleCancel = () => {
  emit("cancel");
};

const showSuccess = (message: string) => {
  successMessage.value = message;
  generalError.value = "";

  setTimeout(() => {
    successMessage.value = "";
  }, 3000);
};

const showError = (message: string) => {
  generalError.value = message;
  successMessage.value = "";
};

const focusFirstField = async () => {
  await nextTick();
  nombreInput.value?.focus();
};

watch(
  () => props.duenio,
  () => {
    loadDuenioData();
  },
  { immediate: true }
);

watch(
  () => props.mode,
  () => {
    if (props.mode === "create") {
      resetForm();
    }
  },
  { immediate: true }
);

onMounted(() => {
  loadDuenioData();
  if (props.mode === "create") {
    focusFirstField();
  }
});

defineExpose({
  resetForm,
  validateAllFields,
  showSuccess,
  showError,
  focusFirstField,
});

console.log("🔧 Componente DuenioForm cargado");
</script>

<style scoped>
.duenio-form {
  background: white;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  max-width: 600px;
  margin: 0 auto;
}

.duenio-form__header {
  padding: var(--spacing-xl) var(--spacing-xl) var(--spacing-lg);
  border-bottom: 1px solid var(--border-light);
  text-align: center;
}

.duenio-form__title {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--primary-color);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
}

.duenio-form__subtitle {
  margin: 0;
  color: var(--text-light);
  font-size: var(--font-size-sm);
}

.duenio-form__body {
  padding: var(--spacing-xl);
}

.form-group {
  margin-bottom: var(--spacing-lg);
}

.form-input--textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.duenio-form__footer {
  display: flex;
  gap: var(--spacing-md);
  padding: var(--spacing-lg) var(--spacing-xl) var(--spacing-xl);
  border-top: 1px solid var(--border-light);
  background-color: var(--background-color);
  justify-content: flex-end;
}

.duenio-form__success {
  margin: var(--spacing-md) var(--spacing-xl) 0;
  padding: var(--spacing-md);
  background-color: var(--success-light);
  color: var(--success-color);
  border-radius: var(--border-radius-md);
  font-weight: var(--font-weight-medium);
  text-align: center;
}

.duenio-form__error {
  margin: var(--spacing-md) var(--spacing-xl) 0;
  padding: var(--spacing-md);
  background-color: var(--danger-light);
  color: var(--danger-color);
  border-radius: var(--border-radius-md);
  font-weight: var(--font-weight-medium);
  text-align: center;
}

/* Responsive */
@media (max-width: 768px) {
  .duenio-form {
    margin: 0;
    border-radius: 0;
    box-shadow: none;
  }

  .duenio-form__header,
  .duenio-form__body,
  .duenio-form__footer {
    padding-left: var(--spacing-md);
    padding-right: var(--spacing-md);
  }

  .duenio-form__footer {
    flex-direction: column-reverse;
  }

  .btn {
    width: 100%;
  }
}

.form-input:valid:not(:placeholder-shown) {
  border-color: var(--success-color);
}

.form-input:invalid:not(:placeholder-shown) {
  border-color: var(--warning-color);
}

.form-input:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

.duenio-form__success,
.duenio-form__error {
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
