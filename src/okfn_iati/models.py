from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Union

from okfn_iati.enums import (
    ActivityStatus, ActivityScope, BudgetStatus, BudgetType,
    ContactType, DocumentCategory, ActivityDateType,
    FinanceType, FlowType, GeographicalPrecision,
    IndicatorMeasure,
    LocationReach, LocationType, OrganisationRole, OrganisationType,
    RelatedActivityType,
    ResultType, SectorCategory, TiedStatus, TransactionType, LocationID,
    DisbursementChannel, RecipientRegion, CollaborationType
)
from okfn_iati.validators import crs_channel_code_validator


@dataclass
class Narrative:
    """
    Narrative element for multilingual text content.

    Args:
        text: The text content of the narrative
        lang: Optional language code (ISO 639-1)

    References:
        https://iatistandard.org/en/iati-standard/201/activity-standard/iati-activities/iati-activity/reporting-org/narrative/
        https://iatistandard.org/en/iati-standard/201/activity-standard/iati-activities/iati-activity/title/narrative/

        and much more. It could be used in many places in the IATI standard.
        https://iatistandard.org/en/iati-standard/upgrades/upgrade-changelogs/integer-upgrade-to-2-01/2-01-changes/#narrative-new-elements
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
        receiver_org_activity_id: Optional activity identifier from the referenced organization.

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/reporting-org/
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/transaction/provider-org/
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/transaction/receiver-org/
    """
    ref: str
    type: Optional[str] = None  # See OrganisationType enum for valid values
    narratives: List[Narrative] = field(default_factory=list)
    receiver_org_activity_id: Optional[str] = None
    secondary_reporter: Optional[bool] = None

    def __post_init__(self):
        # Validate type is a valid OrganisationType if it's provided and numeric
        if self.type:
            org_types = [e.value for e in OrganisationType]
            if self.type not in org_types:
                raise ValueError(f"Invalid organization type: '{self.type}'. Valid values are: {org_types}")


@dataclass
class ParticipatingOrg:
    """
    Organization participating in the activity.

    Args:
        role: Organization's role in the activity (see OrganisationRole enum)
        ref: Optional organization identifier
        type: Optional organization type (see OrganisationType enum)
        activity_id: Optional activity identifier the organization is associated with
        crs_channel_code: Optional CRS channel code.
            See codes https://iatistandard.org/en/iati-standard/203/codelists/crschannelcode/
        narratives: List of narrative elements with organization names

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/participating-org/
    """
    role: Union[OrganisationRole, str]
    ref: Optional[str] = None
    type: Optional[Union[OrganisationType, str]] = None
    activity_id: Optional[str] = None
    crs_channel_code: Optional[str] = None
    narratives: List[Narrative] = field(default_factory=list)

    def __post_init__(self):
        errors = []
        valid_org_roles = [e.value for e in OrganisationRole]

        # Validate role
        if isinstance(self.role, str) and self.role not in valid_org_roles:
            errors.append(f"Invalid organization role: {self.role}. Valid values are: {valid_org_roles}")
        elif hasattr(self.role, 'value') and self.role.value not in valid_org_roles:
            errors.append(f"Invalid organization role: {self.role}. Valid values are: {valid_org_roles}")

        # Validate type
        if self.type:
            org_types = [e.value for e in OrganisationType]
            if isinstance(self.type, str) and self.type not in org_types:
                errors.append(f"Invalid organization type: '{self.type}'. Valid values are: {org_types}")
            elif hasattr(self.type, 'value') and self.type.value not in org_types:
                errors.append(f"Invalid organization type: '{self.type}'. Valid values are: {org_types}")

        # Validate CRS channel code
        if self.crs_channel_code and not crs_channel_code_validator.is_valid_code(self.crs_channel_code):
            errors.append(f"Invalid CRS channel code: '{self.crs_channel_code}'")

        if errors:
            raise ValueError(" ".join(errors))


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
    type: Union[ActivityDateType, str]
    iso_date: str  # ISO 8601 format (YYYY-MM-DD)
    narratives: List[Narrative] = field(default_factory=list)

    def __post_init__(self):
        errors = []
        # Convert string to enum if needed
        if isinstance(self.type, str):
            try:
                self.type = next(e for e in ActivityDateType if e.value == self.type)
            except (StopIteration, ValueError):
                valid_types = [e.value for e in ActivityDateType]
                errors.append(f"Invalid date type: {self.type}. Valid values are: {valid_types}")
        elif hasattr(self.type, 'value') and self.type.value not in [e.value for e in ActivityDateType]:
            valid_types = [e.value for e in ActivityDateType]
            errors.append(f"Invalid date type: {self.type}. Valid values are: {valid_types}")

        # Validate ISO date format
        try:
            datetime.strptime(self.iso_date, "%Y-%m-%d")
        except ValueError:
            errors.append(f"Invalid ISO date format: {self.iso_date}. Expected YYYY-MM-DD")

        if errors:
            raise ValueError(" ".join(errors))


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
    type: Optional[Union[ContactType, str]] = None
    organisation: Optional[List[Narrative]] = None
    department: Optional[List[Narrative]] = None
    person_name: Optional[List[Narrative]] = None
    job_title: Optional[List[Narrative]] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    mailing_address: Optional[List[Narrative]] = None

    def __post_init__(self):
        valid_types = [e.value for e in ContactType]

        # Fix: Handle both string and enum instances for type
        if isinstance(self.type, str) and self.type and self.type not in valid_types:
            raise ValueError(f"Invalid contact type: {self.type}. Valid values are: {valid_types}")
        elif hasattr(self.type, 'value') and self.type.value not in valid_types:
            raise ValueError(f"Invalid contact type: {self.type}. Valid values are: {valid_types}")


@dataclass
class LocationIdentifier:
    """
    Location identifier with vocabulary and code.

    Args:
        vocabulary: Location identification vocabulary (see LocationID enum)
        code: Location identifier code

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/location/location-id/
    """
    vocabulary: Union[LocationID, str]
    code: str

    def __post_init__(self):
        # Validate vocabulary against LocationID enum
        valid_vocabs = [e.value for e in LocationID]
        if isinstance(self.vocabulary, str) and self.vocabulary not in valid_vocabs:
            raise ValueError(f"Invalid location vocabulary: {self.vocabulary}. Valid values are: {valid_vocabs}")
        elif hasattr(self.vocabulary, 'value') and self.vocabulary.value not in valid_vocabs:
            raise ValueError(f"Invalid location vocabulary: {self.vocabulary}. Valid values are: {valid_vocabs}")


@dataclass
class Location:
    """
    Geographical location information.

    Args:
        location_reach: Optional location reach (see LocationReach enum)
        location_id: Optional location identifier (vocabulary and code)
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
    ref: Optional[str] = None
    location_reach: Optional[Union[LocationReach, str]] = None
    location_id: Optional[LocationIdentifier] = None  # Updated to use LocationIdentifier
    name: Optional[List[Narrative]] = None
    description: Optional[List[Narrative]] = None
    activity_description: Optional[List[Narrative]] = None
    administrative: Optional[List[Dict[str, str]]] = None
    point: Optional[Dict[str, str]] = None
    exactness: Optional[Union[GeographicalPrecision, str]] = None
    location_class: Optional[Union[LocationType, str]] = None
    feature_designation: Optional[str] = None

    def __post_init__(self):
        # Convert string to enum if needed for location_reach
        if isinstance(self.location_reach, str):
            try:
                self.location_reach = next(e for e in LocationReach if e.value == self.location_reach)
            except (StopIteration, ValueError, TypeError):
                pass

        # Convert string to enum if needed for exactness
        if isinstance(self.exactness, str):
            try:
                self.exactness = next(e for e in GeographicalPrecision if e.value == self.exactness)
            except (StopIteration, ValueError, TypeError):
                pass

        # Convert string to enum if needed for location_class
        if isinstance(self.location_class, str):
            try:
                self.location_class = next(e for e in LocationType if e.value == self.location_class)
            except (StopIteration, ValueError, TypeError):
                pass


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
    categories: List[Union[DocumentCategory, str]] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    description: Optional[List[Narrative]] = field(default_factory=list)
    document_date: Optional[str] = None

    def __post_init__(self):
        # Convert string values in categories to enums if possible
        for i, category in enumerate(self.categories):
            if isinstance(category, str):
                try:
                    self.categories[i] = next(e for e in DocumentCategory if e.value == category)
                except (StopIteration, ValueError):
                    pass  # Keep as string if not found

        # Validate document date if provided
        if self.document_date:
            try:
                datetime.strptime(self.document_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Invalid document date format: {self.document_date}. Expected YYYY-MM-DD")


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
    type: Union[BudgetType, str]
    status: Union[BudgetStatus, str]
    period_start: str  # ISO 8601 format
    period_end: str  # ISO 8601 format
    value: float
    currency: Optional[str] = None  # ISO 4217
    value_date: Optional[str] = None  # ISO 8601 format
    raw_value: Optional[str] = None

    def __post_init__(self):  # noqa: C901
        # Convert strings to enums if needed
        if isinstance(self.type, str):
            try:
                self.type = next(e for e in BudgetType if e.value == self.type)
            except (StopIteration, ValueError):
                pass
        elif hasattr(self.type, 'value') and self.type.value not in [e.value for e in BudgetType]:
            raise ValueError(f"Invalid budget type: {self.type}. Valid values are: {[e.value for e in BudgetType]}")

        if isinstance(self.status, str):
            try:
                self.status = next(e for e in BudgetStatus if e.value == self.status)
            except (StopIteration, ValueError):
                pass
        elif hasattr(self.status, 'value') and self.status.value not in [e.value for e in BudgetStatus]:
            raise ValueError(f"Invalid budget status: {self.status}. Valid values are: {[e.value for e in BudgetStatus]}")

        # Validate ISO date formats
        try:
            datetime.strptime(self.period_start, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid period_start format: {self.period_start}. Expected YYYY-MM-DD")

        try:
            datetime.strptime(self.period_end, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid period_end format: {self.period_end}. Expected YYYY-MM-DD")

        if self.value_date:
            try:
                datetime.strptime(self.value_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Invalid value_date format: {self.value_date}. Expected YYYY-MM-DD")


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
        recipient_country: Optional dictionary with recipient country information
        recipient_region: Optional dictionary with recipient region information
        flow_type: Optional flow type code (see FlowType enum)
        finance_type: Optional finance type code (see FinanceType enum)
        aid_type: Optional dictionary with aid type information
        tied_status: Optional tied status code (see TiedStatus enum)
        currency: Optional currency code (ISO 4217)
        value_date: Optional ISO 8601 date for currency exchange rate
        disebursement_channel: Optional disbursement channel code (see DisbursementChannel enum)
        sectors: List of dictionaries with sector information

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/transaction/
    """
    type: Union[TransactionType, str]
    date: str  # ISO 8601 format
    value: float
    description: Optional[List[Narrative]] = None
    provider_org: Optional[OrganizationRef] = None
    receiver_org: Optional[OrganizationRef] = None
    transaction_ref: Optional[str] = None
    recipient_country: Optional[Dict[str, Any]] = None
    flow_type: Optional[Union[FlowType, str]] = None
    finance_type: Optional[Union[FinanceType, str]] = None
    aid_type: Optional[Dict[str, str]] = None
    tied_status: Optional[Union[TiedStatus, str]] = None
    currency: Optional[str] = None  # ISO 4217
    value_date: Optional[str] = None  # ISO 8601 format
    # https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/transaction/disbursement-channel/
    # codes https://iatistandard.org/en/iati-standard/203/codelists/disbursementchannel/
    disbursement_channel: Optional[Union[DisbursementChannel, str]] = None
    recipient_region: Optional[Union[RecipientRegion, str]] = None
    sectors: List[Dict[str, Any]] = field(default_factory=list)
    humanitarian: Optional[bool] = None  # Change from bool to Optional[bool]
    raw_value: Optional[str] = None

    def __post_init__(self):  # noqa: C901
        # Convert strings to enums if needed
        if isinstance(self.type, str):
            try:
                self.type = next(e for e in TransactionType if e.value == self.type)
            except (StopIteration, ValueError):
                pass
        elif hasattr(self.type, 'value') and self.type.value not in [e.value for e in TransactionType]:
            raise ValueError(f"Invalid transaction type: {self.type}. Valid values are: {[e.value for e in TransactionType]}")

        if isinstance(self.flow_type, str) and self.flow_type is not None:
            try:
                self.flow_type = next(e for e in FlowType if e.value == self.flow_type)
            except (StopIteration, ValueError):
                pass
        elif hasattr(self.flow_type, 'value') and self.flow_type.value not in [e.value for e in FlowType]:
            raise ValueError(f"Invalid flow type: {self.flow_type}. Valid values are: {[e.value for e in FlowType]}")

        if isinstance(self.finance_type, str) and self.finance_type is not None:
            try:
                self.finance_type = next(e for e in FinanceType if e.value == self.finance_type)
            except (StopIteration, ValueError):
                pass
        elif hasattr(self.finance_type, 'value') and self.finance_type.value not in [e.value for e in FinanceType]:
            raise ValueError(f"Invalid finance type: {self.finance_type}. Valid values are: {[e.value for e in FinanceType]}")

        if isinstance(self.tied_status, str) and self.tied_status is not None:
            try:
                self.tied_status = next(e for e in TiedStatus if e.value == self.tied_status)
            except (StopIteration, ValueError):
                pass
        elif hasattr(self.tied_status, 'value') and self.tied_status.value not in [e.value for e in TiedStatus]:
            raise ValueError(f"Invalid tied status: {self.tied_status}. Valid values are: {[e.value for e in TiedStatus]}")

        # Validate disbursement channel
        channel_values = [e.value for e in DisbursementChannel]
        if isinstance(self.disbursement_channel, str) and self.disbursement_channel is not None:
            try:
                self.disbursement_channel = next(e for e in DisbursementChannel if e.value == self.disbursement_channel)
            except (StopIteration, ValueError):
                pass
        elif hasattr(self.disbursement_channel, 'value') and self.disbursement_channel.value not in channel_values:
            raise ValueError(f"Invalid disbursement channel: {self.disbursement_channel}. Valid values are: {channel_values}")

        # Validate recipient region
        if isinstance(self.recipient_region, str) and self.recipient_region is not None and self.recipient_region:
            try:
                self.recipient_region = next(e for e in RecipientRegion if e.value == self.recipient_region)
            except (StopIteration, ValueError):
                # Keep as string if not found in enum - allows for codes not in our enum
                pass
        elif hasattr(self.recipient_region, 'value'):
            region_values = [e.value for e in RecipientRegion]
            if self.recipient_region.value not in region_values:
                # Allow it but keep as enum instance
                pass

        # Validate ISO date format
        try:
            datetime.strptime(self.date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid transaction date format: {self.date}. Expected YYYY-MM-DD")

        if self.value_date:
            try:
                datetime.strptime(self.value_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Invalid value_date format: {self.value_date}. Expected YYYY-MM-DD")


@dataclass
class IndicatorBaseline:
    """
    Baseline information for an indicator.

    Args:
        year: The year the baseline value was taken (yyyy)
        iso_date: Optional ISO 8601 date when baseline was taken
        value: Optional baseline value (omit for qualitative measures)
        comment: Optional list of narratives with baseline comments
        location: Optional list of location references
        dimension: Optional list of dimension information for disaggregation

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/result/indicator/baseline/
    """
    year: int
    iso_date: Optional[str] = None
    value: Optional[str] = None
    comment: Optional[List[Narrative]] = None
    location: Optional[List[Dict[str, str]]] = None
    dimension: Optional[List[Dict[str, str]]] = None

    def __post_init__(self):
        # Validate ISO date format if provided
        if self.iso_date:
            try:
                datetime.strptime(self.iso_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Invalid ISO date format: {self.iso_date}. Expected YYYY-MM-DD")


@dataclass
class IndicatorPeriodTarget:
    """
    Target information for an indicator period.

    Args:
        value: Optional target value (omit for qualitative measures)
        comment: Optional list of narratives with target comments
        location: Optional list of location references
        dimension: Optional list of dimension information for disaggregation

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/result/indicator/period/target/
    """
    value: Optional[str] = None
    comment: Optional[List[Narrative]] = None
    location: Optional[List[Dict[str, str]]] = None
    dimension: Optional[List[Dict[str, str]]] = None


@dataclass
class IndicatorPeriodActual:
    """
    Actual result information for an indicator period.

    Args:
        value: Optional actual value (omit for qualitative measures)
        comment: Optional list of narratives with actual result comments
        location: Optional list of location references
        dimension: Optional list of dimension information for disaggregation

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/result/indicator/period/actual/
    """
    value: Optional[str] = None
    comment: Optional[List[Narrative]] = None
    location: Optional[List[Dict[str, str]]] = None
    dimension: Optional[List[Dict[str, str]]] = None


@dataclass
class IndicatorPeriod:
    """
    Period information for an indicator.

    Args:
        period_start: Start date of the reporting period (ISO 8601)
        period_end: End date of the reporting period (ISO 8601)
        target: Optional list of target information
        actual: Optional list of actual result information

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/result/indicator/period/
    """
    period_start: str
    period_end: str
    target: Optional[List[IndicatorPeriodTarget]] = None
    actual: Optional[List[IndicatorPeriodActual]] = None

    def __post_init__(self):
        # Validate ISO date formats
        try:
            datetime.strptime(self.period_start, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid period_start format: {self.period_start}. Expected YYYY-MM-DD")

        try:
            datetime.strptime(self.period_end, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid period_end format: {self.period_end}. Expected YYYY-MM-DD")


@dataclass
class Indicator:
    """
    Indicator information for results.

    Args:
        measure: Unit of measure (see IndicatorMeasure enum)
        title: List of narratives with indicator title
        description: Optional list of narratives with indicator description
        ascending: Optional boolean indicating if indicator improves from small to large
        aggregation_status: Optional boolean indicating if data is suitable for aggregation
        baseline: Optional list of baseline information
        period: Optional list of period information
        reference: Optional list of reference information for coded identification

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/result/indicator/
    """
    measure: Union[IndicatorMeasure, str]
    title: List[Narrative] = field(default_factory=list)
    description: Optional[List[Narrative]] = None
    ascending: Optional[bool] = None
    aggregation_status: Optional[bool] = None
    baseline: Optional[List[IndicatorBaseline]] = None
    period: Optional[List[IndicatorPeriod]] = None
    reference: Optional[List[Dict[str, str]]] = None

    def __post_init__(self):
        # Import here to avoid circular imports
        from okfn_iati.enums import IndicatorMeasure

        # Convert string to enum if needed
        if isinstance(self.measure, str):
            try:
                self.measure = next(e for e in IndicatorMeasure if e.value == self.measure)
            except (StopIteration, ValueError):
                valid_measures = [e.value for e in IndicatorMeasure]
                raise ValueError(f"Invalid indicator measure: {self.measure}. Valid values are: {valid_measures}")
        elif hasattr(self.measure, 'value') and self.measure.value not in [e.value for e in IndicatorMeasure]:
            valid_measures = [e.value for e in IndicatorMeasure]
            raise ValueError(f"Invalid indicator measure: {self.measure}. Valid values are: {valid_measures}")


@dataclass
class Result:
    """
    Results information for the activity.

    Args:
        type: Result type (see ResultType enum)
        aggregation_status: Optional boolean indicating if result can be aggregated
        title: Optional list of narratives with result title
        description: Optional list of narratives with result description
        indicator: List of indicators for this result
        reference: Optional list of reference information for results framework

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/result/
    """
    type: Union[ResultType, str]
    aggregation_status: Optional[bool] = None
    title: Optional[List[Narrative]] = None
    description: Optional[List[Narrative]] = None
    indicator: List[Indicator] = field(default_factory=list)
    reference: Optional[List[Dict[str, str]]] = None

    def __post_init__(self):
        # Convert string to enum if needed
        if isinstance(self.type, str):
            try:
                self.type = next(e for e in ResultType if e.value == self.type)
            except (StopIteration, ValueError):
                pass
        elif hasattr(self.type, 'value') and self.type.value not in [e.value for e in ResultType]:
            raise ValueError(f"Invalid result type: {self.type}. Valid values are: {[e.value for e in ResultType]}")


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
    activity_status: Optional[ActivityStatus] = None
    activity_dates: List[ActivityDate] = field(default_factory=list)
    contact_info: Optional[ContactInfo] = None
    # TODO add a new CSV file for multiple countries/regions
    recipient_countries: List[Dict[str, Union[str, int, List[Narrative]]]] = field(default_factory=list)
    # Region codes can be found here: https://iatistandard.org/en/iati-standard/203/codelists/region/
    recipient_regions: List[Dict[str, Union[str, int, List[Narrative]]]] = field(default_factory=list)
    locations: List[Location] = field(default_factory=list)
    # Sector codes https://iatistandard.org/en/iati-standard/203/codelists/sector/
    # Sector vocabularies can be found here: https://iatistandard.org/en/iati-standard/203/codelists/sectorvocabulary/
    sectors: List[Dict[str, Any]] = field(default_factory=list)
    document_links: List[DocumentLink] = field(default_factory=list)
    budgets: List[Budget] = field(default_factory=list)
    transactions: List[Transaction] = field(default_factory=list)
    related_activities: List[Dict[str, str]] = field(default_factory=list)
    results: List[Result] = field(default_factory=list)
    country_budget_items: List[Dict[str, Any]] = field(default_factory=list)

    # IATI Activity attributes
    default_currency: Optional[str] = None  # ISO 4217 Currency code
    hierarchy: Optional[str] = "1"  # Activity hierarchy level (1=program, 2=project, etc.)
    last_updated_datetime: Optional[str] = None  # ISO 8601 datetime
    xml_lang: Optional[str] = "en"  # ISO 639-1 language code
    humanitarian: Optional[bool] = None  # True if humanitarian activity, False otherwise
    activity_scope: Optional[Union[ActivityScope, str]] = None
    collaboration_type: Optional[Union[CollaborationType, str]] = None  # Add collaboration_type field

    conditions_attached: Optional[str] = None  # "0" or "1" or None (missing)
    conditions: List[Dict[str, str]] = field(default_factory=list)

    # Add default type fields (activity-level defaults)
    # default_flow_type: https://iatistandard.org/en/iati-standard/203/codelists/flowtype/
    default_flow_type: Optional[str] = None
    default_finance_type: Optional[str] = None
    default_aid_type: Optional[str] = None
    default_tied_status: Optional[str] = None

    def __post_init__(self):  # noqa: C901
        # Validate related activities
        for related in self.related_activities:
            if "type" in related:
                type_value = related["type"]
                if isinstance(type_value, str):
                    # Ensure it's a valid RelatedActivityType
                    valid_types = [e.value for e in RelatedActivityType]
                    if type_value not in valid_types:
                        raise ValueError(f"Invalid related activity type: {type_value}")

        # Validate sectors
        for sector in self.sectors:
            if "code" in sector and isinstance(sector["code"], str):
                # Optionally validate against SectorCategory if code format matches
                try:
                    sector = getattr(SectorCategory, sector["code"])
                except AttributeError:
                    raise ValueError(f"Invalid sector code: {sector['code']}")

        # Convert activity_scope to enum if it's a string
        if isinstance(self.activity_scope, str) and self.activity_scope is not None:
            try:
                self.activity_scope = next(e for e in ActivityScope if e.value == self.activity_scope)
            except (StopIteration, ValueError):
                pass

        # Convert collaboration_type to enum if it's a string
        if isinstance(self.collaboration_type, str) and self.collaboration_type is not None:
            try:
                self.collaboration_type = next(e for e in CollaborationType if e.value == self.collaboration_type)
            except (StopIteration, ValueError):
                pass

        # Validate datetime format if provided
        if self.last_updated_datetime:
            try:
                # Check if it's a valid ISO datetime
                # Handle Python < 3.11 limitation with >6 digits in microseconds
                dt_to_validate = self.last_updated_datetime.replace('Z', '+00:00')
                if '.' in dt_to_validate:
                    # Truncate microseconds to 6 digits for validation
                    import re
                    dt_to_validate = re.sub(r'(\.\d{6})\d+', r'\1', dt_to_validate)
                datetime.fromisoformat(dt_to_validate)
            except ValueError:
                raise ValueError(f"Invalid datetime format: {self.last_updated_datetime}")


@dataclass
class IatiActivities:
    """
    Container for IATI activities.

    References:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/
    """
    version: str = "2.03"  # IATI standard version
    generated_datetime: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
    linked_data_default: Optional[str] = None  # Optional linked data URI
    activities: List[Activity] = field(default_factory=list)

    def __post_init__(self):
        # Validate version
        valid_versions = ["2.03"]
        if not self.version:
            raise ValueError("Version cannot be empty")
        if self.version not in valid_versions:
            raise ValueError(f"Invalid IATI version: {self.version}. Valid values are: {valid_versions}")
