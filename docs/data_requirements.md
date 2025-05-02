# IATI Data Requirements for Development Bank

## Introduction

This document outlines the data needed from your organization to generate compliant IATI (International Aid Transparency Initiative) XML files. IATI is a global standard for publishing transparent data about development and humanitarian activities.

The data you provide will be transformed into IATI XML format and published on the IATI Registry, making your development activities transparent and accessible to the international community.

## What data can we publish?

IATI is designed to track the flow of development and humanitarian resources. As a development bank, you can publish information about a wide range of financial instruments and activities, including:

- **Loan operations**: Both concessional and non-concessional lending to governments, state-owned enterprises, and private sector entities
- **Grant programs**: Technical assistance grants, research grants, and other non-reimbursable funding
- **Equity investments**: Direct investments in companies and funds that support development objectives
- **Guarantee schemes**: Financial guarantees that help mobilize additional resources
- **Co-financing arrangements**: Projects jointly funded with other development institutions
- **Technical cooperation**: Advisory services and capacity building programs
- **Trust funds**: Management of resources on behalf of donors for specific purposes
- **Policy-based financing**: Support for policy and institutional reforms
- **Emergency response funding**: Rapid financing for disaster recovery and resilience
- **Regional integration initiatives**: Cross-border projects that promote regional development

IATI allows tracking of all stages of these operations from initial approval through implementation to results, providing a comprehensive view of your development portfolio and its impacts. This transparency helps demonstrate the value of your institution's work while facilitating coordination with other development partners.

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
| Activity Status | Current status of the activity | [IATI ActivityStatus code](https://iatistandard.org/en/iati-standard/203/codelists/activitystatus/) (1=Planning, 2=Implementation, etc.) | Yes | 2 (Implementation) |

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
| Organization Type | Type of organization | [IATI OrganisationType code](https://iatistandard.org/en/iati-standard/203/codelists/organisationtype/) (10=Government, 40=Multilateral, etc.) | Yes | 40 (Multilateral) |

#### 3.2. Participating Organizations

For each organization participating in the activity, please provide:

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Organization Name | Name of the participating organization | Text | Yes | "Ministry of Finance, Honduras" |
| Organization ID | IATI identifier of the organization (if known) | Text | If available | `XM-DAC-HN-MOF` |
| Organization Role | Role in the activity | [IATI OrganisationRole code](https://iatistandard.org/en/iati-standard/203/codelists/organisationrole/) (1=Funding, 4=Implementing, etc.) | Yes | 4 (Implementing) |
| Organization Type | Type of organization | [IATI OrganisationType code](https://iatistandard.org/en/iati-standard/203/codelists/organisationtype/) | Yes | 10 (Government) |

### 4. Geographic Location

#### 4.1. Recipient Country/Region

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Recipient Country | Country where the activity takes place | [ISO 3166-1 alpha-2 code](https://iatistandard.org/en/iati-standard/203/codelists/country/) | Yes (if no region) | HN (for Honduras) |
| Percentage | Percentage of activity in this country | Number (0-100) | If multiple countries | 100 |

OR

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Recipient Region | Region where activity takes place | [IATI Region code](https://iatistandard.org/en/iati-standard/203/codelists/region/) | Yes (if no country) | 298 (Central America) |
| Percentage | Percentage of activity in this region | Number (0-100) | If multiple regions | 100 |

#### 4.2. Specific Locations (if applicable)

For each specific location within the country:

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Location Name | Name of the specific location | Text | Yes | "Tegucigalpa" |
| Location Description | Brief description of this location | Text | No | "Capital city area" |
| Coordinates | Geographic coordinates | Latitude,Longitude | If available | "14.0723,-87.1921" |
| Location Type | Type of location | [IATI LocationType code](https://iatistandard.org/en/iati-standard/203/codelists/locationtype/) | If available | 2 (Populated Place) |

### 5. Sectors

For each sector the activity addresses:

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Sector Code | Code representing the sector | [OECD DAC 5-digit purpose code](https://iatistandard.org/en/iati-standard/203/codelists/sector/) | Yes | 11110 (Education Policy) |
| Sector Name | Name of the sector | Text | Yes | "Education Policy & Administrative Management" |
| Percentage | Percentage of activity focused on this sector | Number (0-100) | If multiple sectors | 60 |

### 6. Financial Information

#### 6.1. Budgets

For each budget period:

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Budget Type | Type of budget | [IATI BudgetType code](https://iatistandard.org/en/iati-standard/203/codelists/budgettype/) (1=Original, 2=Revised) | Yes | 1 (Original) |
| Status | Budget status | [IATI BudgetStatus code](https://iatistandard.org/en/iati-standard/203/codelists/budgetstatus/) (1=Indicative, 2=Committed) | Yes | 2 (Committed) |
| Period Start | Start of budget period | YYYY-MM-DD | Yes | 2023-01-01 |
| Period End | End of budget period | YYYY-MM-DD | Yes | 2023-12-31 |
| Amount | Value of budget | Number | Yes | 1500000 |
| Currency | Currency of budget | [ISO 4217 3-letter code](https://iatistandard.org/en/iati-standard/203/codelists/currency/) | Yes | USD |
| Value Date | Exchange rate date | YYYY-MM-DD | Yes | 2023-01-01 |

#### 6.2. Transactions

For each financial transaction:

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Transaction Type | Type of transaction | [IATI TransactionType code](https://iatistandard.org/en/iati-standard/203/codelists/transactiontype/) | Yes | 3 (Disbursement) |
| Transaction Date | Date of transaction | YYYY-MM-DD | Yes | 2023-03-15 |
| Amount | Transaction amount | Number | Yes | 500000 |
| Currency | Currency of transaction | [ISO 4217 3-letter code](https://iatistandard.org/en/iati-standard/203/codelists/currency/) | Yes | USD |
| Value Date | Exchange rate date | YYYY-MM-DD | Yes | 2023-03-15 |
| Provider Organization | Organization providing the funds | Text | For incoming funds | "World Bank" |
| Receiver Organization | Organization receiving the funds | Text | For outgoing funds | "Ministry of Education, Honduras" |
| Finance Type | Type of finance | [IATI FinanceType code](https://iatistandard.org/en/iati-standard/203/codelists/financetype/) | If available | 110 (Standard Grant) |
| Flow Type | Type of flow | [IATI FlowType code](https://iatistandard.org/en/iati-standard/203/codelists/flowtype/) | If available | 10 (ODA) |

### 7. Results (if available)

For each result being tracked:

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Result Type | Type of result | [IATI ResultType code](https://iatistandard.org/en/iati-standard/203/codelists/resulttype/) (1=Output, 2=Outcome, etc.) | Yes | 2 (Outcome) |
| Result Title | Title of the result | Text | Yes | "Increased access to education" |
| Result Description | Description of the result | Text | Yes | "Measure of increased school enrollment in target areas" |
| Indicator Title | Title of the indicator | Text | Yes | "School enrollment rate" |
| Indicator Description | Description of the indicator | Text | Yes | "Percentage of school-age children enrolled" |
| Indicator Measure | Type of measurement | [IATI IndicatorMeasure code](https://iatistandard.org/en/iati-standard/203/codelists/indicatormeasure/) | Yes | 2 (Percentage) |
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
| Document Category | Type of document | [IATI DocumentCategory code](https://iatistandard.org/en/iati-standard/203/codelists/documentcategory/) | Yes | A02 (Objectives) |

## Policy Markers (if applicable)

For each policy marker that applies to the activity:

| Field | Description | Format | Required | Example |
|-------|-------------|--------|----------|---------|
| Policy Marker | Type of policy | [IATI PolicyMarker code](https://iatistandard.org/en/iati-standard/203/codelists/policymarker/) | Yes | 1 (Gender Equality) |
| Significance | Degree of focus | [IATI PolicySignificance code](https://iatistandard.org/en/iati-standard/203/codelists/policysignificance/) | Yes | 1 (Significant Objective) |

## Data Validation Notes

1. **Activity Identifiers**: Must start with your organization's identifier followed by a hyphen and a unique code.
2. **Dates**: All dates must be in YYYY-MM-DD format.
3. **Percentages**: When multiple countries, regions or sectors are listed, percentages should add up to 100%.
4. **Currency**: Use standard 3-letter ISO currency codes (USD, EUR, GBP, etc.).
5. **Country Codes**: Use standard ISO 2-letter country codes (HN, SV, GT, NI, CR, PA, etc.).
6. **Sector Codes**: Use the OECD DAC 5-digit purpose codes.
7. **Codelist Values**: All fields with specific codelists must use the exact code values from the linked IATI standard codelists.

## Additional Information Needed

If you have any of the following information, please include it:

1. **Default Currency**: The main currency used for the activity (use [ISO 4217 code](https://iatistandard.org/en/iati-standard/203/codelists/currency/))
2. **Humanitarian Flag**: Whether the activity is humanitarian in nature (Yes/No)
3. **Related Activities**: If this activity is related to other activities you report (specify [RelatedActivityType code](https://iatistandard.org/en/iati-standard/203/codelists/relatedactivitytype/))
4. **Collaboration Type**: Type of collaboration (use [CollaborationType code](https://iatistandard.org/en/iati-standard/203/codelists/collaborationtype/))
5. **Aid Type**: Type of aid (use [AidType code](https://iatistandard.org/en/iati-standard/203/codelists/aidtype/))

## Questions?

If you're unsure about any data field or need clarification on format requirements, please contact our team at [your-email@example.com].

## Next Steps

1. Compile your data in a CSV or Excel file following the structure above
2. Include one row per activity with columns matching the fields described
3. Send your completed file to us by [deadline]
4. Our team will validate the data and convert it to IATI XML format
5. We'll share the generated IATI file with you for review before publication
