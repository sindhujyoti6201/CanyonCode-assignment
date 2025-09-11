// TypeScript types for Camera Feed Query System

export interface CameraFeed {
  camera_id: string;
  location: string;
  region: string;
  clarity_score: number;
  status: 'active' | 'inactive' | 'maintenance' | 'error';
  bandwidth_usage: number;
  storage_usage: number;
  encoder_config_id: string;
  decoder_config_id: string;
  last_updated: string;
}

export interface EncoderConfig {
  id: string;
  bitrate: number;
  resolution: string;
  framerate: number;
  codec: string;
  quality_preset: string;
  gop_size: number;
}

export interface DecoderConfig {
  id: string;
  buffer_size: number;
  hardware_acceleration: boolean;
  thread_count: number;
  output_format: string;
  deinterlace: boolean;
  color_space: string;
}

export interface SystemHealth {
  health_score: number;
  status: string;
  total_cameras: number;
  active_cameras: number;
  error_cameras: number;
  uptime_percentage: number;
}

export interface SystemStatistics {
  total_cameras: number;
  status_distribution: Record<string, number>;
  region_distribution: Record<string, number>;
  clarity_statistics: {
    min: number;
    max: number;
    average: number;
  };
  usage_statistics: {
    average_bandwidth_mbps: number;
    average_storage_gb: number;
  };
}

export interface RegionComparison {
  region: string;
  camera_count: number;
  average_clarity: number;
  average_bandwidth_mbps: number;
  average_storage_gb: number;
  active_cameras: number;
  uptime_percentage: number;
}

export interface OptimizationSuggestion {
  camera_id: string;
  location: string;
  region: string;
  current_bandwidth_mbps: number;
  current_clarity: number;
  suggestion: string;
  potential_savings_mbps?: number;
  estimated_improvement?: string;
}

export interface QueryRequest {
  query: string;
  include_metadata?: boolean;
}

export interface QueryResponse {
  response: string;
  query_type?: string;
  execution_time?: number;
  metadata?: Record<string, any>;
}

export interface PerformanceAnalysis {
  clarity_analysis: {
    mean: number;
    median: number;
    std_dev: number;
    min: number;
    max: number;
  };
  bandwidth_analysis: {
    mean_mbps: number;
    median_mbps: number;
    total_mbps: number;
  };
  storage_analysis: {
    mean_gb: number;
    median_gb: number;
    total_gb: number;
  };
  sample_size: number;
}

export interface ConfigAnalysis {
  config_id: string;
  resolution?: string;
  codec?: string;
  bitrate_kbps?: number;
  output_format?: string;
  hardware_acceleration?: boolean;
  thread_count?: number;
  usage_count: number;
  average_clarity: number;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface FilterOptions {
  region?: string;
  status?: string;
  min_clarity?: number;
  max_clarity?: number;
  location?: string;
  limit?: number;
}
