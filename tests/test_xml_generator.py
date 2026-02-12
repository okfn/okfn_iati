import unittest
from okfn_iati import (
    Activity, Narrative, OrganizationRef, ActivityStatus,
    ActivityDate, ActivityDateType, IatiActivities, IatiXmlGenerator
)


class TestXmlGenerator(unittest.TestCase):
    def test_generate_xml(self):
        # Create a simple activity
        activity = Activity(
            iati_identifier="XM-EXAMPLE-12345",
            reporting_org=OrganizationRef(
                ref="XM-EXAMPLE",
                type="10",
                narratives=[Narrative(text="Example Organization")]
            ),
            reporting_org_role="1",
            title=[Narrative(text="Example Project")],
            activity_status=ActivityStatus.IMPLEMENTATION,
            activity_dates=[
                ActivityDate(type=ActivityDateType.PLANNED_START, iso_date="2024-01-01")
            ],
        )
        activity_no_org_role = Activity(
            # Do not use reporting_org_role to test defaulting
            iati_identifier="XM-EXAMPLE-2-12346",
            reporting_org=OrganizationRef(
                ref="XM-EXAMPLE-2",
                type="21",
                narratives=[Narrative(text="Example Organization 2")]
            ),
            title=[Narrative(text="Example Project")],
            activity_status=ActivityStatus.IMPLEMENTATION,
            activity_dates=[
                ActivityDate(type=ActivityDateType.PLANNED_START, iso_date="2024-01-01")
            ],
        )

        # Create container
        iati_activities = IatiActivities(
            activities=[activity, activity_no_org_role]
        )

        # Generate XML
        generator = IatiXmlGenerator()
        xml_string = generator.generate_iati_activities_xml(iati_activities)

        # Basic validation
        self.assertIn("<iati-activities", xml_string)
        self.assertIn("<iati-identifier>XM-EXAMPLE-12345</iati-identifier>", xml_string)
        self.assertIn("<narrative>Example Project</narrative>", xml_string)
        self.assertIn('<activity-status code="2"', xml_string)
        # participating-org ref="XM-DAC-46007" type="40" role="4">
        self.assertIn('<participating-org ref="XM-EXAMPLE" type="10" role="1">', xml_string)
        self.assertIn("<iati-identifier>XM-EXAMPLE-2-12346</iati-identifier>", xml_string)
        # Default role for second activity
        self.assertIn('<participating-org ref="XM-EXAMPLE-2" type="21" role="4">', xml_string)

    def test_generate_save_xml(self):
        # Create a simple activity
        activity = Activity(
            iati_identifier="XM-EXAMPLE-12345",
            reporting_org=OrganizationRef(
                ref="XM-EXAMPLE",
                type="10",
                narratives=[Narrative(text="Example Organization")]
            ),
            title=[Narrative(text="Example Project")],
            activity_status=ActivityStatus.IMPLEMENTATION,
            activity_dates=[
                ActivityDate(type=ActivityDateType.PLANNED_START, iso_date="2024-01-01")
            ],
        )

        # Create container
        iati_activities = IatiActivities(
            activities=[activity]
        )

        # Generate XML and save to file
        generator = IatiXmlGenerator()
        file_path = "test_output.xml"
        generator.save_to_file(iati_activities, file_path)

        # Check if the file was created
        with open(file_path, 'r') as f:
            xml_string = f.read()
            self.assertIn("<iati-activities", xml_string)
            self.assertIn("<iati-identifier>XM-EXAMPLE-12345</iati-identifier>", xml_string)
            self.assertIn("<narrative>Example Project</narrative>", xml_string)
            self.assertIn('<activity-status code="2"', xml_string)
        # Clean up
        import os
        if os.path.exists(file_path):
            os.remove(file_path)

    def test_activity_date_enum(self):
        # Create activity with enum-based date types
        activity = Activity(
            iati_identifier="XM-EXAMPLE-12345",
            reporting_org=OrganizationRef(
                ref="XM-EXAMPLE",
                type="10",
                narratives=[Narrative(text="Example Organization")]
            ),
            title=[Narrative(text="Example Project")],
            activity_dates=[
                ActivityDate(
                    type=ActivityDateType.PLANNED_START,
                    iso_date="2023-01-01",
                    narratives=[Narrative(text="Planned start date")]
                ),
                ActivityDate(
                    type=ActivityDateType.ACTUAL_START,
                    iso_date="2023-01-15",
                    narratives=[Narrative(text="Actual start date")]
                )
            ]
        )

        # Create container
        iati_activities = IatiActivities(
            activities=[activity]
        )

        # Generate XML
        generator = IatiXmlGenerator()
        xml_string = generator.generate_iati_activities_xml(iati_activities)

        # Validate date types in XML
        self.assertIn('activity-date type="1"', xml_string)
        self.assertIn('activity-date type="2"', xml_string)

    def test_activity_without_dates_is_skipped(self):
        """Activities with no activity_dates are skipped with a warning."""
        activity_with_dates = Activity(
            iati_identifier="XM-EXAMPLE-001",
            reporting_org=OrganizationRef(
                ref="XM-EXAMPLE",
                type="10",
                narratives=[Narrative(text="Example Org")]
            ),
            title=[Narrative(text="With dates")],
            activity_dates=[
                ActivityDate(
                    type=ActivityDateType.PLANNED_START,
                    iso_date="2024-01-01",
                )
            ],
        )
        activity_no_dates = Activity(
            iati_identifier="XM-EXAMPLE-002",
            reporting_org=OrganizationRef(
                ref="XM-EXAMPLE",
                type="10",
                narratives=[Narrative(text="Example Org")]
            ),
            title=[Narrative(text="No dates")],
            activity_dates=[],
        )

        iati_activities = IatiActivities(
            activities=[activity_with_dates, activity_no_dates]
        )

        generator = IatiXmlGenerator()
        xml_string = generator.generate_iati_activities_xml(iati_activities)

        # Activity with dates is included
        self.assertIn("XM-EXAMPLE-001", xml_string)
        # Activity without dates is excluded
        self.assertNotIn("XM-EXAMPLE-002", xml_string)
        # Warning is recorded
        self.assertEqual(len(generator.warnings), 1)
        self.assertIn("XM-EXAMPLE-002", generator.warnings[0])


if __name__ == '__main__':
    unittest.main()
