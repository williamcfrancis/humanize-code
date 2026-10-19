"""
Invoicer: generate invoices from order files.

Reads an order JSON file, adds the standard handling fee, applies an optional
discount, and writes the invoice in the requested format.
"""

import argparse
import json
from typing import Any, Dict, List, Optional

from invoicer.exporters import EXPORTERS
from invoicer.models import LineItem
from invoicer.pricing import PriceCalculator


def parse_arguments(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse the command-line arguments.

    Args:
        argv (Optional[List[str]]): The list of command-line arguments.

    Returns:
        argparse.Namespace: The parsed command-line arguments.
    """
    # Create the argument parser, using the module docstring as the description
    parser = argparse.ArgumentParser(
        prog="invoicer",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Add the command-line arguments
    parser.add_argument("order_file", help="path to the order JSON file")
    parser.add_argument("--format", choices=sorted(EXPORTERS), default="csv", help="output format")
    parser.add_argument("--output", required=True, help="path of the invoice file to write")
    parser.add_argument("--discount", type=float, default=None, help="discount percentage to apply")

    # Parse and return the arguments
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for the Invoicer command-line interface.

    Args:
        argv (Optional[List[str]]): The list of command-line arguments.

    Returns:
        int: The exit code (0 for success, 1 for failure).
    """
    # Parse the command-line arguments
    arguments = parse_arguments(argv)

    try:
        # Load the order data from the JSON file
        with open(arguments.order_file, encoding="utf-8") as order_file_handle:
            order_data: Dict[str, Any] = json.load(order_file_handle)

        # Convert the raw items into LineItem objects
        line_items: List[LineItem] = [LineItem(**raw_item) for raw_item in order_data["items"]]

        # Calculate the loyalty points on the merchandise only, before any fees are added
        merchandise_subtotal = PriceCalculator.calculate_order_subtotal(line_items)
        loyalty_points = PriceCalculator.calculate_loyalty_points(merchandise_subtotal)

        # Add the default fees to the line items
        all_line_items = PriceCalculator.add_default_fees(line_items)

        # Calculate the subtotal and the discounted total
        subtotal = PriceCalculator.calculate_order_subtotal(all_line_items)
        total = PriceCalculator.apply_discount(subtotal, discount_percentage=arguments.discount)

        # Export the invoice using the selected exporter
        exporter_function = EXPORTERS[arguments.format]
        exporter_function(arguments.output, order_data["invoice_id"], all_line_items, total)

        # Print a summary for the user
        print(f"✅ Invoice {order_data['invoice_id']} written to {arguments.output}")
        print(f"📦 {len(line_items)} line items, total ${total:.2f}, {loyalty_points} loyalty points")
        return 0
    except Exception as e:
        # Print the error message and return a non-zero exit code
        print(f"❌ An error occurred: {e}")
        return 1
