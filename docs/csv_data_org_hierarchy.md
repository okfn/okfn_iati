# IATI Organization Data Hierarchy

This document explains how IATI Organization XML data is structured and mapped to CSV format, clarifying the data organization and relationships for organization-level reporting.

## Overview of IATI Organization XML Structure

IATI Organization XML follows a simpler structure than activity files, where each `<iati-organisation>` contains organizational information:

```xml
<iati-organisations>
  <iati-organisation>
    ├── Basic Organization Info (identifier, name, reporting-org)
    ├── Total Budgets (multiple)
    │   ├── Budget Periods
    │   └── Budget Lines (optional)
    ├── Recipient Organization Budgets (multiple)
    │   ├── Recipient Organizations
    │   ├── Budget Periods
    │   └── Budget Lines (optional)
    ├── Recipient Country Budgets (multiple)
    │   ├── Recipient Countries
    │   ├── Budget Periods
    │   └── Budget Lines (optional)
    ├── Recipient Region Budgets (multiple)
    │   ├── Recipient Regions
    │   ├── Budget Periods
    │   └── Budget Lines (optional)
    ├── Total Expenditures (multiple)
    │   ├── Expenditure Periods
    │   └── Expense Lines (optional)
    └── Document Links (multiple)
        ├── Document Categories
        └── Document Languages
  </iati-organisation>
</iati-organisations>
```

## Single CSV Data Mapping

The organization CSV converter flattens this structure into a single CSV file where each row represents one organization with its associated data.

### Organization CSV Structure

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `organisation_identifier` | `<organisation-identifier>` | Unique organization ID (PRIMARY KEY) |
| `name` | `<name><narrative>` | Organization name |
| `reporting_org_ref` | `<reporting-org>` @ref | Reporting organization reference |
| `reporting_org_type` | `<reporting-org>` @type | Reporting organization type code |
| `reporting_org_name` | `<reporting-org><narrative>` | Reporting organization name |
| `budget_kind` | Budget element name | Type of budget (total-budget, recipient-org-budget, etc.) |
| `budget_status` | `<budget>` @status | Budget status (1=Indicative, 2=Committed) |
| `budget_period_start` | `<budget><period-start>` @iso-date | Budget period start date |
| `budget_period_end` | `<budget><period-end>` @iso-date | Budget period end date |
| `budget_value` | `<budget><value>` | Budget amount |
| `currency` | `<budget><value>` @currency | Currency code |
| `value_date` | `<budget><value>` @value-date | Value date for currency |
| `recipient_org_ref` | `<recipient-org>` @ref | Recipient organization reference |
| `recipient_org_type` | `<recipient-org>` @type | Recipient organization type |
| `recipient_org_name` | `<recipient-org><narrative>` | Recipient organization name |
| `recipient_country_code` | `<recipient-country>` @code | Recipient country code |
| `recipient_region_code` | `<recipient-region>` @code | Recipient region code |
| `recipient_region_vocabulary` | `<recipient-region>` @vocabulary | Region vocabulary code |
| `expenditure_period_start` | `<total-expenditure><period-start>` @iso-date | Expenditure period start |
| `expenditure_period_end` | `<total-expenditure><period-end>` @iso-date | Expenditure period end |
| `expenditure_value` | `<total-expenditure><value>` | Expenditure amount |
| `expenditure_currency` | `<total-expenditure><value>` @currency | Expenditure currency |
| `document_url` | `<document-link>` @url | Document URL |
| `document_format` | `<document-link>` @format | Document MIME type |
| `document_title` | `<document-link><title><narrative>` | Document title |
| `document_category` | `<document-link><category>` @code | Document category code |
| `document_language` | `<document-link><language>` @code | Document language |
| `document_date` | `<document-link><document-date>` @iso-date | Document publication date |

## Data Extraction Rules

### Single Organization per File
Each CSV file represents one organization. The organization CSV converter reads the first data row and creates a complete organization record.

### Budget Type Handling
Organizations can have multiple budget types, but the CSV format focuses on the primary budget:

1. **Total Budget**: Organization's overall budget (`total-budget`)
2. **Recipient Organization Budget**: Budget for specific organizations (`recipient-org-budget`)
3. **Recipient Country Budget**: Budget for specific countries (`recipient-country-budget`)
4. **Recipient Region Budget**: Budget for specific regions (`recipient-region-budget`)

The converter automatically determines the budget type based on the data provided:
- If `budget_kind` is specified, it uses that value
- If recipient organization fields are populated, it assumes `recipient-org-budget`
- If recipient country code is provided, it assumes `recipient-country-budget`
- If recipient region code is provided, it assumes `recipient-region-budget`
- Otherwise, it defaults to `total-budget`

### Multi-Year Data
Organizations often have multiple budget and expenditure periods. The CSV format handles this by:
- Using the most recent or primary budget/expenditure for the main fields
- Future enhancement may support multiple periods through additional rows or JSON fields

### Document Handling
Organizations typically have multiple documents (annual reports, policies, audits). The CSV format:
- Uses the primary document (usually annual report) for main fields
- Future versions may support multiple documents through additional CSV files

### Missing Data
- Empty cells indicate missing XML elements
- Default values are applied according to IATI standards:
  - Budget status defaults to "2" (Committed)
  - Currency defaults to "USD" if not specified
  - Reporting organization fields default to main organization info if not provided

## Multiple Organization Processing

### Folder-Based Processing
The organization converter can process multiple CSV files from a folder:

```
organizations/
├── org-cabei.csv          (XM-DAC-46002)
├── org-ministry-cr.csv    (CR-GOV-12345)
├── org-ngo-guatemala.csv  (GT-NGO-67890)
└── org-foundation.csv     (US-EIN-123456789)
```

Each file contains one organization's data, and the converter combines them into a single IATI XML file with multiple `<iati-organisation>` elements.

### Validation Across Files
When processing multiple organizations, the converter:
- Checks for duplicate organization identifiers
- Validates each organization's data independently
- Reports any processing errors for individual files
- Continues processing valid files even if some files have errors

## XML Generation Process

### From CSV to XML Elements

1. **Basic Organization Info**:
   ```xml
   <iati-organisation last-updated-datetime="..." xml:lang="en">
     <organisation-identifier>XM-DAC-46002</organisation-identifier>
     <name><narrative>Central American Bank for Economic Integration</narrative></name>
     <reporting-org ref="XM-DAC-46002" type="40">
       <narrative>Central American Bank for Economic Integration</narrative>
     </reporting-org>
   ```

2. **Budget Information** (based on budget_kind):
   ```xml
   <total-budget status="2">
     <period-start iso-date="2025-01-01"/>
     <period-end iso-date="2025-12-31"/>
     <value currency="USD" value-date="2025-01-01">1000000</value>
   </total-budget>
   ```

3. **Recipient-Specific Budgets**:
   ```xml
   <recipient-org-budget status="2">
     <recipient-org ref="CR-GOV-12345" type="10">
       <narrative>Costa Rica Ministry of Health</narrative>
     </recipient-org>
     <period-start iso-date="2025-01-01"/>
     <period-end iso-date="2025-12-31"/>
     <value currency="USD" value-date="2025-01-01">500000</value>
   </recipient-org-budget>
   ```

4. **Expenditure Information**:
   ```xml
   <total-expenditure>
     <period-start iso-date="2024-01-01"/>
     <period-end iso-date="2024-12-31"/>
     <value currency="USD" value-date="2024-01-01">950000</value>
   </total-expenditure>
   ```

5. **Document Links**:
   ```xml
   <document-link url="https://example.org/annual-report.pdf" format="application/pdf">
     <title><narrative>Annual Report 2024</narrative></title>
     <category code="A01"/>
     <language code="en"/>
     <document-date iso-date="2025-01-15"/>
   </document-link>
   ```

## Working with Organization Data

### Creating Organization CSV Files
1. **Start with Template**: Generate a CSV template using the library
2. **One Organization per File**: Each CSV file should contain exactly one organization
3. **Complete Core Fields**: Ensure organization identifier and name are always provided
4. **Choose Budget Type**: Decide which type of budget information to include
5. **Add Supporting Data**: Include expenditures and document links where available

### Processing Multiple Organizations
1. **Consistent Structure**: All CSV files should have the same column structure
2. **Unique Identifiers**: Each organization must have a unique identifier
3. **Folder Organization**: Place all organization CSV files in a single folder
4. **Batch Processing**: Use the folder conversion method to process all organizations at once

### Data Validation
1. **Required Fields**: Validate that identifier and name are provided
2. **Budget Consistency**: Ensure budget type matches the data provided
3. **Date Formats**: Verify all dates are in YYYY-MM-DD format
4. **Currency Codes**: Check that currency codes are valid ISO 4217 codes
5. **Document URLs**: Ensure document URLs are accessible

## Example CSV-to-XML Mapping

### Input CSV:
```csv
Organisation Identifier,Name,Reporting Org Ref,Budget Kind,Budget Value,Currency,Document URL,Document Title
XM-DAC-46002,Central American Bank for Economic Integration,XM-DAC-46002,total-budget,1000000,USD,https://cabei.org/report.pdf,Annual Report 2024
```

### Generated XML:
```xml
<iati-organisations version="2.03" generated-datetime="2025-01-20T10:00:00Z">
  <iati-organisation last-updated-datetime="2025-01-20T10:00:00Z" xml:lang="en">
    <organisation-identifier>XM-DAC-46002</organisation-identifier>
    <name><narrative>Central American Bank for Economic Integration</narrative></name>
    <reporting-org ref="XM-DAC-46002" type="40">
      <narrative>Central American Bank for Economic Integration</narrative>
    </reporting-org>
    <total-budget status="2">
      <period-start iso-date="2025-01-01"/>
      <period-end iso-date="2025-12-31"/>
      <value currency="USD" value-date="2025-01-01">1000000</value>
    </total-budget>
    <document-link url="https://cabei.org/report.pdf" format="text/html">
      <title><narrative>Annual Report 2024</narrative></title>
      <category code="A01"/>
      <language code="en"/>
    </document-link>
  </iati-organisation>
</iati-organisations>
```

## Benefits of This Approach

### Simplicity
- One row per organization makes data entry straightforward
- No complex relationships to manage
- Excel-friendly format for easy editing

### Flexibility
- Supports all four IATI organization budget types
- Accommodates different organizational reporting needs
- Extensible for future IATI standard updates

### Batch Processing
- Process multiple organizations efficiently
- Maintain data consistency across organizations
- Enable organizational reporting at scale

### IATI Compliance
- Generates valid IATI 2.03 XML
- Follows IATI organization standard requirements
- Supports IATI transparency principles

This organization data hierarchy ensures that complex IATI organization structures are accessible through simple CSV files while maintaining full compliance with IATI standards.
