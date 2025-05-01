import unittest
from okfn_iati import ActivityDate, Narrative
from okfn_iati.enums import ActivityDateType


class TestActivityDate(unittest.TestCase):
    def test_valid_activity_date_literal(self):
        """Test creating a valid ActivityDate with literal values."""
        date = ActivityDate(
            type="1",  # Planned start
            iso_date="2023-01-01",
            narratives=[Narrative(text="Planned start date")]
        )
        self.assertEqual(date.type, ActivityDateType.PLANNED_START)  # Should convert to enum
        self.assertEqual(date.iso_date, "2023-01-01")
        self.assertEqual(len(date.narratives), 1)

    def test_valid_activity_date_enum(self):
        """Test creating a valid ActivityDate with enum values."""
        date = ActivityDate(
            type=ActivityDateType.ACTUAL_START,
            iso_date="2023-01-15",
            narratives=[Narrative(text="Actual start date")]
        )
        self.assertEqual(date.type, ActivityDateType.ACTUAL_START)
        self.assertEqual(date.iso_date, "2023-01-15")

    def test_invalid_date_type(self):
        """Test validation of invalid date type."""
        with self.assertRaises(ValueError) as context:
            ActivityDate(
                type="999",  # Invalid type
                iso_date="2023-01-01"
            )
        self.assertIn("Invalid date type", str(context.exception))

    def test_invalid_date_format(self):
        """Test validation of invalid date format."""
        with self.assertRaises(ValueError) as context:
            ActivityDate(
                type="1",
                iso_date="01/01/2023"  # Invalid format
            )
        self.assertIn("Invalid ISO date format", str(context.exception))


if __name__ == '__main__':
    unittest.main()
