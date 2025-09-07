<template>
  <div
    class="loading-spinner"
    :class="[
      `loading-spinner--${size}`,
      { 'loading-spinner--overlay': overlay },
    ]"
    role="status"
    :aria-label="ariaLabel"
  >
    <div class="loading-spinner__spinner" :style="spinnerStyle"></div>

    <div
      v-if="text"
      class="loading-spinner__text"
      :class="[`loading-spinner__text--${size}`]"
    >
      {{ text }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

export interface LoadingSpinnerProps {
  size?: "small" | "medium" | "large";
  color?: string;
  text?: string;
  overlay?: boolean;
  speed?: "slow" | "normal" | "fast";
}

const props = withDefaults(defineProps<LoadingSpinnerProps>(), {
  size: "medium",
  color: "#2c5aa0",
  overlay: false,
  speed: "normal",
});

const spinnerStyle = computed(() => ({
  borderTopColor: props.color,
  borderRightColor: props.color,
  animationDuration: getAnimationDuration(),
}));

const ariaLabel = computed(() => {
  if (props.text) {
    return `Cargando: ${props.text}`;
  }
  return "Cargando contenido";
});

const getAnimationDuration = (): string => {
  const durations = {
    slow: "2s",
    normal: "1s",
    fast: "0.5s",
  };
  return durations[props.speed];
};

console.log("🔧 Componente LoadingSpinner cargado");
</script>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.loading-spinner--overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  z-index: 10;
  backdrop-filter: blur(2px);
}

.loading-spinner__spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #2c5aa0;
  border-right: 3px solid #2c5aa0;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-spinner--small .loading-spinner__spinner {
  width: 20px;
  height: 20px;
  border-width: 2px;
}

.loading-spinner--medium .loading-spinner__spinner {
  width: 40px;
  height: 40px;
  border-width: 3px;
}

.loading-spinner--large .loading-spinner__spinner {
  width: 60px;
  height: 60px;
  border-width: 4px;
}

.loading-spinner__text {
  color: #666;
  font-weight: 500;
  text-align: center;
  margin: 0;
}

.loading-spinner__text--small {
  font-size: 0.875rem;
}

.loading-spinner__text--medium {
  font-size: 1rem;
}

.loading-spinner__text--large {
  font-size: 1.125rem;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .loading-spinner__spinner {
    animation: spin 2s linear infinite;
  }
}

@media (prefers-color-scheme: dark) {
  .loading-spinner--overlay {
    background-color: rgba(30, 30, 30, 0.9);
  }

  .loading-spinner__text {
    color: #ccc;
  }

  .loading-spinner__spinner {
    border-color: #444;
  }
}

@media (max-width: 768px) {
  .loading-spinner--large .loading-spinner__spinner {
    width: 50px;
    height: 50px;
  }

  .loading-spinner__text--large {
    font-size: 1rem;
  }
}
</style>
