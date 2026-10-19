// Debug script to test rendering - can be removed later
import { renderProductCard } from './src/components/ProductCard.js';

console.log('🔍 Testing product card render...');
console.log(renderProductCard({ id: 'test', name: 'test product', price: 10 }));
