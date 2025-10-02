# IATI Organization Data Requirements

This document outlines the data requirements for creating IATI-compliant organization files using the OKFN-IATI library. Organization files contain information about the publishing organization itself, including budgets, expenditures, and documents.

## Overview

IATI organization files follow the IATI Organization Standard v2.03 and contain:
- Basic organization information (identifier, name, reporting details)
- Organization budgets (total, recipient-specific)
- Total expenditures
- Document links
- Contact information (planned for future versions)

## Required Fields

### Core Organization Information

| Field | Description | Required | Example |
|-------|-------------|----------|---------|
| **Organisation Identifier** | Unique organization identifier in format {RegistrationAgency}-{RegistrationNumber} | ✅ | `XM-DAC-46002` |
| **Name** | Organization name | ✅ | `Central American Bank for Economic Integration` |

### Reporting Organization

| Field | Description | Required | Example |
|-------|-------------|----------|---------|
| **Reporting Org Ref** | Reference to reporting organization | ✅ | `XM-DAC-46002` |
| **Reporting Org Type** | Type of reporting organization | ✅ | `40` (International NGO) |
| **Reporting Org Name** | Name of reporting organization | ✅ | `Central American Bank for Economic Integration` |

## Optional Fields

### Budget Information

Organizations can report different types of budgets:

#### Total Budget
| Field | Description | Example |
|-------|-------------|---------|
| **Budget Kind** | Type of budget | `total-budget` |
| **Budget Status** | Budget status (1=Indicative, 2=Committed) | `2` |
| **Budget Period Start** | Start date (YYYY-MM-DD) | `2025-01-01` |
| **Budget Period End** | End date (YYYY-MM-DD) | `2025-12-31` |
| **Budget Value** | Budget amount | `1000000` |
| **Currency** | Currency code (ISO 4217) | `USD` |
| **Value Date** | Date for currency conversion | `2025-01-01` |

#### Recipient Organization Budget
| Field | Description | Example |
|-------|-------------|---------|
| **Budget Kind** | Must be `recipient-org-budget` | `recipient-org-budget` |
| **Recipient Org Ref** | Recipient organization reference | `CR-RPN-123456` |
| **Recipient Org Type** | Recipient organization type | `22` |
| **Recipient Org Name** | Recipient organization name | `Costa Rica Ministry of Health` |

#### Recipient Country Budget
| Field | Description | Example |
|-------|-------------|---------|
| **Budget Kind** | Must be `recipient-country-budget` | `recipient-country-budget` |
| **Recipient Country Code** | ISO 3166-1 alpha-2 country code | `CR` |

#### Recipient Region Budget
| Field | Description | Example |
|-------|-------------|---------|
| **Budget Kind** | Must be `recipient-region-budget` | `recipient-region-budget` |
| **Recipient Region Code** | Region code from OECD DAC list | `289` |
| **Recipient Region Vocabulary** | Vocabulary used (1=OECD DAC) | `1` |

### Expenditure Information

| Field | Description | Example |
|-------|-------------|---------|
| **Expenditure Period Start** | Start date of expenditure period | `2024-01-01` |
| **Expenditure Period End** | End date of expenditure period | `2024-12-31` |
| **Expenditure Value** | Total expenditure amount | `950000` |
| **Expenditure Currency** | Currency code | `USD` |

### Document Information

| Field | Description | Example |
|-------|-------------|---------|
| **Document URL** | URL to the document | `https://example.org/annual-report.pdf` |
| **Document Format** | MIME type | `application/pdf` |
| **Document Title** | Document title | `Annual Report 2024` |
| **Document Category** | Document category code | `A01` (Annual Report) |
| **Document Language** | ISO 639-1 language code | `en` |
| **Document Date** | Document publication date | `2025-01-15` |

## Data Validation Rules

### Organization Identifier
- Must follow format: `{RegistrationAgency}-{RegistrationNumber}`
- Registration agency must be from IATI Organization Registration Agency codelist
- Must be unique across all organization records

### Budget Types
Organizations must specify one of four budget types:
1. **total-budget**: Organization's overall budget
2. **recipient-org-budget**: Budget allocated to specific organizations
3. **recipient-country-budget**: Budget allocated to specific countries
4. **recipient-region-budget**: Budget allocated to specific regions

### Budget Status Codes
- `1`: Indicative budget
- `2`: Committed budget

### Organization Type Codes (Common Values)
- `10`: Government
- `15`: Other Public Sector
- `21`: International NGO
- `22`: National NGO
- `23`: Regional NGO
- `30`: Public Private Partnership
- `40`: Multilateral
- `60`: Foundation
- `70`: Private Sector
- `80`: Academic, Training and Research

### Document Category Codes (Common Values)
- `A01`: Annual Report
- `A02`: Institutional Strategy Paper
- `A03`: Country strategy paper
- `A04`: Aid Allocation Policy
- `A05`: Procurement Policy and Procedure
- `A06`: Institutional Audit Report
- `A07`: Country Audit Report
- `A08`: Exclusions Policy
- `A09`: Institutional Evaluation Report
- `A10`: Country Evaluation Report
- `A11`: Sector Evaluation Report
- `B01`: Budget
- `B02`: Budget Amendment
- `B03`: Budget Revision

### Currency Codes
Use ISO 4217 three-letter currency codes:
- `USD`: US Dollar
- `EUR`: Euro
- `GBP`: British Pound
- `JPY`: Japanese Yen
- `CAD`: Canadian Dollar

### Country Codes
Use ISO 3166-1 alpha-2 country codes:
- `CR`: Costa Rica
- `GT`: Guatemala
- `HN`: Honduras
- `NI`: Nicaragua
- `PA`: Panama
- `BZ`: Belize
- `SV`: El Salvador
- `DO`: Dominican Republic

### Region Codes (OECD DAC)
- `289`: South & Central Asia
- `298`: Africa, regional
- `389`: North & Central America, regional
- `489`: South America, regional
- `589`: Middle East, regional
- `689`: Europe, regional
- `789`: Oceania, regional
- `998`: Developing countries, unspecified

## Date Formats

All dates must be in ISO 8601 format: `YYYY-MM-DD`

Examples:
- `2025-01-01` (January 1, 2025)
- `2024-12-31` (December 31, 2024)

## File Structure

### Single Organization per File
Each CSV file should contain data for one organization only. The first data row contains all the organization information.

### Multiple Files in Folder
When processing multiple organizations, place each organization's CSV file in a folder. The converter will process all CSV files and combine them into a single IATI XML file.

## Example CSV Structure

```csv
Organisation Identifier,Name,Reporting Org Ref,Reporting Org Type,Reporting Org Name,Budget Kind,Budget Status,Budget Period Start,Budget Period End,Budget Value,Currency,Document URL,Document Title,Document Category
XM-DAC-46002,Central American Bank for Economic Integration,XM-DAC-46002,40,Central American Bank for Economic Integration,total-budget,2,2025-01-01,2025-12-31,1000000,USD,https://cabei.org/annual-report,Annual Report 2024,A01
```

## Best Practices

### Data Quality
1. **Consistent Identifiers**: Use the same organization identifier across all your IATI publications
2. **Complete Information**: Provide as much detail as possible, especially for budgets and expenditures
3. **Regular Updates**: Update organization files at least annually
4. **Currency Consistency**: Use a consistent base currency, typically USD for international organizations

### Budget Reporting
1. **Forward-Looking**: Report budgets for the current and next 2-3 years
2. **Historical Expenditures**: Report actual expenditures for the past 2-3 years
3. **Budget Alignment**: Ensure budget periods align with your organization's fiscal year
4. **Multiple Budget Types**: Use different budget types to show how funds are allocated

### Documentation
1. **Annual Reports**: Always link to your organization's annual report
2. **Strategic Documents**: Include links to strategic plans and policies
3. **Financial Reports**: Link to detailed financial statements
4. **Language**: Provide documents in both local and international languages when possible

### File Management
1. **Naming Convention**: Use descriptive file names like `{org-identifier}-org-{year}.csv`
2. **Version Control**: Keep track of file versions and update dates
3. **Backup**: Maintain backups of your data files
4. **Validation**: Always validate generated XML before publishing

## Common Errors and Solutions

### Missing Required Fields
**Error**: Organization identifier or name is missing
**Solution**: Ensure both fields are populated in your CSV

### Invalid Date Formats
**Error**: Dates not in YYYY-MM-DD format
**Solution**: Convert all dates to ISO 8601 format

### Currency Inconsistencies
**Error**: Missing or invalid currency codes
**Solution**: Use standard ISO 4217 three-letter currency codes

### Budget Type Mismatches
**Error**: Recipient information doesn't match budget type
**Solution**: Ensure recipient fields are only used with appropriate budget types

### Large File Sizes
**Error**: CSV files become too large to process
**Solution**: Split data across multiple CSV files, one per organization

## Getting Help

If you encounter issues:
1. Check this documentation for data requirements
2. Validate your CSV structure against the template
3. Use the built-in validation tools
4. Consult the IATI Organization Standard documentation
5. Contact the development team for technical support

Remember: IATI organization files are about transparency in organizational reporting. Focus on providing clear, accurate, and up-to-date information about your organization's structure, finances, and activities.
