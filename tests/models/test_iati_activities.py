import unittest
from okfn_iati import (
    IatiActivities, Activity, OrganizationRef, Narrative,
    ActivityStatus
)


class TestIatiActivities(unittest.TestCase):
    def test_valid_iati_activities(self):
        """Test creating a valid IatiActivities container."""
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

        # Create the container
        iati_activities = IatiActivities(
            version="2.03",
            activities=[activity]
        )

        self.assertEqual(iati_activities.version, "2.03")
        self.assertEqual(len(iati_activities.activities), 1)
        self.assertEqual(iati_activities.activities[0].iati_identifier, "XM-EXAMPLE-12345")

    def test_default_values(self):
        """Test default values for IatiActivities."""
        iati_activities = IatiActivities()
        self.assertEqual(iati_activities.version, "2.03")  # Default version
        self.assertTrue(iati_activities.generated_datetime)  # Should have a datetime
        self.assertEqual(len(iati_activities.activities), 0)  # Empty activities list

    def test_invalid_version(self):
        """Test validation of invalid IATI version."""
        with self.assertRaises(ValueError) as context:
            IatiActivities(version="9.99")  # Invalid version
        self.assertIn("Invalid IATI version", str(context.exception))


if __name__ == '__main__':
    unittest.main()
