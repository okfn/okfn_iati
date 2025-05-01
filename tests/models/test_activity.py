import unittest
from okfn_iati import (
    Activity, Narrative, OrganizationRef,
)
from okfn_iati.enums import (
    ActivityStatus, ActivityScope,
)


class TestActivity(unittest.TestCase):
    def test_valid_activity_literals(self):
        """Test creating a valid Activity with literal values."""
        activity = Activity(
            iati_identifier="XM-EXAMPLE-12345",
            reporting_org=OrganizationRef(
                ref="XM-EXAMPLE",
                type="10",  # Government
                narratives=[Narrative(text="Example Organization")]
            ),
            title=[Narrative(text="Example Project")],
            activity_status=ActivityStatus.IMPLEMENTATION,
            activity_scope="4"  # National
        )
        self.assertEqual(activity.iati_identifier, "XM-EXAMPLE-12345")
        self.assertEqual(activity.activity_status, ActivityStatus.IMPLEMENTATION)
        self.assertEqual(activity.activity_scope, ActivityScope.NATIONAL)  # Should convert to enum

    def test_valid_activity_enums(self):
        """Test creating a valid Activity with enum values."""
        activity = Activity(
            iati_identifier="XM-EXAMPLE-12345",
            reporting_org=OrganizationRef(
                ref="XM-EXAMPLE",
                type="10",
                narratives=[Narrative(text="Example Organization")]
            ),
            activity_status=ActivityStatus.IMPLEMENTATION,
            activity_scope=ActivityScope.NATIONAL
        )
        self.assertEqual(activity.activity_status, ActivityStatus.IMPLEMENTATION)
        self.assertEqual(activity.activity_scope, ActivityScope.NATIONAL)

    def test_valid_related_activities(self):
        """Test creating an Activity with related activities."""
        activity = Activity(
            iati_identifier="XM-EXAMPLE-12345",
            reporting_org=OrganizationRef(
                ref="XM-EXAMPLE",
                type="10",
                narratives=[]
            ),
            related_activities=[
                {"ref": "XM-EXAMPLE-12340", "type": "1"},  # Parent
                {"ref": "XM-EXAMPLE-12346", "type": "2"}   # Child
            ]
        )
        self.assertEqual(len(activity.related_activities), 2)

    def test_invalid_related_activity_type(self):
        """Test validation of invalid related activity type."""
        with self.assertRaises(ValueError) as context:
            Activity(
                iati_identifier="XM-EXAMPLE-12345",
                reporting_org=OrganizationRef(
                    ref="XM-EXAMPLE",
                    type="10",
                    narratives=[]
                ),
                related_activities=[
                    {"ref": "XM-EXAMPLE-12340", "type": "999"}  # Invalid type
                ]
            )
        self.assertIn("Invalid related activity type", str(context.exception))

    def test_invalid_datetime_format(self):
        """Test validation of invalid datetime format."""
        with self.assertRaises(ValueError) as context:
            Activity(
                iati_identifier="XM-EXAMPLE-12345",
                reporting_org=OrganizationRef(
                    ref="XM-EXAMPLE",
                    type="10",
                    narratives=[]
                ),
                last_updated_datetime="2023/01/15"  # Invalid format
            )
        self.assertIn("Invalid datetime format", str(context.exception))


if __name__ == '__main__':
    unittest.main()
