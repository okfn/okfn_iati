# IATI Multi-CSV Data Hierarchy

This document explains how IATI XML data is structured and mapped to the multi-CSV format, clarifying the relationships between different CSV files and their data sources.

## Overview of IATI XML Structure

IATI XML follows a hierarchical structure where each `<iati-activity>` contains multiple nested elements:

```
<iati-activities>
  <iati-activity>
    ├── Basic Activity Info (identifier, title, description, dates)
    ├── Reporting Organization
    ├── Participating Organizations (multiple)
    ├── Recipient Countries/Regions (multiple)
    ├── Sectors (multiple)
    ├── Budgets (multiple)
    │   └── Budget Periods
    ├── Transactions (multiple)
    │   ├── Provider/Receiver Organizations
    │   └── Financial Details
    ├── Locations (multiple)
    │   ├── Geographic Coordinates
    │   └── Administrative Areas
    ├── Document Links (multiple)
    ├── Results (multiple)
    │   └── Indicators (multiple)
    │       ├── Baselines
    │       ├── Targets
    │       └── Actual Values
    └── Contact Information (multiple)
```

## Multi-CSV Data Mapping

The multi-CSV converter flattens this hierarchical structure into related tables, preserving relationships through the `activity_identifier` foreign key.

### 1. activities.csv (Parent Table)
**Source**: `<iati-activity>` root element and its direct child elements
**Purpose**: Main activity information and one-to-one relationships

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | `<iati-identifier>` | Unique activity ID (PRIMARY KEY) |
| `title` | `<title><narrative>` | Activity title |
| `description` | `<description><narrative>` | Activity description |
| `activity_status` | `<iati-activity>` @activity-status | Current status code |
| `activity_scope` | `<activity-scope>` @code | Geographic scope |
| `default_currency` | `<iati-activity>` @default-currency | Default currency |
| `humanitarian` | `<iati-activity>` @humanitarian | Humanitarian flag |
| `hierarchy` | `<iati-activity>` @hierarchy | Hierarchy level |
| `last_updated_datetime` | `<iati-activity>` @last-updated-datetime | Last update |
| `xml_lang` | `<iati-activity>` @xml:lang | Language |
| `reporting_org_*` | `<reporting-org>` | Reporting organization details |
| `planned_start_date` | `<activity-date>` type="1" | Planned start |
| `actual_start_date` | `<activity-date>` type="2" | Actual start |
| `planned_end_date` | `<activity-date>` type="3" | Planned end |
| `actual_end_date` | `<activity-date>` type="4" | Actual end |
| `recipient_country_*` | `<recipient-country>` (first/primary) | Primary country |
| `recipient_region_*` | `<recipient-region>` (first/primary) | Primary region |
| `collaboration_type` | `<collaboration-type>` @code | Collaboration type |
| `default_flow_type` | `<default-flow-type>` @code | Default flow type |
| `default_finance_type` | `<default-finance-type>` @code | Default finance type |
| `default_aid_type` | `<default-aid-type>` @code | Default aid type |
| `default_tied_status` | `<default-tied-status>` @code | Default tied status |

### 2. participating_orgs.csv (One-to-Many)
**Source**: `<participating-org>` elements
**Purpose**: Organizations involved in the activity

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `org_ref` | `<participating-org>` @ref | Organization reference |
| `org_name` | `<participating-org><narrative>` | Organization name |
| `org_type` | `<participating-org>` @type | Organization type code |
| `role` | `<participating-org>` @role | Role code (1=Funding, 4=Implementing) |
| `activity_id` | `<participating-org>` @activity-id | Related activity ID |
| `crs_channel_code` | `<participating-org>` @crs-channel-code | CRS channel code |

**Relationship**: `activities.activity_identifier = participating_orgs.activity_identifier`

### 3. sectors.csv (One-to-Many)
**Source**: `<sector>` elements
**Purpose**: Sector classifications for the activity

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `sector_code` | `<sector>` @code | DAC sector code |
| `sector_name` | `<sector><narrative>` | Sector name |
| `vocabulary` | `<sector>` @vocabulary | Vocabulary used |
| `percentage` | `<sector>` @percentage | Percentage allocation |
| `vocabulary_uri` | `<sector>` @vocabulary-uri | Vocabulary URI |

**Relationship**: `activities.activity_identifier = sectors.activity_identifier`

### 4. budgets.csv (One-to-Many)
**Source**: `<budget>` elements
**Purpose**: Budget information by period

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `budget_type` | `<budget>` @type | Budget type (1=Original, 2=Revised) |
| `status` | `<budget>` @status | Budget status |
| `period_start` | `<budget><period-start>` @iso-date | Period start date |
| `period_end` | `<budget><period-end>` @iso-date | Period end date |
| `amount` | `<budget><value>` | Budget amount |
| `currency` | `<budget><value>` @currency | Currency code |
| `value_date` | `<budget><value>` @value-date | Value date |

**Relationship**: `activities.activity_identifier = budgets.activity_identifier`

### 5. transactions.csv (One-to-Many)
**Source**: `<transaction>` elements
**Purpose**: Financial transactions (disbursements, commitments, etc.)

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `transaction_type` | `<transaction><transaction-type>` @code | Transaction type |
| `transaction_date` | `<transaction><transaction-date>` @iso-date | Transaction date |
| `amount` | `<transaction><value>` | Transaction amount |
| `currency` | `<transaction><value>` @currency | Currency |
| `value_date` | `<transaction><value>` @value-date | Value date |
| `provider_org_ref` | `<transaction><provider-org>` @ref | Provider org reference |
| `provider_org_name` | `<transaction><provider-org><narrative>` | Provider org name |
| `provider_org_type` | `<transaction><provider-org>` @type | Provider org type |
| `receiver_org_ref` | `<transaction><receiver-org>` @ref | Receiver org reference |
| `receiver_org_name` | `<transaction><receiver-org><narrative>` | Receiver org name |
| `receiver_org_type` | `<transaction><receiver-org>` @type | Receiver org type |
| `finance_type` | `<transaction><finance-type>` @code | Finance type |
| `flow_type` | `<transaction><flow-type>` @code | Flow type |
| `aid_type` | `<transaction><aid-type>` @code | Aid type |
| `tied_status` | `<transaction><tied-status>` @code | Tied status |
| `disbursement_channel` | `<transaction><disbursement-channel>` @code | Disbursement channel |
| `recipient_country_code` | `<transaction><recipient-country>` @code | Recipient country |
| `recipient_region_code` | `<transaction><recipient-region>` @code | Recipient region |
| `description` | `<transaction><description><narrative>` | Transaction description |

**Relationship**: `activities.activity_identifier = transactions.activity_identifier`

### 6. locations.csv (One-to-Many)
**Source**: `<location>` elements
**Purpose**: Geographic information and specific locations

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `location_ref` | `<location>` @ref | Location reference |
| `location_id` | `<location><location-id>` @code | Location ID |
| `name` | `<location><name><narrative>` | Location name |
| `description` | `<location><description><narrative>` | Location description |
| `location_type` | `<location><location-type>` @code | Location type |
| `location_reach` | `<location><location-reach>` @code | Location reach |
| `location_class` | `<location><location-class>` @code | Location class |
| `feature_designation` | `<location><feature-designation>` @code | Feature designation |
| `coordinates_latitude` | `<location><point><pos>` | Latitude |
| `coordinates_longitude` | `<location><point><pos>` | Longitude |
| `coordinates_precision` | `<location><point>` @precision | Coordinate precision |
| `administrative_country` | `<location><administrative>` @country | Administrative country |
| `administrative_adm1` | `<location><administrative>` @adm1 | Administrative level 1 |
| `administrative_adm2` | `<location><administrative>` @adm2 | Administrative level 2 |
| `exactness` | `<location><exactness>` @code | Location exactness |
| `activity_description` | `<location><activity-description><narrative>` | Activity at location |

**Relationship**: `activities.activity_identifier = locations.activity_identifier`

### 7. documents.csv (One-to-Many)
**Source**: `<document-link>` elements
**Purpose**: Document attachments and links

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `url` | `<document-link>` @url | Document URL |
| `format` | `<document-link>` @format | MIME type |
| `title` | `<document-link><title><narrative>` | Document title |
| `description` | `<document-link><description><narrative>` | Document description |
| `category_code` | `<document-link><category>` @code | Document category |
| `category_name` | Document category name lookup | Category name |
| `language_code` | `<document-link><language>` @code | Document language |

**Relationship**: `activities.activity_identifier = documents.activity_identifier`

### 8. results.csv (One-to-Many)
**Source**: `<result>` elements
**Purpose**: Results framework (outcomes, outputs)

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `result_type` | `<result>` @type | Result type (1=Output, 2=Outcome) |
| `aggregation_status` | `<result>` @aggregation-status | Aggregation status |
| `title` | `<result><title><narrative>` | Result title |
| `description` | `<result><description><narrative>` | Result description |
| `result_ref` | `<result>` @ref | Result reference |

**Relationship**: `activities.activity_identifier = results.activity_identifier`

### 9. indicators.csv (One-to-Many with Results)
**Source**: `<result><indicator>` elements
**Purpose**: Performance indicators with baselines, targets, and actuals

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `result_ref` | Parent `<result>` @ref | FOREIGN KEY to results |
| `indicator_ref` | `<indicator>` @ref | Indicator reference |
| `measure` | `<indicator>` @measure | Measurement type |
| `ascending` | `<indicator>` @ascending | Ascending indicator |
| `aggregation_status` | `<indicator>` @aggregation-status | Aggregation status |
| `title` | `<indicator><title><narrative>` | Indicator title |
| `description` | `<indicator><description><narrative>` | Indicator description |
| `baseline_year` | `<indicator><baseline>` @year | Baseline year |
| `baseline_value` | `<indicator><baseline>` @value | Baseline value |
| `target_value` | `<indicator><target>` @value | Target value |

**Relationships**: 
- `activities.activity_identifier = indicators.activity_identifier`
- `results.result_ref = indicators.result_ref` (when available)

### 10. contact_info.csv (One-to-Many)
**Source**: `<contact-info>` elements
**Purpose**: Contact information for the activity

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `contact_type` | `<contact-info>` @type | Contact type |
| `organization` | `<contact-info><organisation><narrative>` | Organization name |
| `department` | `<contact-info><department><narrative>` | Department |
| `person_name` | `<contact-info><person-name><narrative>` | Person name |
| `job_title` | `<contact-info><job-title><narrative>` | Job title |
| `telephone` | `<contact-info><telephone>` | Phone number |
| `email` | `<contact-info><email>` | Email address |
| `website` | `<contact-info><website>` | Website URL |
| `mailing_address` | `<contact-info><mailing-address><narrative>` | Mailing address |

**Relationship**: `activities.activity_identifier = contact_info.activity_identifier`

## Data Extraction Rules

### Handling Multiple Values
When XML elements can appear multiple times (e.g., multiple countries, sectors), the converter:

1. **Primary Country/Region**: The first `<recipient-country>` or `<recipient-region>` goes to `activities.csv`
2. **Additional Countries/Regions**: Currently not extracted to separate tables (future enhancement)
3. **All Organizations**: Each `<participating-org>` becomes a row in `participating_orgs.csv`
4. **All Sectors**: Each `<sector>` becomes a row in `sectors.csv`
5. **All Budgets**: Each `<budget>` becomes a row in `budgets.csv`
6. **All Transactions**: Each `<transaction>` becomes a row in `transactions.csv`

### Date Handling
Activity dates are mapped by type code:
- Type 1 (Planned start) → `planned_start_date`
- Type 2 (Actual start) → `actual_start_date`
- Type 3 (Planned end) → `planned_end_date`
- Type 4 (Actual end) → `actual_end_date`

### Narrative Elements
Multi-language `<narrative>` elements are handled by:
- Taking the first narrative in the default language
- Falling back to the first available narrative if default language not found
- Preserving language information in `xml_lang` field

### Missing Data
- Empty cells in CSV indicate missing XML elements
- Default values are not applied during extraction
- Optional fields may be empty

## Using the Hierarchy

### Joining Data Across Files
To reconstruct complete activity information:

```sql
SELECT a.title, po.org_name, s.sector_name, t.amount
FROM activities a
LEFT JOIN participating_orgs po ON a.activity_identifier = po.activity_identifier
LEFT JOIN sectors s ON a.activity_identifier = s.activity_identifier  
LEFT JOIN transactions t ON a.activity_identifier = t.activity_identifier
WHERE a.activity_identifier = 'US-GOV-1-7200AA18C00086'
```

### Working with Specific Data Types
- **Financial Analysis**: Use `budgets.csv` and `transactions.csv`
- **Geographic Analysis**: Use `activities.csv` (primary country) and `locations.csv` (detailed locations)
- **Organizational Analysis**: Use `participating_orgs.csv`
- **Results Tracking**: Use `results.csv` and `indicators.csv`

This hierarchy structure ensures that:
1. Data integrity is maintained through foreign key relationships
2. Each CSV file is focused and manageable
3. Complex IATI structures are preserved in a relational format
4. Users can work with specific aspects of the data independently
5. The data can be reconstructed into valid IATI XML format
