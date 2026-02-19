"""
IATI Organisation XML Generator (Legacy Re-exporter).

This module provides backward compatibility by re-exporting classes from the
refactored organisations module. All functionality has been moved to the
organisations subpackage for better modularity and maintainability.

Legacy imports are supported:
    from okfn_iati.organisation_xml_generator import IatiOrganisationXMLGenerator
    from okfn_iati.organisation_xml_generator import IatiOrganisationMultiCsvConverter

New imports are recommended:
    from okfn_iati.organisations import IatiOrganisationXMLGenerator
    from okfn_iati.organisations import IatiOrganisationMultiCsvConverter
"""

# Re-export main classes from new location for backward compatibility
from .organisations import (
    IatiOrganisationXMLGenerator,
    IatiOrganisationMultiCsvConverter,
    OrganisationRecord,
    OrganisationBudget,
    OrganisationExpenditure,
    OrganisationDocument
)

__all__ = [
    "IatiOrganisationXMLGenerator",
    "IatiOrganisationMultiCsvConverter",
    "OrganisationRecord",
    "OrganisationBudget",
    "OrganisationExpenditure",
    "OrganisationDocument"
]
