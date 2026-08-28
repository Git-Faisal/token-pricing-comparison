# Corpus provenance

Text extracted from official filings published on the Saudi Exchange
(saudiexchange.sa), retrieved 2026-08-28. Each filing is the company's
interim condensed consolidated financial statements for the six-month
period ended 30 June 2026, in the company's own official English and
Arabic versions (not translations made by us).

Extraction: pdf.js text layer, per page, whitespace-normalized, with
`=== PAGE n ===` markers. Pages listed as "image-only" are scanned
signature pages with no text layer (typically the auditor's report and
primary statements); their financial figures also appear in the digital
notes pages, which is what the tasks are graded on. No OCR was applied.
Arabic text carries the usual PDF letterform extraction artifacts, which
is representative of real-world Arabic document pipelines.

| File | Company | Symbol | Source PDF | Pages | Image-only pages |
|---|---|---|---|---|---|
| mis_7200_h1-2026_en.txt | Al Moammar Information Systems | 7200 | saudiexchange.sa/Resources/fsPdf/1361_0_2026-08-09_10-47-58_En.pdf | 26 | 3-7 |
| mis_7200_h1-2026_ar.txt | Al Moammar Information Systems | 7200 | saudiexchange.sa/Resources/fsPdf/1361_0_2026-08-09_10-47-58_Ar.pdf | 26 | 3-7 |
| aramco_2222_h1-2026_en.txt | Saudi Arabian Oil Co. (Aramco) | 2222 | saudiexchange.sa/Resources/fsPdf/1541_0_2026-08-04_07-43-39_En.pdf | 44 | none |
| aramco_2222_h1-2026_ar.txt | Saudi Arabian Oil Co. (Aramco) | 2222 | saudiexchange.sa/Resources/fsPdf/1541_0_2026-08-04_07-43-39_Ar.pdf | 43 | none |
| alrajhi_1120_h1-2026_en.txt | Al Rajhi Banking & Investment Corp. | 1120 | saudiexchange.sa/Resources/fsPdf/353_0_2026-07-29_14-52-14_En.pdf | 43 | 4-10 |
| alrajhi_1120_h1-2026_ar.txt | Al Rajhi Banking & Investment Corp. | 1120 | saudiexchange.sa/Resources/fsPdf/353_0_2026-07-29_14-52-14_Ar.pdf | 49 | 4-10 |

The PDFs are publicly accessible from each company's profile page on
saudiexchange.sa (Financial Statements and Reports tab). Direct requests
outside a browser session may be blocked by the site's WAF; to replicate
the extraction, open the URLs in a browser.

These are public disclosure documents used here for research/benchmarking
of language-model costs; all rights in the underlying filings remain with
their issuers.
