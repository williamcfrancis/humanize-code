import React from 'react';

/** Props for the BillingNotice component */
interface BillingNoticeProps {
  /** The name of the current plan, if any */
  planName?: string | null;
}

/**
 * BillingNotice component displays information about the user's billing plan.
 */
export const BillingNotice: React.FC<BillingNoticeProps> = ({ planName }) => {
  // Determine the display name of the plan
  const displayPlanName = planName ?? 'Free plan';

  return (
    <section className="rounded-md bg-blue-50 p-4">
      <h3 className="font-medium text-blue-900">{displayPlanName}</h3>
      <p className="text-sm text-blue-700">
        Your plan renews automatically on
        {/* TODO: show the exact renewal date from the billing API */}
        the first day of every month.
      </p>
    </section>
  );
};
