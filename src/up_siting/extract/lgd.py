"""Parse LGD's "Districts of <State>" PDF export into a tidy table.

WORKED EXAMPLE: PDF-table extractor pattern. Later PDF extractors (circle rates, tariff
orders, ...) follow the same shape: find columns -> split rows -> stitch -> name -> check.
Learn: docs/learn/pdf-tables.md

Why not just `page.extract_tables()`? The LGD PDF shades every other row. pdfplumber's
default "lines" strategy treats each shaded band as a separate one-row table, so it finds
only the shaded rows and silently drops the white ones (try it in a notebook). Instead:

1. Columns: the header row IS drawn as a bordered table, so we take the column edges from
   it (`page.find_tables()[0].columns`) and reuse them as explicit vertical lines.
2. Rows: split by text lines (`horizontal_strategy="text"`). A cell that wraps over two
   lines ("Uttar / Pradesh(State)", "Not / Covered") becomes two text rows.
3. Stitch: a text row whose S No cell is a number starts a new record; a row with an empty
   S No continues the record above, even across a page break (row 26 does this).
   Header and title rows (S No cell is text) are skipped.
4. Name: map the printed headers to snake_case column names; fail loudly on anything
   unexpected, because a changed layout must not produce a quietly wrong table.
5. Everything stays TEXT. Codes such as "06" have meaningful leading zeros; casting and
   cleaning ("000" = no code) belong to the next step, not to the extractor.
"""

from pathlib import Path

import pandas as pd
import pdfplumber

# Printed header (both lines joined) -> our column name. "View ..." columns are web links
# in the LGD site and are always empty in the PDF, so they are dropped.
HEADER_TO_COLUMN: dict[str, str | None] = {
    "S No": "s_no",
    "District LGD Code": "lgd_district_code",
    "District Name (In English)": "district_name_en",
    "District Name (In Local language)": "district_name_local",
    "Hierarchy": "hierarchy",
    "Short Name of District": "short_name",
    "Census 2001 Code": "census_2001_code",
    "Census2011 Code": "census_2011_code",
    "Pesa Status": "pesa_status",
    "View Details": None,
    "View History": None,
    "View Government Order": None,
    "View Map": None,
}

OUTPUT_COLUMNS = [c for c in HEADER_TO_COLUMN.values() if c is not None]


def _column_edges(page: pdfplumber.page.Page) -> list[float]:
    """x positions of the column borders, taken from the bordered header table."""
    tables = page.find_tables()
    if not tables:
        raise ValueError(f"page {page.page_number}: no bordered header table found")
    columns = tables[0].columns
    return [c.bbox[0] for c in columns] + [columns[-1].bbox[2]]


def _text_rows(page: pdfplumber.page.Page) -> list[list[str]]:
    """One list of cell strings per text line, using the header's column borders."""
    settings = {
        "vertical_strategy": "explicit",
        "explicit_vertical_lines": _column_edges(page),
        "horizontal_strategy": "text",
    }
    rows = page.extract_table(settings) or []
    return [[(cell or "").strip() for cell in row] for row in rows]


def _read_header(rows: list[list[str]]) -> list[str]:
    """Join the two header lines ("S"/"No", "District LGD"/"Code", ...) into full names."""
    first = next(i for i, row in enumerate(rows) if row and row[0] == "S")
    top, bottom = rows[first], rows[first + 1]
    return [" ".join(part for part in (a, b) if part) for a, b in zip(top, bottom, strict=True)]


def parse_lgd_districts_pdf(pdf_path: Path) -> pd.DataFrame:
    """Extract the district table from an LGD "Districts of <State>" PDF.

    Returns one row per district, all columns as text (see OUTPUT_COLUMNS), plus
    `_source_file` (file name) and `_page` (page where the record starts).
    Raises ValueError if the headers differ from HEADER_TO_COLUMN or S No has gaps.
    """
    pdf_path = Path(pdf_path)
    records: list[dict[str, str | int]] = []
    header: list[str] | None = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            rows = _text_rows(page)
            page_header = _read_header(rows)
            if header is None:
                unknown = [h for h in page_header if h not in HEADER_TO_COLUMN]
                if unknown:
                    raise ValueError(f"{pdf_path.name}: unexpected headers {unknown}")
                header = page_header
            elif page_header != header:
                raise ValueError(f"{pdf_path.name} p{page.page_number}: header changed")

            for row in rows:
                cells = dict(zip(header, row, strict=False))
                s_no = cells.get("S No", "")
                if s_no.isdigit():  # a new record starts here
                    record: dict[str, str | int] = {"_page": page.page_number}
                    record.update(cells)
                    records.append(record)
                elif s_no == "" and records and any(row):  # wrapped cell: continue last record
                    last = records[-1]
                    for col, text in cells.items():
                        if text:
                            last[col] = f"{last.get(col, '')} {text}".strip()
                # else: title or header line -> skip

    if header is None or not records:
        raise ValueError(f"{pdf_path.name}: no district rows found")

    df = pd.DataFrame.from_records(records)
    df = df.rename(columns={h: c for h, c in HEADER_TO_COLUMN.items() if c})
    df = df[[*OUTPUT_COLUMNS, "_page"]].fillna("").astype({c: "string" for c in OUTPUT_COLUMNS})
    df["_source_file"] = pdf_path.name

    # Cheap structural check: S No must run 1..n with no gaps or repeats.
    s_no = df["s_no"].astype(int).tolist()
    if s_no != list(range(1, len(s_no) + 1)):
        raise ValueError(f"{pdf_path.name}: S No is not 1..{len(s_no)} (rows lost or doubled)")
    return df
