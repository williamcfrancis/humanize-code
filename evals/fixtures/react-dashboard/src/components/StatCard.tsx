import React from 'react';
import { formatValue } from '../lib/formatRegistry';
import type { TrendDirection } from '../types';

/** Props for the StatCard component */
interface StatCardProps {
  /** The label displayed above the value */
  label: string;
  /** The numeric value to display */
  value: number;
  /** The name of the formatter to use */
  format?: string;
  /** The trend direction of the stat */
  trend?: TrendDirection;
}

/** Mapping of trend directions to their indicator icons */
const TREND_INDICATOR_ICONS: Record<TrendDirection, string> = {
  up: '▲',
  down: '▼',
  flat: '—',
};

/**
 * StatCard component displays a single statistic along with its trend.
 */
export const StatCard: React.FC<StatCardProps> = ({ label, value, format = 'compact', trend = 'flat' }) => {
  // Format the value using the registered formatter
  const formattedValue = formatValue(format, value);

  // Get the trend indicator icon
  const trendIndicatorIcon = TREND_INDICATOR_ICONS[trend];

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      {/* Stat Label */}
      <p className="text-sm text-gray-500">{label}</p>
      {/* Stat Value and Trend */}
      <p className="mt-1 text-2xl font-semibold text-gray-900">
        {formattedValue} <span className="text-sm">{trendIndicatorIcon}</span>
      </p>
    </div>
  );
};
