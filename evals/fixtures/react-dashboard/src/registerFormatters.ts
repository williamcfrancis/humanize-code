// ==========================================
// Register Default Formatters
// ==========================================
import { registerFormatter } from './lib/formatRegistry';

// Register the currency formatter for displaying monetary values
registerFormatter('currency', (value: number): string =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value),
);

// Register the percentage formatter for displaying ratios
registerFormatter('percent', (value: number): string => `${(value * 100).toFixed(1)}%`);

// Register the compact number formatter for displaying large numbers
registerFormatter('compact', (value: number): string =>
  new Intl.NumberFormat('en-US', { notation: 'compact' }).format(value),
);
