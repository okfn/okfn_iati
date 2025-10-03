# IATI Organization CSV Converter Guide

This guide explains how to use the IATI Organization CSV Converter to create and manage IATI organization data using CSV files instead of complex XML.

## Overview

The Organization CSV Converter allows you to:
- Generate CSV templates for IATI organization data
- Convert IATI organization XML files to CSV format
- Convert CSV files to IATI-compliant organization XML
- Process multiple organizations in batch
- Validate organization data

## Installation

```bash
pip install okfn-iati
```

Or for development:
```bash
git clone https://github.com/okfn/okfn-iati.git
cd okfn-iati
pip install -e .
```

## Basic Usage

### Importing the Converter

```python
from okfn_iati.organisation_xml_generator import IatiOrganisationCSVConverter

converter = IatiOrganisationCSVConverter()
```

### Generate a CSV Template

Start by creating a template to understand the required structure:

```python
# Generate template with examples
converter.generate_template('organization_template.csv', with_examples=True)

# Generate empty template
converter.generate_template('organization_template.csv', with_examples=False)
```

### Convert Single CSV to XML

```python
# Convert one organization CSV file to XML
output_path = converter.convert_to_xml('my_organization.csv', 'output.xml')
print(f"XML generated: {output_path}")
```

### Convert XML to CSV

```python
# Extract organization data from XML to CSV
org_record = converter.read_from_file('existing_org.xml')
# This creates an OrganisationRecord object that you can inspect or modify
```

### Process Multiple Organizations

```python
# Convert all CSV files in a folder to a single XML file
output_path = converter.convert_folder_to_xml('organizations_folder/', 'combined_orgs.xml')
print(f"Combined XML with multiple organizations: {output_path}")
```

## Command Line Interface

The converter includes a command-line tool for easy use:

### Generate Template
```bash
python -m okfn_iati.organisation_xml_generator template organization_template.csv
```

### Convert Single File
```bash
python -m okfn_iati.organisation_xml_generator convert my_org.csv output.xml
```

### Convert Folder of Files
```bash
python -m okfn_iati.organisation_xml_generator convert --folder organizations/ combined_output.xml
```

### Validate Organization Data
```bash
# Validate single file
python -m okfn_iati.organisation_xml_generator validate my_org.csv

# Validate folder
python -m okfn_iati.organisation_xml_generator validate --folder organizations/
```

## CSV Template Structure

The generated template includes these key sections:

### Required Fields
```csv
Organisation Identifier,Name,Reporting Org Ref,Reporting Org Type,Reporting Org Name
XM-DAC-46002,Sample Organisation,XM-DAC-46002,40,Sample Organisation
```

### Budget Information
```csv
Budget Kind,Budget Status,Budget Period Start,Budget Period End,Budget Value,Currency
total-budget,2,2025-01-01,2025-12-31,1000000,USD
```

### Recipient-Specific Fields (when applicable)
```csv
Recipient Org Ref,Recipient Org Name,Recipient Country Code,Recipient Region Code
CR-GOV-12345,Costa Rica Ministry of Health,CR,289
```

### Document Information
```csv
Document URL,Document Format,Document Title,Document Category,Document Language
https://example.org/annual-report,text/html,Annual Report,A01,en
```

### Expenditure Information
```csv
Expenditure Period Start,Expenditure Period End,Expenditure Value,Expenditure Currency
2024-01-01,2024-12-31,950000,USD
```

## Working with Different Budget Types

### Total Budget (Organization's Overall Budget)
```csv
Organisation Identifier,Name,Budget Kind,Budget Value,Currency
XM-DAC-46002,My Organization,total-budget,5000000,USD
```

### Recipient Organization Budget
```csv
Organisation Identifier,Name,Budget Kind,Budget Value,Recipient Org Ref,Recipient Org Name
XM-DAC-46002,My Organization,recipient-org-budget,2000000,CR-GOV-123,Costa Rica Ministry
```

### Recipient Country Budget
```csv
Organisation Identifier,Name,Budget Kind,Budget Value,Recipient Country Code
XM-DAC-46002,My Organization,recipient-country-budget,3000000,CR
```

### Recipient Region Budget
```csv
Organisation Identifier,Name,Budget Kind,Budget Value,Recipient Region Code,Recipient Region Vocabulary
XM-DAC-46002,My Organization,recipient-region-budget,1500000,289,1
```

## Advanced Features

### Batch Processing with Error Handling

```python
import logging

# Enable logging to see processing details
logging.basicConfig(level=logging.INFO)

try:
    # Process multiple organizations
    records = converter.read_multiple_from_folder('organizations/')
    
    # Check for duplicates
    duplicates = converter.validate_organisation_identifiers(records)
    if duplicates:
        print(f"Warning: Duplicate identifiers found: {duplicates}")
    
    # Generate XML
    output = converter.convert_folder_to_xml('organizations/', 'output.xml')
    print(f"Successfully processed {len(records)} organizations")
    
except ValueError as e:
    print(f"Processing error: {e}")
```

### Custom Data Validation

```python
def validate_my_organization_data(csv_file):
    """Custom validation for organization data."""
    try:
        record = converter.read_from_file(csv_file)
        
        # Check required fields
        if not record.org_identifier:
            return False, "Missing organization identifier"
        
        if not record.name:
            return False, "Missing organization name"
        
        # Check budget data
        if record.budgets:
            for budget in record.budgets:
                if not budget.value:
                    return False, f"Budget {budget.kind} missing value"
                if not budget.period_start or not budget.period_end:
                    return False, f"Budget {budget.kind} missing period dates"
        
        return True, "Validation passed"
        
    except Exception as e:
        return False, str(e)

# Use custom validation
is_valid, message = validate_my_organization_data('my_org.csv')
print(f"Validation result: {message}")
```

### Working with Excel Files

If you have pandas installed, you can work with Excel files:

```python
# Convert Excel to CSV first (if you have pandas)
import pandas as pd

# Read Excel file
df = pd.read_excel('organizations.xlsx')

# Save as CSV
df.to_csv('organizations.csv', index=False)

# Then use the converter
converter.convert_to_xml('organizations.csv', 'output.xml')
```

## File Organization Best Practices

### Single Organization Files
```
my_organizations/
├── cabei_2025.csv              # Central American Bank for Economic Integration
├── ministry_health_cr.csv      # Costa Rica Ministry of Health
├── ngo_guatemala.csv           # Guatemala NGO
└── foundation_education.csv    # Education Foundation
```

### Naming Conventions
- Use descriptive names: `{organization-short-name}_{year}.csv`
- Include organization identifier in filename when possible
- Use consistent date formats
- Avoid spaces and special characters

### Folder Structure for Different Years
```
organization_data/
├── 2023/
│   ├── cabei_2023.csv
│   └── ministry_cr_2023.csv
├── 2024/
│   ├── cabei_2024.csv
│   └── ministry_cr_2024.csv
└── 2025/
    ├── cabei_2025.csv
    └── ministry_cr_2025.csv
```

## Common Use Cases

### 1. New Organization Reporting
```python
# Generate template for new organization
converter.generate_template('new_org_template.csv', with_examples=True)

# Edit the CSV file with your organization's data
# Then convert to XML
converter.convert_to_xml('new_org_data.csv', 'new_org_iati.xml')
```

### 2. Updating Existing Organization Data
```python
# Read existing XML to understand current structure
existing_record = converter.read_from_file('existing_org.xml')

# Create new CSV with updated data
# Convert back to XML
converter.convert_to_xml('updated_org.csv', 'updated_org_iati.xml')
```

### 3. Multi-Organization Reporting (e.g., for networks)
```python
# Prepare CSV files for each member organization
# Place all files in a folder
# Convert to combined XML
converter.convert_folder_to_xml('member_organizations/', 'network_report.xml')
```

### 4. Quarterly/Annual Reporting
```python
# Create quarterly reports
quarters = ['Q1', 'Q2', 'Q3', 'Q4']

for quarter in quarters:
    converter.convert_to_xml(
        f'org_data_{quarter}_2025.csv',
        f'org_report_{quarter}_2025.xml'
    )
```

## Error Handling and Troubleshooting

### Common Errors and Solutions

#### Missing Required Fields
```
Error: Missing required 'organisation identifier' or 'name' in the file
Solution: Ensure both Organisation Identifier and Name columns have values
```

#### Invalid Budget Type
```
Error: Invalid budget kind: my-budget. Must be one of: total-budget, recipient-org-budget, recipient-country-budget, recipient-region-budget
Solution: Use only the four valid budget types defined by IATI
```

#### Date Format Issues
```
Error: Invalid date format
Solution: Use YYYY-MM-DD format for all dates (e.g., 2025-01-01)
```

#### File Processing Errors
```python
# Robust error handling
def safe_convert_folder(input_folder, output_file):
    try:
        result = converter.convert_folder_to_xml(input_folder, output_file)
        return True, result
    except ValueError as e:
        if "No CSV or Excel files found" in str(e):
            return False, "No valid files found in folder"
        elif "No valid organisation data found" in str(e):
            return False, "All files had errors - check data format"
        else:
            return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {e}"

success, message = safe_convert_folder('my_orgs/', 'output.xml')
if success:
    print(f"Success: {message}")
else:
    print(f"Error: {message}")
```

## Integration Examples

### With Web Applications
```python
from flask import Flask, request, send_file
import tempfile
import os

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_csv_to_xml():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']
    if file.filename.endswith('.csv'):
        # Save uploaded file
        temp_csv = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        file.save(temp_csv.name)
        
        # Convert to XML
        temp_xml = tempfile.NamedTemporaryFile(delete=False, suffix='.xml')
        
        try:
            converter.convert_to_xml(temp_csv.name, temp_xml.name)
            return send_file(temp_xml.name, as_attachment=True, 
                           download_name='organization.xml')
        except Exception as e:
            return f'Conversion error: {e}', 500
        finally:
            os.unlink(temp_csv.name)
            os.unlink(temp_xml.name)
    
    return 'Invalid file type', 400
```

### With Data Pipelines
```python
import schedule
import time
from pathlib import Path

def daily_organization_update():
    """Daily job to process organization updates."""
    source_folder = Path('data/organizations/pending/')
    output_folder = Path('data/organizations/processed/')
    
    if source_folder.exists() and any(source_folder.glob('*.csv')):
        # Process new/updated organization files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_folder / f'organizations_{timestamp}.xml'
        
        try:
            result = converter.convert_folder_to_xml(source_folder, output_file)
            print(f"Processed organizations: {result}")
            
            # Move processed files
            processed_folder = source_folder / 'processed'
            processed_folder.mkdir(exist_ok=True)
            
            for csv_file in source_folder.glob('*.csv'):
                csv_file.rename(processed_folder / csv_file.name)
                
        except Exception as e:
            print(f"Processing failed: {e}")

# Schedule daily processing
schedule.every().day.at("02:00").do(daily_organization_update)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Performance Considerations

### Large Organizations
For organizations with extensive data:
- Split complex budgets across multiple periods/files
- Use separate files for different budget types
- Consider file size limits (keep under 10MB per CSV)

### Batch Processing
When processing many organizations:
- Process files in smaller batches if memory is limited
- Use logging to track progress
- Implement retry logic for failed conversions

### Validation Performance
- Validate data before batch processing
- Use schema validation tools
- Cache validation results for unchanged files

## Best Practices Summary

1. **Data Quality**: Always validate your CSV data before conversion
2. **Consistent Naming**: Use clear, consistent file naming conventions
3. **Version Control**: Keep track of changes to your organization data
4. **Backup Strategy**: Maintain backups of both CSV and generated XML files
5. **Regular Updates**: Update organization data at least annually
6. **Documentation**: Document any custom fields or special handling
7. **Testing**: Test conversions with sample data before production use
8. **Compliance**: Ensure generated XML complies with IATI standards

## Getting Help

If you encounter issues:
1. Check the [Data Requirements Guide](data_org_requirements.md)
2. Review the [Data Hierarchy Documentation](csv_data_org_hierarchy.md)
3. Use the built-in validation tools
4. Check the IATI Organization Standard documentation
5. Submit issues to the project repository

The Organization CSV Converter makes IATI organization reporting accessible to non-technical users while maintaining full compliance with IATI standards.
