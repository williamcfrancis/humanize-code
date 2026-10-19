import { getSerializer } from './registry';
import type { ExportMetadata, ExportOptions, User } from './types';

/**
 * Exports the users in the requested format.
 * @param users - The users to export.
 * @param options - The export options.
 * @returns The serialized export.
 */
export function exportUsers(users: User[], options: ExportOptions): string {
  // Build the export metadata, including the debug flag only when it is enabled
  const exportMetadata: ExportMetadata = {
    format: options.format,
    count: users.length,
    ...(options.includeDebugInfo ? { debug: true } : {}),
  };

  // Look up the serializer for the requested format
  const serializerFunction = getSerializer(options.format);

  // Throw an error if the format is not supported
  if (serializerFunction === undefined) {
    throw new Error(`Unknown export format: ${options.format}`);
  }

  // Serialize the users and return the result
  return serializerFunction(users, exportMetadata);
}
