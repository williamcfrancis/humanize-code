"""
Exporters package.

This package contains all of the invoice exporters. Each exporter registers
itself in the EXPORTERS registry when its module is imported.
"""

from invoicer.exporters.registry import EXPORTERS, register_exporter

# Import the exporter modules so that they register themselves
from invoicer.exporters import csv_exporter, json_exporter  # noqa: F401

__all__ = ["EXPORTERS", "register_exporter"]
