/**
 * Visualization service - integrates with backend API for filters and chart data
 */

import apiClient from './api';
import type { FilterOption } from '../types/api';
import type { FilterOptionsResponse } from '../types/api';
import type { ChartData } from '../types/api';

// Export types for component usage
export type { FilterOption, ChartData };

/**
 * Fetch filter options from backend API
 * @param filterType - Type of filter ('source' or 'product')
 * @returns Promise resolving to array of FilterOption objects
 * @throws Error if API request fails or invalid filter type
 */
export const getFilterOptions = async (
  filterType: 'source' | 'product'
): Promise<FilterOption[]> => {
  try {
    const response = await apiClient.get<FilterOptionsResponse>(`/api/filters/${filterType}`);
    return response.data.data;
  } catch (error) {
    console.error(`Error fetching ${filterType} filter options:`, error);
    throw error;
  }
};

/**
 * Fetch chart data from backend API based on selected filters
 * @param sourceId - Selected source filter value
 * @param productId - Selected product filter value
 * @returns Promise resolving to ChartData object
 * @throws Error if API request fails
 */
export const getChartData = async (
  sourceId: string | number,
  productId: string | number
): Promise<ChartData> => {
  try {
    const response = await apiClient.get<ChartData>('/api/chart-data', {
      params: {
        source: sourceId,
        product: productId,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching chart data:', error);
    throw error;
  }
};
