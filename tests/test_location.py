import unittest
from okfn_iati import (
    Location, LocationIdentifier, LocationID, Narrative,
    IatiXmlGenerator, Activity, OrganizationRef, IatiActivities
)


class TestLocation(unittest.TestCase):
    def test_location_identifier(self):
        # Test with valid enum value
        loc_id = LocationIdentifier(vocabulary=LocationID.GEONAMES, code="1453782")
        self.assertEqual(loc_id.vocabulary, LocationID.GEONAMES)
        self.assertEqual(loc_id.code, "1453782")

        # Test with valid string value
        loc_id = LocationIdentifier(vocabulary="G1", code="1453782")
        self.assertEqual(loc_id.vocabulary, "G1")
        self.assertEqual(loc_id.code, "1453782")

        # Test with invalid value
        with self.assertRaises(ValueError):
            LocationIdentifier(vocabulary="INVALID", code="1453782")

    def test_location_xml_generation(self):
        # Create a location with a location ID
        location = Location(
            location_id=LocationIdentifier(vocabulary=LocationID.GEONAMES, code="1453782"),
            name=[Narrative(text="Test Location")]
        )

        # Create an activity with this location
        activity = Activity(
            iati_identifier="TEST-123",
            reporting_org=OrganizationRef(ref="TEST", type="10"),
            locations=[location]
        )

        # Generate XML
        iati_activities = IatiActivities(activities=[activity])
        generator = IatiXmlGenerator()
        xml_string = generator.generate_iati_activities_xml(iati_activities)

        # Check for the location ID in the XML
        self.assertIn('<location-id vocabulary="G1" code="1453782"', xml_string)


if __name__ == '__main__':
    unittest.main()
