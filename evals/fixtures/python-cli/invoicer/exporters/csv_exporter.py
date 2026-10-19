"""CSV exporter for invoices."""

import csv
from typing import List

from invoicer.exporters.registry import register_exporter
from invoicer.models import LineItem


@register_exporter("csv")
def export_invoice_to_csv(output_path: str, invoice_id: str, line_items: List[LineItem], total: float) -> None:
    """
    Export the invoice to a CSV file.

    Args:
        output_path (str): The path of the CSV file to write.
        invoice_id (str): The ID of the invoice.
        line_items (List[LineItem]): The line items to include.
        total (float): The invoice total.
    """
    # Open the output file for writing
    with open(output_path, "w", newline="", encoding="utf-8") as csv_file_handle:
        # Create a CSV writer for the file
        csv_writer = csv.writer(csv_file_handle)

        # Write the header row
        csv_writer.writerow(["invoice_id", "description", "unit_price", "quantity", "line_total"])

        # Write each line item as a row
        for line_item in line_items:
            line_total = line_item.unit_price * line_item.quantity
            csv_writer.writerow(
                [invoice_id, line_item.description, f"{line_item.unit_price:.2f}", line_item.quantity, f"{line_total:.2f}"]
            )

        # Write the total row
        csv_writer.writerow([invoice_id, "TOTAL", "", "", f"{total:.2f}"])
