import unittest
from okfn_iati.validators import crs_channel_code_validator
from okfn_iati import ParticipatingOrg, OrganisationRole, Narrative


class TestCRSChannelCodeValidator(unittest.TestCase):
    def test_valid_codes(self):
        """Test validation of valid CRS channel codes."""
        # Test a few valid codes
        self.assertTrue(crs_channel_code_validator.is_valid_code("10000"))  # Public Sector Institutions
        self.assertTrue(crs_channel_code_validator.is_valid_code("11000"))  # Donor Government
        self.assertTrue(crs_channel_code_validator.is_valid_code("47000"))  # Other multilateral institution

    def test_invalid_codes(self):
        """Test validation of invalid CRS channel codes."""
        self.assertFalse(crs_channel_code_validator.is_valid_code("99999"))  # Non-existent code
        self.assertFalse(crs_channel_code_validator.is_valid_code("ABCDE"))  # Invalid format

    def test_get_name_and_category(self):
        """Test retrieving name and category for a code."""
        # Check a valid code
        self.assertEqual(crs_channel_code_validator.get_name("10000"), "Public Sector Institutions")
        self.assertEqual(crs_channel_code_validator.get_category("11000"), "10000")

        # Check an invalid code
        self.assertIsNone(crs_channel_code_validator.get_name("99999"))
        self.assertIsNone(crs_channel_code_validator.get_category("99999"))

    def test_contains_operator(self):
        """Test the __contains__ method."""
        self.assertIn("10000", crs_channel_code_validator)
        self.assertNotIn("99999", crs_channel_code_validator)


class TestParticipatingOrgValidation(unittest.TestCase):
    def test_valid_crs_channel_code(self):
        """Test creating a ParticipatingOrg with a valid CRS channel code."""
        org = ParticipatingOrg(
            role=OrganisationRole.FUNDING,
            ref="XM-EXAMPLE",
            crs_channel_code="10000",  # Valid code
            narratives=[Narrative(text="Example Organization")]
        )
        self.assertEqual(org.crs_channel_code, "10000")

    def test_invalid_crs_channel_code(self):
        """Test creating a ParticipatingOrg with an invalid CRS channel code."""
        with self.assertRaises(ValueError) as context:
            ParticipatingOrg(
                role=OrganisationRole.FUNDING,
                ref="XM-EXAMPLE",
                crs_channel_code="99999",  # Invalid code
                narratives=[Narrative(text="Example Organization")]
            )
        self.assertIn("Invalid CRS channel code", str(context.exception))


if __name__ == '__main__':
    unittest.main()
