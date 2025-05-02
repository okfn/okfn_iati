# IATI Data Requirements for Development Bank

## Introduction

This document outlines the data needed from your organization to generate compliant IATI (International Aid Transparency Initiative) XML files. IATI is a global standard for publishing transparent data about development and humanitarian activities.

The data you provide will be transformed into IATI XML format and published on the IATI Registry, making your development activities transparent and accessible to the international community.

## Data Format

Please provide your data in **CSV** or **Excel** format, with one row per activity. The sections below explain what information we need for each activity.

## Essential Activity Information

For each development activity (project, program, or intervention), we need:

### 1. Basic Identification

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Activity Identifier | A unique code for this activity | Text (must start with your org ID) | Yes | `XM-DAC-12345-PROJECT001` |
| Activity Title | The name of the activity | Text | Yes | "Small Business Support Program" |
| Activity Description | A detailed description of what the activity involves | Text | Yes | "This program supports small businesses in rural areas through microfinance and training" |
| Activity Status | Current status of the activity | Choose one: Planning, Implementation, Completion, Post-completion, Cancelled, Suspended | Yes | Implementation |

### 2. Dates

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Planned Start Date | When the activity is scheduled to begin | YYYY-MM-DD | Yes | 2023-01-15 |
| Actual Start Date | When the activity actually began | YYYY-MM-DD | If started | 2023-01-20 |
| Planned End Date | When the activity is scheduled to end | YYYY-MM-DD | Yes | 2024-01-15 |
| Actual End Date | When the activity actually ended | YYYY-MM-DD | If completed | - |

### 3. Organizations Involved

#### 3.1. Your Organization (Reporting Organization)

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Organization ID | Your organization's IATI identifier | Text | Yes | `XM-DAC-12345` |
| Organization Name | Your organization's name | Text | Yes | "Central American Bank for Economic Integration" |
| Organization Type | Type of organization | Choose one: Government, NGO, Multilateral, Foundation, Private Sector | Yes | Multilateral |

#### 3.2. Participating Organizations

For each organization participating in the activity, please provide:

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Organization Name | Name of the participating organization | Text | Yes | "Ministry of Finance, Honduras" |
| Organization ID | IATI identifier of the organization (if known) | Text | If available | `XM-DAC-HN-MOF` |
| Organization Role | Role in the activity | Choose one: Funding, Implementing, Accountable, Extending | Yes | Implementing |
| Organization Type | Type of organization | Choose one: Government, NGO, Multilateral, Foundation, Private Sector | Yes | Government |

### 4. Geographic Location

#### 4.1. Recipient Country/Region

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Recipient Country | Country where the activity takes place | ISO 2-letter country code | Yes (if no region) | HN (for Honduras) |
| Percentage | Percentage of activity in this country | Number (0-100) | If multiple countries | 100 |

OR

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Recipient Region | Region where activity takes place | OECD DAC region code | Yes (if no country) | 298 (for Central America) |
| Percentage | Percentage of activity in this region | Number (0-100) | If multiple regions | 100 |

#### 4.2. Specific Locations (if applicable)

For each specific location within the country:

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Location Name | Name of the specific location | Text | Yes | "Tegucigalpa" |
| Location Description | Brief description of this location | Text | No | "Capital city area" |
| Coordinates | Geographic coordinates | Latitude,Longitude | If available | "14.0723,-87.1921" |

### 5. Sectors

For each sector the activity addresses:

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Sector Code | Code representing the sector | DAC 5-digit code | Yes | 11110 (Education Policy) |
| Sector Name | Name of the sector | Text | Yes | "Education Policy & Administrative Management" |
| Percentage | Percentage of activity focused on this sector | Number (0-100) | If multiple sectors | 60 |

### 6. Financial Information

#### 6.1. Budgets

For each budget period:

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Budget Type | Type of budget | Choose one: Original, Revised | Yes | Original |
| Status | Budget status | Choose one: Indicative, Committed | Yes | Committed |
| Period Start | Start of budget period | YYYY-MM-DD | Yes | 2023-01-01 |
| Period End | End of budget period | YYYY-MM-DD | Yes | 2023-12-31 |
| Amount | Value of budget | Number | Yes | 1500000 |
| Currency | Currency of budget | 3-letter code | Yes | USD |
| Value Date | Exchange rate date | YYYY-MM-DD | Yes | 2023-01-01 |

#### 6.2. Transactions

For each financial transaction:

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Transaction Type | Type of transaction | Choose one: Commitment, Disbursement, Expenditure, Incoming Funds | Yes | Disbursement |
| Transaction Date | Date of transaction | YYYY-MM-DD | Yes | 2023-03-15 |
| Amount | Transaction amount | Number | Yes | 500000 |
| Currency | Currency of transaction | 3-letter code | Yes | USD |
| Value Date | Exchange rate date | YYYY-MM-DD | Yes | 2023-03-15 |
| Provider Organization | Organization providing the funds | Text | For incoming funds | "World Bank" |
| Receiver Organization | Organization receiving the funds | Text | For outgoing funds | "Ministry of Education, Honduras" |

### 7. Results (if available)

For each result being tracked:

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Result Type | Type of result | Choose one: Output, Outcome, Impact | Yes | Outcome |
| Result Title | Title of the result | Text | Yes | "Increased access to education" |
| Result Description | Description of the result | Text | Yes | "Measure of increased school enrollment in target areas" |
| Indicator Title | Title of the indicator | Text | Yes | "School enrollment rate" |
| Indicator Description | Description of the indicator | Text | Yes | "Percentage of school-age children enrolled" |
| Baseline Year | Year of baseline data | YYYY | If available | 2022 |
| Baseline Value | Baseline value | Number or Text | If available | "45%" |
| Target Year | Year of target | YYYY | If available | 2024 |
| Target Value | Target value | Number or Text | If available | "60%" |
| Actual Year | Year of actual result | YYYY | If available | 2023 |
| Actual Value | Actual achieved value | Number or Text | If available | "52%" |

### 8. Documents

For each document related to the activity:

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Document Title | Title of document | Text | Yes | "Project Proposal" |
| Document URL | Web address of document | URL | Yes | "https://example.org/docs/proposal.pdf" |
| Document Format | Format of document | MIME type | Yes | "application/pdf" |
| Document Category | Type of document | Category code | Yes | A02 (Objectives) |

## Data Validation Notes

1. **Activity Identifiers**: Must start with your organization's identifier followed by a hyphen and a unique code.
2. **Dates**: All dates must be in YYYY-MM-DD format.
3. **Percentages**: When multiple countries, regions or sectors are listed, percentages should add up to 100%.
4. **Currency**: Use standard 3-letter ISO currency codes (USD, EUR, GBP, etc.).
5. **Country Codes**: Use standard ISO 2-letter country codes (HN, SV, GT, NI, CR, PA, etc.).
6. **Sector Codes**: Use the OECD DAC 5-digit purpose codes.

## Additional Information Needed

If you have any of the following information, please include it:

1. **Policy Markers**: If the activity targets specific policy areas (gender equality, environment, etc.)
2. **Default Currency**: The main currency used for the activity
3. **Humanitarian Flag**: Whether the activity is humanitarian in nature (Yes/No)
4. **Related Activities**: If this activity is related to other activities you report

## Questions?

If you're unsure about any data field or need clarification on format requirements, please contact our team at [your-email@example.com].

## Next Steps

1. Compile your data in a CSV or Excel file following the structure above
2. Include one row per activity with columns matching the fields described
3. Send your completed file to us by [deadline]
4. Our team will validate the data and convert it to IATI XML format
5. We'll share the generated IATI file with you for review before publication
