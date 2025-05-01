import unittest
from okfn_iati import Result, Narrative
from okfn_iati.enums import ResultType


class TestResult(unittest.TestCase):
    def test_valid_result_literal(self):
        """Test creating a valid Result with literal values."""
        result = Result(
            type="1",  # Output
            aggregation_status=True,
            title=[Narrative(text="Project Output")],
            description=[Narrative(text="Description of the output")]
        )
        self.assertEqual(result.type, ResultType.OUTPUT)  # Should convert to enum
        self.assertTrue(result.aggregation_status)
        self.assertEqual(len(result.title), 1)
        self.assertEqual(len(result.description), 1)

    def test_valid_result_enum(self):
        """Test creating a valid Result with enum values."""
        result = Result(
            type=ResultType.OUTCOME,
            aggregation_status=False,
            title=[Narrative(text="Project Outcome")]
        )
        self.assertEqual(result.type, ResultType.OUTCOME)
        self.assertFalse(result.aggregation_status)

    def test_enum_conversion(self):
        """Test that string values are converted to enums when possible."""
        result = Result(
            type="2",  # Outcome
            title=[Narrative(text="Project Outcome")]
        )
        self.assertEqual(result.type, ResultType.OUTCOME)

    def test_optional_fields(self):
        """Test with optional fields."""
        result = Result(
            type="1",  # Output
        )
        self.assertEqual(result.type, ResultType.OUTPUT)
        self.assertIsNone(result.aggregation_status)
        self.assertIsNone(result.title)
        self.assertIsNone(result.description)


if __name__ == '__main__':
    unittest.main()
