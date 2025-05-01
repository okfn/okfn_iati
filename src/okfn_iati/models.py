from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Union

from okfn_iati.enums import (
    ActivityStatus,
    # DocumentCategory,
    # TransactionType,
)


@dataclass
class Narrative:
    text: str
    lang: Optional[str] = None


@dataclass
class OrganizationRef:
    ref: str
    type: str
    narratives: List[Narrative] = field(default_factory=list)


@dataclass
class ParticipatingOrg:
    role: str  # 1=Funding, 2=Accountable, 3=Extending, 4=Implementing
    ref: Optional[str] = None
    type: Optional[str] = None
    activity_id: Optional[str] = None
    crs_channel_code: Optional[str] = None
    narratives: List[Narrative] = field(default_factory=list)


@dataclass
class ActivityDate:
    type: str  # 1=Planned start, 2=Actual start, 3=Planned end, 4=Actual end
    iso_date: str
    narratives: List[Narrative] = field(default_factory=list)


@dataclass
class ContactInfo:
    type: Optional[str] = None
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
    location_reach: Optional[str] = None
    location_id: Optional[Dict[str, str]] = None
    name: Optional[List[Narrative]] = None
    description: Optional[List[Narrative]] = None
    activity_description: Optional[List[Narrative]] = None
    administrative: Optional[List[Dict[str, str]]] = None
    point: Optional[Dict[str, str]] = None
    exactness: Optional[str] = None
    location_class: Optional[str] = None
    feature_designation: Optional[str] = None


@dataclass
class DocumentLink:
    url: str
    format: str
    title: List[Narrative] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    document_date: Optional[str] = None


@dataclass
class Budget:
    type: str
    status: str
    period_start: str
    period_end: str
    value: float
    currency: Optional[str] = None
    value_date: Optional[str] = None


@dataclass
class Transaction:
    type: str
    date: str
    value: float
    description: Optional[List[Narrative]] = None
    provider_org: Optional[OrganizationRef] = None
    receiver_org: Optional[OrganizationRef] = None
    transaction_ref: Optional[str] = None
    sector: Optional[Dict[str, Any]] = None
    recipient_country: Optional[Dict[str, Any]] = None
    recipient_region: Optional[Dict[str, Any]] = None
    flow_type: Optional[str] = None
    finance_type: Optional[str] = None
    aid_type: Optional[Dict[str, str]] = None
    tied_status: Optional[str] = None
    currency: Optional[str] = None
    value_date: Optional[str] = None


@dataclass
class Result:
    type: str
    aggregation_status: Optional[bool] = None
    title: Optional[List[Narrative]] = None
    description: Optional[List[Narrative]] = None
    # indicators would be here in a more complete implementation


@dataclass
class Activity:
    iati_identifier: str
    reporting_org: OrganizationRef
    title: List[Narrative] = field(default_factory=list)
    description: List[Dict[str, List[Narrative]]] = field(default_factory=list)
    participating_orgs: List[ParticipatingOrg] = field(default_factory=list)
    activity_status: Optional[ActivityStatus] = None
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
    default_currency: Optional[str] = None
    hierarchy: Optional[str] = "1"
    last_updated_datetime: Optional[str] = None
    xml_lang: Optional[str] = "en"
    humanitarian: Optional[bool] = None


@dataclass
class IatiActivities:
    version: str = "2.03"
    generated_datetime: str = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    activities: List[Activity] = field(default_factory=list)
