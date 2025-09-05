import ApiService from "@/services/ApiService";
import type {
  CreateDuenioPayload,
  Duenio,
  UpdateDuenioPayload,
} from "@/types/models";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

export const useDuenioStore = defineStore("duenio", () => {
  // 🏪 Estado reactivo
  const duenios = ref<Duenio[]>([]);
  const currentDuenio = ref<Duenio | null>(null);
  const searchResults = ref<Duenio[]>([]);
  const loading = ref<boolean>(false);
  const error = ref<string | null>(null);

  // 📊 Getters computados
  const totalDuenios = computed(() => duenios.value.length);
  const hasError = computed(() => error.value !== null);
  const isLoading = computed(() => loading.value);

  // 🔄 Acciones

  /**
   * 7.1.3 - Obtener todos los dueños
   */
  const fetchAll = async (): Promise<void> => {
    try {
      loading.value = true;
      error.value = null;

      console.log("🔍 Obteniendo lista de dueños...");
      const response = await ApiService.getDuenios();

      duenios.value = response.data.duenios || response || [];
      console.log(`✅ ${duenios.value.length} dueños cargados`);
    } catch (err: any) {
      error.value =
        err.response?.data?.message || err.message || "Error al cargar dueños";
      console.error("❌ Error al obtener dueños:", error.value);
      duenios.value = [];
    } finally {
      loading.value = false;
    }
  };

  /**
   * Obtener un dueño específico por ID
   */
  const fetchOne = async (id: number): Promise<Duenio | null> => {
    try {
      loading.value = true;
      error.value = null;

      console.log(`🔍 Obteniendo dueño ID: ${id}`);
      const response = await ApiService.getDuenio(id);

      currentDuenio.value = response.data || response;
      console.log("✅ Dueño obtenido:", currentDuenio.value?.nombre_apellido);

      return currentDuenio.value;
    } catch (err: any) {
      error.value =
        err.response?.data?.message || err.message || "Error al cargar dueño";
      console.error("❌ Error al obtener dueño:", error.value);
      currentDuenio.value = null;
      return null;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 7.1.4 - Crear nuevo dueño
   */
  const create = async (data: CreateDuenioPayload): Promise<Duenio | null> => {
    try {
      loading.value = true;
      error.value = null;

      console.log("➕ Creando nuevo dueño:", data.nombre_apellido);
      const response = await ApiService.createDuenio(data);

      const { duenio } = response.data;

      duenios.value.push(duenio);
      currentDuenio.value = duenio;

      console.log("✅ Dueño creado exitosamente:", duenio.nombre_apellido);
      return duenio;
    } catch (err: any) {
      error.value =
        err.response?.data?.message || err.message || "Error al crear dueño";
      console.error("❌ Error al crear dueño:", error.value);
      return null;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 7.1.5 - Actualizar dueño existente
   */
  const update = async (
    id: number,
    data: UpdateDuenioPayload
  ): Promise<Duenio | null> => {
    try {
      loading.value = true;
      error.value = null;

      console.log(`✏️ Actualizando dueño ID: ${id}`);
      const response = await ApiService.updateDuenio(id, data);

      const { duenio: updatedDuenio } = response.data || response;

      // Actualizar en la lista
      const index = duenios.value.findIndex((d) => d.id === id);
      if (index !== -1) {
        duenios.value[index] = updatedDuenio;
      }

      // Actualizar dueño actual si corresponde
      if (currentDuenio.value?.id === id) {
        currentDuenio.value = updatedDuenio;
      }

      console.log("✅ Dueño actualizado:", updatedDuenio.nombre_apellido);
      return updatedDuenio;
    } catch (err: any) {
      error.value =
        err.response?.data?.message ||
        err.message ||
        "Error al actualizar dueño";
      console.error("❌ Error al actualizar dueño:", error.value);
      return null;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 7.1.6 - Eliminar dueño
   */
  const remove = async (id: number): Promise<boolean> => {
    try {
      loading.value = true;
      error.value = null;

      console.log(`🗑️ Eliminando dueño ID: ${id}`);
      await ApiService.deleteDuenio(id);

      // Remover de la lista
      duenios.value = duenios.value.filter((d) => d.id !== id);

      // Limpiar dueño actual si era el eliminado
      if (currentDuenio.value?.id === id) {
        currentDuenio.value = null;
      }

      console.log("✅ Dueño eliminado exitosamente");
      return true;
    } catch (err: any) {
      error.value =
        err.response?.data?.message || err.message || "Error al eliminar dueño";
      console.error("❌ Error al eliminar dueño:", error.value);
      return false;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 7.1.7 - Buscar dueños por nombre/email
   */
  const search = async (query: string): Promise<void> => {
    try {
      loading.value = true;
      error.value = null;

      if (!query.trim()) {
        searchResults.value = [];
        return;
      }

      console.log(`🔍 Buscando dueños: "${query}"`);
      const response = await ApiService.searchDuenios(query);

      searchResults.value = response.data || response || [];
      console.log("ACAAAA", searchResults.value);
      console.log(`✅ ${searchResults.value.length} resultados encontrados`);
    } catch (err: any) {
      error.value =
        err.response?.data?.message || err.message || "Error en la búsqueda";
      console.error("❌ Error en búsqueda:", error.value);
      searchResults.value = [];
    } finally {
      loading.value = false;
    }
  };

  /**
   * Limpiar resultados de búsqueda
   */
  const clearSearch = (): void => {
    searchResults.value = [];
    error.value = null;
  };

  /**
   * Limpiar errores
   */
  const clearError = (): void => {
    error.value = null;
  };

  /**
   * Limpiar dueño actual
   */
  const clearCurrent = (): void => {
    currentDuenio.value = null;
  };

  /**
   * Encontrar dueño por ID en la lista cargada
   */
  const findById = (id: number): Duenio | undefined => {
    return duenios.value.find((d) => d.id === id);
  };

  /**
   * Filtrar dueños por texto (búsqueda local)
   */
  const filterLocal = computed(() => (query: string): Duenio[] => {
    if (!query.trim()) return duenios.value;

    const searchTerm = query.toLowerCase().trim();
    return duenios.value.filter(
      (duenio) =>
        duenio.nombre_apellido.toLowerCase().includes(searchTerm) ||
        duenio.email.toLowerCase().includes(searchTerm) ||
        duenio.telefono.includes(searchTerm)
    );
  });

  // 🔄 Retornar estado y acciones
  return {
    // Estado
    duenios,
    currentDuenio,
    searchResults,
    loading,
    error,

    // Getters
    totalDuenios,
    hasError,
    isLoading,
    filterLocal,

    // Acciones
    fetchAll,
    fetchOne,
    create,
    update,
    remove,
    search,
    clearSearch,
    clearError,
    clearCurrent,
    findById,
  };
});
