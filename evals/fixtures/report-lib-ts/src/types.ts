/**
 * Shared type definitions for the reporting library.
 */

/** Represents a user record returned by the API */
export interface User {
  /** The unique identifier of the user */
  id: string;
  /** The email address of the user */
  email: string;
  /** The optional nickname of the user */
  nickname?: string;
  /** Whether the user account is active */
  active: boolean;
}

/** Represents a normalized user record used in reports */
export interface NormalizedUserRecord {
  /** The unique identifier of the user */
  id: string;
  /** The display name of the user */
  name: string;
}

/** Represents the summary of all users */
export interface UserSummary {
  /** The list of normalized user records */
  normalizedUserRecords: NormalizedUserRecord[];
  /** The total number of users */
  totalUserCount: number;
}

/** Represents the options for exporting users */
export interface ExportOptions {
  /** The export format (for example 'csv', 'json' or 'legacy-csv') */
  format: string;
  /** Whether to include debug information in the export metadata */
  includeDebugInfo?: boolean;
}

/** Represents the metadata attached to every export */
export type ExportMetadata = Record<string, string | number | boolean | undefined>;

/** Represents a serializer function that turns users into text */
export type Serializer = (users: User[], metadata: ExportMetadata) => string;
