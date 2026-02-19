"""
Compatibility layer for backward compatibility.

This module provides backward compatibility for code that imports from multi_csv_converter.
New code should import from okfn_iati.activities instead.

The original large file has been refactored into a more modular structure:
- okfn_iati/activities/base.py (main converter class)
- okfn_iati/activities/process_xml/extractors.py (XML to CSV extraction functions)
- okfn_iati/activities/process_csv/builders.py (CSV to XML building functions)
"""

# Re-export from the new location for backward compatibility
from .activities import IatiMultiCsvConverter

__all__ = ['IatiMultiCsvConverter']
