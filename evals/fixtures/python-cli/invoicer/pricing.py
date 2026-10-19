"""
Pricing module for the Invoicer application.

This module provides comprehensive pricing utilities, including subtotal
calculation, discount handling, default fees, and loyalty point computation.
"""

import logging
from typing import List, Optional

from invoicer.models import LineItem

# Configure logging for the pricing module
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ==========================================
# Constants
# ==========================================

# Number of loyalty points awarded per whole currency unit spent
LOYALTY_POINTS_PER_UNIT: int = 10

# Default fees that are added to every invoice
DEFAULT_FEES: List[LineItem] = [LineItem(description="Handling fee", unit_price=1.0, quantity=1)]


class PriceCalculator:
    """
    A utility class responsible for calculating prices, fees, and loyalty points.

    This class provides static methods for computing invoice totals with
    optional discounts and for determining the loyalty points earned.
    """

    @staticmethod
    def calculate_order_subtotal(line_items: List[LineItem]) -> float:
        """
        Calculate the subtotal for a list of line items.

        Args:
            line_items (List[LineItem]): The line items to total.

        Returns:
            float: The computed subtotal.
        """
        # Initialize the running subtotal
        running_subtotal: float = 0.0

        # Iterate over each line item and accumulate unit_price * quantity
        for line_item in line_items:
            running_subtotal += line_item.unit_price * line_item.quantity

        # Return the final subtotal
        return running_subtotal

    @staticmethod
    def apply_discount(subtotal: float, discount_percentage: Optional[float] = None) -> float:
        """
        Apply an optional percentage discount to a subtotal.

        Args:
            subtotal (float): The subtotal before the discount.
            discount_percentage (Optional[float]): The discount percentage (0-100).

        Returns:
            float: The subtotal after the discount has been applied.
        """
        try:
            # Only apply the discount if a positive percentage was provided
            if discount_percentage is not None and discount_percentage > 0:
                discount_amount: float = subtotal * (discount_percentage / 100)
                discounted_subtotal: float = subtotal - discount_amount
                logger.info(f"✅ Applied {discount_percentage}% discount successfully!")
                return discounted_subtotal

            # Return the original subtotal if no discount applies
            return subtotal
        except Exception as e:
            # Log the error and re-raise it so the caller can handle it
            logger.error(f"An error occurred while applying the discount: {str(e)}")
            raise

    @staticmethod
    def add_default_fees(line_items: List[LineItem]) -> List[LineItem]:
        """
        Add the default fees to a list of line items.

        Args:
            line_items (List[LineItem]): The original line items.

        Returns:
            List[LineItem]: The line items including the default fees.
        """
        # Create the full list of line items, including the default fees
        all_line_items = line_items
        all_line_items += DEFAULT_FEES

        # Return the complete list of line items
        return all_line_items

    @staticmethod
    def calculate_loyalty_points(subtotal: float) -> int:
        """
        Calculate the loyalty points earned for a given subtotal.

        Args:
            subtotal (float): The invoice subtotal.

        Returns:
            int: The number of loyalty points earned.
        """
        # Validate the subtotal value
        if subtotal is None:
            raise ValueError("Subtotal cannot be None")

        # Award points for each whole currency unit spent
        whole_units_spent: int = int(subtotal)
        loyalty_points: int = whole_units_spent * LOYALTY_POINTS_PER_UNIT
        return loyalty_points


# Example usage
if __name__ == "__main__":
    example_items = [LineItem(description="Widget", unit_price=9.99, quantity=3)]
    example_subtotal = PriceCalculator.calculate_order_subtotal(example_items)
    print(f"Example subtotal: {example_subtotal}")
