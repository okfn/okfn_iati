[![Python Tests](https://github.com/okfn/okfn_iati/workflows/Python%20IATI%20Tests/badge.svg)](https://github.com/okfn/okfn_iati/actions)

**Note**: This library is under development and in Beta status.   

# OKFN IATI XML Handler

A Python library for working with IATI XML data according to the IATI 2.03 standard.

## Features

- Data models that represent IATI XML elements with validation
- XML generator to create valid IATI XML from Python objects
- Multi-CSV converter for easy data editing in spreadsheet tools
- Support for IATI 2.03 standard
- Enums for standardized code lists
- Data validation to ensure compliance with the standard

## Installation

```bash
pip install okfn-iati
```

## Usage

### Option 1: Multi-CSV Workflow (Recommended)

The easiest way to work with IATI data is using the multi-CSV approach, which splits data into manageable spreadsheet files:

```python
from okfn_iati import IatiMultiCsvConverter

# Create converter
converter = IatiMultiCsvConverter()

# Generate CSV templates with examples
converter.generate_csv_templates(
    output_folder="./my_iati_data",
    include_examples=True
)

# Edit the CSV files in Excel/LibreOffice, then convert to XML
converter.csv_folder_to_xml(
    csv_folder="./my_iati_data",
    xml_output="output.xml",
    validate_output=True
)
```

This creates multiple CSV files:
- `activities.csv` - Main activity information
- `participating_orgs.csv` - Organizations involved
- `budgets.csv` - Budget information
- `transactions.csv` - Financial transactions
- `locations.csv` - Geographic locations
- `sectors.csv` - Sector classifications
- `documents.csv` - Document links
- `results.csv` - Results and indicators
- `contact_info.csv` - Contact information

### Option 2: Programmatic Creation

Create IATI activities directly in Python:

```python
from okfn_iati import (
    # Main models
    Activity, Narrative, OrganizationRef, ParticipatingOrg, ActivityDate,
    Location, LocationIdentifier, DocumentLink,
    Budget, Transaction, IatiActivities,

    # Enums - use these constants instead of strings
    ActivityStatus, ActivityDateType, TransactionType, BudgetType, BudgetStatus,
    OrganisationRole, OrganisationType, LocationID, DocumentCategory,

    # Generator
    IatiXmlGenerator
)

# Define reporting organization identifier (following IATI standard format)
reporting_org_id = "XM-DAC-12345"

# Create an IATI Activity
activity = Activity(
    # The activity identifier should begin with the reporting org identifier 
    # followed by a hyphen and a unique string: {org-id}-{activity-unique-id}
    iati_identifier=f"{reporting_org_id}-PROJECT001",
    reporting_org=OrganizationRef(
        ref=reporting_org_id,  # Must match the prefix of the activity identifier
        type=OrganisationType.GOVERNMENT.value,
        narratives=[Narrative(text="Example Organization")]
    ),
    title=[Narrative(text="Example Project")],
    description=[{
        "type": "1", 
        "narratives": [
            Narrative(text="This is an example project description")
        ]
    }],
    activity_status=ActivityStatus.IMPLEMENTATION,
    activity_dates=[
        ActivityDate(
            type=ActivityDateType.PLANNED_START,
            iso_date="2023-01-01",
            narratives=[Narrative(text="Planned start date")]
        )
    ],
    participating_orgs=[
        ParticipatingOrg(
            role=OrganisationRole.FUNDING,
            ref="XM-EXAMPLE-FUNDER",
            type=OrganisationType.GOVERNMENT.value,
            narratives=[Narrative(text="Example Funding Organization")]
        )
    ],
    recipient_countries=[
        {
            "code": "KE",
            "percentage": 100,
            "narratives": [Narrative(text="Kenya")]
        }
    ],
    sectors=[
        {
            "code": "11110",  # Education policy and administrative management
            "vocabulary": "1",  # DAC vocabulary
            "percentage": 100
        }
    ],
    budgets=[
        Budget(
            type=BudgetType.ORIGINAL,
            status=BudgetStatus.INDICATIVE,
            period_start="2023-01-01",
            period_end="2023-12-31",
            value=100000.00,
            currency="USD",
            value_date="2023-01-01"
        )
    ],
    default_currency="USD",
)

# Create an IATI Activities container
iati_activities = IatiActivities(
    version="2.03",
    activities=[activity]
)

# Generate XML
generator = IatiXmlGenerator()
xml_string = generator.generate_iati_activities_xml(iati_activities)

# Save to file
generator.save_to_file(iati_activities, "example_activity.xml")
```

## Command-Line Tools

The library includes command-line tools for working with CSV and XML files:

```bash
# Generate CSV templates with examples
python -m okfn_iati.cli multi-template ./my_data --include-examples

# Convert XML to multiple CSV files
python -m okfn_iati.cli xml-to-csv-folder data.xml ./csv_output

# Convert CSV folder back to XML
python -m okfn_iati.cli csv-folder-to-xml ./csv_output output.xml

# Convert with validation
python -m okfn_iati.cli csv-folder-to-xml ./csv_output output.xml --validate
```

## Working with Existing XML

Convert existing IATI XML to editable CSV files:

```python
from okfn_iati import IatiMultiCsvConverter

converter = IatiMultiCsvConverter()

# Extract XML to CSV files for editing
converter.xml_to_csv_folder(
    xml_input="existing_data.xml",
    csv_folder="./editable_data"
)

# Edit the CSV files as needed, then convert back
converter.csv_folder_to_xml(
    csv_folder="./editable_data",
    xml_output="updated_data.xml",
    validate_output=True
)
```
## Validation with IATI Validator

The XML generated by this library follows the IATI schema and ruleset requirements. To validate your XML:

1. Generate your XML file using this library
2. Upload it to the [IATI Validator](https://validator.iatistandard.org/)
3. Check that it passes both schema validation and IATI ruleset validation

You can validate IATI XML using the built-in `IatiValidator` class:

```python
from okfn_iati import IatiValidator

# Create a validator
validator = IatiValidator()

# Validate XML string
with open("example_activity.xml", "r") as f:
    xml_string = f.read()
    is_valid, errors = validator.validate(xml_string)
    
    if is_valid:
        print("XML is valid!")
    else:
        print("XML validation errors:")
        for schema_error in errors['schema_errors']:
            print(f"  Schema error: {schema_error}")
        for ruleset_error in errors['ruleset_errors']:
            print(f"  Ruleset error: {ruleset_error}")
```

## Organisation Files

In addition to activity files, the library supports IATI organisation files:

```python
from okfn_iati import (
    IatiOrganisationMultiCsvConverter,
    IatiOrganisationXMLGenerator
)

# Generate organisation CSV templates
org_converter = IatiOrganisationMultiCsvConverter()
org_converter.generate_csv_templates(
    output_folder="./org_data",
    include_examples=True
)

# Convert organisation CSV to XML
org_converter.csv_folder_to_xml(
    csv_folder="./org_data",
    xml_output="organisation.xml"
)
```

## Start your IATI project

You can start by creating a CSV file and this library will process it to generate valid IATI XML files.  
Read the docs [here](https://github.com/okfn/okfn_iati/blob/main/docs/data_requirements.md).  
