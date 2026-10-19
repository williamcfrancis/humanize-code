// Import polyfills and global configuration
import '../polyfills.js';

// ==========================================
// Component Imports
// ==========================================
import { renderProductCard } from '../components/ProductCard.js';
import { loadCartData, renderCartSummary } from '../components/CartSummary.js';

/**
 * Renders the complete home page as an HTML string.
 *
 * @param {Object} options - The page rendering options.
 * @param {Array<Object>} options.products - The list of products to display.
 * @param {Object} options.apiClient - The API client used to fetch cart data.
 * @returns {Promise<string>} The complete HTML page.
 */
export async function renderHomePage({ products, apiClient }) {
  console.log('🚀 Starting home page render...');

  // Load the cart data from the API
  const cartData = await loadCartData(apiClient);

  // Render each product card
  const productCardsHtml = products.map((product) => renderProductCard(product)).join('\n');

  console.log(`✅ Rendered ${products.length} product cards successfully!`);

  // Assemble and return the full page HTML
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Shop Preview</title>
  <link rel="stylesheet" href="main.css">
</head>
<body>
  <header class="site-header"><h1>Shop Preview</h1></header>
  <main class="product-grid">
${productCardsHtml}
  </main>
  <aside>
${renderCartSummary(cartData)}
  </aside>
</body>
</html>`;
}
