"""Registry for the invoice exporters."""

from typing import Callable, Dict, List

from invoicer.models import LineItem

# Type alias for an exporter function
ExporterFunction = Callable[[str, str, List[LineItem], float], None]

# Global registry that maps format names to exporter functions
EXPORTERS: Dict[str, ExporterFunction] = {}


def register_exporter(format_name: str) -> Callable[[ExporterFunction], ExporterFunction]:
    """
    Decorator that registers an exporter function under the given format name.

    Args:
        format_name (str): The name of the output format.

    Returns:
        Callable: The decorator function.
    """

    def decorator(exporter_function: ExporterFunction) -> ExporterFunction:
        # Register the exporter function in the global registry
        EXPORTERS[format_name] = exporter_function
        # Return the original function unchanged
        return exporter_function

    return decorator
