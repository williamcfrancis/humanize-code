import { formatPrice, formatRatingStars } from '../utils/formatters.js';
import { StringHelper, escapeHtmlEnhanced, getProductDisplayNameNew } from '../utils/helpers.js';

/** Maximum number of characters to show in the product description */
const MAX_DESCRIPTION_LENGTH = 80;

/**
 * Renders a product card component as an HTML string.
 *
 * @param {Object} product - The product data object.
 * @param {string} product.id - The unique product identifier.
 * @param {string} product.name - The product name.
 * @param {number} product.price - The product price.
 * @param {string} [product.currency] - The currency code.
 * @param {string} [product.description] - The product description.
 * @param {number} [product.rating] - The product rating.
 * @param {number} [product.reviewCount] - The number of reviews.
 * @param {boolean} [product.onSale] - Whether the product is on sale.
 * @param {string} [product.badgeLabel] - Optional badge label.
 * @param {Object} [product.seller] - The seller information.
 * @returns {string} The rendered HTML string.
 */
export function renderProductCard(product) {
  // Get the formatted display name for the product
  const productDisplayName = getProductDisplayNameNew(product);

  // Format the price using the currency formatter
  const formattedPrice = formatPrice(product.price, product.currency);

  // Determine the badge label, defaulting to 'New' if not provided
  const badgeLabelText = product.badgeLabel ?? 'New';

  // Get the seller name with a fallback for missing seller information
  const sellerDisplayName = product.seller?.name ?? 'Marketplace seller';

  // Truncate the description if it exceeds the maximum length
  const truncatedDescription = product.description
    ? StringHelper.truncateText(product.description, MAX_DESCRIPTION_LENGTH)
    : '';

  // Build and return the HTML for the product card
  return `<article class="product-card" data-testid="product-card-${escapeHtmlEnhanced(product.id)}">
  <span class="product-card__badge">${escapeHtmlEnhanced(badgeLabelText)}</span>
  ${product.onSale ? '<span class="product-card__sale">Sale</span>' : ''}
  <h3 class="product-card__title">${escapeHtmlEnhanced(productDisplayName)}</h3>
  <p class="product-card__price">${escapeHtmlEnhanced(formattedPrice)}</p>
  <p class="product-card__rating" aria-label="Rated ${product.rating} out of 5">${formatRatingStars(product.rating)} <span class="product-card__reviews">(${product.reviewCount} reviews)</span></p>
  <p class="product-card__description">${escapeHtmlEnhanced(truncatedDescription)}</p>
  <p class="product-card__seller">Sold by ${escapeHtmlEnhanced(sellerDisplayName)}</p>
  <button class="product-card__button" type="button" aria-label="Add ${escapeHtmlEnhanced(productDisplayName)} to cart">Add to cart 🛒</button>
</article>`;
}
