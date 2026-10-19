// Import and register the default value formatters
import './registerFormatters';

import React from 'react';
import { Dashboard } from './components/Dashboard';
import type { DashboardApi, DashboardResult } from './types';

/** Props for the App component */
interface AppProps {
  /** The ID of the current user */
  userId: string;
  /** The API client used to load data */
  api?: DashboardApi;
  /** Initial data used for server-side rendering */
  initialData?: DashboardResult;
}

/**
 * App component - the root component of the dashboard application.
 */
export const App: React.FC<AppProps> = ({ userId, api, initialData }) => {
  return <Dashboard userId={userId} api={api} initialData={initialData} />;
};
