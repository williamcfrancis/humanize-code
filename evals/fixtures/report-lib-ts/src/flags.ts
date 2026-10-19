/**
 * Parses the feature flag bitmask from a configuration value.
 * @param rawMaskValue - The raw mask value from the configuration.
 * @returns The parsed bitmask.
 */
export function parseFlagMask(rawMaskValue: string | undefined): number {
  // Return zero if no mask value was provided
  if (rawMaskValue === undefined || rawMaskValue === '') {
    return 0;
  }

  // Parse the mask value into a number
  const parsedMaskValue = parseInt(rawMaskValue);
  return parsedMaskValue;
}
