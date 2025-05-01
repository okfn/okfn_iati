import unittest
from okfn_iati import (
    Activity, Narrative, OrganizationRef, ActivityStatus
)


class TestModels(unittest.TestCase):
    def test_create_activity(self):
        # Test creating a basic activity
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

        self.assertEqual(activity.iati_identifier, "XM-EXAMPLE-12345")
        self.assertEqual(activity.reporting_org.ref, "XM-EXAMPLE")
        self.assertEqual(activity.title[0].text, "Example Project")
        self.assertEqual(activity.activity_status, ActivityStatus.IMPLEMENTATION)


if __name__ == '__main__':
    unittest.main()
