"""
Legacy compatibility module for organisation XML/CSV tools.

This module keeps legacy imports and command-line usage working after the
organisation code was moved into ``okfn_iati.organisations``.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

try:
    # Re-export main classes from new location for backward compatibility.
    from okfn_iati.organisations import (
        IatiOrganisationCSVConverter,
        IatiOrganisationMultiCsvConverter,
        IatiOrganisationXMLGenerator,
        OrganisationBudget,
        OrganisationDocument,
        OrganisationExpenditure,
        OrganisationRecord,
    )
except ModuleNotFoundError:
    # Allow running this file directly via ``python src/.../organisation_xml_generator.py``.
    src_root = Path(__file__).resolve().parents[1]
    src_root_str = str(src_root)
    if src_root_str not in sys.path:
        sys.path.insert(0, src_root_str)

    from okfn_iati.organisations import (  # type: ignore[no-redef]
        IatiOrganisationCSVConverter,
        IatiOrganisationMultiCsvConverter,
        IatiOrganisationXMLGenerator,
        OrganisationBudget,
        OrganisationDocument,
        OrganisationExpenditure,
        OrganisationRecord,
    )

__all__ = [
    "IatiOrganisationXMLGenerator",
    "IatiOrganisationCSVConverter",
    "IatiOrganisationMultiCsvConverter",
    "OrganisationRecord",
    "OrganisationBudget",
    "OrganisationExpenditure",
    "OrganisationDocument",
]

logger = logging.getLogger(__name__)


def main() -> int:
    """Command line interface for converting organisation files."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(
        description="Convert between IATI organisation data formats"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    convert_parser = subparsers.add_parser("convert", help="Convert CSV/Excel to IATI XML")
    convert_parser.add_argument("input", help="Input CSV/Excel file or folder")
    convert_parser.add_argument("output", help="Output XML file")
    convert_parser.add_argument(
        "--folder",
        action="store_true",
        help="Process all CSV/Excel files in input folder",
    )

    template_parser = subparsers.add_parser("template", help="Generate a CSV template")
    template_parser.add_argument("output", help="Output template file")
    template_parser.add_argument(
        "--no-examples",
        action="store_true",
        help="Do not include example data",
    )

    multi_template_parser = subparsers.add_parser(
        "multi-template",
        help="Generate multi-CSV templates",
    )
    multi_template_parser.add_argument("output_folder", help="Output folder for CSV templates")
    multi_template_parser.add_argument(
        "--no-examples",
        action="store_true",
        help="Do not include example data",
    )

    xml_to_csv_parser = subparsers.add_parser(
        "xml-to-csv-folder",
        help="Convert organisation XML to CSV folder",
    )
    xml_to_csv_parser.add_argument("input", help="Input XML file")
    xml_to_csv_parser.add_argument("output_folder", help="Output CSV folder")

    csv_to_xml_parser = subparsers.add_parser(
        "csv-folder-to-xml",
        help="Convert organisation CSV folder to XML",
    )
    csv_to_xml_parser.add_argument("input_folder", help="Input CSV folder")
    csv_to_xml_parser.add_argument("output", help="Output XML file")

    validate_parser = subparsers.add_parser("validate", help="Validate organisation data")
    validate_parser.add_argument("input", help="Input CSV/Excel file or folder")
    validate_parser.add_argument(
        "--folder",
        action="store_true",
        help="Process all CSV/Excel files in input folder",
    )

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1

    converter = IatiOrganisationCSVConverter()
    multi_converter = IatiOrganisationMultiCsvConverter()

    try:
        if args.command == "convert":
            if args.folder:
                output = converter.convert_folder_to_xml(args.input, args.output)
            else:
                output = converter.convert_to_xml(args.input, args.output)
            logger.info("Successfully converted to: %s", output)
            return 0

        if args.command == "template":
            converter.generate_template(args.output, not args.no_examples)
            logger.info("Generated template: %s", args.output)
            return 0

        if args.command == "multi-template":
            multi_converter.generate_csv_templates(args.output_folder, not args.no_examples)
            logger.info("Generated multi-CSV templates in: %s", args.output_folder)
            return 0

        if args.command == "xml-to-csv-folder":
            success = multi_converter.xml_to_csv_folder(args.input, args.output_folder)
            if success:
                logger.info("Successfully converted XML to CSV folder: %s", args.output_folder)
                return 0
            logger.error("Failed to convert XML to CSV folder")
            for error in multi_converter.latest_errors:
                logger.error("  - %s", error)
            return 2

        if args.command == "csv-folder-to-xml":
            success = multi_converter.csv_folder_to_xml(args.input_folder, args.output)
            if success:
                logger.info("Successfully converted CSV folder to XML: %s", args.output)
                return 0
            logger.error("Failed to convert CSV folder to XML")
            for error in multi_converter.latest_errors:
                logger.error("  - %s", error)
            return 2

        if args.command == "validate":
            if args.folder:
                records = converter.read_multiple_from_folder(args.input)
            else:
                records = [converter.read_from_file(args.input)]

            duplicates = converter.validate_organisation_identifiers(records)
            if duplicates:
                logger.error("Duplicate organisation identifiers found:")
                for duplicate in duplicates:
                    logger.error("  - %s", duplicate)
                return 2

            logger.info("Validation successful. Records checked: %d", len(records))
            return 0

    except Exception as exc:
        logger.error("Error: %s", exc)
        return 2

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
