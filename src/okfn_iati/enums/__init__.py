"""
Enumerations for IATI standard 2.03 code lists.
References:
- IATI Standard: https://iatistandard.org/en/iati-standard/
- IATI Codelists: https://iatistandard.org/en/iati-standard/203/codelists/
"""
from enum import Enum, IntEnum

from okfn_iati.enums.sector_category import SectorCategoryData, LocationTypeData


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
    # Basket Funds / Pooled Funding
    BASKET_FUNDS_POOLED_FUNDING = "B04"
    # Core Support to NGOs
    CORE_SUPPORT_NGOS = "B01"
    # Core Support to International Organizations
    CORE_SUPPORT_MULTILATERAL = "B02"
    # Core Contributions to Multilateral Institutions
    CORE_CONTRIBUTIONS_TO_MULTILATERAL_INSTITUTIONS = "B021"
    # Core Contributions to Global Funds
    CORE_CONTRIBUTIONS_TO_GLOBAL_FUNDS = "B022"
    # Contributions to Specific Purpose Programmes and Funds
    CONTRIBUTIONS_TO_SPECIFIC_PURPOSE_PROGRAMMES_AND_FUNDS = "B03"
    # Contributions to Multi-donor, Multi-entity Funds
    CONTRIBUTIONS_TO_MULTI_DONOR_MULTI_ENTITY = "B031"
    # Contributions to Multi-donor, Single-entity Funds
    CONTRIBUTIONS_TO_MULTI_DONOR_SINGLE_ENTITY = "B032"
    # Contributions to Single Donor or Earmarked Funds
    CONTRIBUTIONS_TO_SINGLE_DONOR_OR_EARMARKED = "B033"
    # Project-type Interventions
    PROJECT_TYPE = "C01"
    # Donor Country Personnel
    DONOR_PERSONNEL = "D01"
    # Other Technical Assistance
    OTHER_TECHNICAL_ASSISTANCE = "D02"
    # Debt Relief
    DEBT_RELIEF = "F01"
    # Scholarships/training in donor country
    SCHOLARSHIPS_TRAINING_IN_DONOR_COUNTRY = "E01"
    # Imputed student costs
    IMPUTED_STUDENT_COSTS = "E02"
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
    # IN_KIND_VOUCHERS = "H07"


class BudgetIdentifier(Enum):
    """
    International budget identifier to track financial expenditures.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/budgetidentifier/
    """
    # Executive - executive
    EXECUTIVE_EXECUTIVE = "1.1.1"
    # Legislative - legislative
    LEGISLATIVE_LEGISLATIVE = "1.2.1"
    # Accountability - macroeconomic policy
    ACCOUNTABILITY_MACROECONOMIC_POLICY = "1.3.1"
    # Accountability - budgeting
    ACCOUNTABILITY_BUDGETING = "1.3.2"
    # Accountability - planning
    ACCOUNTABILITY_PLANNING = "1.3.3"
    # Accountability - Treasury/Accounts
    ACCOUNTABILITY_TREASURY_ACCOUNTS = "1.3.4"
    # Accountability - debt and aid management
    ACCOUNTABILITY_DEBT_AND_AID_MANAGEMENT = "1.3.5"
    # Accountability - tax policy
    ACCOUNTABILITY_TAX_POLICY = "1.3.6"
    # Accountability - tax collection
    ACCOUNTABILITY_TAX_COLLECTION = "1.3.7"
    # Accountability - local government finance
    ACCOUNTABILITY_LOCAL_GOVERNMENT_FINANCE = "1.3.8"
    # Accountability - other central transfers to institutions
    ACCOUNTABILITY_OTHER_CENTRAL_TRANSFERS_TO_INSTITUTIONS = "1.3.9"
    # Accountability - national audit
    ACCOUNTABILITY_NATIONAL_AUDIT = "1.3.10"
    # Accountability - national monitoring and evaluation
    ACCOUNTABILITY_NATIONAL_MONITORING_AND_EVALUATION = "1.3.11"
    # Accountability - monetary institutions
    ACCOUNTABILITY_MONETARY_INSTITUTIONS = "1.3.12"
    # Accountability - financial sector policy and regulation
    ACCOUNTABILITY_FINANCIAL_SECTOR_POLICY_AND_REGULATION = "1.3.13"
    # External Affairs - foreign affairs
    EXTERNAL_AFFAIRS_FOREIGN_AFFAIRS = "1.4.1"
    # External Affairs - diplomatic missions
    EXTERNAL_AFFAIRS_DIPLOMATIC_MISSIONS = "1.4.2"
    # External Affairs - official development assistance
    EXTERNAL_AFFAIRS_OFFICIAL_DEVELOPMENT_ASSISTANCE = "1.4.3"
    # General Personnel Services - general personnel services
    GENERAL_PERSONNEL_SERVICES_GENERAL_PERSONNEL_SERVICES = "1.5.1"
    # Statistics - statistics
    STATISTICS_STATISTICS = "1.6.1"
    # Other General Services - support to civil society
    OTHER_GENERAL_SERVICES_SUPPORT_TO_CIVIL_SOCIETY = "1.7.1"
    # Other General Services - central procurement
    OTHER_GENERAL_SERVICES_CENTRAL_PROCUREMENT = "1.7.2"
    # Other General Services - Local Government Administration
    OTHER_GENERAL_SERVICES_LOCAL_GOVERNMENT_ADMINISTRATION = "1.7.3"
    # Other General Services - other general services
    OTHER_GENERAL_SERVICES_OTHER_GENERAL_SERVICES = "1.7.4"
    # Elections - elections
    ELECTIONS_ELECTIONS = "1.8.1"
    # Justice, Law and Order - policy, planning and administration
    JUSTICE_LAW_AND_ORDER_POLICY_PLANNING_AND_ADMINISTRATION = "2.1.1"
    # Justice, Law and Order - fire or police
    JUSTICE_LAW_AND_ORDER_FIRE_OR_POLICE = "2.1.2"
    # Justice, Law and Order - judicial affairs
    JUSTICE_LAW_AND_ORDER_JUDICIAL_AFFAIRS = "2.1.3"
    # Justice, Law and Order - Ombudsman
    JUSTICE_LAW_AND_ORDER_OMBUDSMAN = "2.1.4"
    # Justice, Law and Order - human rights affairs
    JUSTICE_LAW_AND_ORDER_HUMAN_RIGHTS_AFFAIRS = "2.1.5"
    # Justice, Law and Order - immigration
    JUSTICE_LAW_AND_ORDER_IMMIGRATION = "2.1.6"
    # Justice, Law and Order - anti corruption
    JUSTICE_LAW_AND_ORDER_ANTI_CORRUPTION = "2.1.7"
    # Justice, Law and Order - prisons
    JUSTICE_LAW_AND_ORDER_PRISONS = "2.1.8"
    # Justice, Law and Order - peace building
    JUSTICE_LAW_AND_ORDER_PEACE_BUILDING = "2.1.9"
    # Justice, Law and Order - demobilisation
    JUSTICE_LAW_AND_ORDER_DEMOBILISATION = "2.1.10"
    # Defence - policy, planning and administration
    DEFENCE_POLICY_PLANNING_AND_ADMINISTRATION = "2.2.1"
    # Defence - military
    DEFENCE_MILITARY = "2.2.2"
    # Defence - civil defence
    DEFENCE_CIVIL_DEFENCE = "2.2.3"
    # Defence - foreign military aid
    DEFENCE_FOREIGN_MILITARY_AID = "2.2.4"
    # General Economic, Commercial and Labour Affairs - policy, planning and administration
    GENERAL_ECONOMIC_COMMERCIAL_AND_LABOUR_AFFAIRS_POLICY_PLANNING_AND_ADMINISTRATION = "3.1.1"
    # General Economic, Commercial and Labour Affairs - general economic affairs
    GENERAL_ECONOMIC_COMMERCIAL_AND_LABOUR_AFFAIRS_GENERAL_ECONOMIC_AFFAIRS = "3.1.2"
    # General Economic, Commercial and Labour Affairs - investment promotion
    GENERAL_ECONOMIC_COMMERCIAL_AND_LABOUR_AFFAIRS_INVESTMENT_PROMOTION = "3.1.3"
    # General Economic, Commercial and Labour Affairs - privatisation
    GENERAL_ECONOMIC_COMMERCIAL_AND_LABOUR_AFFAIRS_PRIVATISATION = "3.1.4"
    # General Economic, Commercial and Labour Affairs - trade
    GENERAL_ECONOMIC_COMMERCIAL_AND_LABOUR_AFFAIRS_TRADE = "3.1.5"
    # General Economic, Commercial and Labour Affairs - labour
    GENERAL_ECONOMIC_COMMERCIAL_AND_LABOUR_AFFAIRS_LABOUR = "3.1.6"
    # General Economic, Commercial and Labour Affairs - national standards development
    GENERAL_ECONOMIC_COMMERCIAL_AND_LABOUR_AFFAIRS_NATIONAL_STANDARDS_DEVELOPMENT = "3.1.7"
    # Public Works - policy, planning and administration
    PUBLIC_WORKS_POLICY_PLANNING_AND_ADMINISTRATION = "3.2.1"
    # Public Works - construction regulation
    PUBLIC_WORKS_CONSTRUCTION_REGULATION = "3.2.2"
    # Public Works - mechanical services
    PUBLIC_WORKS_MECHANICAL_SERVICES = "3.2.3"
    # Agriculture - policy, planning and administration
    AGRICULTURE_POLICY_PLANNING_AND_ADMINISTRATION = "3.3.1"
    # Agriculture - irrigation
    AGRICULTURE_IRRIGATION = "3.3.2"
    # Agriculture - inputs
    AGRICULTURE_INPUTS = "3.3.3"
    # Agriculture - food crop
    AGRICULTURE_FOOD_CROP = "3.3.4"
    # Agriculture - industrial crop
    AGRICULTURE_INDUSTRIAL_CROP = "3.3.5"
    # Agriculture - livestock
    AGRICULTURE_LIVESTOCK = "3.3.6"
    # Agriculture - agricultural training and extension
    AGRICULTURE_AGRICULTURAL_TRAINING_AND_EXTENSION = "3.3.7"
    # Agriculture - research
    AGRICULTURE_RESEARCH = "3.3.8"
    # Agriculture - other services
    AGRICULTURE_OTHER_SERVICES = "3.3.9"
    # Forestry - policy, planning and administration
    FORESTRY_POLICY_PLANNING_AND_ADMINISTRATION = "3.4.1"
    # Forestry - development and services
    FORESTRY_DEVELOPMENT_AND_SERVICES = "3.4.2"
    # Forestry - education/training
    FORESTRY_EDUCATION_TRAINING = "3.4.3"
    # Forestry - research
    FORESTRY_RESEARCH = "3.4.4"
    # Fishing and Hunting - policy, planning and administration
    FISHING_AND_HUNTING_POLICY_PLANNING_AND_ADMINISTRATION = "3.5.1"
    # Fishing and Hunting - development and services
    FISHING_AND_HUNTING_DEVELOPMENT_AND_SERVICES = "3.5.2"
    # Fishing and Hunting - education and training
    FISHING_AND_HUNTING_EDUCATION_AND_TRAINING = "3.5.3"
    # Fishing and Hunting - research
    FISHING_AND_HUNTING_RESEARCH = "3.5.4"
    # Energy - policy, planning and administration
    ENERGY_POLICY_PLANNING_AND_ADMINISTRATION = "3.6.1"
    # Energy - education and training
    ENERGY_EDUCATION_AND_TRAINING = "3.6.2"
    # Energy - energy regulation
    ENERGY_ENERGY_REGULATION = "3.6.3"
    # Energy - electricity transmission
    ENERGY_ELECTRICITY_TRANSMISSION = "3.6.4"
    # Energy - nuclear
    ENERGY_NUCLEAR = "3.6.5"
    # Energy - power generation
    ENERGY_POWER_GENERATION = "3.6.6"
    # Energy - gas
    ENERGY_GAS = "3.6.7"
    # Mining and Mineral Development - policy, planning and administration
    MINING_AND_MINERAL_DEVELOPMENT_POLICY_PLANNING_AND_ADMINISTRATION = "3.7.1"
    # Mining and Mineral Development - prospection and exploration
    MINING_AND_MINERAL_DEVELOPMENT_PROSPECTION_AND_EXPLORATION = "3.7.2"
    # Mining and Mineral Development - coal and other solid mineral fuels
    MINING_AND_MINERAL_DEVELOPMENT_COAL_AND_OTHER_SOLID_MINERAL_FUELS = "3.7.3"
    # Mining and Mineral Development - petroleum and gas
    MINING_AND_MINERAL_DEVELOPMENT_PETROLEUM_AND_GAS = "3.7.4"
    # Mining and Mineral Development - other fuel
    MINING_AND_MINERAL_DEVELOPMENT_OTHER_FUEL = "3.7.6"
    # Mining and Mineral Development - non fuel minerals
    MINING_AND_MINERAL_DEVELOPMENT_NON_FUEL_MINERALS = "3.7.7"
    # Transport - policy, planning and administration
    TRANSPORT_POLICY_PLANNING_AND_ADMINISTRATION = "3.8.1"
    # Transport - transport regulation
    TRANSPORT_TRANSPORT_REGULATION = "3.8.2"
    # Transport - feeder road construction
    TRANSPORT_FEEDER_ROAD_CONSTRUCTION = "3.8.3"
    # Transport - feeder road maintenance
    TRANSPORT_FEEDER_ROAD_MAINTENANCE = "3.8.4"
    # Transport - national road construction
    TRANSPORT_NATIONAL_ROAD_CONSTRUCTION = "3.8.5"
    # Transport - national road maintenance
    TRANSPORT_NATIONAL_ROAD_MAINTENANCE = "3.8.6"
    # Transport - rail
    TRANSPORT_RAIL = "3.8.7"
    # Transport - water
    TRANSPORT_WATER = "3.8.8"
    # Transport - air
    TRANSPORT_AIR = "3.8.9"
    # Transport - pipeline
    TRANSPORT_PIPELINE = "3.8.10"
    # Transport - storage and distribution
    TRANSPORT_STORAGE_AND_DISTRIBUTION = "3.8.11"
    # Transport - public transport services
    TRANSPORT_PUBLIC_TRANSPORT_SERVICES = "3.8.12"
    # Transport - meteorological services
    TRANSPORT_METEOROLOGICAL_SERVICES = "3.8.13"
    # Transport - education and training
    TRANSPORT_EDUCATION_AND_TRAINING = "3.8.14"
    # Industry - policy, planning and administration
    INDUSTRY_POLICY_PLANNING_AND_ADMINISTRATION = "3.9.1"
    # Industry - development and services
    INDUSTRY_DEVELOPMENT_AND_SERVICES = "3.9.2"
    # Industry - industrial research
    INDUSTRY_INDUSTRIAL_RESEARCH = "3.9.3"
    # Industry - (investment in industry)
    INDUSTRY_INVESTMENT_IN_INDUSTRY = "3.9.4"
    # Communications - policy, planning and administration
    COMMUNICATIONS_POLICY_PLANNING_AND_ADMINISTRATION = "3.10.1"
    # Communications - ICT Infrastructure
    COMMUNICATIONS_ICT_INFRASTRUCTURE = "3.10.2"
    # Communications - telecoms and postal services
    COMMUNICATIONS_TELECOMS_AND_POSTAL_SERVICES = "3.10.3"
    # Communications - information services
    COMMUNICATIONS_INFORMATION_SERVICES = "3.10.4"
    # Tourism - policy, planning and administration
    TOURISM_POLICY_PLANNING_AND_ADMINISTRATION = "3.11.1"
    # Tourism - services
    TOURISM_SERVICES = "3.11.2"
    # Microfinance and financial services - Microfinance and financial services
    MICROFINANCE_AND_FINANCIAL_SERVICES_MICROFINANCE_AND_FINANCIAL_SERVICES = "3.12.1"
    # Water supply and Sanitation - policy, planning and administration
    WATER_SUPPLY_AND_SANITATION_POLICY_PLANNING_AND_ADMINISTRATION = "4.1.1"
    # Water supply and Sanitation - education/training
    WATER_SUPPLY_AND_SANITATION_EDUCATION_TRAINING = "4.1.2"
    # Water supply and Sanitation - rural water supply and sanitation
    WATER_SUPPLY_AND_SANITATION_RURAL_WATER_SUPPLY_AND_SANITATION = "4.1.3"
    # Water supply and Sanitation - urban water supply and sanitation
    WATER_SUPPLY_AND_SANITATION_URBAN_WATER_SUPPLY_AND_SANITATION = "4.1.4"
    # Water supply and Sanitation - rural water supply
    WATER_SUPPLY_AND_SANITATION_RURAL_WATER_SUPPLY = "4.1.5"
    # Water supply and Sanitation - urban water supply
    WATER_SUPPLY_AND_SANITATION_URBAN_WATER_SUPPLY = "4.1.6"
    # Water supply and Sanitation - rural sanitation
    WATER_SUPPLY_AND_SANITATION_RURAL_SANITATION = "4.1.7"
    # Water supply and Sanitation - urban sanitation
    WATER_SUPPLY_AND_SANITATION_URBAN_SANITATION = "4.1.8"
    # Water supply and Sanitation - sewage and waste management
    WATER_SUPPLY_AND_SANITATION_SEWAGE_AND_WASTE_MANAGEMENT = "4.1.9"
    # Environment - policy, planning and administration
    ENVIRONMENT_POLICY_PLANNING_AND_ADMINISTRATION = "4.2.1"
    # Environment - research/ education and training
    ENVIRONMENT_RESEARCH_EDUCATION_AND_TRAINING = "4.2.2"
    # Environment - natural resource management
    ENVIRONMENT_NATURAL_RESOURCE_MANAGEMENT = "4.2.3"
    # Environment - water resources management
    ENVIRONMENT_WATER_RESOURCES_MANAGEMENT = "4.2.4"
    # Environment - wildlife protection, parks and site preservation
    ENVIRONMENT_WILDLIFE_PROTECTION_PARKS_AND_SITE_PRESERVATION = "4.2.5"
    # Health - policy, planning and administration
    HEALTH_POLICY_PLANNING_AND_ADMINISTRATION = "5.1.1"
    # Recreation, Culture and Religion - recreation and sport
    RECREATION_CULTURE_AND_RELIGION_RECREATION_AND_SPORT = "5.2.1"
    # Recreation, Culture and Religion - culture
    RECREATION_CULTURE_AND_RELIGION_CULTURE = "5.2.2"
    # Recreation, Culture and Religion - broadcasting and publishing
    RECREATION_CULTURE_AND_RELIGION_BROADCASTING_AND_PUBLISHING = "5.2.3"
    # Recreation, Culture and Religion - religion
    RECREATION_CULTURE_AND_RELIGION_RELIGION = "5.2.4"
    # Education - administration, policy and planning
    EDUCATION_ADMINISTRATION_POLICY_AND_PLANNING = "5.3.1"
    # Education - research
    EDUCATION_RESEARCH = "5.3.2"
    # Education - pre-primary
    EDUCATION_PRE_PRIMARY = "5.3.3"
    # Education - primary
    EDUCATION_PRIMARY = "5.3.4"
    # Education - lower secondary
    EDUCATION_LOWER_SECONDARY = "5.3.5"
    # Education - upper secondary
    EDUCATION_UPPER_SECONDARY = "5.3.6"
    # Education - post secondary non tertiary
    EDUCATION_POST_SECONDARY_NON_TERTIARY = "5.3.7"
    # Education - tertiary
    EDUCATION_TERTIARY = "5.3.8"
    # Education - vocational training
    EDUCATION_VOCATIONAL_TRAINING = "5.3.9"
    # Education - advanced technical and managerial training
    EDUCATION_ADVANCED_TECHNICAL_AND_MANAGERIAL_TRAINING = "5.3.10"
    # Education - basic adult education
    EDUCATION_BASIC_ADULT_EDUCATION = "5.3.11"
    # Education - teacher training
    EDUCATION_TEACHER_TRAINING = "5.3.12"
    # Education - subsidiary services
    EDUCATION_SUBSIDIARY_SERVICES = "5.3.13"
    # Social Protection, Land Housing and Community Amenities - policy, planning and administration
    SOCIAL_PROTECTION_LAND_HOUSING_AND_COMMUNITY_AMENITIES_POLICY_PLANNING_AND_ADMINISTRATION = "5.4.1"
    # Social Protection, Land Housing and Community Amenities - social security (excl pensions)
    SOCIAL_PROTECTION_LAND_HOUSING_AND_COMMUNITY_AMENITIES_SOCIAL_SECURITY_EXCL_PENSIONS = "5.4.2"
    # Social Protection, Land Housing and Community Amenities - general pensions
    SOCIAL_PROTECTION_LAND_HOUSING_AND_COMMUNITY_AMENITIES_GENERAL_PENSIONS = "5.4.3"
    # Social Protection, Land Housing and Community Amenities - civil service and military pensions
    SOCIAL_PROTECTION_LAND_HOUSING_AND_COMMUNITY_AMENITIES_CIVIL_SERVICE_AND_MILITARY_PENSIONS = "5.4.4"
    # Social Protection, Land Housing and Community Amenities - social services (incl youth development and women+ children)
    SOCIAL_PROTECTION_LAND_HOUSING_AND_COMMUNITY_AMENITIES_SOCIAL_SERVICES_INCL_YOUTH_DEVELOPMENT_AND_WOMEN_CHILDREN = "5.4.5"
    # Social Protection, Land Housing and Community Amenities - land policy and management
    SOCIAL_PROTECTION_LAND_HOUSING_AND_COMMUNITY_AMENITIES_LAND_POLICY_AND_MANAGEMENT = "5.4.6"
    # Social Protection, Land Housing and Community Amenities - rural devt
    SOCIAL_PROTECTION_LAND_HOUSING_AND_COMMUNITY_AMENITIES_RURAL_DEVT = "5.4.7"
    # Social Protection, Land Housing and Community Amenities - urban devt
    SOCIAL_PROTECTION_LAND_HOUSING_AND_COMMUNITY_AMENITIES_URBAN_DEVT = "5.4.8"
    # Social Protection, Land Housing and Community Amenities - housing and community amenities
    SOCIAL_PROTECTION_LAND_HOUSING_AND_COMMUNITY_AMENITIES_HOUSING_AND_COMMUNITY_AMENITIES = "5.4.9"
    # Social Protection, Land Housing and Community Amenities - emergency relief
    SOCIAL_PROTECTION_LAND_HOUSING_AND_COMMUNITY_AMENITIES_EMERGENCY_RELIEF = "5.4.10"
    # Social Protection, Land Housing and Community Amenities - disaster prevention and preparedness
    SOCIAL_PROTECTION_LAND_HOUSING_AND_COMMUNITY_AMENITIES_DISASTER_PREVENTION_AND_PREPAREDNESS = "5.4.11"
    # Social Protection, Land Housing and Community Amenities - support to refugees and internally displaced persons
    SOCIAL_PROTECTION_LAND_HOUSING_AND_COMMUNITY_AMENITIES_SUPPORT_TO_REFUGEES_AND_INTERNALLY_DISPLACED_PERSONS = "5.4.12"
    # Development Partner affairs - policy planning and administration
    DEVELOPMENT_PARTNER_AFFAIRS_POLICY_PLANNING_AND_ADMINISTRATION = "6.1.1"
    # Development Partner affairs - Technical staff services
    DEVELOPMENT_PARTNER_AFFAIRS_TECHNICAL_STAFF_SERVICES = "6.1.2"
    # External to government sector - External to general government sector
    EXTERNAL_TO_GOVERNMENT_SECTOR_EXTERNAL_TO_GENERAL_GOVERNMENT_SECTOR = "7.1.1"
    # General Budget Support - General Budget Support
    GENERAL_BUDGET_SUPPORT_GENERAL_BUDGET_SUPPORT = "7.2.1"


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
    # withdrawn 451, 452, 453
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


# This is a huge list so we load it from a CSV file
# Location type - administrative region, populated place, etc.
# Reference: https://iatistandard.org/en/iati-standard/203/codelists/locationtype/

LocationType = LocationTypeData.to_enum("LocationType")


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


# This is a huge list so we load it from a CSV file
SectorCategory = SectorCategoryData.to_enum(enum_name="SectorCategory")


class TiedStatus(Enum):
    """
    Tied status - untied, partially tied, etc.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/tiedstatus/
    """
    PARTIALLY_TIED = "3"
    TIED = "4"
    UNTIED = "5"


class DisbursementChannel(Enum):
    """
    Disbursement channel - how funds are delivered.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/disbursementchannel/
    """
    CENTRAL_MINISTRY_OF_FINANCE = "1"
    DIRECTLY_TO_IMPLEMENTING_INSTITUTION = "2"
    IN_KIND_THROUGH_THIRD_PARTY = "3"
    IN_KIND_MANAGED_BY_DONOR = "4"


class RecipientRegion(Enum):
    """
    DAC regions and other regional classifications.
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/region/
    """
    # DAC Regions
    EX_YUGOSLAVIA_UNSPECIFIED = "88"
    EUROPE_REGIONAL = "89"
    NORTH_OF_SAHARA_REGIONAL = "189"
    SOUTH_OF_SAHARA_REGIONAL = "289"
    AFRICA_REGIONAL = "298"
    CARIBBEAN_AND_CENTRAL_AMERICA_REGIONAL = "389"
    SOUTH_AMERICA_REGIONAL = "489"
    AMERICA_REGIONAL = "498"
    MIDDLE_EAST_REGIONAL = "589"
    CENTRAL_ASIA_REGIONAL = "619"
    SOUTH_ASIA_REGIONAL = "679"
    SOUTH_AND_CENTRAL_ASIA_REGIONAL = "689"
    FAR_EAST_ASIA_REGIONAL = "789"
    ASIA_REGIONAL = "798"
    OCEANIA_REGIONAL = "889"
    DEVELOPING_COUNTRIES_UNSPECIFIED = "998"
    EASTERN_AFRICA_REGIONAL = "1027"
    MIDDLE_AFRICA_REGIONAL = "1028"
    SOUTHERN_AFRICA_REGIONAL = "1029"
    WESTERN_AFRICA_REGIONAL = "1030"
    CARIBBEAN_REGIONAL = "1031"
    CENTRAL_AMERICA_REGIONAL = "1032"
    MELANESIA_REGIONAL = "1033"
    MICRONESIA_REGIONAL = "1034"
    POLYNESIA_REGIONAL = "1035"


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


class PolicyMarkerVocabulary(Enum):
    """
    Vocabulary type - OECD DAC, UN, etc.
    Previous reference (outdated): https://iatistandard.org/en/iati-standard/203/codelists/vocabulary/
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/policymarkervocabulary/
    """
    OECD_DAC_CRS = "1"
    REPORTING_ORGANISATION = "99"


class Sector_Vocabulary(Enum):
    """
    Vocabulary type - OECD DAC, UN, etc.
    Previous reference (outdated): https://iatistandard.org/en/iati-standard/203/codelists/vocabulary/
    Reference: https://iatistandard.org/en/iati-standard/203/codelists/sectorvocabulary/
    """
    OECD_DAC_CRS_PURPOSE = "1"
    OECD_DAC_CRS_SECTOR_CATEGORY = "2"
    UN_COFOG = "3"
    EU_NACE_REV2 = "4"
    US_NTEE = "5"
    AIDDATA = "6"
    UNSDG_GOAL = "7"
    UNSDG_TARGET = "8"
    UNSDG_INDICATOR = "9"
    IASC_HUMANITARIAN_CLUSTERS = "10"
    US_NAICS = "11"
    UN_DATA_STANDARDS = "12"
    REPORTING_ORG_2 = "98"
    REPORTING_ORG = "99"


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


# NO aparece en la version 2.03
# class AidTypeFlag(Enum):
#     """
#     Flag indicating type of aid.
#     Reference: https://iatistandard.org/en/iati-standard/203/codelists/aidtypeflag/
#     """
#     FREE_STANDING_TECHNICAL_COOPERATION = "1"
#     PROGRAM_BASED_APPROACH = "2"
#     INVESTMENT_PROJECT = "3"
#     ASSOCIATED_FINANCING = "4"


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
