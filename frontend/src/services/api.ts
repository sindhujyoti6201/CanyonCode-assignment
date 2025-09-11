// API service for Camera Feed Query System
import axios from 'axios';
import {
  CameraFeed,
  SystemHealth,
  SystemStatistics,
  RegionComparison,
  OptimizationSuggestion,
  QueryRequest,
  QueryResponse,
  PerformanceAnalysis,
  ConfigAnalysis,
  FilterOptions,
  EncoderConfig,
  DecoderConfig
} from '../types';

const API_BASE_URL = (process as any).env.REACT_APP_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config: any) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error: any) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: any) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error: any) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const cameraFeedApi = {
  // Query endpoints
  async processQuery(query: string, includeMetadata = false): Promise<QueryResponse> {
    const response = await api.post('/query', {
      query,
      include_metadata: includeMetadata,
    });
    return response.data as QueryResponse;
  },

  // Camera feed endpoints
  async getCameras(filters?: FilterOptions): Promise<CameraFeed[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    
    const response = await api.get(`/cameras?${params.toString()}`);
    return response.data as CameraFeed[];
  },

  async getCameraById(cameraId: string): Promise<CameraFeed & { encoder_config?: EncoderConfig; decoder_config?: DecoderConfig }> {
    const response = await api.get(`/cameras/${cameraId}`);
    return response.data as CameraFeed & { encoder_config?: EncoderConfig; decoder_config?: DecoderConfig };
  },

  async searchCameras(query: string): Promise<CameraFeed[]> {
    const response = await api.get(`/search?q=${encodeURIComponent(query)}`);
    return (response.data as { results: CameraFeed[] }).results;
  },

  // System endpoints
  async getSystemHealth(): Promise<SystemHealth> {
    const response = await api.get('/health');
    return response.data as SystemHealth;
  },

  async getSystemStatistics(): Promise<SystemStatistics> {
    const response = await api.get('/statistics');
    return response.data as SystemStatistics;
  },

  // Analysis endpoints
  async getPerformanceAnalysis(region?: string): Promise<PerformanceAnalysis> {
    const params = region ? `?region=${encodeURIComponent(region)}` : '';
    const response = await api.get(`/analysis/performance${params}`);
    return response.data as PerformanceAnalysis;
  },

  async getRegionComparison(): Promise<{ region_comparison: RegionComparison[] }> {
    const response = await api.get('/analysis/regions');
    return response.data as { region_comparison: RegionComparison[] };
  },

  async getBandwidthOptimization(): Promise<{ suggestions: OptimizationSuggestion[] }> {
    const response = await api.get('/analysis/optimization/bandwidth');
    return response.data as { suggestions: OptimizationSuggestion[] };
  },

  async getClarityOptimization(): Promise<{ opportunities: OptimizationSuggestion[] }> {
    const response = await api.get('/analysis/optimization/clarity');
    return response.data as { opportunities: OptimizationSuggestion[] };
  },

  // Configuration endpoints
  async getEncoderConfigurations(): Promise<{ configurations: EncoderConfig[] }> {
    const response = await api.get('/configurations/encoders');
    return response.data as { configurations: EncoderConfig[] };
  },

  async getDecoderConfigurations(): Promise<{ configurations: DecoderConfig[] }> {
    const response = await api.get('/configurations/decoders');
    return response.data as { configurations: DecoderConfig[] };
  },

  // Utility endpoints
  async getRegions(): Promise<{ regions: string[] }> {
    const response = await api.get('/regions');
    return response.data as { regions: string[] };
  },

  async getLocations(region?: string): Promise<{ locations: string[] }> {
    const params = region ? `?region=${encodeURIComponent(region)}` : '';
    const response = await api.get(`/locations${params}`);
    return response.data as { locations: string[] };
  },

  // Health check
  async healthCheck(): Promise<{ status: string; message: string }> {
    const response = await api.get('/');
    return response.data as { status: string; message: string };
  },
};

export default api;
