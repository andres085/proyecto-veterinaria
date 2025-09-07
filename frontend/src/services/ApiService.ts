import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios";

class ApiService {
  private api: AxiosInstance;

  constructor() {
    const baseURL = "http://localhost:5000/api";

    this.api = axios.create({
      baseURL,
      timeout: 15000,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      withCredentials: false,
    });

    console.log(`🔧 ApiService initialized with baseURL: ${baseURL}`);

    this.api.interceptors.request.use(
      (config) => {
        console.log(
          `🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`
        );
        return config;
      },
      (error) => {
        console.error("❌ API Request Error:", error);
        return Promise.reject(error);
      }
    );

    this.api.interceptors.response.use(
      (response) => {
        console.log(
          `✅ API Response: ${response.status} ${response.config.url}`
        );
        return response;
      },
      (error) => {
        console.error(
          "❌ API Response Error:",
          error.response?.data || error.message
        );

        if (error.code === "ERR_NETWORK" || error.message.includes("CORS")) {
          console.error(
            "🚫 CORS Error detected. Make sure backend CORS is configured properly."
          );
          throw new Error(
            "Error de conexión con el servidor. Verifique que el backend esté ejecutándose."
          );
        }

        if (error.response) {
          const status = error.response.status;
          const message =
            error.response.data?.message ||
            error.response.data?.error ||
            "Error desconocido";

          switch (status) {
            case 400:
              throw new Error(`Datos inválidos: ${message}`);
            case 401:
              throw new Error("No autorizado");
            case 403:
              throw new Error("Acceso prohibido");
            case 404:
              throw new Error("Recurso no encontrado");
            case 500:
              throw new Error("Error interno del servidor");
            default:
              throw new Error(`Error ${status}: ${message}`);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.api.get(url, config);
    return response.data;
  }

  async post<T>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.api.post(url, data, config);
    return response.data;
  }

  async put<T>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.api.put(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.api.delete(url, config);
    return response.data;
  }

  getDuenios() {
    return this.get("/duenios");
  }

  getDuenio(id: number) {
    return this.get(`/duenios/${id}`);
  }

  createDuenio(data: any) {
    return this.post("/duenios", data);
  }

  updateDuenio(id: number, data: any) {
    return this.put(`/duenios/${id}`, data);
  }

  deleteDuenio(id: number) {
    return this.delete(`/duenios/${id}`);
  }

  searchDuenios(query: string) {
    return this.get(`/duenios/search?q=${encodeURIComponent(query)}`);
  }

  getTurnos() {
    return this.get("/turnos");
  }

  getTurno(id: number) {
    return this.get(`/turnos/${id}`);
  }

  createTurno(data: any) {
    return this.post("/turnos", data);
  }

  updateTurno(id: number, data: any) {
    return this.put(`/turnos/${id}`, data);
  }

  deleteTurno(id: number) {
    return this.delete(`/turnos/${id}`);
  }

  getTurnosByDuenio(idDuenio: number) {
    return this.get(`/turnos/duenio/${idDuenio}`);
  }

  getTurnosByFecha(fecha: string) {
    return this.get(`/turnos/fecha/${fecha}`);
  }

  updateTurnoEstado(id: number, estado: string) {
    return this.put(`/turnos/${id}/estado`, { estado });
  }
}

export default new ApiService();
