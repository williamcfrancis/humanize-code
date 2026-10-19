"""JSON exporter for invoices."""

import json
from typing import Any, Dict, List

from invoicer.exporters.registry import register_exporter
from invoicer.models import LineItem


@register_exporter("json")
def export_invoice_to_json(output_path: str, invoice_id: str, line_items: List[LineItem], total: float) -> None:
    """
    Export the invoice to a JSON file.

    Args:
        output_path (str): The path of the JSON file to write.
        invoice_id (str): The ID of the invoice.
        line_items (List[LineItem]): The line items to include.
        total (float): The invoice total.
    """
    # Build the invoice dictionary
    invoice_data: Dict[str, Any] = {
        "invoice_id": invoice_id,
        "items": [
            {
                "description": line_item.description,
                "unit_price": line_item.unit_price,
                "quantity": line_item.quantity,
            }
            for line_item in line_items
        ],
        "total": round(total, 2),
    }

    # Write the invoice data to the JSON file
    with open(output_path, "w", encoding="utf-8") as json_file_handle:
        json.dump(invoice_data, json_file_handle, indent=2)
