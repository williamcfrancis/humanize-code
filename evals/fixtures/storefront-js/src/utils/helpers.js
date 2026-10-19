// ==========================================
// Helper Utilities
// ==========================================

/**
 * StringHelper class provides static utility methods for string manipulation.
 */
export class StringHelper {
  /**
   * Capitalizes the first letter of a string.
   * @param {string} inputString - The string to capitalize.
   * @returns {string} The capitalized string.
   */
  static capitalizeFirstLetter(inputString) {
    // Check if the input string is empty or not a string
    if (!inputString || typeof inputString !== 'string') {
      return '';
    }
    // Capitalize the first character and concatenate with the rest of the string
    return inputString.charAt(0).toUpperCase() + inputString.slice(1);
  }

  /**
   * Truncates a string to the specified maximum length.
   * @param {string} text - The text to truncate.
   * @param {number} maxLength - The maximum allowed length.
   * @returns {string} The truncated string with an ellipsis if needed.
   */
  static truncateText(text, maxLength) {
    // Return the original text if it is within the limit
    if (text.length <= maxLength) {
      return text;
    }
    // Truncate and append ellipsis
    return text.slice(0, maxLength).trimEnd() + '…';
  }
}

/**
 * Escapes HTML special characters to prevent XSS attacks.
 * @param {string} unsafeString - The string to escape.
 * @returns {string} The escaped string, safe for HTML insertion.
 */
export function escapeHtmlEnhanced(unsafeString) {
  // Convert the input to a string to handle non-string values
  const stringValue = String(unsafeString);

  // Replace each special character with its corresponding HTML entity
  return stringValue
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/**
 * Wrapper function to get the display name for a product.
 * @param {Object} product - The product object.
 * @returns {string} The display name.
 */
export function getProductDisplayNameNew(product) {
  return StringHelper.capitalizeFirstLetter(product.name);
}
