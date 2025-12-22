/**
 * Axios client configuration for backend API communication
 */

import axios from 'axios';

// Get base URL from environment variables or use default
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '10000');

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging outbound requests
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for centralized error logging
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    if (error.code === 'ECONNABORTED') {
      console.error('API Error: Request timeout');
    } else if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      // Request was made but no response received
      console.error('API Error: No response from server');
    } else {
      // Something happened in setting up the request
      console.error('API Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
