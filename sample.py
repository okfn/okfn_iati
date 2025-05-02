from okfn_iati import (
    # Main models
    Activity, Narrative, OrganizationRef, ParticipatingOrg, ActivityDate,
    Location, LocationIdentifier, DocumentLink,
    Budget, Transaction, IatiActivities,

    # Enums - use these constants instead of strings
    ActivityStatus, ActivityDateType, TransactionType, BudgetType, BudgetStatus,
    OrganisationRole, OrganisationType, LocationID, DocumentCategory,
    SectorCategory,

    # Generator
    IatiXmlGenerator
)

# Create an IATI Activity
activity = Activity(
    iati_identifier="XM-EXAMPLE-12345",
    reporting_org=OrganizationRef(
        ref="XM-DAC-12345",  # Using an approved format with "XM-DAC-" prefix
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
    # Required: recipient country or region
    recipient_countries=[
        {
            "code": "KE",
            "percentage": 100,
            "narratives": [Narrative(text="Kenya")]
        }
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
    # Required: sector information
    sectors=[
        {
            "code": SectorCategory.EDUCATION_GENERAL.value,  # "11110"
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
            value_date="2023-01-01"  # Added required value_date
        )
    ],
    transactions=[
        Transaction(
            type=TransactionType.DISBURSEMENT,
            date="2023-03-15",
            value=50000.00,
            currency="USD",
            value_date="2023-03-15"  # Added required value_date
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
