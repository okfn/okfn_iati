import unittest
from okfn_iati import (
    Activity, Narrative, OrganizationRef, ActivityStatus,
    ActivityDateType, ActivityDate, IatiActivities,
    OrganisationType, OrganisationRole, BudgetType, BudgetStatus,
    ParticipatingOrg, TransactionType, Transaction, Budget,
    IatiXmlGenerator
)
from okfn_iati.iati_schema_validator import IatiValidator


class TestValidator(unittest.TestCase):
    def setUp(self):
        # Set up a valid activity
        self.valid_activity = Activity(
            iati_identifier="XM-DAC-12345-PROJECT001",
            reporting_org=OrganizationRef(
                ref="XM-DAC-12345",
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
                    iso_date="2023-01-01"
                ),
                ActivityDate(
                    type=ActivityDateType.ACTUAL_START,
                    iso_date="2023-01-15"
                )
            ],
            participating_orgs=[
                ParticipatingOrg(
                    role=OrganisationRole.FUNDING,
                    ref="XM-DAC-12345",
                    type=OrganisationType.GOVERNMENT.value,
                    narratives=[Narrative(text="Example Funding Organization")]
                )
            ],
            recipient_countries=[
                {
                    "code": "KE",
                    "percentage": 100
                }
            ],
            sectors=[
                {
                    "code": "11120",
                    "vocabulary": "1",
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
                    value_date="2023-01-01"  # Required
                )
            ],
            transactions=[
                Transaction(
                    type=TransactionType.DISBURSEMENT,
                    date="2023-03-15",
                    value=50000.00,
                    currency="USD",
                    value_date="2023-03-15"  # Required
                )
            ]
        )

        # Generate XML from valid activity
        self.activities_container = IatiActivities(activities=[self.valid_activity])
        self.generator = IatiXmlGenerator()
        self.validator = IatiValidator()
        self.valid_xml = self.generator.generate_iati_activities_xml(self.activities_container)

    def test_valid_xml(self):
        """Test that a valid XML passes both schema and ruleset validation."""
        # Create a validator that uses local schemas
        validator = IatiValidator()

        # Validate the XML
        is_valid, errors = validator.validate(self.valid_xml)

        # Check if validation succeeded
        self.assertTrue(is_valid, f"XML should be valid. Errors: {errors}")
        self.assertEqual(len(errors['schema_errors']), 0)
        self.assertEqual(len(errors['ruleset_errors']), 0)

    def test_missing_value_date(self):
        """Test detection of missing value-date attribute."""
        invalid_activity = self.valid_activity
        invalid_activity.budgets[0].value_date = None  # Remove required attribute

        invalid_xml = self.generator.generate_iati_activities_xml(IatiActivities(activities=[invalid_activity]))

        is_valid, errors = self.validator.validate(invalid_xml)
        """
        AssertionError: False is not true :
        Errors: {
          'schema_errors': [
            "<string>:26:0:ERROR:SCHEMASV:SCHEMAV_CVC_COMPLEX_TYPE_4:
            Element 'value': The attribute 'value-date' is required but missing."
          ],
          'ruleset_errors': ['Missing required value-date attribute in budget/value element']
        }
        """
        self.assertFalse(is_valid)
        self.assertEqual(len(errors['schema_errors']), 1)
        self.assertEqual(len(errors['ruleset_errors']), 1)
        expected = "The attribute 'value-date' is required but missing"
        error1 = errors['schema_errors'][0]
        self.assertTrue(expected in error1, f'Expected error not found. Errors: {errors}')
        expected = "Missing required value-date"
        error2 = errors['ruleset_errors'][0]
        self.assertTrue(expected in error2, f'Expected error not found. Errors: {errors}')

    def test_missing_sector(self):
        """Test detection of missing sector."""
        invalid_activity = self.valid_activity
        invalid_activity.sectors = []  # Remove required sectors

        invalid_xml = self.generator.generate_iati_activities_xml(IatiActivities(activities=[invalid_activity]))

        is_valid, errors = self.validator.validate(invalid_xml)
        """
        AssertionError: False is not true :
        Errors: {
          'schema_errors': [],
          'ruleset_errors': ['Each activity must have either a sector element or all transactions must have sector elements']
        }
        """
        self.assertFalse(is_valid, f'Errors: {errors}')
        self.assertEqual(len(errors['schema_errors']), 0)
        self.assertEqual(len(errors['ruleset_errors']), 1)
        expected_error = "Each activity must have either a sector element or all transactions must have sector elements"
        error1 = errors['ruleset_errors'][0]
        self.assertTrue(expected_error in error1, f'Expected error not found. Errors: {errors}')


if __name__ == '__main__':
    unittest.main()
