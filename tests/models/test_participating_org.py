import unittest
from okfn_iati import ParticipatingOrg, Narrative
from okfn_iati.enums import OrganisationRole, OrganisationType


class TestParticipatingOrg(unittest.TestCase):
    def test_valid_participating_org_literal(self):
        """Test creating a valid ParticipatingOrg with literal values."""
        org = ParticipatingOrg(
            role="1",  # Funding role
            ref="XM-EXAMPLE",
            type="10",  # Government type
            narratives=[Narrative(text="Example Organization")]
        )
        self.assertEqual(org.role, "1")
        self.assertEqual(org.ref, "XM-EXAMPLE")
        self.assertEqual(org.type, "10")
        self.assertEqual(len(org.narratives), 1)

    def test_invalid_role(self):
        """Test validation of invalid role."""
        with self.assertRaises(ValueError) as context:
            ParticipatingOrg(
                role="999",  # Invalid role
                ref="XM-EXAMPLE"
            )
        self.assertIn("Invalid organization role", str(context.exception))

    def test_invalid_type(self):
        """Test validation of invalid type."""
        with self.assertRaises(ValueError) as context:
            ParticipatingOrg(
                role="1",
                ref="XM-EXAMPLE",
                type="999"  # Invalid type
            )
        self.assertIn("Invalid organization type", str(context.exception))


if __name__ == '__main__':
    unittest.main()
