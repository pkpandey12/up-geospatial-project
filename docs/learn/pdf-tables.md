# Extracting tables from PDFs (pdfplumber)

**What it is.** pdfplumber reads a PDF's drawing instructions: characters with x/y
positions, lines and rectangles. It reconstructs words and tables from them. A PDF has **no
table structure**, only text placed at coordinates, so every table extractor is a set of
heuristics.

**Why here.** Indian government data often comes only as PDF: the LGD list, circle-rate
schedules (*mulyankan suchi*), tariff orders. Worked example: `src/up_siting/extract/lgd.py`.

## Concepts that matter

1. **Text-based vs scanned.** If `page.extract_text()` returns text, it's text-based. Scanned
   PDFs are images and need OCR (a different tool; flag it as a decision).
2. **Coordinates.** `x0, x1, top, bottom` in points (1/72 inch), origin top-left.
   `page.extract_words()` is the ground truth to debug with.
3. **Table strategies.** `"lines"` (default) uses drawn lines/rectangles; `"text"` infers
   columns/rows from text alignment; `"explicit"` takes your own x/y lines. Mix them per axis.
4. **The LGD trap: zebra striping.** Shaded rows are rectangles, so the "lines" strategy
   sees each shaded row as its own table and **silently skips every white row**. Count your
   rows against a known total (75), always.
5. **Recipe used for LGD**: column edges from the bordered header → `explicit` verticals +
   `text` horizontals → stitch continuation lines (empty first cell) onto the record above,
   **across page breaks** → map printed headers to names → fail on unknown headers.
6. **Keep everything as text** in the extractor (leading zeros, `'000'` codes). Cast and clean
   in the next step, where it's visible and tested.
7. **Garbage characters.** Fonts without a Unicode map produce NULs or private-use
   characters (Mirzapur's local name → `\x00` × 9). Detect with `unicodedata.category(ch) == "Cc"`.
8. **Hindi headers/values.** Normalise Unicode (NFKC) before comparing; Devanagari vowel signs
   are combining marks, so don't strip them with `\W` regexes.

## Commands you'll run

```python
import pdfplumber

pdf = pdfplumber.open(path)
page = pdf.pages[0]
page.extract_words()[:20]  # positions
page.find_tables()  # what "lines" finds
page.extract_table({"vertical_strategy": "text", "horizontal_strategy": "text"})
page.to_image(resolution=100).debug_tablefinder().save("debug.png")  # see what it detected
```

## Common mistakes

- Trusting `extract_tables()` without a row-count check.
- Hard-coding x coordinates: derive them from the header so a slightly different layout still works.
- Fixing values by hand in the PDF output. Fix the parser, or record it as a data-quality issue.

## Interview question

- *How would you make a PDF-scraping pipeline robust to the publisher changing the layout?*
  (Validate headers against an expected list and fail loudly; assert row counts and key
  uniqueness; keep raw files and parser version so you can re-run; alert, don't guess.)
