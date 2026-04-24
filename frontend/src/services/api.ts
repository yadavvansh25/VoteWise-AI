import axios from 'axios';
import type { ChatRequest, ChatResponse, HealthResponse, LanguagesResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use((config) => {
  console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error(`[API Error] ${error.response.status}: ${error.response.data?.detail || 'Unknown error'}`);
    } else if (error.request) {
      console.error('[API Error] No response received — server might be offline');
    } else {
      console.error('[API Error]', error.message);
    }
    return Promise.reject(error);
  }
);

export const api = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>('/api/chat', request);
    return response.data;
  },

  async healthCheck(): Promise<HealthResponse> {
    const response = await apiClient.get<HealthResponse>('/api/health');
    return response.data;
  },

  async getLanguages(): Promise<LanguagesResponse> {
    const response = await apiClient.get<LanguagesResponse>('/api/languages');
    return response.data;
  },
};

export default api;
