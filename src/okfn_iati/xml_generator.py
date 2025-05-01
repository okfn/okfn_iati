import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from typing import List

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

    def _create_narrative_elements(self, parent_element: ET.Element, narratives: List[Narrative]) -> None:
        for narrative in narratives:
            narrative_el = ET.SubElement(parent_element, "narrative")
            narrative_el.text = narrative.text
            if narrative.lang:
                narrative_el.set("xml:lang", narrative.lang)

    def _add_organization_ref(self, parent_element: ET.Element, org: OrganizationRef) -> ET.Element:
        if org.ref:
            parent_element.set("ref", org.ref)
        if org.type:
            parent_element.set("type", org.type)

        if org.narratives:
            self._create_narrative_elements(parent_element, org.narratives)

        return parent_element

    def _add_participating_org(self, activity_el: ET.Element, org: ParticipatingOrg) -> None:
        org_el = ET.SubElement(activity_el, "participating-org")
        org_el.set("role", org.role)

        if org.ref:
            org_el.set("ref", org.ref)
        if org.type:
            org_el.set("type", org.type)
        if org.activity_id:
            org_el.set("activity-id", org.activity_id)
        if org.crs_channel_code:
            org_el.set("crs-channel-code", org.crs_channel_code)

        self._create_narrative_elements(org_el, org.narratives)

    def _add_activity_date(self, activity_el: ET.Element, date: ActivityDate) -> None:
        date_el = ET.SubElement(activity_el, "activity-date")
        date_el.set("type", date.type)
        date_el.set("iso-date", date.iso_date)

        self._create_narrative_elements(date_el, date.narratives)

    def _add_contact_info(self, activity_el: ET.Element, contact: ContactInfo) -> None:
        contact_el = ET.SubElement(activity_el, "contact-info")

        if contact.type:
            contact_el.set("type", contact.type)

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
            reach_el.set("code", location.location_reach)

        if location.location_id:
            id_el = ET.SubElement(loc_el, "location-id")
            for key, value in location.location_id.items():
                id_el.set(key, value)

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
            exact_el.set("code", location.exactness)

        if location.location_class:
            class_el = ET.SubElement(loc_el, "location-class")
            class_el.set("code", location.location_class)

        if location.feature_designation:
            feat_el = ET.SubElement(loc_el, "feature-designation")
            feat_el.set("code", location.feature_designation)

    def _add_document_link(self, activity_el: ET.Element, doc: DocumentLink) -> None:
        doc_el = ET.SubElement(activity_el, "document-link")
        doc_el.set("url", doc.url)
        doc_el.set("format", doc.format)

        title_el = ET.SubElement(doc_el, "title")
        self._create_narrative_elements(title_el, doc.title)

        for category in doc.categories:
            cat_el = ET.SubElement(doc_el, "category")
            cat_el.set("code", category)

        for language in doc.languages:
            lang_el = ET.SubElement(doc_el, "language")
            lang_el.set("code", language)

        if doc.document_date:
            date_el = ET.SubElement(doc_el, "document-date")
            date_el.set("iso-date", doc.document_date)

    def _add_budget(self, activity_el: ET.Element, budget: Budget) -> None:
        budget_el = ET.SubElement(activity_el, "budget")
        budget_el.set("type", budget.type)
        budget_el.set("status", budget.status)

        start_el = ET.SubElement(budget_el, "period-start")
        start_el.set("iso-date", budget.period_start)

        end_el = ET.SubElement(budget_el, "period-end")
        end_el.set("iso-date", budget.period_end)

        value_el = ET.SubElement(budget_el, "value")
        value_el.text = str(budget.value)

        if budget.currency:
            value_el.set("currency", budget.currency)

        if budget.value_date:
            value_el.set("value-date", budget.value_date)

    def _add_transaction(self, activity_el: ET.Element, transaction: Transaction) -> None:
        trans_el = ET.SubElement(activity_el, "transaction")

        if transaction.transaction_ref:
            trans_el.set("ref", transaction.transaction_ref)

        type_el = ET.SubElement(trans_el, "transaction-type")
        type_el.set("code", transaction.type)

        date_el = ET.SubElement(trans_el, "transaction-date")
        date_el.set("iso-date", transaction.date)

        value_el = ET.SubElement(trans_el, "value")
        value_el.text = str(transaction.value)

        if transaction.currency:
            value_el.set("currency", transaction.currency)

        if transaction.value_date:
            value_el.set("value-date", transaction.value_date)

        if transaction.description:
            desc_el = ET.SubElement(trans_el, "description")
            self._create_narrative_elements(desc_el, transaction.description)

        if transaction.provider_org:
            provider_el = ET.SubElement(trans_el, "provider-org")
            self._add_organization_ref(provider_el, transaction.provider_org)

        if transaction.receiver_org:
            receiver_el = ET.SubElement(trans_el, "receiver-org")
            self._add_organization_ref(receiver_el, transaction.receiver_org)

        # Additional transaction elements would go here (sector, recipient-country, etc.)

    def _add_result(self, activity_el: ET.Element, result: Result) -> None:
        result_el = ET.SubElement(activity_el, "result")
        result_el.set("type", result.type)

        if result.aggregation_status is not None:
            result_el.set("aggregation-status", str(1 if result.aggregation_status else 0))

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
            activity_el.set("default-currency", activity.default_currency)

        if activity.hierarchy:
            activity_el.set("hierarchy", activity.hierarchy)

        if activity.last_updated_datetime:
            activity_el.set("last-updated-datetime", activity.last_updated_datetime)
        else:
            activity_el.set("last-updated-datetime", datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))

        if activity.xml_lang:
            activity_el.set("xml:lang", activity.xml_lang)

        if activity.humanitarian is not None:
            activity_el.set("humanitarian", "1" if activity.humanitarian else "0")

        # Add identifier
        id_el = ET.SubElement(activity_el, "iati-identifier")
        id_el.text = activity.iati_identifier

        # Add reporting org
        reporting_org_el = ET.SubElement(activity_el, "reporting-org")
        self._add_organization_ref(reporting_org_el, activity.reporting_org)

        # Add title
        title_el = ET.SubElement(activity_el, "title")
        self._create_narrative_elements(title_el, activity.title)

        # Add descriptions
        for desc in activity.description:
            desc_el = ET.SubElement(activity_el, "description")
            if "type" in desc:
                desc_el.set("type", desc["type"])
            self._create_narrative_elements(desc_el, desc["narratives"])

        # Add participating orgs
        for org in activity.participating_orgs:
            self._add_participating_org(activity_el, org)

        # Add activity status
        if activity.activity_status:
            status_el = ET.SubElement(activity_el, "activity-status")
            status_el.set("code", str(activity.activity_status.value))

        # Add activity dates
        for date in activity.activity_dates:
            self._add_activity_date(activity_el, date)

        # Add contact info
        if activity.contact_info:
            self._add_contact_info(activity_el, activity.contact_info)

        # Add recipient countries
        for country in activity.recipient_countries:
            country_el = ET.SubElement(activity_el, "recipient-country")
            country_el.set("code", country["code"])

            if "percentage" in country:
                country_el.set("percentage", str(country["percentage"]))

            if "narratives" in country:
                self._create_narrative_elements(country_el, country["narratives"])

        # Add recipient regions
        for region in activity.recipient_regions:
            region_el = ET.SubElement(activity_el, "recipient-region")
            region_el.set("code", region["code"])

            if "vocabulary" in region:
                region_el.set("vocabulary", region["vocabulary"])

            if "percentage" in region:
                region_el.set("percentage", str(region["percentage"]))

            if "narratives" in region:
                self._create_narrative_elements(region_el, region["narratives"])

        # Add locations
        for location in activity.locations:
            self._add_location(activity_el, location)

        # Add sectors
        for sector in activity.sectors:
            sector_el = ET.SubElement(activity_el, "sector")
            sector_el.set("code", sector["code"])

            if "vocabulary" in sector:
                sector_el.set("vocabulary", sector["vocabulary"])

            if "percentage" in sector:
                sector_el.set("percentage", str(sector["percentage"]))

            if "narratives" in sector:
                self._create_narrative_elements(sector_el, sector["narratives"])

        # Add document links
        for doc in activity.document_links:
            self._add_document_link(activity_el, doc)

        # Add budgets
        for budget in activity.budgets:
            self._add_budget(activity_el, budget)

        # Add transactions
        for transaction in activity.transactions:
            self._add_transaction(activity_el, transaction)

        # Add related activities
        for related in activity.related_activities:
            related_el = ET.SubElement(activity_el, "related-activity")
            related_el.set("ref", related["ref"])
            related_el.set("type", related["type"])

        # Add results
        for result in activity.results:
            self._add_result(activity_el, result)

        return activity_el

    def generate_iati_activities_xml(self, iati_activities: IatiActivities) -> str:
        root = ET.Element("iati-activities")
        root.set("version", iati_activities.version)
        root.set("generated-datetime", iati_activities.generated_datetime)

        for activity in iati_activities.activities:
            activity_el = self.generate_activity_xml(activity)
            root.append(activity_el)

        # Convert to string with pretty formatting
        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def save_to_file(self, iati_activities: IatiActivities, file_path: str) -> None:
        xml_string = self.generate_iati_activities_xml(iati_activities)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_string)
