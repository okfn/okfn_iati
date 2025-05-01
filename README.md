# IATI XML Handler

![Python Tests](https://github.com/okfn/okfn-iati/actions/workflows/python-tests.yml/badge.svg)

Python Library to generate and publish IATI XML files.  

## Installation

```bash
pip install okfn-iati
```

A Python library for working with IATI XML data according to the IATI 2.03 standard.

## Features

- Data models that represent IATI XML elements
- XML generator to create valid IATI XML from Python objects
- Support for IATI 2.03 standard

## Installation

```bash
pip install okfn-iati
```

Usage
Creating and Exporting IATI Activity

```python
from iati_xml_handler import (
    Activity, Narrative, OrganizationRef, IatiActivities,
    ActivityDate, ActivityStatus, IatiXmlGenerator
)

# Create an IATI Activity
activity = Activity(
    iati_identifier="XM-EXAMPLE-12345",
    reporting_org=OrganizationRef(
        ref="XM-EXAMPLE",
        type="10",
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
            type="1",
            iso_date="2023-01-01",
            narratives=[Narrative(text="Planned start date")]
        ),
        ActivityDate(
            type="2",
            iso_date="2023-01-15",
            narratives=[Narrative(text="Actual start date")]
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

