/**
 * Data sources service - integrates with backend API
 */

import apiClient from './api';
import type { DataSource } from '../types/api';
import type { DataSourcesResponse } from '../types/api';

// Export DataSource type for component usage
export type { DataSource };

/**
 * Fetch all data sources from backend API
 * @returns Promise resolving to array of DataSource objects
 * @throws Error if API request fails
 */
export const getDataSources = async (): Promise<DataSource[]> => {
  try {
    const response = await apiClient.get<DataSourcesResponse>('/api/data-sources');
    return response.data.data;
  } catch (error) {
    console.error('Error fetching data sources:', error);
    throw error;
  }
};
