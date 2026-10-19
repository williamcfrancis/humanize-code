import type { User } from './types';

/**
 * Collects the IDs of all active users, skipping any inactive ones.
 * @param users - The list of users to filter.
 * @returns The IDs of the active users.
 */
export function collectActiveUserIds(users: User[]): string[] {
  // Initialize the result array
  const activeUserIds: string[] = [];

  // Iterate through each user
  users.forEach((user) => {
    // Skip inactive users
    if (!user.active) {
      return;
    }
    // Add the active user's ID to the result
    activeUserIds.push(user.id);
  });

  // Return the collected IDs
  return activeUserIds;
}
