import unittest
from okfn_iati.enums import SectorCategory
from okfn_iati.enums.sector_category import SectorCategoryData
from okfn_iati import (
    Activity, ActivityDate, ActivityDateType,
    Narrative, OrganizationRef, ActivityStatus,
    IatiActivities, IatiXmlGenerator, IatiValidator,
    OrganisationRole, OrganisationType, ParticipatingOrg
)


class TestSectorCategory(unittest.TestCase):
    def setUp(self):
        self.sector_data = SectorCategoryData()

    def test_sector_category_enum_creation(self):
        """Test that SectorCategory enum is created properly from CSV data."""
        # Test that the enum exists and has members
        self.assertTrue(hasattr(SectorCategory, '__members__'))
        self.assertGreater(len(SectorCategory.__members__), 0)

    def test_valid_sector_codes(self):
        """Test accessing valid sector category codes."""
        # Load the data to check what codes are available
        data = self.sector_data.load_data()

        # Test accessing the first few codes from the data
        available_codes = list(data.keys())[:3]  # Get first 3 codes

        for code in available_codes:
            # Test accessing via enum
            sector = getattr(SectorCategory, code, None)
            self.assertIsNotNone(sector, f"Sector code {code} should exist in enum")

            # Test accessing via data class
            sector_info = self.sector_data[code]
            self.assertIsNotNone(sector_info, f"Sector code {code} should exist in data")
            self.assertIn('name', sector_info)

    def test_invalid_sector_code(self):
        """Test handling of invalid sector category codes."""
        invalid_code = "INVALID_CODE_999"

        # Test that invalid code is not in enum
        sector = getattr(SectorCategory, invalid_code, None)
        self.assertIsNone(sector, f"Invalid sector code {invalid_code} should not exist in enum")

        # Test that accessing invalid code via data class raises KeyError
        with self.assertRaises(KeyError):
            self.sector_data[invalid_code]

    def test_activity_with_valid_sector_category(self):
        """Test creating an activity with a valid sector category code."""
        valid_code = "11120"

        activity = Activity(
            iati_identifier="XM-EXAMPLE-SECTOR-001",
            reporting_org=OrganizationRef(
                ref="XM-EXAMPLE",
                type=OrganisationType.GOVERNMENT.value,
                narratives=[Narrative(text="Example Organization")]
            ),
            title=[Narrative(text="Sector Category Test Project")],
            description=[{
                "type": "1",
                "narratives": [
                    Narrative(text="Testing sector category validation")
                ]
            }],
            participating_orgs=[
                ParticipatingOrg(
                    role=OrganisationRole.FUNDING,
                    ref="XM-DAC-12345",
                    type=OrganisationType.GOVERNMENT.value,
                    narratives=[Narrative(text="Example Funding Organization")]
                )
            ],
            activity_status=ActivityStatus.IMPLEMENTATION,
            sectors=[
                {
                    "code": valid_code,
                    "vocabulary": "1",
                    "percentage": 100
                }
            ],
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
            ],
            recipient_countries=[
                    {"code": "KE", "percentage": 100},
                ]
        )

        # Generate XML and validate
        iati_activities = IatiActivities(activities=[activity])
        generator = IatiXmlGenerator()
        xml_string = generator.generate_iati_activities_xml(iati_activities)

        # Validate the XML
        validator = IatiValidator()
        is_valid, errors = validator.validate(xml_string)

        self.assertTrue(is_valid, f"Activity with valid sector code should be valid. Errors: {errors}")

    def test_activity_with_invalid_sector_category(self):
        """Test creating an activity with an invalid sector category code."""
        invalid_sector_code = "99999"  # Assuming this is invalid

        # this will raise ValueError(f"Invalid sector code: {invalid_sector_code}")
        with self.assertRaises(ValueError) as context:
            Activity(
                iati_identifier="XM-EXAMPLE-SECTOR-002",
                reporting_org=OrganizationRef(
                    ref="XM-EXAMPLE",
                    type=OrganisationType.GOVERNMENT.value,
                    narratives=[Narrative(text="Example Organization")]
                ),
                title=[Narrative(text="Invalid Sector Category Test Project")],
                description=[{
                    "type": "1",
                    "narratives": [
                        Narrative(text="Testing invalid sector category")
                    ]
                }],
                activity_status=ActivityStatus.IMPLEMENTATION,
                sectors=[
                    {
                        "code": invalid_sector_code,
                        "vocabulary": "1",
                        "percentage": 100
                    }
                ],
                recipient_countries=[
                    {
                        "code": "KE",
                        "percentage": 100
                    }
                ]
            )
            # check the error
            self.assertIn("Invalid sector code", str(context.exception))

    def test_sector_category_data_structure(self):
        """Test the structure of sector category data."""
        data = self.sector_data.load_data()

        # Test that we have data
        self.assertGreater(len(data), 0, "Should have sector category data")

        # Test structure of first item
        first_code = list(data.keys())[0]
        first_item = data[first_code]

        self.assertIn('name', first_item, "Each sector should have a name")
        self.assertIsInstance(first_item['name'], str, "Sector name should be a string")

    def test_enum_comparison_with_sector_data(self):
        """Test that enum members match the data loaded from CSV."""
        data = self.sector_data.load_data()
        enum_members = {member.name for member in SectorCategory}
        data_codes = set(data.keys())

        # All enum members should have corresponding data entries
        for member_name in enum_members:
            self.assertIn(
                member_name, data_codes,
                f"Enum member {member_name} should exist in sector data"
            )


if __name__ == '__main__':
    unittest.main()
