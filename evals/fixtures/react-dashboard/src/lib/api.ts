import type { DashboardApi, DashboardResult, StatsQuery } from '../types';

/**
 * Fetches the dashboard stats from the API with comprehensive error handling.
 * @param api - The API client instance.
 * @param query - The query parameters for the request.
 * @returns A promise that resolves to the dashboard result.
 */
export async function fetchDashboardStats(api: DashboardApi, query: StatsQuery): Promise<DashboardResult> {
  try {
    // Fetch the stats from the API
    return await api.getStats(query);
  } catch (error) {
    // Log the error for debugging purposes
    console.error('❌ Error fetching dashboard stats:', error);
    // Return a structured error result
    return {
      status: 'error',
      message: error instanceof Error ? error.message : 'An unknown error occurred',
    };
  }
}
