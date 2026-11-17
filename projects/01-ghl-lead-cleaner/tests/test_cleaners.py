"""
Tests for cleaners.py
Run from the project folder with:  python -m unittest discover tests
All numbers and emails here are fake.
"""

import sys
import unittest
from pathlib import Path

# Let the tests find cleaners.py in the folder above
sys.path.insert(0, str(Path(__file__).parent.parent))

from cleaners import AMBIGUOUS, clean_email, clean_name, clean_phone, clean_source, clean_tags, split_full_name


class TestPhilippinesPhones(unittest.TestCase):
    def test_local_09(self):
        self.assertEqual(clean_phone("09170001234"), "+639170001234")

    def test_local_with_spaces_and_brackets(self):
        self.assertEqual(clean_phone("(0917) 000-1234"), "+639170001234")

    def test_country_code_no_plus(self):
        self.assertEqual(clean_phone("63-917-000-1234"), "+639170001234")

    def test_country_code_with_plus(self):
        self.assertEqual(clean_phone("+63 917 000 1234"), "+639170001234")

    def test_missing_zero_uses_default_country(self):
        self.assertEqual(clean_phone("9170001234", "PH"), "+639170001234")


class TestUSPhones(unittest.TestCase):
    def test_ten_digits(self):
        self.assertEqual(clean_phone("(212) 555-0123"), "+12125550123")

    def test_one_plus_ten_digits(self):
        self.assertEqual(clean_phone("1.212.555.0123"), "+12125550123")

    def test_with_plus(self):
        self.assertEqual(clean_phone("+1 212 555 0123"), "+12125550123")

    def test_starts_with_9_uses_default_country(self):
        self.assertEqual(clean_phone("9175550123", "US"), "+19175550123")


class TestAustraliaPhones(unittest.TestCase):
    def test_mobile_04(self):
        self.assertEqual(clean_phone("0491 570 123"), "+61491570123")

    def test_mobile_in_brackets(self):
        self.assertEqual(clean_phone("(04) 9157 0123"), "+61491570123")

    def test_landline_02(self):
        self.assertEqual(clean_phone("02 5550 1234"), "+61255501234")

    def test_country_code_no_plus(self):
        self.assertEqual(clean_phone("61491570123"), "+61491570123")

    def test_with_plus(self):
        self.assertEqual(clean_phone("+61 491 570 123"), "+61491570123")

    def test_missing_zero_uses_default_country(self):
        self.assertEqual(clean_phone("491570123", "AU"), "+61491570123")


class TestTrickyPhones(unittest.TestCase):
    def test_ambiguous_without_default(self):
        self.assertEqual(clean_phone("9170001234"), AMBIGUOUS)

    def test_junk(self):
        self.assertIsNone(clean_phone("call me"))
        self.assertIsNone(clean_phone("12345"))
        self.assertIsNone(clean_phone(""))


class TestEmails(unittest.TestCase):
    def test_trim_and_lowercase(self):
        self.assertEqual(clean_email("  Anna.Test@EXAMPLE.com "), "anna.test@example.com")

    def test_typos_are_rejected(self):
        for bad in ["a@@example.com", "a@example,com", "aexample.com", "a@example", "a@example..com", "a@example.cmo"]:
            self.assertIsNone(clean_email(bad), bad)


class TestNamesSourcesTags(unittest.TestCase):
    def test_name_caps_spaces_title(self):
        self.assertEqual(clean_name("  dR.  aNNA   testington "), "Anna Testington")

    def test_split_full_name(self):
        self.assertEqual(split_full_name("anna mae testington"), ("Anna", "Mae Testington"))
        self.assertEqual(split_full_name("Anna"), ("Anna", None))

    def test_source_aliases(self):
        self.assertEqual(clean_source("FB ads"), "Facebook Ads")
        self.assertEqual(clean_source("", "Website Form"), "Website Form")

    def test_tags(self):
        self.assertEqual(clean_tags("Dental, NEW lead,dental", ["promo"]), "dental, new lead, promo")


if __name__ == "__main__":
    unittest.main()
