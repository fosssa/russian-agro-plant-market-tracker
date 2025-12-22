/**
 * TypeScript interfaces matching backend Pydantic models
 */

// DataSource model - matches backend data_source.py
export interface DataSource {
  id: number;
  name: string;
  location: string;
  lastRunStatus: boolean;
  lastRunDate: string;
}

// Response wrapper for data sources list
export interface DataSourcesResponse {
  data: DataSource[];
  total: number;
}

// FilterOption model - matches backend visualization.py
export interface FilterOption {
  value: string | number;
  label: string;
}

// Response wrapper for filter options list
export interface FilterOptionsResponse {
  data: FilterOption[];
  total: number;
}

// ChartData model - matches backend visualization.py
export interface ChartData {
  xAxisData: string[];
  seriesData: number[];
  seriesName: string;
}
