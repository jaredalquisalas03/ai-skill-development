# CLAUDE.md — GHL Lead Cleaner

## What this project is
A Python tool that takes a messy lead CSV and outputs a clean, GoHighLevel-ready import file.

**Users:** marketing VAs and agencies. Many are not developers.
They should be able to run it with one command and understand the code by reading it.

## Hard rules
- **Python 3 and pandas only.** Standard library is fine (`re`, `argparse`, `pathlib`, `csv`).
  No other third-party packages (no `phonenumbers`, no `numpy` imports, no CLI frameworks).
- **Beginner-friendly code.** Short functions. Clear names. A comment above every function and every non-obvious line.
  Prefer plain loops and `if` statements over clever one-liners.
- **Never use real client data.** All sample and test files use fake names, `example.com` emails,
  and made-up numbers. Never commit files from `input/` or `output/`.
- **Supported phone countries:** Philippines (+63), US (+1), Australia (+61). Nothing else.

## Folder layout
```
01-ghl-lead-cleaner/
  CLAUDE.md
  README.md            # How to install and run, for non-developers
  requirements.txt     # pandas only
  clean_leads.py       # Main script (entry point)
  cleaners.py          # Small cleaning functions (name, email, phone, tags)
  sample-data/
    messy_leads.csv    # Fake data only
  input/               # User drops real files here (git-ignored)
  output/              # Clean + rejected files land here (git-ignored)
  tests/
    test_cleaners.py   # Simple asserts, runnable with: python -m unittest
```

## How it runs
```bash
python clean_leads.py input/leads.csv --default-country PH
```
Outputs:
- `output/<name>_ghl_ready.csv` — rows ready for GHL import.
- `output/<name>_rejected.csv` — rows that failed, with a `reject_reason` column.
- A short summary printed to the terminal (rows in, rows clean, rows rejected, duplicates removed).

## Output format (GHL import)
Columns, in this order, with these exact headers:

| Column | Rule |
|---|---|
| First Name | Trimmed, Title Case |
| Last Name | Trimmed, Title Case |
| Email | Trimmed, lowercase, basic format check |
| Phone | E.164 format, e.g. `+639171234567` |
| Company Name | Trimmed |
| Tags | Comma-separated, lowercase, no duplicates |
| Source | Passed through or set from `--source` flag |
| Notes | Trimmed. Not a standard GHL field: map it to a custom field on import |

- If only a "Full Name" column exists, split on the first space.
- Map common header variations (e.g. `email address`, `E-mail`, `mobile`, `contact no.`) to the columns above.
- A row needs at least a valid email **or** a valid phone. Otherwise it goes to the rejected file.
- If one of the two is invalid but the other is valid, keep the row and leave the invalid field blank.
- Find duplicates by email, then by phone. Keep the first occurrence and merge the duplicate into it:
  fill its blank fields, and combine Tags and Notes. Never replace a value the kept row already has.
  The duplicate is listed in the rejected file as `duplicate email/phone (merged into row N)`.
- Output encoding: UTF-8.

## Phone rules
Strip everything except digits and a leading `+` first. Then:

| Country | Accepted input | Output |
|---|---|---|
| PH (+63) | `09XXXXXXXXX` (11 digits), `639XXXXXXXXX`, `+639XXXXXXXXX` | `+639XXXXXXXXX` |
| US (+1) | `XXXXXXXXXX` (10 digits), `1XXXXXXXXXX`, `+1XXXXXXXXXX` | `+1XXXXXXXXXX` |
| AU (+61) | `04XXXXXXXX` / `0[2378]XXXXXXXX` (10 digits), `61XXXXXXXXX`, `+61XXXXXXXXX` | `+61XXXXXXXXX` (drop the leading 0) |

- Numbers with a `+` or country code are read as-is.
- Numbers without a country code are **ambiguous** (e.g. a 10-digit number starting with 9 could be PH or US).
  Use the `--default-country` flag (PH, US or AU) to decide. Never guess silently.
- An invalid phone is left blank. If the row also has no valid email, it goes to the rejected file with `reject_reason = "invalid phone"`.

## Coding style
- Each cleaning function takes one value and returns the cleaned value (or `None` if invalid).
  This makes them easy to test and explain.
- Use `df.apply()` with these small functions instead of complex pandas chains.
- Friendly error messages. Example: `"Could not find an email or phone column. Check your CSV headers."`
- No logging frameworks. Use `print()` for the summary.

## Testing
- Add a test in `tests/test_cleaners.py` for every phone format in the table above.
- Run tests with:
  ```bash
  python -m unittest discover tests
  ```
- Before finishing any change, run the tool on `sample-data/messy_leads.csv` and check the output.

## When unsure
Ask before adding a new dependency, a new country, or changing the output columns.
