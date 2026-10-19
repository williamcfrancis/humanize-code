import React from 'react';
import type { SubscriptionStatus } from '../types';

/** Props for the StatusBadge component */
interface StatusBadgeProps {
  /** The subscription status to display */
  status: SubscriptionStatus;
}

/** Mapping of subscription statuses to their Tailwind CSS classes */
const STATUS_BADGE_STYLES: Record<SubscriptionStatus, string> = {
  active: 'bg-green-100 text-green-800',
  paused: 'bg-yellow-100 text-yellow-800',
  cancelled: 'bg-red-100 text-red-800',
};

/** Mapping of subscription statuses to their display labels */
const STATUS_BADGE_LABELS: Record<SubscriptionStatus, string> = {
  active: 'Active',
  paused: 'Paused',
  cancelled: 'Cancelled',
};

/**
 * StatusBadge component displays the subscription status as a colored badge.
 */
export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  // Get the styles and the label for the current status
  const badgeStyles = STATUS_BADGE_STYLES[status];
  const badgeLabel = STATUS_BADGE_LABELS[status];

  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${badgeStyles}`}>
      {badgeLabel}
    </span>
  );
};
