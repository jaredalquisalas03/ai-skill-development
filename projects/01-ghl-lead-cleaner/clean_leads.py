"""
clean_leads.py
Cleans a messy lead CSV and creates a GoHighLevel-ready import file.

How to run:
    python clean_leads.py input/leads.csv --default-country PH

Optional extras:
    --source "Facebook Ads"      Fill blank sources with this value
    --tags "dental, new lead"    Add these tags to every lead

Creates two files in the output/ folder:
    <name>_ghl_ready.csv   Clean rows, ready to import into GHL
    <name>_rejected.csv    Rows we could not use, with a reason
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

from cleaners import (
    AMBIGUOUS,
    clean_email,
    clean_name,
    clean_phone,
    clean_source,
    clean_tags,
    clean_text,
    split_full_name,
    standard_header,
)

# The exact GHL columns we output, in this order.
# "Notes" is not a standard GHL field. Map it to a custom field when you import.
GHL_COLUMNS = ["First Name", "Last Name", "Email", "Phone", "Company Name", "Tags", "Source", "Notes"]

# Output files go next to this script, in a folder called "output".
OUTPUT_FOLDER = Path(__file__).parent / "output"


def read_csv(path):
    """Read the CSV as plain text. Tries UTF-8 first, then the older Excel encoding."""
    # dtype=str keeps phone numbers as text, so leading zeros are not lost.
    # keep_default_na=False keeps empty cells as "" instead of NaN.
    try:
        return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="latin-1")


def get_column(df, name):
    """Return a column if it exists, or a column of blanks if it doesn't."""
    if name in df.columns:
        return df[name]
    return pd.Series([""] * len(df), index=df.index)


def clean_dataframe(df, default_country, fallback_source, extra_tags):
    """Clean every column and return a new table with the GHL columns,
    plus an 'Original Phone' helper column used for reject reasons."""
    clean = pd.DataFrame(index=df.index)

    # --- Names ---
    # If the file has First/Last Name columns, use them. Otherwise split Full Name.
    if "First Name" in df.columns or "Last Name" in df.columns:
        clean["First Name"] = get_column(df, "First Name").apply(clean_name)
        clean["Last Name"] = get_column(df, "Last Name").apply(clean_name)
    else:
        # split_full_name returns two values, so we unpack them into two lists
        names = get_column(df, "Full Name").apply(split_full_name)
        clean["First Name"] = [first for first, last in names]
        clean["Last Name"] = [last for first, last in names]

    # --- Contact details ---
    clean["Email"] = get_column(df, "Email").apply(clean_email)
    clean["Phone"] = get_column(df, "Phone").apply(lambda value: clean_phone(value, default_country))

    # --- Everything else ---
    clean["Company Name"] = get_column(df, "Company Name").apply(clean_text)
    clean["Tags"] = get_column(df, "Tags").apply(lambda value: clean_tags(value, extra_tags))
    clean["Source"] = get_column(df, "Source").apply(lambda value: clean_source(value, fallback_source))
    clean["Notes"] = get_column(df, "Notes").apply(clean_text)

    return clean


def find_reject_reason(original_row, clean_row):
    """Explain why a row can't be imported. Returns None if the row is fine.
    A row is fine if it has at least a valid email OR a valid phone."""
    has_email = clean_row["Email"] is not None
    has_phone = clean_row["Phone"] is not None and clean_row["Phone"] != AMBIGUOUS
    if has_email or has_phone:
        return None

    # Build a helpful reason from what went wrong
    reasons = []
    if clean_text(original_row.get("Email")) is not None:
        reasons.append("invalid email")
    if clean_row["Phone"] == AMBIGUOUS:
        reasons.append("ambiguous phone (use --default-country)")
    elif clean_text(original_row.get("Phone")) is not None:
        reasons.append("invalid phone")
    if not reasons:
        reasons.append("no email or phone")
    return "; ".join(reasons)


def row_to_dict(row):
    """Turn a table row into a plain dict.
    pandas stores empty cells as NaN ("not a number"). We swap NaN back to None,
    so the rest of the code only has to check for None."""
    result = {}
    for column, value in row.items():
        if pd.isna(value):
            result[column] = None
        else:
            result[column] = value
    return result


def split_good_and_rejected(df, clean):
    """Go through each row once. Decide if it is good, rejected, or a duplicate."""
    good_rows = []
    rejected_rows = []
    seen_emails = {}  # email -> row number where we first saw it
    seen_phones = {}  # phone -> row number where we first saw it
    duplicates = 0

    for index in df.index:
        original = df.loc[index].to_dict()
        row = row_to_dict(clean.loc[index])
        # Row number as the user sees it in Excel (header is row 1)
        excel_row = index + 2

        # A row with an ambiguous phone is still OK if the email is valid.
        # We just leave the phone blank.
        if row["Phone"] == AMBIGUOUS and row["Email"] is not None:
            row["Phone"] = None

        # 1. Is it missing contact details?
        reason = find_reject_reason(original, row)

        # 2. Is it a duplicate? Check email first, then phone.
        if reason is None and row["Email"] is not None and row["Email"] in seen_emails:
            reason = f"duplicate email (same as row {seen_emails[row['Email']]})"
        if reason is None and row["Phone"] is not None and row["Phone"] in seen_phones:
            reason = f"duplicate phone (same as row {seen_phones[row['Phone']]})"

        if reason is not None:
            if reason.startswith("duplicate"):
                duplicates += 1
            original["reject_reason"] = reason
            rejected_rows.append(original)
            continue

        # The row is good. Remember its email and phone for duplicate checks.
        if row["Email"] is not None:
            seen_emails[row["Email"]] = excel_row
        if row["Phone"] is not None:
            seen_phones[row["Phone"]] = excel_row
        good_rows.append(row)

    good = pd.DataFrame(good_rows, columns=GHL_COLUMNS)
    rejected = pd.DataFrame(rejected_rows, columns=list(df.columns) + ["reject_reason"])
    return good, rejected, duplicates


def main():
    # --- 1. Read the command-line options ---
    parser = argparse.ArgumentParser(description="Clean a lead CSV for GoHighLevel import.")
    parser.add_argument("input_file", help="Path to your messy CSV file")
    parser.add_argument(
        "--default-country",
        choices=["PH", "US", "AU"],
        help="Country to use when a phone number has no country code and could be more than one country",
    )
    parser.add_argument("--source", help="Source to use when a lead's source is blank")
    parser.add_argument("--tags", help='Tags to add to every lead, e.g. "dental, new lead"')
    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Could not find the file: {input_path}")
        sys.exit(1)

    # Turn "dental, new lead" into ["dental", "new lead"]
    extra_tags = args.tags.split(",") if args.tags else []

    # --- 2. Read the file and standardise the headers ---
    df = read_csv(input_path)
    df.columns = [standard_header(column) for column in df.columns]
    df = df.reset_index(drop=True)  # make sure rows are numbered 0, 1, 2...

    if "Email" not in df.columns and "Phone" not in df.columns:
        print("Could not find an email or phone column. Check your CSV headers.")
        sys.exit(1)

    # --- 3. Clean, then sort rows into good and rejected ---
    clean = clean_dataframe(df, args.default_country, args.source, extra_tags)
    good, rejected, duplicates = split_good_and_rejected(df, clean)

    # --- 4. Save the results ---
    OUTPUT_FOLDER.mkdir(exist_ok=True)
    good_path = OUTPUT_FOLDER / f"{input_path.stem}_ghl_ready.csv"
    rejected_path = OUTPUT_FOLDER / f"{input_path.stem}_rejected.csv"
    good.to_csv(good_path, index=False, encoding="utf-8")
    rejected.to_csv(rejected_path, index=False, encoding="utf-8")

    # --- 5. Print a short summary ---
    # Count rows that were kept but had a bad email or phone removed
    emails_removed = (good["Email"].isna() & good["Phone"].notna()).sum()
    print("Done!")
    print(f"  Rows in:            {len(df)}")
    print(f"  Rows clean:         {len(good)}")
    print(f"  Rows rejected:      {len(rejected)}")
    print(f"    - duplicates:     {duplicates}")
    print(f"    - other problems: {len(rejected) - duplicates}")
    print(f"  Clean rows with no email (phone only): {emails_removed}")
    print(f"  Saved: {good_path}")
    print(f"  Saved: {rejected_path}")


# Only run main() when this file is run directly (not when imported by tests)
if __name__ == "__main__":
    main()
