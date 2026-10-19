/**
 * Utility functions for formatting values for display in the UI.
 * This module provides a comprehensive set of robust formatting helpers.
 */

// ==========================================
// Constants
// ==========================================

/** Default currency code used when none is provided */
const DEFAULT_CURRENCY_CODE = 'USD';

/** Fallback text displayed when a price cannot be determined */
const PRICE_UNAVAILABLE_TEXT = 'Price unavailable';

// ==========================================
// Price Formatting
// ==========================================

/**
 * Formats a numeric price into a localized currency string.
 *
 * @param {number} amount - The numeric amount to format.
 * @param {string} [currencyCode='USD'] - The ISO 4217 currency code.
 * @returns {string} The formatted price string.
 */
export function formatPrice(amount, currencyCode = DEFAULT_CURRENCY_CODE) {
  // Validate that the amount is a valid number before formatting
  if (typeof amount !== 'number' || Number.isNaN(amount)) {
    console.warn('⚠️ formatPrice received an invalid amount:', amount);
    return PRICE_UNAVAILABLE_TEXT;
  }

  try {
    // Get the current application locale, falling back to en-US
    const currentLocale = globalThis.__APP_LOCALE__ || 'en-US';

    // Create a new number formatter for the given currency
    const currencyFormatter = new Intl.NumberFormat(currentLocale, {
      style: 'currency',
      currency: currencyCode,
    });

    // Format the amount and return the result
    const formattedPriceString = currencyFormatter.format(amount);
    return formattedPriceString;
  } catch (error) {
    // Handle invalid currency codes gracefully
    console.error('❌ Error formatting price:', error);
    return `${amount.toFixed(2)} ${currencyCode}`;
  }
}

// ==========================================
// Rating Formatting
// ==========================================

/**
 * Formats a rating value into a star string.
 *
 * @param {number} rating - The rating value between 0 and 5.
 * @returns {string} A string of star characters.
 */
export function formatRatingStars(rating) {
  // Ensure the rating is within the valid range
  const clampedRatingValue = Math.max(0, Math.min(5, Math.round(rating)));

  // Build the star string
  const filledStars = '★'.repeat(clampedRatingValue);
  const emptyStars = '☆'.repeat(5 - clampedRatingValue);

  // Return the combined star string
  const starString = filledStars + emptyStars;
  return starString;
}
