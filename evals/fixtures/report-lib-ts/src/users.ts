import { LegacyUser } from './legacyUser';
import type { User, UserSummary } from './types';

/**
 * Returns the display name for a user.
 * @param user - The user object.
 * @returns The display name string.
 */
export function getUserDisplayName(user: User): string {
  // Defensive check: the API no longer returns legacy user objects, but handle them just in case
  if (user instanceof LegacyUser) {
    return user.legacyDisplayName;
  }

  // Use the nickname if one is set, otherwise fall back to the email address
  const displayNameValue = user.nickname ? user.nickname : user.email;
  return displayNameValue;
}

/**
 * Builds a summary of all users for the report header.
 * @param users - The list of users.
 * @returns The user summary.
 */
export function buildUserSummary(users: User[]): UserSummary {
  // Normalize all of the user records
  const normalizedUserRecords = users.map((user) => ({ id: user.id, name: getUserDisplayName(user) }));

  // Calculate the total number of users
  const totalUserCount = normalizedUserRecords.length;

  // Return the summary object
  return { normalizedUserRecords, totalUserCount };
}
