import unittest
from okfn_iati import Narrative


class TestNarrative(unittest.TestCase):
    def test_valid_narrative(self):
        """Test creating a valid Narrative."""
        narrative = Narrative(text="Sample text")
        self.assertEqual(narrative.text, "Sample text")
        self.assertIsNone(narrative.lang)

        # With language specified
        narrative_with_lang = Narrative(text="Texto de ejemplo", lang="es")
        self.assertEqual(narrative_with_lang.text, "Texto de ejemplo")
        self.assertEqual(narrative_with_lang.lang, "es")

    def test_empty_text(self):
        """Test creating a Narrative with empty text."""
        # Empty string is valid
        narrative = Narrative(text="")
        self.assertEqual(narrative.text, "")


if __name__ == '__main__':
    unittest.main()
