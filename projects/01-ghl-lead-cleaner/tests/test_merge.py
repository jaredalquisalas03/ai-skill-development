"""
Tests for duplicate merging in clean_leads.py
Run from the project folder with:  python -m unittest discover tests
All data here is fake.
"""

import sys
import unittest
from pathlib import Path

# Let the tests find clean_leads.py in the folder above
sys.path.insert(0, str(Path(__file__).parent.parent))

from clean_leads import merge_rows


def make_row(**values):
    """Build a row with every GHL column blank, then fill in the given values."""
    row = {"First Name": None, "Last Name": None, "Email": None, "Phone": None,
           "Company Name": None, "Tags": None, "Source": None, "Notes": None}
    row.update(values)
    return row


class TestMergeRows(unittest.TestCase):
    def test_fills_blanks(self):
        kept = make_row(Email="anna@example.com")
        merge_rows(kept, make_row(Email="anna@example.com", Phone="+639170001234"))
        self.assertEqual(kept["Phone"], "+639170001234")

    def test_never_replaces_existing_values(self):
        kept = make_row(Source="Facebook Ads")
        merge_rows(kept, make_row(Source="Google Ads"))
        self.assertEqual(kept["Source"], "Facebook Ads")

    def test_combines_tags_and_notes(self):
        kept = make_row(Tags="dental", Notes="wants whitening")
        merge_rows(kept, make_row(Tags="vip, dental", Notes="emergency"))
        self.assertEqual(kept["Tags"], "dental, vip")
        self.assertEqual(kept["Notes"], "wants whitening | emergency")

    def test_same_note_not_repeated(self):
        kept = make_row(Notes="wants whitening")
        merge_rows(kept, make_row(Notes="wants whitening"))
        self.assertEqual(kept["Notes"], "wants whitening")


if __name__ == "__main__":
    unittest.main()
