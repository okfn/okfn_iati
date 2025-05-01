from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from okfn_iati.enums import ActivityStatus


@dataclass
class Narrative:
    """
    Narrative element for multilingual text content.

    Args:
        text: The text content of the narrative
        lang: Optional language code (ISO 639-1)

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/narrative/
    """
    text: str
    lang: Optional[str] = None


@dataclass
class OrganizationRef:
    """
    Reference to an organization in IATI.

    Args:
        ref: Organization identifier reference code
        type: Organization type code (see OrganisationType enum)
        narratives: List of narrative elements with organization names

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/reporting-org/
    """
    ref: str
    type: str  # See OrganisationType enum for valid values
    narratives: List[Narrative] = field(default_factory=list)


@dataclass
class ParticipatingOrg:
    """
    Organization participating in the activity.

    Args:
        role: Organization's role in the activity (see OrganisationRole enum)
        ref: Optional organization identifier
        type: Optional organization type (see OrganisationType enum)
        activity_id: Optional activity identifier the organization is associated with
        crs_channel_code: Optional CRS channel code
        narratives: List of narrative elements with organization names

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/participating-org/
    """
    role: str  # 1=Funding, 2=Accountable, 3=Extending, 4=Implementing
    ref: Optional[str] = None
    type: Optional[str] = None
    activity_id: Optional[str] = None
    crs_channel_code: Optional[str] = None
    narratives: List[Narrative] = field(default_factory=list)


@dataclass
class ActivityDate:
    """
    Important dates for the activity.

    Args:
        type: Date type (1=Planned start, 2=Actual start, 3=Planned end, 4=Actual end)
        iso_date: Date in ISO 8601 format (YYYY-MM-DD)
        narratives: Optional list of narratives with date descriptions

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/activity-date/
    """
    type: str  # 1=Planned start, 2=Actual start, 3=Planned end, 4=Actual end
    iso_date: str  # ISO 8601 format (YYYY-MM-DD)
    narratives: List[Narrative] = field(default_factory=list)


@dataclass
class ContactInfo:
    """
    Contact information for the activity.

    Args:
        type: Contact type (see ContactType enum)
        organisation: Optional list of narratives with organization name
        department: Optional list of narratives with department name
        person_name: Optional list of narratives with person's name
        job_title: Optional list of narratives with job title
        telephone: Optional telephone number
        email: Optional email address
        website: Optional website URL
        mailing_address: Optional list of narratives with mailing address

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/contact-info/
    """
    type: Optional[str] = None  # See ContactType enum
    organisation: Optional[List[Narrative]] = None
    department: Optional[List[Narrative]] = None
    person_name: Optional[List[Narrative]] = None
    job_title: Optional[List[Narrative]] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    mailing_address: Optional[List[Narrative]] = None


@dataclass
class Location:
    """
    Geographical location information.

    Args:
        location_reach: Optional location reach (see LocationReach enum)
        location_id: Optional location identifier dictionary
        name: Optional list of narratives with location name
        description: Optional list of narratives with location description
        activity_description: Optional list of narratives with activity description at location
        administrative: Optional list of dictionaries with administrative boundaries
        point: Optional dictionary with geographical point information
        exactness: Optional exactness code (see GeographicalPrecision enum)
        location_class: Optional location class code (see LocationType enum)
        feature_designation: Optional feature designation code

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/location/
    """
    location_reach: Optional[str] = None  # See LocationReach enum
    location_id: Optional[Dict[str, str]] = None
    name: Optional[List[Narrative]] = None
    description: Optional[List[Narrative]] = None
    activity_description: Optional[List[Narrative]] = None
    administrative: Optional[List[Dict[str, str]]] = None
    point: Optional[Dict[str, str]] = None
    exactness: Optional[str] = None  # See GeographicalPrecision enum
    location_class: Optional[str] = None  # See LocationType enum
    feature_designation: Optional[str] = None


@dataclass
class DocumentLink:
    """
    Link to a document related to the activity.

    Args:
        url: URL to the document
        format: MIME type format of the document
        title: List of narratives with document title
        categories: List of document category codes (see DocumentCategory enum)
        languages: List of language codes (ISO 639-1)
        document_date: Optional ISO 8601 date of the document

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/document-link/
    """
    url: str
    format: str  # MIME type format
    title: List[Narrative] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)  # See DocumentCategory enum
    languages: List[str] = field(default_factory=list)  # ISO 639-1
    document_date: Optional[str] = None  # ISO 8601 format


@dataclass
class Budget:
    """
    Budget information for the activity.

    Args:
        type: Budget type (see BudgetType enum)
        status: Budget status (see BudgetStatus enum)
        period_start: Start date of budget period in ISO 8601 format
        period_end: End date of budget period in ISO 8601 format
        value: Budget value amount
        currency: Optional currency code (ISO 4217)
        value_date: Optional ISO 8601 date for currency exchange rate

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/budget/
    """
    type: str  # See BudgetType enum
    status: str  # See BudgetStatus enum
    period_start: str  # ISO 8601 format
    period_end: str  # ISO 8601 format
    value: float
    currency: Optional[str] = None  # ISO 4217
    value_date: Optional[str] = None  # ISO 8601 format


@dataclass
class Transaction:
    """
    Financial transaction related to the activity.

    Args:
        type: Transaction type (see TransactionType enum)
        date: ISO 8601 date of the transaction
        value: Transaction amount
        description: Optional list of narratives with transaction description
        provider_org: Optional organization providing the funds
        receiver_org: Optional organization receiving the funds
        transaction_ref: Optional transaction reference
        sector: Optional dictionary with sector information
        recipient_country: Optional dictionary with recipient country information
        recipient_region: Optional dictionary with recipient region information
        flow_type: Optional flow type code (see FlowType enum)
        finance_type: Optional finance type code (see FinanceType enum)
        aid_type: Optional dictionary with aid type information
        tied_status: Optional tied status code (see TiedStatus enum)
        currency: Optional currency code (ISO 4217)
        value_date: Optional ISO 8601 date for currency exchange rate

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/transaction/
    """
    type: str  # See TransactionType enum
    date: str  # ISO 8601 format
    value: float
    description: Optional[List[Narrative]] = None
    provider_org: Optional[OrganizationRef] = None
    receiver_org: Optional[OrganizationRef] = None
    transaction_ref: Optional[str] = None
    sector: Optional[Dict[str, Any]] = None  # See SectorCategory enum
    recipient_country: Optional[Dict[str, Any]] = None
    recipient_region: Optional[Dict[str, Any]] = None
    flow_type: Optional[str] = None  # See FlowType enum
    finance_type: Optional[str] = None  # See FinanceType enum
    aid_type: Optional[Dict[str, str]] = None  # See AidType enum
    tied_status: Optional[str] = None  # See TiedStatus enum
    currency: Optional[str] = None  # ISO 4217
    value_date: Optional[str] = None  # ISO 8601 format


@dataclass
class Result:
    """
    Results information for the activity.

    Args:
        type: Result type (see ResultType enum)
        aggregation_status: Optional boolean indicating if result can be aggregated
        title: Optional list of narratives with result title
        description: Optional list of narratives with result description

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/result/
    """
    type: str  # See ResultType enum
    aggregation_status: Optional[bool] = None
    title: Optional[List[Narrative]] = None
    description: Optional[List[Narrative]] = None
    # indicators would be here in a more complete implementation


@dataclass
class Activity:
    """
    IATI Activity - the main unit of an IATI data record.

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/
    """
    iati_identifier: str
    reporting_org: OrganizationRef
    title: List[Narrative] = field(default_factory=list)
    description: List[Dict[str, List[Narrative]]] = field(default_factory=list)
    participating_orgs: List[ParticipatingOrg] = field(default_factory=list)
    activity_status: Optional[ActivityStatus] = None  # See ActivityStatus enum
    activity_dates: List[ActivityDate] = field(default_factory=list)
    contact_info: Optional[ContactInfo] = None
    recipient_countries: List[Dict[str, Union[str, int, List[Narrative]]]] = field(default_factory=list)
    recipient_regions: List[Dict[str, Union[str, int, List[Narrative]]]] = field(default_factory=list)
    locations: List[Location] = field(default_factory=list)
    sectors: List[Dict[str, Any]] = field(default_factory=list)
    document_links: List[DocumentLink] = field(default_factory=list)
    budgets: List[Budget] = field(default_factory=list)
    transactions: List[Transaction] = field(default_factory=list)
    related_activities: List[Dict[str, str]] = field(default_factory=list)
    results: List[Result] = field(default_factory=list)

    # IATI Activity attributes
    default_currency: Optional[str] = None  # ISO 4217 Currency code
    hierarchy: Optional[str] = "1"  # Activity hierarchy level (1=program, 2=project, etc.)
    last_updated_datetime: Optional[str] = None  # ISO 8601 datetime
    xml_lang: Optional[str] = "en"  # ISO 639-1 language code
    humanitarian: Optional[bool] = None  # True if humanitarian activity, False otherwise
    activity_scope: Optional[str] = None  # See ActivityScope enum


@dataclass
class IatiActivities:
    """
    Container for IATI activities.

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/
    """
    version: str = "2.03"  # IATI standard version
    generated_datetime: str = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")  # ISO 8601 datetime
    activities: List[Activity] = field(default_factory=list)
