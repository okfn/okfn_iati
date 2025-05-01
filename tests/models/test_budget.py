import unittest
from okfn_iati import Budget
from okfn_iati.enums import BudgetType, BudgetStatus


class TestBudget(unittest.TestCase):
    def test_valid_budget_literal(self):
        """Test creating a valid Budget with literal values."""
        budget = Budget(
            type="1",  # Original
            status="1",  # Indicative
            period_start="2023-01-01",
            period_end="2023-12-31",
            value=100000.00
        )
        self.assertEqual(budget.type, BudgetType.ORIGINAL)  # Should convert to enum
        self.assertEqual(budget.status, BudgetStatus.INDICATIVE)  # Should convert to enum
        self.assertEqual(budget.value, 100000.00)

    def test_valid_budget_enum(self):
        """Test creating a valid Budget with enum values."""
        budget = Budget(
            type=BudgetType.REVISED,
            status=BudgetStatus.COMMITTED,
            period_start="2023-01-01",
            period_end="2023-12-31",
            value=150000.00,
            currency="USD"
        )
        self.assertEqual(budget.type, BudgetType.REVISED)
        self.assertEqual(budget.status, BudgetStatus.COMMITTED)
        self.assertEqual(budget.currency, "USD")

    def test_invalid_period_dates(self):
        """Test validation of invalid date formats."""
        # Invalid start date
        with self.assertRaises(ValueError) as context:
            Budget(
                type="1",
                status="1",
                period_start="01/01/2023",  # Invalid format
                period_end="2023-12-31",
                value=100000.00
            )
        self.assertIn("Invalid period_start format", str(context.exception))

        # Invalid end date
        with self.assertRaises(ValueError) as context:
            Budget(
                type="1",
                status="1",
                period_start="2023-01-01",
                period_end="31/12/2023",  # Invalid format
                value=100000.00
            )
        self.assertIn("Invalid period_end format", str(context.exception))

    def test_invalid_value_date(self):
        """Test validation of invalid value date format."""
        with self.assertRaises(ValueError) as context:
            Budget(
                type="1",
                status="1",
                period_start="2023-01-01",
                period_end="2023-12-31",
                value=100000.00,
                value_date="01/01/2023"  # Invalid format
            )
        self.assertIn("Invalid value_date format", str(context.exception))


if __name__ == '__main__':
    unittest.main()
