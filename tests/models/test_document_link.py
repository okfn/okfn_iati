import unittest
from okfn_iati import DocumentLink, Narrative
from okfn_iati.enums import DocumentCategory


class TestDocumentLink(unittest.TestCase):
    def test_valid_document_link_literal(self):
        """Test creating a valid DocumentLink with literal values."""
        doc = DocumentLink(
            url="https://example.org/document.pdf",
            format="application/pdf",
            title=[Narrative(text="Example Document")],
            categories=["A01", "A02"],  # Pre/post conditions and Objectives
            languages=["en", "es"]
        )
        self.assertEqual(doc.url, "https://example.org/document.pdf")
        self.assertEqual(doc.format, "application/pdf")
        self.assertEqual(len(doc.title), 1)
        self.assertEqual(len(doc.categories), 2)

    def test_valid_document_link_enum(self):
        """Test creating a valid DocumentLink with enum values."""
        doc = DocumentLink(
            url="https://example.org/document.pdf",
            format="application/pdf",
            categories=[DocumentCategory.OBJECTIVES, DocumentCategory.RESULTS]
        )
        self.assertEqual(doc.url, "https://example.org/document.pdf")
        self.assertEqual(len(doc.categories), 2)
        self.assertEqual(doc.categories[0], DocumentCategory.OBJECTIVES)

    def test_category_conversion(self):
        """Test that string category codes are converted to enums when possible."""
        doc = DocumentLink(
            url="https://example.org/document.pdf",
            format="application/pdf",
            categories=["A02"]  # Objectives
        )
        # Check that string was converted to enum
        self.assertEqual(doc.categories[0], DocumentCategory.OBJECTIVES)

    def test_invalid_date_format(self):
        """Test validation of invalid document date format."""
        with self.assertRaises(ValueError) as context:
            DocumentLink(
                url="https://example.org/document.pdf",
                format="application/pdf",
                document_date="01/01/2023"  # Invalid format
            )
        self.assertIn("Invalid document date format", str(context.exception))


if __name__ == '__main__':
    unittest.main()
