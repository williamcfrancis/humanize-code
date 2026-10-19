import { registerSerializer } from './registry';
import type { ExportMetadata, User } from './types';

/**
 * Formats the export metadata as comment lines.
 * @param metadata - The export metadata.
 * @returns The metadata lines.
 */
function formatMetadataLines(metadata: ExportMetadata): string[] {
  // Convert each metadata entry into a "# key=value" line
  return Object.entries(metadata).map(([metadataKey, metadataValue]) => `# ${metadataKey}=${metadataValue}`);
}

// Register the CSV serializer
registerSerializer('csv', (users: User[], metadata: ExportMetadata): string => {
  const headerLine = 'id,email,active';
  const rowLines = users.map((user) => `${user.id},${user.email},${user.active}`);
  return [...formatMetadataLines(metadata), headerLine, ...rowLines].join('\n');
});

// Register the JSON serializer
registerSerializer('json', (users: User[], metadata: ExportMetadata): string => {
  return JSON.stringify({ metadata, users });
});
