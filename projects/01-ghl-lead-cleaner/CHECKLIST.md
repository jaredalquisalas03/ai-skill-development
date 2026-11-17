# Client Lead Cleanup Checklist

Use this every time a client sends you a messy lead list.
Time needed: about 15 minutes, including the GHL import.

---

## 1. Before you start

- [ ] Ask the client which country most leads are from: PH, US or AU.
- [ ] Ask what source and tags they want on these leads, e.g. `Facebook Ads`, `may promo`.
- [ ] Check that the list has an **email** or **phone** column. Without one, the tool can't run.
- [ ] Work on your **own laptop**. Never upload client lists to GitHub, ChatGPT or Claude.

## 2. Prepare the file

- [ ] Download the list as **CSV** (Google Sheets: File → Download → CSV. Excel: Save As → CSV UTF-8).
- [ ] Rename it with the client's name, no spaces, e.g. `smile-dental.csv`.
- [ ] Move it into the `input/` folder.
- [ ] Keep the client's original file untouched as a backup.

## 3. Run the tool

- [ ] Open a terminal in the `01-ghl-lead-cleaner` folder.
- [ ] Run the command below. Change the file name, country, source and tags to fit the client.

```bash
python clean_leads.py input/smile-dental.csv --default-country PH --source "Facebook Ads" --tags "smile dental"
```

- [ ] Read the summary. Write down: rows in, rows clean, duplicates and other problems.

## 4. Check the results

Open `output/smile-dental_ghl_ready.csv`:
- [ ] Spot-check 5–10 rows. Are the names, emails and phones correct?
- [ ] Phones start with `+63`, `+1` or `+61`.
- [ ] Sources look consistent (no `facebook` and `FB ads` mixed together).

Open `output/smile-dental_rejected.csv`:
- [ ] Read the `reject_reason` column.
- [ ] **Duplicates:** nothing to do. Their details are already merged.
- [ ] **Invalid email / phone:** fix obvious typos by hand if you can. Example: `.cmo` → `.com`.
- [ ] **Ambiguous phone:** run again with the right `--default-country`.
- [ ] **No email or phone:** list these for the client.

**Warning sign:** if more than 20% of rows are rejected, stop. Check the headers and the country setting before importing.

## 5. Import into GHL

- [ ] **Test first:** import 5 rows into GHL and check them before the full list.
- [ ] Go to **Contacts → Import Contacts** and upload the `_ghl_ready.csv` file.
- [ ] Check every column on the mapping screen.
- [ ] Map **Notes** to a custom field (e.g. "Lead Notes"), or skip it.
- [ ] Add an import tag, e.g. `import-2026-11-17`. You can find or undo this batch later.
- [ ] Choose whether to update existing contacts or skip them. Ask the client if you're unsure.
- [ ] **Turn off or check workflows** that trigger on "Contact Created". Otherwise 400 leads may get a welcome SMS at once.
- [ ] Finish the import and check that the contact count in GHL matches.

## 6. Report to the client

- [ ] Send a short update. Template:

> Hi [Name], I cleaned your lead list and imported **[clean]** contacts into GHL.
> I found **[duplicates]** duplicates and merged them, so no one gets double messages.
> **[other problems]** leads had no valid email or phone. I attached them in case your team can fill in the details.

- [ ] Attach the rejected file, if it has rows the client can fix.

## 7. Clean up

- [ ] Delete the client's file from `input/` and `output/` once the job is done.
- [ ] Log your time and the results (e.g. "500 leads → 431 imported, 48 duplicates merged"). These numbers go in your next case study or proposal.
