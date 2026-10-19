import React from 'react';

/** Props for the NotificationBell component */
interface NotificationBellProps {
  /** The number of unread notifications */
  unreadCount: number;
}

/**
 * NotificationBell component displays a bell icon with an unread count badge.
 */
export const NotificationBell: React.FC<NotificationBellProps> = ({ unreadCount }) => {
  return (
    <div className="relative" aria-label={`${unreadCount} unread notifications`}>
      <span aria-hidden="true">🔔</span>
      {/* Only show the badge if there are unread notifications */}
      {unreadCount > 0 && (
        <span className="absolute -top-1 -right-1 rounded-full bg-red-500 px-1.5 text-xs text-white">
          {unreadCount}
        </span>
      )}
    </div>
  );
};
