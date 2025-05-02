import unittest
import os
import csv
from pathlib import Path
from datetime import datetime

from okfn_iati import (
    Activity, Narrative, OrganizationRef, ParticipatingOrg, ActivityDate, Budget, Transaction,
    IatiActivities, IatiXmlGenerator, IatiValidator,  # Changed PDF to IatiValidator
    ActivityStatus, ActivityDateType, TransactionType, BudgetType, BudgetStatus,
    OrganisationRole, OrganisationType
)


class TestCsvToXmlGeneration(unittest.TestCase):
    """Test the generation of XML files from the sample CSV data and validate them."""

    def setUp(self):
        self.csv_file = os.path.join(
            Path(__file__).parent.parent,
            'data-samples', 'sample_activities.csv'
        )
        self.output_xml = os.path.join(
            os.path.dirname(__file__), 'test_activities_generated.xml'
        )

        # Ensure the sample file exists
        self.assertTrue(os.path.exists(self.csv_file), f"CSV sample file not found: {self.csv_file}")

    # def tearDown(self):
    #     # Clean up test files after test
    #     if os.path.exists(self.output_xml):
    #         os.remove(self.output_xml)

    def test_csv_to_xml_generation_and_validation(self):
        """Test converting CSV data to valid IATI XML via IATI objects."""
        # Read CSV and create activities
        activities = self._read_csv_and_create_activities()

        # Create IATI activities container
        iati_activities = IatiActivities(
            version="2.03",
            generated_datetime=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            activities=activities
        )

        # Generate XML
        xml_generator = IatiXmlGenerator()
        xml_string = xml_generator.generate_iati_activities_xml(iati_activities)
        xml_generator.save_to_file(iati_activities, self.output_xml)

        # Verify XML was created properly
        self.assertTrue(os.path.exists(self.output_xml), "Generated XML file not found")

        # Validate XML with internal validator
        validator = IatiValidator()
        is_valid, errors = validator.validate(xml_string)

        # Report on validation results
        if not is_valid:
            print("\nValidation errors found:")
            if 'schema_errors' in errors:
                for error in errors['schema_errors']:
                    print(f"  Schema error: {error}")
            if 'ruleset_errors' in errors:
                for error in errors['ruleset_errors']:
                    print(f"  Ruleset error: {error}")

        # Assert validation success
        self.assertTrue(is_valid, "Generated XML failed validation")

    def _read_csv_and_create_activities(self):
        """Read CSV file and convert each row to an Activity object."""
        activities = []

        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows_number = 0
            rows_failed = 0
            for row in reader:
                rows_number += 1
                # Create an activity from this CSV row
                try:
                    activity = self._create_activity_from_row(row)
                except Exception as e:
                    import traceback
                    trace_err = traceback.format_exc()
                    print(f"Error processing row {rows_number}: {e}\n{trace_err}")
                    rows_failed += 1
                    continue
                activities.append(activity)

        if rows_failed > 0:
            raise Exception(f"Failed to process {rows_failed} of {rows_number} rows in the CSV file.")
        return activities

    def _create_activity_from_row(self, row):
        """Convert a CSV row into an Activity object."""
        # Extract organization ID from activity identifier
        org_id_parts = row['activity_identifier'].split('-')
        if len(org_id_parts) >= 3:
            org_id = f"{org_id_parts[0]}-{org_id_parts[1]}"
        else:
            org_id = org_id_parts[0]

        # Create basic activity with required fields
        activity = Activity(
            iati_identifier=row['activity_identifier'],
            reporting_org=OrganizationRef(
                ref=org_id,
                type=row['reporting_org_type'],
                narratives=[Narrative(text=row['reporting_org'])]
            ),
            title=[Narrative(text=row['title'])],
            description=[{
                "type": "1",  # General description
                "narratives": [Narrative(text=row['description'])]
            }],
            activity_status=ActivityStatus(int(row['activity_status'])),
            default_currency=row.get('default_currency', 'USD')
        )

        # Add dates
        if row.get('planned_start_date'):
            activity.activity_dates.append(ActivityDate(
                type=ActivityDateType.PLANNED_START,
                iso_date=row['planned_start_date']
            ))

        if row.get('actual_start_date'):
            activity.activity_dates.append(ActivityDate(
                type=ActivityDateType.ACTUAL_START,
                iso_date=row['actual_start_date']
            ))

        if row.get('planned_end_date'):
            activity.activity_dates.append(ActivityDate(
                type=ActivityDateType.PLANNED_END,
                iso_date=row['planned_end_date']
            ))

        if row.get('actual_end_date'):
            activity.activity_dates.append(ActivityDate(
                type=ActivityDateType.ACTUAL_END,
                iso_date=row['actual_end_date']
            ))

        # Add participating organizations
        if row.get('participating_org_funding'):
            activity.participating_orgs.append(ParticipatingOrg(
                role=OrganisationRole.FUNDING,
                type=OrganisationType.MULTILATERAL,
                narratives=[Narrative(text=row['participating_org_funding'])]
            ))

        if row.get('participating_org_implementing'):
            activity.participating_orgs.append(ParticipatingOrg(
                role=OrganisationRole.IMPLEMENTING,
                type=OrganisationType.GOVERNMENT,
                narratives=[Narrative(text=row['participating_org_implementing'])]
            ))

        # Add recipient country or region
        if row.get('recipient_country') and row['recipient_country'].strip():
            activity.recipient_countries.append({
                "code": row['recipient_country'],
                "percentage": 100
            })
        elif row.get('recipient_region') and row['recipient_region'].strip():
            activity.recipient_regions.append({
                "code": row['recipient_region'],
                "percentage": 100
            })

        # Add sector
        if row.get('sector_code'):
            sector_data = {
                "code": row['sector_code'],
                "vocabulary": "1",  # DAC
            }
            # Only include percentage if multiple sectors or not 100%
            if row.get('sector_percentage') and int(row.get('sector_percentage')) != 100:
                sector_data["percentage"] = int(row.get('sector_percentage'))
            activity.sectors.append(sector_data)

        # Add budget
        if row.get('budget_value'):
            activity.budgets.append(Budget(
                type=BudgetType.ORIGINAL,
                status=BudgetStatus.COMMITTED,
                period_start=row['budget_start'],
                period_end=row['budget_end'],
                value=float(row['budget_value']),
                currency=row.get('default_currency', 'USD'),
                value_date=row['budget_start']
            ))

        # Add transaction
        if row.get('transaction_value'):
            description = [
                Narrative(text=row.get('transaction_description', ''))
            ] if row.get('transaction_description') else None
            activity.transactions.append(Transaction(
                type=TransactionType(row.get('transaction_type', "2")).value,  # Fixed to use .value
                date=row['transaction_date'],
                value=float(row['transaction_value']),
                currency=row.get('default_currency', 'USD'),
                value_date=row['transaction_date'],
                description=description,
            ))

        return activity


if __name__ == '__main__':
    unittest.main()
