import unittest
from okfn_iati import ContactInfo, Narrative
from okfn_iati.enums import ContactType


class TestContactInfo(unittest.TestCase):
    def test_valid_contact_info_literal(self):
        """Test creating a valid ContactInfo with literal values."""
        contact = ContactInfo(
            type="1",  # General contact type
            organisation=[Narrative(text="Example Organization")],
            person_name=[Narrative(text="John Doe")],
            email="john@example.org"
        )
        self.assertEqual(contact.type, "1")
        self.assertEqual(len(contact.organisation), 1)
        self.assertEqual(contact.email, "john@example.org")

    def test_valid_contact_info_enum(self):
        """Test creating a valid ContactInfo with enum values."""
        contact = ContactInfo(
            type=ContactType.FINANCIAL,
            department=[Narrative(text="Finance Department")],
            telephone="+1234567890"
        )
        self.assertEqual(contact.type, ContactType.FINANCIAL)
        self.assertEqual(len(contact.department), 1)

    def test_invalid_contact_type(self):
        """Test validation of invalid contact type."""
        with self.assertRaises(ValueError) as context:
            ContactInfo(type="999")  # Invalid type
        self.assertIn("Invalid contact type", str(context.exception))

    def test_optional_fields(self):
        """Test with all fields optional except type."""
        contact = ContactInfo()
        self.assertIsNone(contact.type)
        self.assertIsNone(contact.organisation)
        self.assertIsNone(contact.telephone)


if __name__ == '__main__':
    unittest.main()
