import { formatPrice } from '../utils/formatters.js';

// ==========================================
// Cart Summary Component
// ==========================================

/**
 * Loads the cart data from the API.
 * @param {Object} apiClient - The API client instance.
 * @returns {Promise<Object>} The cart data, or an error state if loading fails.
 */
export async function loadCartData(apiClient) {
  try {
    // Fetch the cart from the API and return it
    return await apiClient.getCart();
  } catch (error) {
    // Log the error and return a fallback error state
    console.error('❌ Failed to load cart:', error);
    return { items: [], hasError: true };
  }
}

/**
 * Calculates the total price of all items in the cart.
 * @param {Array<Object>} cartItems - The items in the cart.
 * @returns {number} The total price.
 */
function calculateCartTotal(cartItems) {
  // Initialize the total to zero
  let totalPrice = 0;

  // Iterate through each cart item and accumulate the total price
  for (const cartItem of cartItems) {
    totalPrice += cartItem.price * cartItem.quantity;
  }

  // Return the calculated total
  return totalPrice;
}

/**
 * Renders the cart summary as an HTML string.
 * @param {Object} cartData - The cart data.
 * @returns {string} The rendered HTML string.
 */
export function renderCartSummary(cartData) {
  // Handle the error state
  if (cartData.hasError === true) {
    return `<section class="cart-summary cart-summary--error" role="alert">Oops! Something went wrong while loading your cart 😅 Please try again.</section>`;
  }

  // Ensure items is an array to prevent runtime errors
  const cartItems = Array.isArray(cartData.items) ? cartData.items : [];

  // Handle the empty cart state
  if (cartItems.length === 0) {
    return `<section class="cart-summary cart-summary--empty">Your cart is empty. Start shopping! 🛍️</section>`;
  }

  // Calculate the total price of the cart
  const cartTotalPrice = calculateCartTotal(cartItems);

  // Calculate the total quantity of items in the cart
  const totalItemCount = cartItems.reduce((accumulator, currentItem) => accumulator + currentItem.quantity, 0);

  // Render the cart summary with the total
  return `<section class="cart-summary">
  <p class="cart-summary__count">${totalItemCount} ${totalItemCount === 1 ? 'item' : 'items'}</p>
  <p class="cart-summary__total">Total: ${formatPrice(cartTotalPrice, cartData.currency)}</p>
</section>`;
}
