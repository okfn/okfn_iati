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
    │   ├── Transaction Sectors (multiple)
    │   └── Financial Details
    ├── Locations (multiple)
    │   ├── Geographic Coordinates
    │   └── Administrative Areas
    ├── Document Links (multiple)
    ├── Results (multiple)
    │   └── Indicators (multiple)
    │       ├── Baselines
    │       ├── Targets (via Periods)
    │       └── Actual Values (via Periods)
    ├── Contact Information (multiple)
    ├── Conditions (multiple)
    ├── Country Budget Items (multiple)
    └── Descriptions (multiple, by type)
```

## Multi-CSV Data Mapping

The multi-CSV converter flattens this hierarchical structure into related tables, preserving relationships through the `activity_identifier` foreign key.

### CSV Files Overview

The converter generates the following CSV files:

| # | File | Description |
|---|------|-------------|
| 1 | `activities.csv` | Main activity information (parent table) |
| 2 | `participating_orgs.csv` | Organizations participating in activities |
| 3 | `sectors.csv` | Sector classifications |
| 4 | `budgets.csv` | Budget information |
| 5 | `transactions.csv` | Financial transactions |
| 6 | `transaction_sectors.csv` | Sectors specific to transactions |
| 7 | `locations.csv` | Geographic locations |
| 8 | `documents.csv` | Document links |
| 9 | `results.csv` | Results framework |
| 10 | `indicators.csv` | Performance indicators |
| 11 | `indicator_periods.csv` | Indicator period targets and actuals |
| 12 | `activity_date.csv` | Activity dates with narratives |
| 13 | `contact_info.csv` | Contact information |
| 14 | `conditions.csv` | Activity conditions |
| 15 | `descriptions.csv` | Multiple descriptions by type |
| 16 | `country_budget_items.csv` | Country budget items |

---

### 1. activities.csv (Parent Table)
**Source**: `<iati-activity>` root element and its direct child elements
**Purpose**: Main activity information and one-to-one relationships

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | `<iati-identifier>` | Unique activity ID (PRIMARY KEY) |
| `title` | `<title><narrative>` | Activity title |
| `title_lang` | `<title><narrative>` @xml:lang | Title language code |
| `description` | `<description><narrative>` | Activity description (type 1 or first) |
| `description_lang` | `<description><narrative>` @xml:lang | Description language code |
| `activity_status` | `<activity-status>` @code | Current status code |
| `activity_scope` | `<activity-scope>` @code | Geographic scope |
| `default_currency` | `<iati-activity>` @default-currency | Default currency |
| `humanitarian` | `<iati-activity>` @humanitarian | Humanitarian flag ("", "0", "1") |
| `hierarchy` | `<iati-activity>` @hierarchy | Hierarchy level |
| `last_updated_datetime` | `<iati-activity>` @last-updated-datetime | Last update timestamp |
| `xml_lang` | `<iati-activity>` @xml:lang | Default language |
| `reporting_org_ref` | `<reporting-org>` @ref | Reporting org reference |
| `reporting_org_name` | `<reporting-org><narrative>` | Reporting org name |
| `reporting_org_name_lang` | `<reporting-org><narrative>` @xml:lang | Reporting org name language |
| `reporting_org_type` | `<reporting-org>` @type | Reporting org type code |
| `reporting_org_role` | `<reporting-org>` @role | Reporting org role code, default 4: Implementing |
| `reporting_org_secondary_reporter` | `<reporting-org>` @secondary-reporter | Secondary reporter flag |
| `planned_start_date` | `<activity-date>` type="1" | Planned start date |
| `actual_start_date` | `<activity-date>` type="2" | Actual start date |
| `planned_end_date` | `<activity-date>` type="3" | Planned end date |
| `actual_end_date` | `<activity-date>` type="4" | Actual end date |
| `recipient_country_code` | `<recipient-country>` @code | Primary country code |
| `recipient_country_percentage` | `<recipient-country>` @percentage | Country percentage |
| `recipient_country_name` | `<recipient-country><narrative>` | Country name |
| `recipient_country_lang` | `<recipient-country><narrative>` @xml:lang | Country name language |
| `recipient_region_code` | `<recipient-region>` @code | Primary region code |
| `recipient_region_percentage` | `<recipient-region>` @percentage | Region percentage |
| `recipient_region_name` | `<recipient-region><narrative>` | Region name |
| `recipient_region_lang` | `<recipient-region><narrative>` @xml:lang | Region name language |
| `collaboration_type` | `<collaboration-type>` @code | Collaboration type code |
| `default_flow_type` | `<default-flow-type>` @code | Default flow type code |
| `default_finance_type` | `<default-finance-type>` @code | Default finance type code |
| `default_aid_type` | `<default-aid-type>` @code | Default aid type code |
| `default_tied_status` | `<default-tied-status>` @code | Default tied status code |
| `conditions_attached` | `<conditions>` @attached | Conditions attached flag |

### 2. participating_orgs.csv (One-to-Many)
**Source**: `<participating-org>` elements
**Purpose**: Organizations involved in the activity

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `org_ref` | `<participating-org>` @ref | Organization reference |
| `org_name` | `<participating-org><narrative>` | Organization name |
| `org_name_lang` | `<participating-org><narrative>` @xml:lang | Name language code |
| `org_type` | `<participating-org>` @type | Organization type code |
| `role` | `<participating-org>` @role | Role code (1=Funding, 2=Accountable, 3=Extending, 4=Implementing) |
| `activity_id` | `<participating-org>` @activity-id | Related activity ID |
| `crs_channel_code` | `<participating-org>` @crs-channel-code | CRS channel code |

**Relationship**: `activities.activity_identifier = participating_orgs.activity_identifier`

---

### 3. sectors.csv (One-to-Many)
**Source**: `<sector>` elements
**Purpose**: Sector classifications for the activity

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `sector_code` | `<sector>` @code | Sector code |
| `sector_name` | `<sector><narrative>` | Sector name |
| `vocabulary` | `<sector>` @vocabulary | Vocabulary used (default: 1=DAC) |
| `vocabulary_uri` | `<sector>` @vocabulary-uri | Vocabulary URI |
| `percentage` | `<sector>` @percentage | Percentage allocation |

**Relationship**: `activities.activity_identifier = sectors.activity_identifier`

---

### 4. budgets.csv (One-to-Many)
**Source**: `<budget>` elements
**Purpose**: Budget information by period

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `budget_type` | `<budget>` @type | Budget type (1=Original, 2=Revised) |
| `budget_status` | `<budget>` @status | Budget status (1=Indicative, 2=Committed) |
| `period_start` | `<budget><period-start>` @iso-date | Period start date |
| `period_end` | `<budget><period-end>` @iso-date | Period end date |
| `value` | `<budget><value>` | Budget amount |
| `currency` | `<budget><value>` @currency | Currency code |
| `value_date` | `<budget><value>` @value-date | Value date |

**Relationship**: `activities.activity_identifier = budgets.activity_identifier`

---

### 5. transactions.csv (One-to-Many)
**Source**: `<transaction>` elements
**Purpose**: Financial transactions (disbursements, commitments, etc.)

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `transaction_ref` | `<transaction>` @ref | Transaction reference |
| `transaction_type` | `<transaction><transaction-type>` @code | Transaction type |
| `transaction_date` | `<transaction><transaction-date>` @iso-date | Transaction date |
| `value` | `<transaction><value>` | Transaction amount |
| `currency` | `<transaction><value>` @currency | Currency |
| `value_date` | `<transaction><value>` @value-date | Value date |
| `description` | `<transaction><description><narrative>` | Transaction description |
| `description_lang` | `<transaction><description><narrative>` @xml:lang | Description language |
| `provider_org_ref` | `<transaction><provider-org>` @ref | Provider org reference |
| `provider_org_name` | `<transaction><provider-org><narrative>` | Provider org name |
| `provider_org_lang` | `<transaction><provider-org><narrative>` @xml:lang | Provider org name language |
| `provider_org_type` | `<transaction><provider-org>` @type | Provider org type |
| `receiver_org_ref` | `<transaction><receiver-org>` @ref | Receiver org reference |
| `receiver_org_name` | `<transaction><receiver-org><narrative>` | Receiver org name |
| `receiver_org_lang` | `<transaction><receiver-org><narrative>` @xml:lang | Receiver org name language |
| `receiver_org_type` | `<transaction><receiver-org>` @type | Receiver org type |
| `receiver_org_activity_id` | `<transaction><receiver-org>` @receiver-activity-id | Receiver activity ID |
| `disbursement_channel` | `<transaction><disbursement-channel>` @code | Disbursement channel |
| `flow_type` | `<transaction><flow-type>` @code | Flow type |
| `finance_type` | `<transaction><finance-type>` @code | Finance type |
| `aid_type` | `<transaction><aid-type>` @code | Aid type |
| `tied_status` | `<transaction><tied-status>` @code | Tied status |
| `humanitarian` | `<transaction>` @humanitarian | Humanitarian flag ("", "0", "1") |
| `recipient_region` | `<transaction><recipient-region>` @code | Recipient region code |

**Relationship**: `activities.activity_identifier = transactions.activity_identifier`

---

### 6. transaction_sectors.csv (One-to-Many with Transactions)
**Source**: `<transaction><sector>` elements
**Purpose**: Sectors specific to individual transactions

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY to activities |
| `transaction_ref` | Parent `<transaction>` @ref | FOREIGN KEY to transactions |
| `transaction_type` | Parent `<transaction><transaction-type>` @code | Transaction type (for identification) |
| `sector_code` | `<transaction><sector>` @code | Sector code |
| `sector_name` | `<transaction><sector><narrative>` | Sector name |
| `vocabulary` | `<transaction><sector>` @vocabulary | Vocabulary used |
| `vocabulary_uri` | `<transaction><sector>` @vocabulary-uri | Vocabulary URI |

**Relationships**:
- `activities.activity_identifier = transaction_sectors.activity_identifier`
- `transactions.transaction_ref = transaction_sectors.transaction_ref`

---

### 7. locations.csv (One-to-Many)
**Source**: `<location>` elements
**Purpose**: Geographic information and specific locations

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `location_ref` | `<location>` @ref | Location reference |
| `location_reach` | `<location>` @reach | Location reach code |
| `location_id_vocabulary` | `<location><location-id>` @vocabulary | Location ID vocabulary |
| `location_id_code` | `<location><location-id>` @code | Location ID code |
| `name` | `<location><name><narrative>` | Location name |
| `name_lang` | `<location><name><narrative>` @xml:lang | Name language |
| `description` | `<location><description><narrative>` | Location description |
| `description_lang` | `<location><description><narrative>` @xml:lang | Description language |
| `activity_description` | `<location><activity-description><narrative>` | Activity at location |
| `activity_description_lang` | `<location><activity-description><narrative>` @xml:lang | Activity description language |
| `latitude` | `<location><point><pos>` | Latitude (first coordinate) |
| `longitude` | `<location><point><pos>` | Longitude (second coordinate) |
| `exactness` | `<location>` @exactness | Location exactness code |
| `location_class` | `<location>` @class | Location class code |
| `feature_designation` | `<location>` @feature-designation | Feature designation code |
| `administrative_vocabulary` | `<location><administrative>` @vocabulary | Admin vocabulary |
| `administrative_level` | `<location><administrative>` @level | Admin level |
| `administrative_code` | `<location><administrative>` @code | Admin code |
| `administrative_country` | `<location><administrative>` @country | Admin country |

**Relationship**: `activities.activity_identifier = locations.activity_identifier`

---

### 8. documents.csv (One-to-Many)
**Source**: `<document-link>` elements
**Purpose**: Document attachments and links

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `url` | `<document-link>` @url | Document URL |
| `format` | `<document-link>` @format | MIME type |
| `title` | `<document-link><title><narrative>` | Document title |
| `title_lang` | `<document-link><title><narrative>` @xml:lang | Title language |
| `description` | `<document-link><description><narrative>` | Document description |
| `description_lang` | `<document-link><description><narrative>` @xml:lang | Description language |
| `category_code` | `<document-link><category>` @code | Document category code |
| `language_code` | `<document-link><language>` @code | Document language code |
| `document_date` | `<document-link>` @document-date | Document date |

**Relationship**: `activities.activity_identifier = documents.activity_identifier`

---

### 9. results.csv (One-to-Many)
**Source**: `<result>` elements
**Purpose**: Results framework (outcomes, outputs)

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `result_ref` | `<result>` @ref | Result reference (auto-generated if missing) |
| `result_type` | `<result>` @type | Result type (1=Output, 2=Outcome, 3=Impact, 4=Other) |
| `aggregation_status` | `<result>` @aggregation-status | Aggregation status |
| `title` | `<result><title><narrative>` | Result title |
| `description` | `<result><description><narrative>` | Result description |

**Relationship**: `activities.activity_identifier = results.activity_identifier`

---

### 10. indicators.csv (One-to-Many with Results)
**Source**: `<result><indicator>` elements
**Purpose**: Performance indicators with baselines

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY to activities |
| `result_ref` | Parent `<result>` @ref | FOREIGN KEY to results |
| `indicator_ref` | Generated | Indicator reference (auto-generated) |
| `indicator_measure` | `<indicator>` @measure | Measurement type (1=Unit, 2=Percentage, etc.) |
| `ascending` | `<indicator>` @ascending | Ascending indicator (true/false) |
| `aggregation_status` | `<indicator>` @aggregation-status | Aggregation status |
| `title` | `<indicator><title><narrative>` | Indicator title |
| `description` | `<indicator><description><narrative>` | Indicator description |
| `baseline_year` | `<indicator><baseline>` @year | Baseline year |
| `baseline_iso_date` | `<indicator><baseline>` @iso-date | Baseline ISO date |
| `baseline_value` | `<indicator><baseline>` @value | Baseline value |
| `baseline_comment` | `<indicator><baseline><comment><narrative>` | Baseline comment |

**Relationships**:
- `activities.activity_identifier = indicators.activity_identifier`
- `results.result_ref = indicators.result_ref`

---

### 11. indicator_periods.csv (One-to-Many with Indicators)
**Source**: `<result><indicator><period>` elements
**Purpose**: Time-based targets and actual values for indicators

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY to activities |
| `result_ref` | Parent `<result>` @ref | FOREIGN KEY to results |
| `indicator_ref` | Parent indicator ref | FOREIGN KEY to indicators |
| `period_start` | `<period><period-start>` @iso-date | Period start date |
| `period_end` | `<period><period-end>` @iso-date | Period end date |
| `target_value` | `<period><target>` @value | Target value |
| `target_comment` | `<period><target><comment><narrative>` | Target comment |
| `actual_value` | `<period><actual>` @value | Actual value |
| `actual_comment` | `<period><actual><comment><narrative>` | Actual comment |

**Relationships**:
- `activities.activity_identifier = indicator_periods.activity_identifier`
- `indicators.indicator_ref = indicator_periods.indicator_ref`

---

### 12. activity_date.csv (One-to-Many)
**Source**: `<activity-date>` elements
**Purpose**: Activity dates with optional narratives (for non-standard date handling)

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `type` | `<activity-date>` @type | Date type (1-4) |
| `iso_date` | `<activity-date>` @iso-date | ISO date |
| `narrative` | `<activity-date><narrative>` | Date narrative (optional) |
| `narrative_lang` | `<activity-date><narrative>` @xml:lang | Narrative language |

**Relationship**: `activities.activity_identifier = activity_date.activity_identifier`

**Note**: Standard date types (1-4) are also flattened into activities.csv for convenience.

---

### 13. contact_info.csv (One-to-Many)
**Source**: `<contact-info>` elements
**Purpose**: Contact information for the activity

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `contact_type` | `<contact-info>` @type | Contact type code |
| `organisation` | `<contact-info><organisation><narrative>` | Organization name |
| `organisation_lang` | `<contact-info><organisation><narrative>` @xml:lang | Organization name language |
| `department` | `<contact-info><department><narrative>` | Department name |
| `department_lang` | `<contact-info><department><narrative>` @xml:lang | Department name language |
| `person_name` | `<contact-info><person-name><narrative>` | Person name |
| `person_name_lang` | `<contact-info><person-name><narrative>` @xml:lang | Person name language |
| `person_name_present` | Element presence check | "1" if present, "0" if not |
| `job_title` | `<contact-info><job-title><narrative>` | Job title |
| `job_title_lang` | `<contact-info><job-title><narrative>` @xml:lang | Job title language |
| `telephone` | `<contact-info><telephone>` | Phone number |
| `email` | `<contact-info><email>` | Email address |
| `email_present` | Element presence check | "1" if present, "0" if not |
| `website` | `<contact-info><website>` | Website URL |
| `mailing_address` | `<contact-info><mailing-address><narrative>` | Mailing address |
| `mailing_address_lang` | `<contact-info><mailing-address><narrative>` @xml:lang | Address language |

**Relationship**: `activities.activity_identifier = contact_info.activity_identifier`

---

### 14. conditions.csv (One-to-Many)
**Source**: `<conditions><condition>` elements
**Purpose**: Activity conditions

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `condition_type` | `<condition>` @type | Condition type code |
| `condition_text` | `<condition><narrative>` | Condition text |

**Relationship**: `activities.activity_identifier = conditions.activity_identifier`

---

### 15. descriptions.csv (One-to-Many)
**Source**: `<description>` elements (all types, all narratives)
**Purpose**: Multiple descriptions with types and multi-language support

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `description_type` | `<description>` @type | Description type (1-4) |
| `description_sequence` | Order index | Sequence of description element |
| `narrative` | `<description><narrative>` | Description text |
| `narrative_lang` | `<description><narrative>` @xml:lang | Narrative language |
| `narrative_sequence` | Order index | Sequence of narrative within description |

**Relationship**: `activities.activity_identifier = descriptions.activity_identifier`

**Note**: This table captures ALL descriptions and narratives, unlike activities.csv which only captures the first.

---

### 16. country_budget_items.csv (One-to-Many)
**Source**: `<country-budget-items><budget-item>` elements
**Purpose**: Country budget item breakdowns

| CSV Column | XML Source | Description |
|------------|------------|-------------|
| `activity_identifier` | Parent `<iati-identifier>` | FOREIGN KEY |
| `vocabulary` | `<country-budget-items>` @vocabulary | Budget vocabulary |
| `budget_item_code` | `<budget-item>` @code | Budget item code |
| `budget_item_percentage` | `<budget-item>` @percentage | Percentage allocation |
| `description` | `<budget-item><description><narrative>` | Item description |
| `description_lang` | `<budget-item><description><narrative>` @xml:lang | Description language |

**Relationship**: `activities.activity_identifier = country_budget_items.activity_identifier`

---

## Data Extraction Rules

### Handling Multiple Values
When XML elements can appear multiple times (e.g., multiple countries, sectors), the converter:

1. **Primary Country/Region**: The first `<recipient-country>` or `<recipient-region>` goes to `activities.csv`
2. **Additional Countries/Regions**: Currently not extracted to separate tables (future enhancement)
3. **All Organizations**: Each `<participating-org>` becomes a row in `participating_orgs.csv`
4. **All Sectors**: Each `<sector>` becomes a row in `sectors.csv`
5. **All Budgets**: Each `<budget>` becomes a row in `budgets.csv`
6. **All Transactions**: Each `<transaction>` becomes a row in `transactions.csv`
7. **Transaction Sectors**: Each `<transaction><sector>` becomes a row in `transaction_sectors.csv`
8. **All Descriptions**: Each `<description>` with all narratives goes to `descriptions.csv`
9. **All Conditions**: Each `<condition>` becomes a row in `conditions.csv`

### Date Handling
Activity dates are mapped by type code:
- Type 1 (Planned start) → `planned_start_date` in activities.csv
- Type 2 (Actual start) → `actual_start_date` in activities.csv
- Type 3 (Planned end) → `planned_end_date` in activities.csv
- Type 4 (Actual end) → `actual_end_date` in activities.csv

Additionally, all activity dates (with narratives) are stored in `activity_date.csv` for complete preservation.

### Narrative Elements and Language Attributes
Multi-language `<narrative>` elements are handled by:
- Extracting the text content of the narrative
- Preserving the `xml:lang` attribute in a corresponding `*_lang` column
- For main activity: `title_lang`, `description_lang`, `reporting_org_name_lang`, etc.
- For child elements: Similar `*_lang` columns are provided

### Humanitarian Flag Handling
The `humanitarian` attribute (on activities and transactions) preserves exact values:
- Empty string `""`: Attribute not present in source XML
- `"0"`: Explicitly set to false
- `"1"`: Explicitly set to true

### Element Presence Tracking
Some CSV files include `*_present` columns to track whether an element existed in the XML:
- `contact_info.csv`: `person_name_present`, `email_present`
- This helps distinguish between empty values and missing elements

### Missing Data
- Empty cells in CSV indicate missing XML elements
- Default values are not applied during extraction
- Optional fields may be empty

---

## Entity Relationship Diagram

```
                                  ┌──────────────────┐
                                  │   activities     │
                                  │   (Parent)       │
                                  │                  │
                                  │ PK: activity_    │
                                  │     identifier   │
                                  └────────┬─────────┘
                                           │
           ┌───────────────────────────────┼───────────────────────────────┐
           │                               │                               │
           │                               │                               │
    ┌──────┴──────┐                 ┌──────┴──────┐                 ┌──────┴──────┐
    │participating│                 │  sectors    │                 │   budgets   │
    │   _orgs     │                 │             │                 │             │
    └─────────────┘                 └─────────────┘                 └─────────────┘
           │                               │                               │
           │                               │                               │
    ┌──────┴──────┐                 ┌──────┴──────┐                 ┌──────┴──────┐
    │transactions │                 │  locations  │                 │  documents  │
    │             │                 │             │                 │             │
    └──────┬──────┘                 └─────────────┘                 └─────────────┘
           │                               │                               │
           │                               │                               │
    ┌──────┴──────┐                 ┌──────┴──────┐                 ┌──────┴──────┐
    │ transaction │                 │   results   │                 │contact_info │
    │  _sectors   │                 │             │                 │             │
    └─────────────┘                 └──────┬──────┘                 └─────────────┘
                                           │
                                           │
                                    ┌──────┴──────┐
                                    │ indicators  │
                                    │             │
                                    └──────┬──────┘
                                           │
                                           │
                                    ┌──────┴──────┐
                                    │ indicator_  │
                                    │  periods    │
                                    └─────────────┘

    Additional tables (not shown in diagram for clarity):
    - activity_date
    - conditions
    - descriptions
    - country_budget_items
```

---

## Using the Hierarchy

### Joining Data Across Files
To reconstruct complete activity information:

```sql
SELECT a.title, po.org_name, s.sector_name, t.value
FROM activities a
LEFT JOIN participating_orgs po ON a.activity_identifier = po.activity_identifier
LEFT JOIN sectors s ON a.activity_identifier = s.activity_identifier
LEFT JOIN transactions t ON a.activity_identifier = t.activity_identifier
WHERE a.activity_identifier = 'US-GOV-1-7200AA18C00086'
```

### Working with Results and Indicators
```sql
SELECT r.title as result_title,
       i.title as indicator_title,
       ip.target_value,
       ip.actual_value
FROM results r
JOIN indicators i ON r.activity_identifier = i.activity_identifier
                  AND r.result_ref = i.result_ref
LEFT JOIN indicator_periods ip ON i.activity_identifier = ip.activity_identifier
                               AND i.indicator_ref = ip.indicator_ref
WHERE r.activity_identifier = 'XM-DAC-47066-12345'
```

### Working with Specific Data Types
- **Financial Analysis**: Use `budgets.csv` and `transactions.csv`
- **Geographic Analysis**: Use `activities.csv` (primary country) and `locations.csv` (detailed locations)
- **Organizational Analysis**: Use `participating_orgs.csv`
- **Results Tracking**: Use `results.csv`, `indicators.csv`, and `indicator_periods.csv`
- **Document Management**: Use `documents.csv`
- **Multi-language Content**: Use `descriptions.csv` for complete multi-narrative support

---

## Limitations

> **Important**: Custom namespace elements (e.g., USAID's `usg:treasury-account`) are **NOT preserved** during XML → CSV → XML conversion. These are organization-specific extensions that don't fit into the standard CSV structure. If you need to preserve custom elements, use XML-to-XML transformations instead.

---

This hierarchy structure ensures that:
1. Data integrity is maintained through foreign key relationships
2. Each CSV file is focused and manageable
3. Complex IATI structures are preserved in a relational format
4. Users can work with specific aspects of the data independently
5. Language attributes are preserved for multilingual content
6. The data can be reconstructed into valid IATI XML format
