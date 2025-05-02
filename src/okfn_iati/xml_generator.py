import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from typing import List, Union, Optional, Any
from enum import Enum

from .models import (
    IatiActivities, Activity, Narrative, OrganizationRef, ParticipatingOrg,
    ActivityDate, ContactInfo, Location, DocumentLink, Budget, Transaction,
    Result
)


class IatiXmlGenerator:
    def __init__(self):
        self.nsmap = {
            None: "http://www.iati.org/ns/iati",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance"
        }

    def _get_enum_value(self, value: Union[Enum, str, None]) -> Optional[str]:
        """Helper to extract string value from enum or return string directly"""
        if value is None:
            return None
        if isinstance(value, Enum):
            return value.value
        return value

    def _set_attribute(self, element: ET.Element, name: str, value: Any) -> None:
        """Helper to safely set XML attributes, handling None values"""
        if value is not None:
            element.set(name, str(value))

    def _create_narrative_elements(self, parent_element: ET.Element, narratives: List[Narrative]) -> None:
        for narrative in narratives:
            narrative_el = ET.SubElement(parent_element, "narrative")
            narrative_el.text = narrative.text
            if narrative.lang:
                narrative_el.set("xml:lang", narrative.lang)

    def _add_organization_ref(self, parent_element: ET.Element, org: OrganizationRef) -> ET.Element:
        if org.ref:
            self._set_attribute(parent_element, "ref", org.ref)
        if org.type:
            self._set_attribute(parent_element, "type", org.type)

        if org.narratives:
            self._create_narrative_elements(parent_element, org.narratives)

        return parent_element

    def _add_participating_org(self, activity_el: ET.Element, org: ParticipatingOrg) -> None:
        org_el = ET.SubElement(activity_el, "participating-org")
        self._set_attribute(org_el, "role", self._get_enum_value(org.role))

        if org.ref:
            self._set_attribute(org_el, "ref", org.ref)
        if org.type:
            self._set_attribute(org_el, "type", self._get_enum_value(org.type))
        if org.activity_id:
            self._set_attribute(org_el, "activity-id", org.activity_id)
        if org.crs_channel_code:
            self._set_attribute(org_el, "crs-channel-code", org.crs_channel_code)

        self._create_narrative_elements(org_el, org.narratives)

    def _add_activity_date(self, activity_el: ET.Element, date: ActivityDate) -> None:
        date_el = ET.SubElement(activity_el, "activity-date")
        self._set_attribute(date_el, "type", self._get_enum_value(date.type))
        self._set_attribute(date_el, "iso-date", date.iso_date)

        self._create_narrative_elements(date_el, date.narratives)

    def _add_contact_info(self, activity_el: ET.Element, contact: ContactInfo) -> None:
        contact_el = ET.SubElement(activity_el, "contact-info")

        if contact.type:
            self._set_attribute(contact_el, "type", self._get_enum_value(contact.type))

        if contact.organisation:
            org_el = ET.SubElement(contact_el, "organisation")
            self._create_narrative_elements(org_el, contact.organisation)

        if contact.department:
            dept_el = ET.SubElement(contact_el, "department")
            self._create_narrative_elements(dept_el, contact.department)

        if contact.person_name:
            person_el = ET.SubElement(contact_el, "person-name")
            self._create_narrative_elements(person_el, contact.person_name)

        if contact.job_title:
            job_el = ET.SubElement(contact_el, "job-title")
            self._create_narrative_elements(job_el, contact.job_title)

        if contact.telephone:
            tel_el = ET.SubElement(contact_el, "telephone")
            tel_el.text = contact.telephone

        if contact.email:
            email_el = ET.SubElement(contact_el, "email")
            email_el.text = contact.email

        if contact.website:
            web_el = ET.SubElement(contact_el, "website")
            web_el.text = contact.website

        if contact.mailing_address:
            addr_el = ET.SubElement(contact_el, "mailing-address")
            self._create_narrative_elements(addr_el, contact.mailing_address)

    def _add_location(self, activity_el: ET.Element, location: Location) -> None:  # noqa: C901
        loc_el = ET.SubElement(activity_el, "location")

        if location.location_reach:
            reach_el = ET.SubElement(loc_el, "location-reach")
            self._set_attribute(reach_el, "code", self._get_enum_value(location.location_reach))

        if location.location_id:
            id_el = ET.SubElement(loc_el, "location-id")
            self._set_attribute(id_el, "vocabulary", self._get_enum_value(location.location_id.vocabulary))
            self._set_attribute(id_el, "code", location.location_id.code)

        if location.name:
            name_el = ET.SubElement(loc_el, "name")
            self._create_narrative_elements(name_el, location.name)

        if location.description:
            desc_el = ET.SubElement(loc_el, "description")
            self._create_narrative_elements(desc_el, location.description)

        if location.activity_description:
            act_desc_el = ET.SubElement(loc_el, "activity-description")
            self._create_narrative_elements(act_desc_el, location.activity_description)

        if location.administrative:
            for admin in location.administrative:
                admin_el = ET.SubElement(loc_el, "administrative")
                for key, value in admin.items():
                    admin_el.set(key, value)

        if location.point:
            point_el = ET.SubElement(loc_el, "point")
            if "srsName" in location.point:
                point_el.set("srsName", location.point["srsName"])

            if "pos" in location.point:
                pos_el = ET.SubElement(point_el, "pos")
                pos_el.text = location.point["pos"]

        if location.exactness:
            exact_el = ET.SubElement(loc_el, "exactness")
            self._set_attribute(exact_el, "code", self._get_enum_value(location.exactness))

        if location.location_class:
            class_el = ET.SubElement(loc_el, "location-class")
            self._set_attribute(class_el, "code", self._get_enum_value(location.location_class))

        if location.feature_designation:
            feat_el = ET.SubElement(loc_el, "feature-designation")
            self._set_attribute(feat_el, "code", location.feature_designation)

    def _add_document_link(self, activity_el: ET.Element, doc: DocumentLink) -> None:
        doc_el = ET.SubElement(activity_el, "document-link")
        self._set_attribute(doc_el, "url", doc.url)
        self._set_attribute(doc_el, "format", doc.format)

        title_el = ET.SubElement(doc_el, "title")
        self._create_narrative_elements(title_el, doc.title)

        for category in doc.categories:
            cat_el = ET.SubElement(doc_el, "category")
            self._set_attribute(cat_el, "code", self._get_enum_value(category))

        for language in doc.languages:
            lang_el = ET.SubElement(doc_el, "language")
            self._set_attribute(lang_el, "code", language)

        if doc.document_date:
            date_el = ET.SubElement(doc_el, "document-date")
            self._set_attribute(date_el, "iso-date", doc.document_date)

    def _add_budget(self, activity_el: ET.Element, budget: Budget) -> None:
        budget_el = ET.SubElement(activity_el, "budget")
        self._set_attribute(budget_el, "type", self._get_enum_value(budget.type))
        self._set_attribute(budget_el, "status", self._get_enum_value(budget.status))

        start_el = ET.SubElement(budget_el, "period-start")
        self._set_attribute(start_el, "iso-date", budget.period_start)

        end_el = ET.SubElement(budget_el, "period-end")
        self._set_attribute(end_el, "iso-date", budget.period_end)

        value_el = ET.SubElement(budget_el, "value")
        value_el.text = str(budget.value)

        if budget.currency:
            self._set_attribute(value_el, "currency", budget.currency)

        if budget.value_date:
            self._set_attribute(value_el, "value-date", budget.value_date)

    def _add_transaction(self, activity_el: ET.Element, transaction: Transaction) -> None:
        trans_el = ET.SubElement(activity_el, "transaction")

        if transaction.transaction_ref:
            self._set_attribute(trans_el, "ref", transaction.transaction_ref)

        type_el = ET.SubElement(trans_el, "transaction-type")
        self._set_attribute(type_el, "code", self._get_enum_value(transaction.type))

        date_el = ET.SubElement(trans_el, "transaction-date")
        self._set_attribute(date_el, "iso-date", transaction.date)

        value_el = ET.SubElement(trans_el, "value")
        value_el.text = str(transaction.value)

        if transaction.currency:
            self._set_attribute(value_el, "currency", transaction.currency)

        if transaction.value_date:
            self._set_attribute(value_el, "value-date", transaction.value_date)

        if transaction.description:
            desc_el = ET.SubElement(trans_el, "description")
            self._create_narrative_elements(desc_el, transaction.description)

        if transaction.provider_org:
            provider_el = ET.SubElement(trans_el, "provider-org")
            self._add_organization_ref(provider_el, transaction.provider_org)

        if transaction.receiver_org:
            receiver_el = ET.SubElement(trans_el, "receiver-org")
            self._add_organization_ref(receiver_el, transaction.receiver_org)

        if transaction.flow_type:
            flow_el = ET.SubElement(trans_el, "flow-type")
            self._set_attribute(flow_el, "code", self._get_enum_value(transaction.flow_type))

        if transaction.finance_type:
            finance_el = ET.SubElement(trans_el, "finance-type")
            self._set_attribute(finance_el, "code", self._get_enum_value(transaction.finance_type))

        if transaction.tied_status:
            tied_el = ET.SubElement(trans_el, "tied-status")
            self._set_attribute(tied_el, "code", self._get_enum_value(transaction.tied_status))

    def _add_result(self, activity_el: ET.Element, result: Result) -> None:
        result_el = ET.SubElement(activity_el, "result")
        self._set_attribute(result_el, "type", self._get_enum_value(result.type))

        if result.aggregation_status is not None:
            self._set_attribute(result_el, "aggregation-status", str(1 if result.aggregation_status else 0))

        if result.title:
            title_el = ET.SubElement(result_el, "title")
            self._create_narrative_elements(title_el, result.title)

        if result.description:
            desc_el = ET.SubElement(result_el, "description")
            self._create_narrative_elements(desc_el, result.description)

        # Result indicators would be added here in a more complete implementation

    def generate_activity_xml(self, activity: Activity) -> ET.Element:  # noqa: C901
        activity_el = ET.Element("iati-activity")

        # Set activity attributes
        if activity.default_currency:
            self._set_attribute(activity_el, "default-currency", activity.default_currency)

        if activity.hierarchy:
            self._set_attribute(activity_el, "hierarchy", activity.hierarchy)

        if activity.last_updated_datetime:
            self._set_attribute(activity_el, "last-updated-datetime", activity.last_updated_datetime)
        else:
            self._set_attribute(activity_el, "last-updated-datetime", datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))

        if activity.xml_lang:
            self._set_attribute(activity_el, "xml:lang", activity.xml_lang)

        if activity.humanitarian is not None:
            self._set_attribute(activity_el, "humanitarian", "1" if activity.humanitarian else "0")

        # IMPORTANT: Follow IATI Schema element order
        # 1. Add identifier
        id_el = ET.SubElement(activity_el, "iati-identifier")
        id_el.text = activity.iati_identifier

        # 2. Add reporting org
        reporting_org_el = ET.SubElement(activity_el, "reporting-org")
        self._add_organization_ref(reporting_org_el, activity.reporting_org)

        # 3. Add title
        title_el = ET.SubElement(activity_el, "title")
        self._create_narrative_elements(title_el, activity.title)

        # 4. Add descriptions
        for desc in activity.description:
            desc_el = ET.SubElement(activity_el, "description")
            if "type" in desc:
                self._set_attribute(desc_el, "type", desc["type"])
            self._create_narrative_elements(desc_el, desc["narratives"])

        # 5. Add participating orgs
        for org in activity.participating_orgs:
            self._add_participating_org(activity_el, org)

        # 6. Add activity status
        if activity.activity_status:
            status_el = ET.SubElement(activity_el, "activity-status")
            self._set_attribute(status_el, "code", str(activity.activity_status.value))

        # 7. Add activity dates
        for date in activity.activity_dates:
            self._add_activity_date(activity_el, date)

        # 8. Add contact info
        if activity.contact_info:
            self._add_contact_info(activity_el, activity.contact_info)

        # 9. Add recipient countries
        for country in activity.recipient_countries:
            country_el = ET.SubElement(activity_el, "recipient-country")
            self._set_attribute(country_el, "code", country["code"])

            if "percentage" in country:
                self._set_attribute(country_el, "percentage", str(country["percentage"]))

            if "narratives" in country:
                self._create_narrative_elements(country_el, country["narratives"])

        # 10. Add recipient regions
        for region in activity.recipient_regions:
            region_el = ET.SubElement(activity_el, "recipient-region")
            self._set_attribute(region_el, "code", region["code"])

            if "vocabulary" in region:
                self._set_attribute(region_el, "vocabulary", region["vocabulary"])

            if "percentage" in region:
                self._set_attribute(region_el, "percentage", str(region["percentage"]))

            if "narratives" in region:
                self._create_narrative_elements(region_el, region["narratives"])

        # 11. Add locations
        for location in activity.locations:
            self._add_location(activity_el, location)

        # 12. Add sectors (REQUIRED by IATI rules)
        for sector in activity.sectors:
            sector_el = ET.SubElement(activity_el, "sector")
            self._set_attribute(sector_el, "code", sector["code"])

            if "vocabulary" in sector:
                self._set_attribute(sector_el, "vocabulary", sector["vocabulary"])

            if "percentage" in sector:
                self._set_attribute(sector_el, "percentage", str(sector["percentage"]))

            if "narratives" in sector:
                self._create_narrative_elements(sector_el, sector["narratives"])

        # 13. Add budgets
        for budget in activity.budgets:
            self._add_budget(activity_el, budget)

        # 14. Add transactions (Must come before document-link per IATI schema)
        for transaction in activity.transactions:
            self._add_transaction(activity_el, transaction)

        # 15. Add document links 
        for doc in activity.document_links:
            self._add_document_link(activity_el, doc)

        # 16. Add related activities
        for related in activity.related_activities:
            related_el = ET.SubElement(activity_el, "related-activity")
            self._set_attribute(related_el, "ref", related["ref"])
            if "type" in related:
                self._set_attribute(related_el, "type", self._get_enum_value(related.get("type")))

        # 17. Add results
        for result in activity.results:
            self._add_result(activity_el, result)

        return activity_el

    def generate_iati_activities_xml(self, iati_activities: IatiActivities) -> str:
        root = ET.Element("iati-activities")
        self._set_attribute(root, "version", iati_activities.version)
        self._set_attribute(root, "generated-datetime", iati_activities.generated_datetime)

        # Add XML namespace references to match IATI standard
        self._set_attribute(root, "xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
        self._set_attribute(root, "xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")

        for activity in iati_activities.activities:
            activity_el = self.generate_activity_xml(activity)
            root.append(activity_el)

        # Convert to string with pretty formatting
        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        xml_string = reparsed.toprettyxml(indent="  ")

        # Add generator comment after the XML declaration
        repo_url = "https://github.com/okfn/okfn-iati"
        comment = f"<!-- Generated by OKFN-IATI: {repo_url} -->"
        xml_declaration_end = xml_string.find("?>") + 2
        xml_string = xml_string[:xml_declaration_end] + "\n" + comment + xml_string[xml_declaration_end:]

        return xml_string

    def save_to_file(self, iati_activities: IatiActivities, file_path: str) -> None:
        xml_string = self.generate_iati_activities_xml(iati_activities)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_string)
