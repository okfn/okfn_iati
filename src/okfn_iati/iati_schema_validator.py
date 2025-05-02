from io import BytesIO
from pathlib import Path
from typing import Dict, List, Tuple
from lxml import etree


class IatiValidator:
    """
    Validator for IATI XML documents that checks:
    1. XML schema validity
    2. IATI ruleset compliance
    """

    SCHEMA_PATHS = {
        # from https://raw.githubusercontent.com/IATI/IATI-Schemas/version-2.03/iati-activities-schema.xsd
        # at okfn_iati/schemas/2.03/iati-activities-schema.xsd
        "2.03": {
            "main": "iati-activities-schema.xsd",
            "dependencies": [
                "iati-common.xsd",
                "xml.xsd"
            ]
        }
    }

    def __init__(self, version="2.03"):
        if version not in self.SCHEMA_PATHS:
            raise ValueError(f"Unsupported IATI version: {version}")
        self.version = version
        self.schema = self._load_schema()

    def _load_schema(self):
        """Load schema from local files"""
        schema_path = self.SCHEMA_PATHS[self.version]["main"]
        parser = etree.XMLParser()
        base_schema_folder = Path(__file__).parent / "schemas" / self.version
        schema_path = base_schema_folder / schema_path
        schema_doc = etree.parse(schema_path, parser)
        return etree.XMLSchema(schema_doc)

    def validate_xml(self, xml_string: str) -> Tuple[bool, List[str]]:
        """
        Validate XML against the IATI schema.

        Args:
            xml_string: XML string to validate

        Returns:
            Tuple containing:
                - Boolean indicating if the XML is valid
                - List of error messages
        """
        try:
            # Parse the XML
            parser = etree.XMLParser()
            doc = etree.parse(BytesIO(xml_string.encode('utf-8')), parser)

            # Extract version attribute
            # Validate against schema
            schema = self.schema
            is_valid = schema.validate(doc)

            if is_valid:
                return True, []
            else:
                errors = [str(error) for error in schema.error_log]
                return False, errors

        except etree.XMLSyntaxError as e:
            return False, [f"XML syntax error: {str(e)}"]
        except Exception as e:
            return False, [f"Validation error: {str(e)}"]

    def check_ruleset(self, xml_string: str) -> Tuple[bool, List[str]]:  # noqa: C901
        """
        Check IATI ruleset compliance. This includes rules that aren't part of the XML schema
        but are required for IATI compliance (like required elements).

        Args:
            xml_string: XML string to validate

        Returns:
            Tuple containing:
                - Boolean indicating if the XML complies with IATI rulesets
                - List of ruleset error messages
        """
        errors = []

        try:
            # Parse the XML
            doc = etree.parse(BytesIO(xml_string.encode('utf-8')))
            root = doc.getroot()

            # Check for required value-date attributes in all transaction and budget values
            for value_el in doc.xpath('//value'):
                if value_el.get('value-date') is None:
                    parent = value_el.getparent().tag
                    errors.append(f"Missing required value-date attribute in {parent}/value element")

            # Check for required sector or transaction/sector elements
            activities = root.findall('./iati-activity', root.nsmap)
            for activity in activities:
                has_sector = len(activity.findall('./sector', root.nsmap)) > 0
                trans_sectors = 0
                transactions = activity.findall('./transaction', root.nsmap)

                for transaction in transactions:
                    if transaction.findall('./sector', root.nsmap):
                        trans_sectors += 1

                if not has_sector and (trans_sectors == 0 or trans_sectors != len(transactions)):
                    errors.append(
                        "Each activity must have either a sector element or all transactions must have sector elements"
                    )

            # Check for recipient country or region
            for activity in activities:
                has_recipient_country = len(activity.findall('./recipient-country', root.nsmap)) > 0
                has_recipient_region = len(activity.findall('./recipient-region', root.nsmap)) > 0

                trans_with_country = 0
                trans_with_region = 0
                transactions = activity.findall('./transaction', root.nsmap)

                for transaction in transactions:
                    if transaction.findall('./recipient-country', root.nsmap):
                        trans_with_country += 1
                    if transaction.findall('./recipient-region', root.nsmap):
                        trans_with_region += 1

                has_transaction_recipients = (
                    trans_with_country > 0 or trans_with_region > 0
                ) and (
                    trans_with_country + trans_with_region == len(transactions)
                )

                if not (has_recipient_country or has_recipient_region or has_transaction_recipients):
                    errors.append(
                        "Activity must specify either recipient-country or recipient-region at activity or transaction level"
                    )

            # Check that activity identifier starts with reporting org identifier
            for activity in activities:
                iati_id = activity.findtext('./iati-identifier')
                reporting_org = activity.find('./reporting-org')

                if reporting_org is not None and iati_id:
                    org_ref = reporting_org.get('ref')
                    if org_ref and not iati_id.startswith(org_ref):
                        errors.append(
                            f"Activity identifier '{iati_id}' should start with reporting org identifier '{org_ref}'"
                        )

            return len(errors) == 0, errors

        except Exception as e:
            return False, [f"Ruleset check error: {str(e)}"]

    def validate(self, xml_string: str) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Complete validation of an IATI XML string against both schema and ruleset.

        Args:
            xml_string: XML string to validate

        Returns:
            Tuple containing:
                - Boolean indicating if the XML is valid and complies with the ruleset
                - Dictionary with 'schema_errors' and 'ruleset_errors' lists
        """
        schema_valid, schema_errors = self.validate_xml(xml_string)
        ruleset_valid, ruleset_errors = self.check_ruleset(xml_string)

        all_valid = schema_valid and ruleset_valid
        return all_valid, {
            'schema_errors': schema_errors,
            'ruleset_errors': ruleset_errors
        }
