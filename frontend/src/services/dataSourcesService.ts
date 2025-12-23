/**
 * Data sources service - integrates with backend API
 */

import apiClient from './api';
import type { DataSource } from '../types/api';
import type { DataSourcesResponse, TriggerDataCollectionResponse } from '../types/api';

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

/**
 * Trigger data collection for a specific data source
 * @param sourceId - ID of the data source to collect data from
 * @returns Promise resolving to TriggerDataCollectionResponse
 * @throws Error if API request fails
 */
export const triggerDataCollection = async (sourceId: number): Promise<TriggerDataCollectionResponse> => {
  try {
    const response = await apiClient.post<TriggerDataCollectionResponse>(`/api/data-sources/${sourceId}/collect`);
    return response.data;
  } catch (error) {
    console.error('Error triggering data collection:', error);
    throw error;
  }
};
