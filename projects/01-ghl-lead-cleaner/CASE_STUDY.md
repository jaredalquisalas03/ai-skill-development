# Case Study: How I Turned 200 Messy Dental Leads Into a Clean GHL Import in 0.4 Seconds

**Project:** GHL Lead Cleaner
**Built by:** Jared, Marketing Automation Specialist
**Type:** Portfolio project. Tested on 200 fake leads modelled on a dental clinic's lead list.
**Tools:** Python, pandas, GoHighLevel contact import, Claude (AI pair-programming)

---

## The problem

Clinics and coaches collect leads from many places: Facebook ads, Google ads, website forms, walk-ins and referrals.
When it's time to import them into GoHighLevel, the list is a mess.

In the 200-lead test file:

| Problem | How bad it was |
|---|---|
| Names with wrong capitals or extra spaces | 181 of 200 |
| Phone number formats | 18 different formats across PH, US and AU |
| Ways of writing the lead source | 13 (`facebook`, `FB ads`, `Facebook Ad`…) |
| Duplicate leads | 20 |
| Broken emails (`@@`, `example,com`, `.cmo`) | About 20 |
| Leads with no email and no phone | 10 |

**Why this matters for the business:**
- **Bad phone formats break SMS.** GHL needs numbers like `+639171234567`. A number like `0917 000 1234` can fail to send.
- **Duplicates annoy leads.** The same person gets the same reminder two or three times.
- **Wrong capitals look like spam.** "Hi aNNA" in an email kills trust.
- **Messy sources ruin reporting.** You can't see which ad brings bookings when one source is spelled five ways.

Cleaning this by hand in a spreadsheet takes a VA an estimated **1 to 1.5 hours per 200 leads**. Errors slip through.

## The solution

A one-command tool any VA can run, without coding skills:

```bash
python clean_leads.py input/leads.csv --default-country PH
```

It does six things automatically:

1. **Fixes names.** Trims spaces, fixes capitals, removes titles like "Dr.", and splits full names into first and last.
2. **Checks emails.** Lowercases them and catches typos. It never "guesses" a fix, so mail never goes to a stranger.
3. **Standardises phones.** Converts PH, US and AU numbers into the `+country` format GHL needs for SMS.
4. **Cleans sources.** `facebook`, `FB ads` and `Facebook Ad` all become `Facebook Ads`.
5. **Merges duplicates.** It keeps one lead and fills its blanks from the copies. Tags and notes are combined, so nothing is lost.
6. **Explains every rejected row.** Example: `duplicate email (merged into row 14)` or `invalid phone`.

## Key decisions

- **Safety over guessing.** `9170001234` could be a PH or a US number. The tool uses the client's country setting and never guesses silently.
- **Keep leads, not just rows.** A lead with a bad phone but a good email is kept. Throwing it away over a typo loses a potential booking.
- **Merge, don't delete.** When the same patient fills in two forms, both notes survive. Example: `wants whitening | emergency - tooth pain`.
- **Built for non-developers.** Plain-English README, friendly error messages, and comments on every function.
- **Privacy first.** Real client files are blocked from GitHub. Only fake sample data is in the repo.

## Results (on the 200-lead test file)

| Metric | Result |
|---|---|
| Time to clean | **0.4 seconds** (vs. an estimated 60–90 min by hand) |
| Leads ready to import | 168 |
| Duplicates caught and merged | 20 of 20 |
| Unusable rows flagged with a reason | 12 |
| Phones converted to GHL format | All valid PH, US and AU numbers |
| Automated tests | 27, all passing |

## What this means for a clinic or agency

- **SMS reminders reach the patient**, because every phone is in the right format.
- **No double messages**, because duplicates are merged before import.
- **Accurate ad reporting**, because every lead source is spelled the same way.
- **VA time goes to follow-ups**, not spreadsheet cleanup.

## How AI helped

I used Claude as a coding partner. I set the rules: Python and pandas only, beginner-friendly code, no real client data, and PH/US/AU phone support.
I reviewed each decision, like how to handle ambiguous phones and whether to merge or delete duplicates.
AI sped up the build. The business rules came from knowing how GHL and clinic lead flows work.

## What's next

- Support for more input types, such as Excel `.xlsx` files.
- Optional auto-tagging by source (for example, every Facebook lead gets a `fb-lead` tag).
- A no-code version: upload a CSV, download the clean file.

---

**Need clean lead data or a GHL automation built?** Reach out through my GitHub profile.
