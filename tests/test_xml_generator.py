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
            title=[Narrative(text="Example Project")],
            activity_status=ActivityStatus.IMPLEMENTATION
        )

        # Create container
        iati_activities = IatiActivities(
            activities=[activity]
        )

        # Generate XML
        generator = IatiXmlGenerator()
        xml_string = generator.generate_iati_activities_xml(iati_activities)

        # Basic validation
        self.assertIn("<iati-activities", xml_string)
        self.assertIn("<iati-identifier>XM-EXAMPLE-12345</iati-identifier>", xml_string)
        self.assertIn("<narrative>Example Project</narrative>", xml_string)
        self.assertIn('<activity-status code="2"', xml_string)

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
            activity_status=ActivityStatus.IMPLEMENTATION
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


if __name__ == '__main__':
    unittest.main()
