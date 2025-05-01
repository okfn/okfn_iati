"""
Enumerations for IATI standard 2.03 code lists.
References:
- IATI Standard: https://iatistandard.org/en/iati-standard/
- IATI Codelists: https://iatistandard.org/en/iati-standard/203/codelists/
"""
from enum import Enum, IntEnum


class ActivityStatus(IntEnum):
    """
    Lifecycle status of the activity from pipeline to completion.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/activitystatus/
    """
    PIPELINE = 1
    IMPLEMENTATION = 2
    COMPLETION = 3
    POST_COMPLETION = 4
    CANCELLED = 5
    SUSPENDED = 6


class AidType(Enum):
    """
    Aid Type - Broad categories of aid based on OECD DAC classifications.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/aidtype/
    """
    # General Budget Support
    BUDGET_SUPPORT_GENERAL = "A01"
    # Sector Budget Support
    BUDGET_SUPPORT_SECTOR = "A02"
    # Core Support to NGOs
    CORE_SUPPORT_NGOS = "B01"
    # Core Support to International Organizations
    CORE_SUPPORT_MULTILATERAL = "B02"
    # Project-type Interventions
    PROJECT_TYPE = "C01"
    # Donor Country Personnel
    DONOR_PERSONNEL = "D01"
    # Other Technical Assistance
    OTHER_TECHNICAL_ASSISTANCE = "D02"
    # Debt Relief
    DEBT_RELIEF = "E01"
    # Administrative Costs
    ADMINISTRATIVE_COSTS = "G01"
    # Development Awareness
    DEVELOPMENT_AWARENESS = "H01"
    # Refugees in Donor Countries
    REFUGEES_IN_DONOR_COUNTRY = "H02"
    # Cash Transfers
    CASH_TRANSFER = "H03"
    # Vouchers
    VOUCHERS = "H04"
    # Mobile Phone Cash Transfers
    MOBILE_CASH = "H05"
    # In-kind Transfers
    IN_KIND_TRANSFERS = "H06"
    # In-kind Vouchers
    IN_KIND_VOUCHERS = "H07"


class BudgetIdentifier(Enum):
    """
    International budget identifier to track financial expenditures.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/budgetidentifier/
    """
    # Administration services
    ADMIN = "1.1"
    # Executive services
    EXECUTIVE = "1.2"
    # Public financial management
    PFM = "1.3"
    # Legal and judicial development
    LEGAL = "1.4"
    # Government administration
    GOVT_ADMIN = "1.5"
    # General personnel services
    PERSONNEL = "1.6"
    # Overall planning and statistical services
    PLANNING = "1.7"
    # Foreign affairs
    FOREIGN_AFFAIRS = "1.8"
    # Not applicable
    NOT_APPLICABLE = "1.9"
    # Unassigned
    UNASSIGNED = "1.A"
    # External affairs
    EXTERNAL_AFFAIRS = "1.B"
    # Accountability
    ACCOUNTABILITY = "1.C"
    # Police
    POLICE = "2.1"
    # Fire protection services
    FIRE = "2.2"
    # Justice
    JUSTICE = "2.A"
    # Prisons
    PRISONS = "2.B"
    # Other law and order
    OTHER_LAW_ORDER = "2.C"
    # Primary education
    EDUCATION_PRIMARY = "3.1"
    # Secondary education
    EDUCATION_SECONDARY = "3.2"
    # Tertiary education
    EDUCATION_TERTIARY = "3.3"
    # Pre-school education
    EDUCATION_PRESCHOOL = "3.4"
    # Vocational training
    EDUCATION_VOCATIONAL = "3.5"
    # Education for disadvantaged children
    EDUCATION_DISADVANTAGED = "3.A"
    # Education not elsewhere classified
    EDUCATION_NEC = "3.B"
    # Health
    HEALTH = "4.1"
    # Education and training in health
    HEALTH_EDUCATION = "4.2"
    # Social security (excluding pensions)
    SOCIAL_SECURITY = "5.1"
    # Private pension schemes
    PENSION_PRIVATE = "5.2"
    # Social assistance to households
    SOCIAL_ASSISTANCE = "5.3"
    # Public pension schemes
    PENSION_PUBLIC = "5.4"
    # Social protection and welfare services policy
    SOCIAL_WELFARE_POLICY = "5.A"
    # Housing
    HOUSING = "6.1"
    # Community development
    COMMUNITY_DEV = "6.2"
    # Water supply and sanitation
    WATER_SANITATION = "6.3"
    # Housing policy
    HOUSING_POLICY = "6.A"
    # Recreational and sporting services
    RECREATION_SPORTS = "7.1"
    # Culture
    CULTURE = "7.2"
    # Broadcasting and publishing
    BROADCASTING = "7.3"
    # Recreation and culture
    RECREATION_CULTURE = "7.A"
    # Fuel and energy
    FUEL_ENERGY = "8.1"
    # Agriculture
    AGRICULTURE = "8.2"
    # Mining and mineral development
    MINING = "8.3"
    # Transport
    TRANSPORT = "8.4"
    # Communications
    COMMUNICATIONS = "8.5"
    # Industries
    INDUSTRIES = "8.6"
    # Tourism
    TOURISM = "8.7"
    # Environment protection
    ENVIRONMENT = "8.8"
    # Commerce and business
    COMMERCE = "8.A"
    # Research and development - economic affairs
    RD_ECONOMIC = "8.B"
    # Environment
    ENVIRONMENT_GENERAL = "8.C"
    # Not defined/unallocated budget identifier
    NOT_DEFINED = "9.1"
    # Not applicable
    NA = "9.2"


class BudgetStatus(Enum):
    """
    Budget status - whether budget is indicative or has been formally committed.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/budgetstatus/
    """
    INDICATIVE = "1"
    COMMITTED = "2"


class BudgetType(Enum):
    """
    Type of budget - original, revised or other.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/budgettype/
    """
    ORIGINAL = "1"
    REVISED = "2"


class CollaborationType(Enum):
    """
    Collaboration type - bilateral, multilateral, etc.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/collaborationtype/
    """
    BILATERAL = "1"
    MULTILATERAL = "2"
    BILATERAL_THROUGH_NGO = "3"
    BILATERAL_THROUGH_MULTILATERAL = "4"
    PRIVATE_SECTOR_OUTFLOWS = "6"
    BILATERAL_NGO_CHANNEL = "7"
    OTHER_COLLABORATION = "8"


class ConditionType(Enum):
    """
    Condition type - policy, performance, etc.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/conditiontype/
    """
    POLICY = "1"
    PERFORMANCE = "2"
    FIDUCIARY = "3"


class ContactType(Enum):
    """
    Contact type - general, funding, technical, etc.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/contacttype/
    """
    GENERAL = "1"
    PROJECT_MANAGEMENT = "2"
    FINANCIAL = "3"
    COMMUNICATIONS = "4"


class DocumentCategory(Enum):
    """
    Document category - pre/post-conditions, evaluations, etc.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/documentcategory/
    """
    PRE_AND_POST_PROJECT = "A01"
    OBJECTIVES = "A02"
    INTENDED_ULTIMATE_BENEFICIARIES = "A03"
    CONDITIONS = "A04"
    BUDGET = "A05"
    SUMMARY_INFORMATION = "A06"
    REVIEW_AND_EVALUATION = "A07"
    RESULTS = "A08"
    MEMORANDUM_OF_UNDERSTANDING = "A09"
    TENDER = "A10"
    CONTRACT = "A11"
    ACTIVITY_WEB_PAGE = "A12"
    ANNUAL_REPORT = "B01"
    INSTITUTIONAL_STRATEGY_PAPER = "B02"
    COUNTRY_STRATEGY_PAPER = "B03"
    AID_ALLOCATION_POLICY = "B04"
    PROCUREMENT_POLICY = "B05"
    INSTITUTIONAL_AUDIT_REPORT = "B06"
    COUNTRY_AUDIT_REPORT = "B07"
    EXCLUSIONS_POLICY = "B08"
    INST_EVALUATION_REPORT = "B09"
    COUNTRY_EVAL_REPORT = "B10"
    SECTOR_STRATEGY = "B11"
    THEMATIC_STRATEGY = "B12"
    COUNTRY_LEVEL_MOU = "B13"
    EVALUATION_POLICY = "B14"
    GENERAL_TERMS_AND_CONDITIONS = "B15"
    ORG_WEB_PAGE = "B16"
    COUNTRY_REGIOS_WEB_PAGE = "B17"
    SECTOR_WEB_PAGE = "B18"


class FinanceType(Enum):
    """
    Finance type - grant, loan, etc.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/financetype/
    """
    GNI = "1"  # Gross National Income
    STANDARD_GRANT = "110"
    GUARANTEES_INSURANCE = "1100"
    # withdrawn "111" Subsidies to national private investors
    ODA_GNI = "2"  # ODA % GNI
    INTEREST_SUBSIDY = "210"
    # withdrawn 211 Interest subsidy to national private exporters
    FLOWS_GNI = "3"  # Flows % GNI
    CAPITAL_SUBSCRIPTION_DEPO = "310"
    CAPITAL_SUBSCRIPTION_ENCA = "311"
    POPULATION = "4"
    # withdrawn 410, 411, 412, 413, 414
    STANDARD_LOAN = "421"
    REIMBURSABLE_GRANT = "422"
    BONDS = "423"
    ASSET_SECURITIES = "424"
    OTHER_DEBT_SECURITIES = "425"
    SUBORDINATED_LOAN = "431"
    PREFERRED_EQUITY = "432"
    OTHER_HYBRID = "433"
    # withdrawn 451, 452
    COMMON_EQUITY = "510"
    # withdrawn 511, 512
    SHARES_COLLECTIVE = "520"
    REINVESTED_EARNINGS = "530"
    DEBT_FOR_ODA_P = "610"
    DEBT_FOR_ODA_I = "611"
    DEBT_FOR_OOF_P = "612"
    DEBT_FOR_OOF_I = "613"
    DEBT_FOR_PRIV_P = "614"
    DEBT_FOR_PRIV_I = "615"
    DEBT_FOR_OOF_DSR = "616"
    DEBT_FOR_PRIV_DSR = "617"
    DEBT_FOR_OTHER = "618"
    DEBT_RESCH_ODA_P = "620"
    DEBT_RESCH_ODA_I = "621"
    DEBT_RESCH_OOF_P = "622"
    DEBT_RESCH_OOF_I = "623"
    DEBT_RESCH_PRIV_P = "624"
    DEBT_RESCH_PRIV_I = "625"
    DEBT_RESCH_OOF_DSR = "626"
    DEBT_RESCH_PRIV_DSR = "627"
    DEBT_RESCH_OOF_DSR_ORIG_LOAN_P = "630"
    DEBT_RESCH_OOF_DSR_ORIG_LOAN_I = "631"
    DEBT_RESCH_PRIV_DSR_ORIG_LOAN_P = "632"
    DEBT_FORGIVE_EXPORT_CREDIT_P = "633"
    DEBT_FORGIVE_EXPORT_CREDIT_I = "634"
    DEBT_FORGIVE_EXPORT_CREDIT_DSR = "635"
    DEBT_RESCH_EXPORT_CREDIT_P = "636"
    DEBT_RESCH_EXPORT_CREDIT_I = "637"
    DEBT_RESCH_EXPORT_CREDIT_DSR = "638"
    DEBT_RESCH_EXPORT_CREDIT_DSR_ORIG_LOAN_P = "639"
    # Whitdrawn 710, 711, 712
    # withdrawn 810, 811
    # withdrawn 910, 911, 912, 913


class FlowType(Enum):
    """
    Flow type - ODA, OOF, etc.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/flowtype/
    """
    ODA = "10"
    # withdrawn OTHER_OFFICIAL_FLOWS = "20"
    NON_EXPORT_CREDIT_OOF = "21"
    OFFICIAL_CREDIT_OOF = "22"
    PRIVATE_DEVELOPMENT_FINANCE = "30"
    # withdrawn PRIVATE_MARKET = "35"
    PRIVATE_FOREIGN_DIRECT_INVESTMENT = "36"
    OTHER_PRIVATE_FLOWS = "37"
    NON_FLOWS = "40"
    OTHER_FLOW = "50"


class GeographicalPrecision(Enum):
    """
    Geographical precision - exact location, country, etc.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/geographicalprecision/
    """
    EXACT_LOCATION = "1"
    NEAR_LOCATION = "2"
    ADMI_REGION = "3"
    COUNTRY = "4"
    ESTIMATED_COORDINATES = "5"
    REPORTING_ORG = "6"
    MULTI_COUNTRY = "7"
    GLOBAL = "8"
    UNSPECIFIED = "9"


class IndicatorMeasure(Enum):
    """
    Indicator measure - unit, percentage, etc.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/indicatormeasure/
    """
    UNIT = "1"
    PERCENTAGE = "2"
    NOMINAL = "3"
    ORDINAL = "4"
    QUALITATIVE = "5"


class LocationReach(Enum):
    """
    Location reach - activity, beneficiary, etc.
    Reference:
        https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/location/location-reach/
    """
    ACTIVITY = "1"
    BENEFICIARY = "2"


class LocationID(Enum):
    """
    Location ID - unique identifier for a location.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/geographicvocabulary/
    """
    GAUL = "A1"  # Global Administrative Unit Layers
    # http://www.fao.org/geonetwork/srv/en/metadata.show?id=12691
    UN_SECONDARY = "A2"  # UN Second Administrative Level
    # http://www.unsalb.org/
    GAA = "A3"  # Global Administrative Areas
    # http://www.gadm.org/
    ISO_3166_1 = "A4"  # ISO 3166-1 alpha-2 country codes
    # https://iatistandard.org/en/iati-standard/203/codelists/Country/
    GEONAMES = "G1"  # http://www.geonames.org/
    OSM = "G2"  # OpenStreetMap http://www.openstreetmap.org/
    # Note: the code should be formed by prefixing the relevant OpenStreetMap ID with node/ way/ or
    # relation/ as appropriate, e.g. node/1234567


class LocationType(Enum):
    """
    Location type - administrative region, populated place, etc.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/locationtype/
    """
    ADMIN_REGION = "1"
    POPULATED_PLACE = "2"
    STRUCTURE = "3"
    OTHER = "4"


class OrganisationRole(Enum):
    """
    Organisation role - funding, implementing, etc.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/organisationrole/
    """
    FUNDING = "1"
    ACCOUNTABLE = "2"
    EXTENDING = "3"
    IMPLEMENTING = "4"


class OrganisationType(Enum):
    """
    Organisation type - government, NGO, etc.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/organisationtype/
    """
    GOVERNMENT = "10"
    LOCAL_GOVERNMENT = "11"
    OTHER_PUBLIC_SECTOR = "15"
    INTERNATIONAL_NGO = "21"
    NATIONAL_NGO = "22"
    REGIONAL_NGO = "23"
    PARTNER_COUNTRY_BASED_NGO = "24"
    PUBLIC_PRIVATE_PARTNERSHIP = "30"
    MULTILATERAL = "40"
    FOUNDATION = "60"
    PRIVATE_SECTOR = "70"
    PRIVATE_SECTOR_IN_PROV_COUNTRY = "71"
    PRIVATE_SECTOR_IN_AID_COUNTRY = "72"
    PRIVATE_SECTOR_IN_THIRD_COUNTRY = "73"
    ACADEMIC = "80"
    OTHER = "90"


class PolicyMarker(Enum):
    """
    Policy marker - gender equality, environment, etc.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/policymarker/
    """
    GENDER_EQUALITY = "1"
    AID_TO_ENVIRONMENT = "2"
    PARTICIPATORY_DEVELOPMENT = "3"
    TRADE_DEVELOPMENT = "4"
    BIODIVERSITY = "5"
    CLIMATE_CHANGE_MITIGATION = "6"
    CLIMATE_CHANGE_ADAPTATION = "7"
    DESERTIFICATION = "8"
    DISASTER_RISK_REDUCTION = "9"
    DISABILITY = "10"
    INDIGENOUS_PEOPLES = "11"
    NUTRITION = "12"


class PolicySignificance(Enum):
    """
    Policy significance - not targeted, significant objective, etc.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/policysignificance/
    """
    NOT_TARGETED = "0"
    SIGNIFICANT_OBJECTIVE = "1"
    PRINCIPAL_OBJECTIVE = "2"
    PRINCIPAL_OBJECTIVE_AND_IN_SUPPORT_OF_ACTION = "3"
    EXPLICIT_PRIMARY_OBJECTIVE = "4"


class ResultType(Enum):
    """
    Result type - output, outcome, etc.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/resulttype/
    """
    OUTPUT = "1"
    OUTCOME = "2"
    IMPACT = "3"
    OTHER = "9"


class SectorCategory(Enum):
    """
    Sector category - education, health, etc. (DAC 5-digit purpose codes)
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/sector/
    """
    # This is a subset of common sectors - the full list has over 200 codes
    EDUCATION_GENERAL = "11110"
    PRIMARY_EDUCATION = "11220"
    HEALTH_GENERAL = "12110"
    BASIC_HEALTH = "12220"
    WATER_SANITATION = "14010"
    GOVERNMENT_CIVIL_SOCIETY = "15110"
    AGRICULTURE = "31110"
    TRANSPORT = "21010"
    ENERGY = "23010"
    BANKING_FINANCIAL = "24010"
    BUSINESS = "25010"
    ENVIRONMENT = "41010"
    EMERGENCY_RESPONSE = "72010"
    RECONSTRUCTION_RELIEF = "73010"
    DISASTER_PREVENTION = "74010"


class TiedStatus(Enum):
    """
    Tied status - untied, partially tied, etc.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/tiedstatus/
    """
    PARTIALLY_TIED = "3"
    TIED = "4"
    UNTIED = "5"


class TransactionType(Enum):
    """
    Transaction type - commitment, disbursement, etc.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/transactiontype/
    """
    INCOMING_FUNDS = "1"
    OUT_COMMITMENT = "2"
    DISBURSEMENT = "3"
    EXPENDITURE = "4"
    INTEREST_PAYMENT = "5"
    LOAN_REPAYMENT = "6"
    REIMBURSEMENT = "7"
    PURCHASE_OF_EQUITY = "8"
    SALE_OF_EQUITY = "9"
    CREDIT_GUARANTEE = "10"
    INCOMING_COMMITMENT = "11"
    OUTGOING_PLEDGE = "12"
    INCOMING_PLEDGE = "13"


class VocabularyType(Enum):
    """
    Vocabulary type - OECD DAC, UN, etc.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/vocabulary/
    """
    OECD_DAC_CRS_PURPOSE = "1"
    OECD_DAC_CRS_CHANNEL = "2"
    CLASSIFICATION_COUNTRY_SPECIFIC = "3"
    REPORTING_ORG = "4"
    TRACEABILITY = "5"
    UN_SDGS = "6"
    UN_HUMANITARIAN_GLOBAL_THEMES = "7"
    UN_HUMANITARIAN_CLUSTERS = "8"
    UN_HUMANITARIAN_GLOBAL_CLUSTERS = "9"
    UN_HUMANITARIAN_HUMANITARIAN_RESPONSE_PLAN = "10"
    UN_HUMANITARIAN_ACTIVITY_CATEGORIES = "11"
    UN_HUMANITARIAN_INTER_AGENCY = "12"
    UN_HUMANITARIAN_FINANCIAL_TRACKING = "13"
    UN_HUMANITARIAN_APPEAL = "14"
    UN_HUMANITARIAN_CASH_VOUCHER = "15"
    UN_OCHA_COVID19 = "16"
    UN_DISASTER_RISK_REDUCTION = "17"
    UN_DISASTER_RISK_REDUCTION_SENDAI = "18"
    INTERNAL_VOCABULARY = "99"


class ActivityScope(Enum):
    """
    Activity scope - global, regional, national, etc.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/activityscope/
    """
    GLOBAL = "1"
    REGIONAL = "2"
    MULTI_NATIONAL = "3"
    NATIONAL = "4"
    SUB_NATIONAL_MULTI_FIRST_ADM = "5"
    SUB_NATIONAL_SINGLE_FIRST_ADM = "6"
    SUB_NATIONAL_MULTI_SECOND_ADM = "7"
    SUB_NATIONAL_SINGLE_SECOND_ADM = "8"


class AidTypeFlag(Enum):
    """
    Flag indicating type of aid.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/aidtypeflag/
    """
    FREE_STANDING_TECHNICAL_COOPERATION = "1"
    PROGRAM_BASED_APPROACH = "2"
    INVESTMENT_PROJECT = "3"
    ASSOCIATED_FINANCING = "4"


class RelatedActivityType(Enum):
    """
    Type of relationship between activities.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/relatedactivitytype/
    """
    PARENT = "1"
    CHILD = "2"
    SIBLING = "3"
    CO_FUNDED = "4"
    THIRD_PARTY = "5"


class ActivityDateType(Enum):
    """
    Type of activity date being reported.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/activitydatetype/
    """
    PLANNED_START = "1"
    ACTUAL_START = "2"
    PLANNED_END = "3"
    ACTUAL_END = "4"
