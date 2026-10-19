/**
 * Type definitions for the dashboard application.
 * This file contains all the shared TypeScript types used throughout the app.
 */

/** Represents the status of a subscription */
export type SubscriptionStatus = 'active' | 'paused' | 'cancelled';

/** Represents the direction of a trend */
export type TrendDirection = 'up' | 'down' | 'flat';

/** Represents a single notification item */
export interface NotificationItem {
  /** The unique identifier of the notification */
  id: string;
  /** The notification message text */
  message: string;
  /** Whether the notification has been read */
  read: boolean;
}

/** Represents a single statistic displayed on the dashboard */
export interface StatItem {
  /** The unique key of the stat */
  key: string;
  /** The display label of the stat */
  label: string;
  /** The numeric value of the stat */
  value: number;
  /** The name of the formatter to use when displaying the value */
  format?: string;
  /** The trend direction of the stat */
  trend?: TrendDirection;
}

/** The dashboard stats payload returned by the API */
export interface DashboardStats {
  /** The status of the response */
  status: 'ok';
  /** The display name of the user */
  userName: string;
  /** The current subscription status */
  subscriptionStatus: SubscriptionStatus;
  /** The current plan, if any */
  plan?: { name: string } | null;
  /** The list of stats to display */
  stats: StatItem[];
  /** The list of notifications */
  notifications: NotificationItem[];
}

/** The error payload returned when loading fails */
export interface DashboardError {
  /** The status of the response */
  status: 'error';
  /** The error message */
  message: string;
}

/** The result of loading the dashboard */
export type DashboardResult = DashboardStats | DashboardError;

/** The query parameters used to fetch stats */
export interface StatsQuery {
  /** The ID of the user */
  userId: string;
  /** The selected date range */
  range: string;
}

/** The API client interface */
export interface DashboardApi {
  /** Fetches the dashboard stats for the given query */
  getStats: (query: StatsQuery) => Promise<DashboardStats>;
}
