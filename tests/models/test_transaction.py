import unittest
from okfn_iati import Transaction, Narrative
from okfn_iati.enums import TransactionType, FlowType, FinanceType, TiedStatus


class TestTransaction(unittest.TestCase):
    def test_valid_transaction_literal(self):
        """Test creating a valid Transaction with literal values."""
        transaction = Transaction(
            type="2",  # Commitment
            date="2023-01-15",
            value=50000.00,
            description=[Narrative(text="Project commitment")]
        )
        self.assertEqual(transaction.type, TransactionType.OUT_COMMITMENT)  # Should convert to enum
        self.assertEqual(transaction.date, "2023-01-15")
        self.assertEqual(transaction.value, 50000.00)

    def test_valid_transaction_enum(self):
        """Test creating a valid Transaction with enum values."""
        transaction = Transaction(
            type=TransactionType.DISBURSEMENT,
            date="2023-02-15",
            value=25000.00,
            flow_type=FlowType.ODA,
            finance_type=FinanceType.STANDARD_GRANT,
            tied_status=TiedStatus.UNTIED
        )
        self.assertEqual(transaction.type, TransactionType.DISBURSEMENT)
        self.assertEqual(transaction.flow_type, FlowType.ODA)
        self.assertEqual(transaction.finance_type, FinanceType.STANDARD_GRANT)
        self.assertEqual(transaction.tied_status, TiedStatus.UNTIED)

    def test_enum_conversion(self):
        """Test that string values are converted to enums when possible."""
        transaction = Transaction(
            type="3",  # Disbursement
            date="2023-03-15",
            value=15000.00,
            flow_type="10",  # ODA
            finance_type="110",  # Standard grant
            tied_status="5"  # Untied
        )
        self.assertEqual(transaction.type, TransactionType.DISBURSEMENT)
        self.assertEqual(transaction.flow_type, FlowType.ODA)
        self.assertEqual(transaction.finance_type, FinanceType.STANDARD_GRANT)
        self.assertEqual(transaction.tied_status, TiedStatus.UNTIED)

    def test_invalid_date_format(self):
        """Test validation of invalid date format."""
        with self.assertRaises(ValueError) as context:
            Transaction(
                type="2",
                date="15/01/2023",  # Invalid format
                value=50000.00
            )
        self.assertIn("Invalid transaction date format", str(context.exception))

    def test_invalid_value_date_format(self):
        """Test validation of invalid value date format."""
        with self.assertRaises(ValueError) as context:
            Transaction(
                type="2",
                date="2023-01-15",
                value=50000.00,
                value_date="15/01/2023"  # Invalid format
            )
        self.assertIn("Invalid value_date format", str(context.exception))


if __name__ == '__main__':
    unittest.main()
