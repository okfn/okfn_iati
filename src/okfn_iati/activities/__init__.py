"""
IATI Activities module - Multi-CSV converter for IATI data.

This module provides functionality to convert between IATI XML and multiple related CSV files
that preserve the hierarchical structure while remaining user-friendly for editing in Excel
or other tools.

LIMITATIONS:
- Custom namespace elements (e.g., USAID's usg:treasury-account) are NOT preserved
  during XML -> CSV -> XML conversion. These are organization-specific extensions
  that don't fit into the standard CSV structure.
- If you need to preserve custom elements, use XML-to-XML transformations instead.
"""

from .base import IatiMultiCsvConverter

__all__ = ['IatiMultiCsvConverter']
