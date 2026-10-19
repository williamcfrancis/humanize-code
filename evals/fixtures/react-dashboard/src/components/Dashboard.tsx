import React, { useState } from 'react';
import { useDashboardData } from '../hooks/useDashboardData';
import { useLocalStorage } from '../hooks/useLocalStorage';
import { StatusBadge } from './StatusBadge';
import { StatCard } from './StatCard';
import { NotificationBell } from './NotificationBell';
import { BillingNotice } from './BillingNotice';
import type { DashboardApi, DashboardResult } from '../types';

/** Props for the Dashboard component */
interface DashboardProps {
  /** The ID of the current user */
  userId: string;
  /** The API client used to load data */
  api?: DashboardApi;
  /** Initial data used for server-side rendering */
  initialData?: DashboardResult;
}

/** Available date range options */
const DATE_RANGE_OPTIONS: string[] = ['7d', '30d', '90d'];

/**
 * Dashboard component displays an overview of the user's account.
 */
export const Dashboard: React.FC<DashboardProps> = ({ userId, api, initialData }) => {
  // Persist the selected date range in localStorage
  const [selectedRange, setSelectedRange] = useLocalStorage<string>('dashboard-range', '30d');

  // State to track whether the notifications panel is expanded
  const [isNotificationsPanelOpen, setIsNotificationsPanelOpen] = useState<boolean>(false);

  // Load the dashboard data
  const dashboardResult = useDashboardData(api, userId, selectedRange, initialData);

  // Render the loading state
  if (dashboardResult === null) {
    return <div className="p-6 text-gray-500">Loading your dashboard...</div>;
  }

  // Render the error state
  if (dashboardResult.status === 'error') {
    return (
      <div className="p-6 text-red-600" role="alert">
        Oops! Something went wrong 😕 {dashboardResult.message}
      </div>
    );
  }

  // Calculate the number of unread notifications
  const unreadNotificationsCount = dashboardResult.notifications.filter((notification) => !notification.read).length;

  return (
    <main className="mx-auto max-w-5xl p-6">
      {/* ===== Header Section ===== */}
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Welcome back, {dashboardResult.userName}!</h1>
          <StatusBadge status={dashboardResult.subscriptionStatus} />
        </div>
        <button
          type="button"
          className="rounded p-2 hover:bg-gray-100"
          onClick={() => setIsNotificationsPanelOpen(!isNotificationsPanelOpen)}
          aria-expanded={isNotificationsPanelOpen}
        >
          <NotificationBell unreadCount={unreadNotificationsCount} />
        </button>
      </header>

      {/* ===== Date Range Selector ===== */}
      <div className="mb-4 flex gap-2" role="group" aria-label="Date range">
        {DATE_RANGE_OPTIONS.map((rangeOption) => (
          <button
            key={rangeOption}
            type="button"
            className={rangeOption === selectedRange ? 'rounded bg-gray-900 px-3 py-1 text-white' : 'rounded px-3 py-1 text-gray-700'}
            onClick={() => setSelectedRange(rangeOption)}
          >
            {rangeOption}
          </button>
        ))}
      </div>

      {/* ===== Stats Grid ===== */}
      <section className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {dashboardResult.stats.map((statItem) => (
          <StatCard
            key={statItem.key}
            label={statItem.label}
            value={statItem.value}
            format={statItem.format}
            trend={statItem.trend}
          />
        ))}
      </section>

      {/* ===== Notifications Panel ===== */}
      {isNotificationsPanelOpen && (
        <section className="mt-6" aria-label="Notifications">
          {dashboardResult.notifications.length === 0 ? (
            <p className="text-gray-500">🎉 You're all caught up! No new notifications.</p>
          ) : (
            <ul className="divide-y">
              {dashboardResult.notifications.map((notificationItem) => (
                <li key={notificationItem.id} className={notificationItem.read ? 'py-2 text-gray-500' : 'py-2 font-medium'}>
                  {notificationItem.message}
                </li>
              ))}
            </ul>
          )}
        </section>
      )}

      {/* ===== Billing Section ===== */}
      <BillingNotice planName={dashboardResult.plan?.name} />
    </main>
  );
};
