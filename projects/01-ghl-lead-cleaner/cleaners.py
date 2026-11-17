"""
cleaners.py
Small helper functions that clean ONE value at a time.

Each function takes a messy value and returns:
  - the cleaned value, or
  - None if the value is empty or invalid.

Keeping them small makes them easy to read, test, and change.
"""

import re


# ---------------------------------------------------------------------------
# Header mapping
# ---------------------------------------------------------------------------

# Different CSV exports name the same column in different ways.
# Left side = a simplified header we might see. Right side = our standard name.
HEADER_ALIASES = {
    "full name": "Full Name",
    "name": "Full Name",
    "lead name": "Full Name",
    "contact name": "Full Name",
    "first name": "First Name",
    "firstname": "First Name",
    "first": "First Name",
    "last name": "Last Name",
    "lastname": "Last Name",
    "surname": "Last Name",
    "last": "Last Name",
    "email": "Email",
    "e mail": "Email",
    "email address": "Email",
    "phone": "Phone",
    "phone number": "Phone",
    "mobile": "Phone",
    "mobile number": "Phone",
    "cell": "Phone",
    "contact no": "Phone",
    "contact number": "Phone",
    "company": "Company Name",
    "company name": "Company Name",
    "business name": "Company Name",
    "tags": "Tags",
    "tag": "Tags",
    "source": "Source",
    "lead source": "Source",
}


def standard_header(header):
    """Turn a messy header like ' E-mail Address: ' into a standard name like 'Email'.
    Returns the original header (trimmed) if we don't recognise it."""
    # Lowercase, and swap any punctuation (like - . : _) for a space
    simple = re.sub(r"[^a-z0-9]+", " ", str(header).lower()).strip()
    return HEADER_ALIASES.get(simple, str(header).strip())


# ---------------------------------------------------------------------------
# Text and names
# ---------------------------------------------------------------------------

def clean_text(value):
    """Trim spaces and squash repeated spaces. Returns None if empty."""
    if value is None:
        return None
    text = " ".join(str(value).split())  # split() removes ALL extra whitespace
    if text == "":
        return None
    return text


# Titles we remove so emails say "Hi Anna", not "Hi Dr."
TITLES = ["dr", "dr.", "mr", "mr.", "mrs", "mrs.", "ms", "ms.", "miss"]


def clean_name(value):
    """Trim, remove titles like 'Dr.', and fix capitals: 'aNNA  testington' -> 'Anna Testington'."""
    text = clean_text(value)
    if text is None:
        return None

    words = text.split(" ")

    # Drop a title at the start, but only if there is a name after it
    if len(words) > 1 and words[0].lower() in TITLES:
        words = words[1:]

    # .capitalize() makes the first letter upper and the rest lower
    return " ".join(word.capitalize() for word in words)


def split_full_name(full_name):
    """Split 'Anna Mae Testington' into ('Anna', 'Mae Testington').
    We split on the FIRST space only. A single word becomes the first name."""
    name = clean_name(full_name)
    if name is None:
        return None, None
    if " " not in name:
        return name, None
    first, last = name.split(" ", 1)
    return first, last


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

# Basic shape: something @ something . letters
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$")

# Common typos in the ending of an email (e.g. '.con' instead of '.com')
BAD_ENDINGS = ["con", "cmo", "comm", "cm", "om", "c0m"]


def clean_email(value):
    """Trim and lowercase an email. Returns None if it looks invalid.
    We do NOT try to auto-fix typos. A wrong guess sends emails to a stranger."""
    text = clean_text(value)
    if text is None:
        return None

    email = text.lower().replace(" ", "")

    if not EMAIL_PATTERN.match(email):
        return None
    if ".." in email:
        return None

    ending = email.rsplit(".", 1)[1]  # the part after the last dot
    if ending in BAD_ENDINGS:
        return None

    return email


# ---------------------------------------------------------------------------
# Phone
# ---------------------------------------------------------------------------

AMBIGUOUS = "AMBIGUOUS"  # special result: we can't tell the country


def clean_phone(value, default_country=None):
    """Convert a PH, US or AU number to E.164 format (e.g. +639171234567).

    default_country is 'PH', 'US', 'AU' or None.
    It is only used when a number has no country code and could belong to more than one country.

    Returns:
      - the E.164 number, or
      - None if the number is empty or invalid, or
      - AMBIGUOUS if we can't tell the country and no default was given.
    """
    text = clean_text(value)
    if text is None:
        return None

    # Keep only the digits: '+63 (917) 000-1234' -> '639170001234'
    digits = re.sub(r"\D", "", text)
    if digits == "":
        return None

    # --- 1. Numbers that already include a country code -------------------

    # Philippines mobile: 63 + 9XXXXXXXXX (12 digits)
    if len(digits) == 12 and digits.startswith("639"):
        return "+" + digits

    # Australia: 61 + 9 digits (11 digits)
    if len(digits) == 11 and digits.startswith("61"):
        return "+" + digits

    # US: 1 + 10 digits (11 digits)
    if len(digits) == 11 and digits.startswith("1"):
        return "+" + digits

    # --- 2. Local numbers (no country code) --------------------------------

    # Philippines mobile: 09XXXXXXXXX (11 digits) -> drop the 0, add +63
    if len(digits) == 11 and digits.startswith("09"):
        return "+63" + digits[1:]

    # Australia: 04XXXXXXXX mobile, or 02/03/07/08 landline (10 digits) -> drop the 0, add +61
    if len(digits) == 10 and digits[:2] in ["02", "03", "04", "07", "08"]:
        return "+61" + digits[1:]

    # 10 digits starting with 9: could be a PH mobile without the 0, OR a US number.
    if len(digits) == 10 and digits.startswith("9"):
        if default_country == "PH":
            return "+63" + digits
        if default_country == "US":
            return "+1" + digits
        return AMBIGUOUS

    # 10 digits starting with 2-8: only a US number fits this shape
    if len(digits) == 10 and digits[0] in "2345678":
        return "+1" + digits

    # Australian mobile typed without the 0: 4XXXXXXXX (9 digits)
    if len(digits) == 9 and digits.startswith("4"):
        if default_country == "AU":
            return "+61" + digits
        return AMBIGUOUS

    # Nothing matched
    return None


# ---------------------------------------------------------------------------
# Source and tags
# ---------------------------------------------------------------------------

# Turn the many ways people write a source into one clean label.
SOURCE_ALIASES = {
    "facebook": "Facebook Ads",
    "facebook ad": "Facebook Ads",
    "facebook ads": "Facebook Ads",
    "fb": "Facebook Ads",
    "fb ad": "Facebook Ads",
    "fb ads": "Facebook Ads",
    "google": "Google Ads",
    "google ad": "Google Ads",
    "google ads": "Google Ads",
    "instagram": "Instagram",
    "ig": "Instagram",
    "website": "Website Form",
    "website form": "Website Form",
    "web form": "Website Form",
    "referral": "Referral",
    "walk in": "Walk-in",
    "walkin": "Walk-in",
}


def clean_source(value, fallback=None):
    """Standardise the lead source. Blank sources use the fallback (from --source)."""
    text = clean_text(value)
    if text is None:
        return fallback
    simple = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
    # If we know this source, use the clean label. Otherwise keep it, in Title Case.
    return SOURCE_ALIASES.get(simple, text.title())


def clean_tags(value, extra_tags=None):
    """Make tags lowercase, trimmed, comma-separated, with no duplicates.
    extra_tags is a list of tags to add to every lead (from --tags)."""
    tags = []
    text = clean_text(value) or ""
    all_tags = text.split(",") + (extra_tags or [])

    for tag in all_tags:
        tag = tag.strip().lower()
        if tag != "" and tag not in tags:  # skip blanks and repeats
            tags.append(tag)

    if not tags:
        return None
    return ", ".join(tags)
