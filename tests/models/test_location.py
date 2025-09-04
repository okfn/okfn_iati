import unittest
from okfn_iati import Location, Narrative
from okfn_iati.enums import LocationReach, GeographicalPrecision, LocationType


class TestLocation(unittest.TestCase):
    def test_valid_location_literal(self):
        """Test creating a valid Location with literal values."""
        location = Location(
            location_reach="1",  # Activity reach
            name=[Narrative(text="Project Site")],
            point={"srsName": "http://www.opengis.net/def/crs/EPSG/0/4326", "pos": "-34.603722 -58.381592"}
        )
        self.assertEqual(location.location_reach, LocationReach.ACTIVITY)  # Should convert to enum
        self.assertEqual(location.name[0].text, "Project Site")

    def test_valid_location_enum(self):
        """Test creating a valid Location with enum values."""
        location = Location(
            location_reach=LocationReach.BENEFICIARY,
            exactness=GeographicalPrecision.EXACT_LOCATION,
            location_class=LocationType.POPULATED_PLACE
        )
        self.assertEqual(location.location_reach, LocationReach.BENEFICIARY)
        self.assertEqual(location.exactness, GeographicalPrecision.EXACT_LOCATION)
        self.assertEqual(location.location_class, LocationType.POPULATED_PLACE)

    def test_location_conversion(self):
        """Test that string values are converted to enums when possible."""
        location = Location(
            location_reach="1",
            exactness="1",
            location_class="PPL"
        )
        self.assertEqual(location.location_reach, LocationReach.ACTIVITY)
        self.assertEqual(location.exactness, GeographicalPrecision.EXACT_LOCATION)
        self.assertEqual(location.location_class, LocationType.POPULATED_PLACE)


if __name__ == '__main__':
    unittest.main()
