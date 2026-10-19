import { useEffect, useMemo, useState } from 'react';
import { fetchDashboardStats } from '../lib/api';
import type { DashboardApi, DashboardResult, StatsQuery } from '../types';

/**
 * Custom hook that loads the dashboard data for a user.
 * @param api - The API client instance.
 * @param userId - The ID of the user.
 * @param range - The selected date range.
 * @param initialData - Optional initial data, used for server-side rendering.
 * @returns The dashboard result, or null while loading.
 */
export function useDashboardData(
  api: DashboardApi | undefined,
  userId: string,
  range: string,
  initialData?: DashboardResult,
): DashboardResult | null {
  // State to store the dashboard result
  const [dashboardResult, setDashboardResult] = useState<DashboardResult | null>(initialData ?? null);

  // Memoize the query object to keep a stable reference between renders
  const statsQuery = useMemo<StatsQuery>(() => ({ userId, range }), [userId, range]);

  // Fetch the dashboard data whenever the query changes
  useEffect(() => {
    // Skip fetching if no API client was provided
    if (!api) {
      return;
    }

    // Track whether the component is still mounted
    let isComponentMounted = true;

    // Load the data from the API
    fetchDashboardStats(api, statsQuery).then((result) => {
      // Only update the state if the component is still mounted
      if (isComponentMounted) {
        setDashboardResult(result);
      }
    });

    // Cleanup function to prevent state updates after unmount
    return () => {
      isComponentMounted = false;
    };
  }, [api, statsQuery]);

  // Return the current dashboard result
  return dashboardResult;
}
