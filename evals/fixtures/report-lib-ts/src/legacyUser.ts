import { registerSerializer } from './registry';
import type { User } from './types';

/**
 * Represents a user record from the legacy (v1) API.
 */
export class LegacyUser {
  constructor(
    public id: string,
    public legacyDisplayName: string,
  ) {}
}

// Register the legacy CSV serializer used by the old reporting dashboard
registerSerializer('legacy-csv', (users: User[]): string => {
  return users.map((user) => `${user.id};${user.email}`).join('\r\n');
});
