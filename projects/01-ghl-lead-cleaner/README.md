# GHL Lead Cleaner

Turn a messy lead spreadsheet into a clean file you can import straight into GoHighLevel.

Built for marketing VAs and agencies. No coding needed to use it.

## What it fixes

| Problem | Before | After |
|---|---|---|
| Messy names | `  dR. aNNA   testington ` | `Anna` / `Testington` |
| Messy emails | ` Anna.Test@EXAMPLE.com ` | `anna.test@example.com` |
| Mixed phone formats | `0917 000 1234`, `(212) 555-0123`, `0491 570 123` | `+639170001234`, `+12125550123`, `+61491570123` |
| Messy sources | `facebook`, `FB ads`, `Facebook Ad` | `Facebook Ads` |
| Duplicate leads | Same person 3 times | Kept once, with details from all 3 merged |
| Unusable rows | No email and no phone | Moved to a separate file with a reason |

Phone numbers from the **Philippines (+63)**, **US (+1)** and **Australia (+61)** are supported.

## What you get

Two files in the `output/` folder:

- **`<file name>_ghl_ready.csv`**: clean leads, ready to import.
- **`<file name>_rejected.csv`**: leads that were skipped, with a `reject_reason` column.
  Check this file. Some leads can be fixed by hand and imported later.

The tool also prints a short summary, like this:

```
Done!
  Rows in:            200
  Rows clean:         168
  Rows rejected:      32
    - duplicates:     20
    - other problems: 12
```

## One-time setup

1. Install Python 3 from https://www.python.org/downloads/
   On Windows, tick **"Add Python to PATH"** during install.
2. Download this folder.
3. Open a terminal in this folder. (Windows: open the folder, type `cmd` in the address bar and press Enter. Mac: right-click the folder, then New Terminal at Folder.)
4. Install the one library it needs:

```bash
pip install -r requirements.txt
```

On Mac, use `pip3` and `python3` if `pip` and `python` don't work.

## How to use it

1. Export your leads as a **CSV** file. (Excel or Google Sheets: File, then Download or Save As, then CSV.)
2. Put the file in the `input/` folder. Create the folder if it's missing.
3. Run:

```bash
python clean_leads.py input/leads.csv --default-country PH
```

Replace `leads.csv` with your file name. Use `PH`, `US` or `AU` for the client's main country.

### Optional settings

| Setting | What it does | Example |
|---|---|---|
| `--default-country` | Country to use when a number has no country code and could be more than one country | `--default-country AU` |
| `--source` | Fills in blank sources | `--source "Website Form"` |
| `--tags` | Adds tags to every lead | `--tags "dental, new lead"` |

Example with everything:

```bash
python clean_leads.py input/leads.csv --default-country PH --source "Facebook Ads" --tags "dental, may promo"
```

### Try it first with fake data

```bash
python clean_leads.py sample-data/messy_leads.csv --default-country PH
```

## Your CSV columns

The tool recognises common header names, so you usually don't need to rename anything.

| Output column | Headers it understands |
|---|---|
| First Name / Last Name | `First Name`, `Last Name`, `Surname`, or one `Full Name` / `Name` column (split at the first space) |
| Email | `Email`, `E-mail`, `Email Address` |
| Phone | `Phone`, `Mobile`, `Cell`, `Contact No.`, `Phone Number` |
| Company Name | `Company`, `Company Name`, `Business Name` |
| Tags | `Tags`, `Tag` |
| Source | `Source`, `Lead Source` |
| Notes | `Notes`, `Comments`, `Remarks` |

You need at least an email column or a phone column.

## Importing into GoHighLevel

1. In GHL, go to **Contacts**, then **Import Contacts**.
2. Upload the `_ghl_ready.csv` file.
3. Most columns map themselves. Check each one on the mapping screen.
4. **Notes** is not a standard GHL field. Map it to a custom field (for example, "Lead Notes"), or skip it.
5. Finish the import, then spot-check a few contacts.

## Rules the tool follows

- **A lead needs a valid email or a valid phone.** If one is bad but the other is fine, the lead is kept and the bad one is left blank.
- **Duplicates** are found by email first, then by phone. The first one in the file is kept.
  Details from the copies are merged in: blank fields are filled, and Tags and Notes are combined. Nothing already in the kept lead is overwritten.
- **Emails are never auto-fixed.** A wrong guess could send your client's emails to a stranger. Bad emails are left blank or the row is rejected.
- **Ambiguous phone numbers are never guessed.** For example, `9170001234` could be PH or US. The tool uses `--default-country` to decide. Without it, the number is left blank.
- **Titles are removed** from names (`Dr.`, `Mr.`, `Mrs.`, `Ms.`), so emails say "Hi Anna", not "Hi Dr."

## Privacy

- Files in `input/` and `output/` are never uploaded to GitHub.
- `sample-data/` holds fake data only. Never put real client data there.

## Common problems

| Message | Fix |
|---|---|
| `python is not recognized` | Reinstall Python and tick "Add Python to PATH". Or try `python3`. |
| `No module named pandas` | Run `pip install -r requirements.txt` again. |
| `Could not find the file` | Check the file name and that it's in the `input/` folder. |
| `Could not find an email or phone column` | Rename your email or phone column header to `Email` or `Phone`. |
| Lots of `ambiguous phone` rejects | Add `--default-country` with the client's country. |

## For developers

Run the tests from this folder:

```bash
python -m unittest discover tests
```

Files:

- `clean_leads.py`: main script.
- `cleaners.py`: one small function per field.
- `tests/test_cleaners.py`: tests for every phone format and cleaning rule.
- `tests/test_merge.py`: tests for duplicate merging.
