[![Python Tests](https://github.com/okfn/okfn_iati/workflows/Python%20IATI%20Tests/badge.svg)](https://github.com/okfn/okfn_iati/actions)

# OKFN IATI XML Handler

A Python library for working with IATI XML data according to the IATI 2.03 standard.

## Features

- Data models that represent IATI XML elements with validation
- XML generator to create valid IATI XML from Python objects
- Support for IATI 2.03 standard
- Enums for standardized code lists
- Data validation to ensure compliance with the standard

## Installation

```bash
pip install okfn-iati
```

## Usage

### Creating an IATI Activity

```python
from okfn_iati import (
    # Main models
    Activity, Narrative, OrganizationRef, ParticipatingOrg, ActivityDate,
    ContactInfo, Location, LocationIdentifier, DocumentLink,
    Budget, Transaction, Result, IatiActivities,
    
    # Enums - use these constants instead of strings
    ActivityStatus, ActivityDateType, TransactionType, BudgetType, BudgetStatus,
    OrganisationRole, OrganisationType, LocationID, DocumentCategory,
    
    # Generator
    IatiXmlGenerator
)

# Create an IATI Activity
activity = Activity(
    iati_identifier="XM-EXAMPLE-12345",
    reporting_org=OrganizationRef(
        ref="XM-EXAMPLE",
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
        ),
        ActivityDate(
            type=ActivityDateType.ACTUAL_START,
            iso_date="2023-01-15"
        )
    ],
    participating_orgs=[
        ParticipatingOrg(
            role=OrganisationRole.FUNDING,
            ref="XM-EXAMPLE-FUNDER",
            type=OrganisationType.GOVERNMENT.value,
            narratives=[Narrative(text="Example Funding Organization")]
        ),
        ParticipatingOrg(
            role=OrganisationRole.IMPLEMENTING,
            ref="XM-EXAMPLE-IMPL",
            narratives=[Narrative(text="Example Implementing Organization")]
        )
    ],
    locations=[
        Location(
            location_id=LocationIdentifier(
                vocabulary=LocationID.GEONAMES,
                code="1234567"
            ),
            name=[Narrative(text="Example Location")]
        )
    ],
    transactions=[
        Transaction(
            type=TransactionType.DISBURSEMENT,
            date="2023-03-15",
            value=50000.00,
            currency="USD"
        )
    ],
    budgets=[
        Budget(
            type=BudgetType.ORIGINAL,
            status=BudgetStatus.INDICATIVE,
            period_start="2023-01-01",
            period_end="2023-12-31",
            value=100000.00,
            currency="USD"
        )
    ],
    document_links=[
        DocumentLink(
            url="https://example.org/docs/report.pdf",
            format="application/pdf",
            title=[Narrative(text="Project Report")],
            categories=[DocumentCategory.OBJECTIVES]
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
