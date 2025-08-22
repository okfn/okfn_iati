# IATI CSV Converter Documentation

This library provides two approaches for working with IATI data in CSV format:

1. **Single CSV Converter** (`IatiCsvConverter`) - All data in one file with JSON fields for complex structures
2. **Multi-CSV Converter** (`IatiMultiCsvConverter`) - Data spread across multiple related CSV files

## Multi-CSV Converter (Recommended)

The multi-CSV approach splits IATI data into separate CSV files for different data types, making it easier to work with in Excel and other tools.

For a detailed explanation of how IATI XML data maps to the CSV structure and the relationships between files, see the [CSV Data Hierarchy Guide](csv_data_hierarchy.md).

### Files Generated

- `activities.csv` - Main activity information
- `participating_orgs.csv` - Organizations involved in activities
- `sectors.csv` - Sector classifications
- `budgets.csv` - Budget information
- `transactions.csv` - Financial transactions
- `locations.csv` - Geographic information
- `documents.csv` - Document links
- `results.csv` - Results and indicators data
- `indicators.csv` - Performance indicators
- `contact_info.csv` - Contact information

### Usage

#### Generate CSV Templates

```python
from okfn_iati import IatiMultiCsvConverter

converter = IatiMultiCsvConverter()
converter.generate_csv_templates('./my_csv_templates', include_examples=True)
```

#### Convert XML to Multiple CSV Files

```python
from okfn_iati import IatiMultiCsvConverter

converter = IatiMultiCsvConverter()
success = converter.xml_to_csv_folder('data.xml', './output_csv_folder')
```

#### Convert Multiple CSV Files back to XML

```python
from okfn_iati import IatiMultiCsvConverter

converter = IatiMultiCsvConverter()
success = converter.csv_folder_to_xml('./csv_folder', 'output.xml')
```

### Command Line Interface

The library includes a command-line tool for easy conversion:

```bash
# Generate templates
python scripts/csv_tools.py multi-template ./templates

# Convert XML to CSV folder
python scripts/csv_tools.py xml-to-csv-folder data.xml ./csv_output

# Convert CSV folder to XML
python scripts/csv_tools.py csv-folder-to-xml ./csv_folder output.xml
```

### Data Relationships

All CSV files are related through the `activity_identifier` field, which serves as a foreign key to link data across files. This preserves the hierarchical structure of IATI data while keeping each CSV file simple and Excel-friendly.

### Benefits

- **Excel-friendly**: No JSON fields, all data is in simple columns
- **Modular**: Work with specific data types independently
- **Scalable**: Large datasets can be processed file by file
- **Familiar**: Standard relational database approach
- **Flexible**: Add/remove files based on your needs

## Single CSV Converter

The single CSV approach puts all data in one file, using JSON for complex nested structures.

```python
from okfn_iati import IatiCsvConverter

converter = IatiCsvConverter()

# Generate template
converter.generate_csv_template('template.csv', format_type='basic')

# Convert XML to CSV
converter.xml_to_csv('data.xml', 'output.csv')

# Convert CSV to XML
converter.csv_to_xml('input.csv', 'output.xml')
```

## Installation Requirements

The converters require:
- Python 3.8+
- Standard library modules (csv, json, xml.etree.ElementTree, pathlib)
- Optional: pandas for DataFrame operations

For XML validation features, additional dependencies may be required.
