#!/usr/bin/env python3
"""
IATI CSV Tools

This script provides tools for converting between IATI XML and CSV formats.
It supports both single CSV file and multi-CSV folder approaches.
"""

import argparse
import sys
from pathlib import Path
from okfn_iati import IatiCsvConverter, IatiMultiCsvConverter


# Add the src directory to the path so we can import okfn_iati
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def generate_template(output_path: str, format_type: str = 'basic', include_examples: bool = True):
    """Generate a single CSV template for IATI data entry."""
    converter = IatiCsvConverter()

    print(f"Generating {format_type} CSV template: {output_path}")
    converter.generate_csv_template(
        output_path=output_path,
        format_type=format_type,
        include_examples=include_examples
    )
    print(f"Template saved to: {output_path}")

    # Print column information
    if format_type == 'basic':
        columns = converter._get_basic_columns()
        print(f"\nBasic template includes {len(columns)} essential columns:")
    else:
        columns = converter.CSV_COLUMNS
        print(f"\nFull template includes {len(columns)} columns:")

    for i, col in enumerate(columns[:10], 1):
        print(f"  {i}. {col}")

    if len(columns) > 10:
        print(f"  ... and {len(columns) - 10} more columns")


def generate_multi_templates(output_folder: str, include_examples: bool = True):
    """Generate multiple CSV templates in a folder."""
    converter = IatiMultiCsvConverter()

    print(f"Generating multi-CSV templates in folder: {output_folder}")
    converter.generate_csv_templates(
        output_folder=output_folder,
        include_examples=include_examples
    )
    print(f"Templates saved to folder: {output_folder}")

    # Print file information
    print(f"\nGenerated {len(converter.csv_files)} CSV template files:")
    for csv_type, csv_config in converter.csv_files.items():
        print(f"  📄 {csv_config['filename']}: {len(csv_config['columns'])} columns")


def xml_to_csv(xml_path: str, csv_path: str):
    """Convert IATI XML file to single CSV format."""
    converter = IatiCsvConverter()

    print("Converting XML to single CSV:")
    print(f"  Input:  {xml_path}")
    print(f"  Output: {csv_path}")

    try:
        converter.xml_to_csv(xml_path, csv_path)
        print("✅ Conversion completed successfully!")

        # Count rows
        import csv
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            row_count = sum(1 for row in reader) - 1  # Subtract header
        print(f"📊 Extracted {row_count} activities")

    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return False

    return True


def xml_to_csv_folder(xml_path: str, csv_folder: str):
    """Convert IATI XML file to multiple CSV files in a folder."""
    converter = IatiMultiCsvConverter()

    print("Converting XML to multi-CSV folder:")
    print(f"  Input:  {xml_path}")
    print(f"  Output: {csv_folder}")

    success = converter.xml_to_csv_folder(xml_path, csv_folder)

    if success:
        # Count total records
        folder_path = Path(csv_folder)
        total_records = 0
        file_counts = {}

        for csv_type, csv_config in converter.csv_files.items():
            csv_file = folder_path / csv_config['filename']
            if csv_file.exists():
                import csv
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    count = sum(1 for row in reader) - 1  # Subtract header
                    file_counts[csv_config['filename']] = count
                    if csv_type == 'activities':
                        total_records = count

        print(f"📊 Extracted {total_records} activities across {len(file_counts)} files:")
        for filename, count in file_counts.items():
            if count > 0:
                print(f"   📄 {filename}: {count} records")

    return success


def csv_to_xml(csv_path: str, xml_path: str, validate: bool = True):
    """Convert single CSV file to IATI XML format."""
    converter = IatiCsvConverter()

    print("Converting single CSV to XML:")
    print(f"  Input:  {csv_path}")
    print(f"  Output: {xml_path}")

    success = converter.csv_to_xml(csv_path, xml_path, validate_output=validate)

    if success:
        print("✅ Conversion completed successfully!")
        if validate:
            print("✅ XML validation passed")
    else:
        print("❌ Conversion failed or validation errors found")

    return success


def csv_folder_to_xml(csv_folder: str, xml_path: str, validate: bool = True):
    """Convert multiple CSV files in a folder to IATI XML format."""
    converter = IatiMultiCsvConverter()

    print("Converting multi-CSV folder to XML:")
    print(f"  Input:  {csv_folder}")
    print(f"  Output: {xml_path}")

    success = converter.csv_folder_to_xml(csv_folder, xml_path, validate_output=validate)

    if success:
        print("✅ Conversion completed successfully!")
        if validate:
            print("✅ XML validation passed")
    else:
        print("❌ Conversion failed or validation errors found")

    return success


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="IATI CSV/XML Conversion Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate single CSV template
  %(prog)s template output.csv --format basic

  # Generate multi-CSV templates
  %(prog)s multi-template ./csv_folder

  # Convert XML to single CSV
  %(prog)s xml-to-csv data.xml output.csv

  # Convert XML to multiple CSV files
  %(prog)s xml-to-csv-folder data.xml ./csv_folder

  # Convert single CSV to XML
  %(prog)s csv-to-xml input.csv output.xml

  # Convert multiple CSV files to XML
  %(prog)s csv-folder-to-xml ./csv_folder output.xml
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Template command
    template_parser = subparsers.add_parser('template', help='Generate single CSV template')
    template_parser.add_argument('output', help='Output CSV file path')
    template_parser.add_argument('--format', choices=['basic', 'full'], default='basic',
                                 help='Template format (default: basic)')
    template_parser.add_argument('--no-examples', action='store_true',
                                 help='Skip example data in template')

    # Multi-template command
    multi_template_parser = subparsers.add_parser('multi-template',
                                                  help='Generate multiple CSV templates')
    multi_template_parser.add_argument('output_folder', help='Output folder path')
    multi_template_parser.add_argument('--no-examples', action='store_true',
                                       help='Skip example data in templates')

    # XML to CSV command
    xml_to_csv_parser = subparsers.add_parser('xml-to-csv',
                                              help='Convert XML to single CSV')
    xml_to_csv_parser.add_argument('xml_file', help='Input XML file')
    xml_to_csv_parser.add_argument('csv_file', help='Output CSV file')

    # XML to CSV folder command
    xml_to_folder_parser = subparsers.add_parser('xml-to-csv-folder',
                                                 help='Convert XML to multiple CSV files')
    xml_to_folder_parser.add_argument('xml_file', help='Input XML file')
    xml_to_folder_parser.add_argument('csv_folder', help='Output CSV folder')

    # CSV to XML command
    csv_to_xml_parser = subparsers.add_parser('csv-to-xml',
                                              help='Convert single CSV to XML')
    csv_to_xml_parser.add_argument('csv_file', help='Input CSV file')
    csv_to_xml_parser.add_argument('xml_file', help='Output XML file')
    csv_to_xml_parser.add_argument('--no-validate', action='store_true',
                                   help='Skip XML validation')

    # CSV folder to XML command
    folder_to_xml_parser = subparsers.add_parser('csv-folder-to-xml',
                                                 help='Convert multiple CSV files to XML')
    folder_to_xml_parser.add_argument('csv_folder', help='Input CSV folder')
    folder_to_xml_parser.add_argument('xml_file', help='Output XML file')
    folder_to_xml_parser.add_argument('--no-validate', action='store_true',
                                      help='Skip XML validation')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        # Execute commands
        if args.command == 'template':
            generate_template(
                args.output,
                args.format,
                not args.no_examples
            )

        elif args.command == 'multi-template':
            generate_multi_templates(
                args.output_folder,
                not args.no_examples
            )

        elif args.command == 'xml-to-csv':
            success = xml_to_csv(args.xml_file, args.csv_file)
            if not success:
                sys.exit(1)

        elif args.command == 'xml-to-csv-folder':
            success = xml_to_csv_folder(args.xml_file, args.csv_folder)
            if not success:
                sys.exit(1)

        elif args.command == 'csv-to-xml':
            success = csv_to_xml(
                args.csv_file,
                args.xml_file,
                not args.no_validate
            )
            if not success:
                sys.exit(1)

        elif args.command == 'csv-folder-to-xml':
            success = csv_folder_to_xml(
                args.csv_folder,
                args.xml_file,
                not args.no_validate
            )
            if not success:
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()


def main():
    parser = argparse.ArgumentParser(
        description="IATI CSV/XML Converter - Convert between IATI XML and CSV formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a basic CSV template
  python csv_tools.py template basic_template.csv --format basic

  # Generate a full CSV template with examples
  python csv_tools.py template full_template.csv --format full --examples

  # Convert XML to CSV
  python csv_tools.py xml-to-csv input.xml output.csv

  # Convert CSV to XML
  python csv_tools.py csv-to-xml input.csv output.xml

  # Convert CSV to XML without validation
  python csv_tools.py csv-to-xml input.csv output.xml --no-validate
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Template generation command
    template_parser = subparsers.add_parser('template', help='Generate CSV template')
    template_parser.add_argument('output', help='Output CSV template file')
    template_parser.add_argument(
        '--format', choices=['basic', 'full'], default='basic',
        help='Template format (basic=essential fields, full=all fields)'
    )
    template_parser.add_argument(
        '--examples', action='store_true',
        help='Include example rows in template'
    )

    # XML to CSV command
    xml_csv_parser = subparsers.add_parser('xml-to-csv', help='Convert XML to CSV')
    xml_csv_parser.add_argument('xml_input', help='Input IATI XML file')
    xml_csv_parser.add_argument('csv_output', help='Output CSV file')

    # CSV to XML command
    csv_xml_parser = subparsers.add_parser('csv-to-xml', help='Convert CSV to XML')
    csv_xml_parser.add_argument('csv_input', help='Input CSV file')
    csv_xml_parser.add_argument('xml_output', help='Output IATI XML file')
    csv_xml_parser.add_argument('--no-validate', action='store_true',
                                help='Skip XML validation')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'template':
            generate_template(args.output, args.format, args.examples)

        elif args.command == 'xml-to-csv':
            if not Path(args.xml_input).exists():
                print(f"❌ Error: Input file does not exist: {args.xml_input}")
                return
            xml_to_csv(args.xml_input, args.csv_output)

        elif args.command == 'csv-to-xml':
            if not Path(args.csv_input).exists():
                print(f"❌ Error: Input file does not exist: {args.csv_input}")
                return
            csv_to_xml(args.csv_input, args.xml_output, not args.no_validate)

    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
