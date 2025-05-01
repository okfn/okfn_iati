import unittest
from okfn_iati import OrganizationRef, Narrative
from okfn_iati.enums import OrganisationType


class TestOrganizationRef(unittest.TestCase):
    def test_valid_organization_ref(self):
        """Test creating a valid OrganizationRef."""
        # Using string value
        org_ref = OrganizationRef(
            ref="XM-EXAMPLE",
            type="10",  # Government type
            narratives=[Narrative(text="Example Organization")]
        )
        self.assertEqual(org_ref.ref, "XM-EXAMPLE")
        self.assertEqual(org_ref.type, "10")
        self.assertEqual(len(org_ref.narratives), 1)

    def test_invalid_type(self):
        """Test validation of invalid organization type."""
        with self.assertRaises(ValueError) as context:
            OrganizationRef(
                ref="XM-EXAMPLE",
                type="999",  # Invalid type
                narratives=[]
            )
        self.assertIn("Invalid organization type", str(context.exception))

    def test_empty_narratives(self):
        """Test with empty narratives list."""
        org_ref = OrganizationRef(
            ref="XM-EXAMPLE",
            type="10",
            narratives=[]
        )
        self.assertEqual(len(org_ref.narratives), 0)


if __name__ == '__main__':
    unittest.main()
