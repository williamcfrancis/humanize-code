// ==========================================
// Formatter Registry
// ==========================================

/** Type definition for a value formatter function */
type FormatterFunction = (value: number) => string;

/** Internal registry map that stores all registered formatters */
const formatterRegistryMap: Map<string, FormatterFunction> = new Map<string, FormatterFunction>();

/**
 * Registers a formatter function under the given name.
 * @param formatterName - The unique name of the formatter.
 * @param formatterFunction - The formatter function to register.
 */
export function registerFormatter(formatterName: string, formatterFunction: FormatterFunction): void {
  formatterRegistryMap.set(formatterName, formatterFunction);
}

/**
 * Formats a value using a registered formatter.
 * Falls back to the plain string representation if the formatter is not found.
 * @param formatterName - The name of the formatter to use.
 * @param value - The numeric value to format.
 * @returns The formatted string.
 */
export function formatValue(formatterName: string | undefined, value: number): string {
  // Check if a formatter name was provided
  if (formatterName === undefined) {
    return String(value);
  }

  // Retrieve the formatter from the registry
  const formatterFunction = formatterRegistryMap.get(formatterName);

  // Return the formatted value, or fall back to the string representation
  if (formatterFunction !== undefined) {
    return formatterFunction(value);
  } else {
    return String(value);
  }
}
