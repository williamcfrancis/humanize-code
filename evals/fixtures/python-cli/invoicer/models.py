"""
Data models for the Invoicer application.

This module defines the core data structures used throughout the application.
"""

from dataclasses import dataclass


@dataclass
class LineItem:
    """
    Represents a single line item on an invoice.

    Attributes:
        description (str): The description of the line item.
        unit_price (float): The price per unit.
        quantity (int): The number of units.
    """

    description: str
    unit_price: float
    quantity: int
