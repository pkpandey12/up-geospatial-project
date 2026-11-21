"""LGD PDF extractor (worked example), tested against the real export for UP."""

from pathlib import Path

import pandas as pd
import pytest

from up_siting.extract.lgd import OUTPUT_COLUMNS, parse_lgd_districts_pdf


@pytest.fixture(scope="module")
def lgd(request: pytest.FixtureRequest) -> pd.DataFrame:
    pdf = Path(__file__).parent / "fixtures" / "lgd" / "Districts_of_Uttar_Pradesh_State.pdf"
    return parse_lgd_districts_pdf(pdf)


def test_all_75_rows_including_white_ones(lgd: pd.DataFrame) -> None:
    # pdfplumber's default extract_tables() finds only the ~38 shaded rows.
    assert len(lgd) == 75
    assert lgd["s_no"].tolist() == [str(i) for i in range(1, 76)]


def test_columns_and_everything_is_text(lgd: pd.DataFrame) -> None:
    assert list(lgd.columns) == [*OUTPUT_COLUMNS, "_page", "_source_file"]
    for col in OUTPUT_COLUMNS:
        assert str(lgd[col].dtype) == "string", col


def test_row_split_across_page_break_is_stitched(lgd: pd.DataFrame) -> None:
    # Row 26 (Farrukhabad) starts at the foot of page 1; its wrapped cells end on page 2.
    farrukhabad = lgd.loc[lgd["s_no"] == "26"].iloc[0]
    assert farrukhabad["district_name_en"] == "Farrukhabad"
    assert farrukhabad["hierarchy"] == "Uttar Pradesh(State)"
    assert farrukhabad["pesa_status"] == "Not Covered"
    assert farrukhabad["_page"] == 1


def test_leading_zeros_survive(lgd: pd.DataFrame) -> None:
    amroha = lgd.loc[lgd["district_name_en"] == "Amroha"].iloc[0]
    assert amroha["census_2001_code"] == "06"


def test_known_rows(lgd: pd.DataFrame) -> None:
    by_name = lgd.set_index("district_name_en")
    assert by_name.loc["Agra", "lgd_district_code"] == "118"
    assert by_name.loc["Prayagraj", "short_name"] == "ALB"  # left over from "Allahabad"
    assert by_name.loc["Hapur", "census_2011_code"] == "000"  # created after Census 2011
    assert by_name.loc["Hapur", "census_2001_code"] == ""


def test_unexpected_layout_fails_loudly(tmp_path: Path) -> None:
    not_a_pdf = tmp_path / "broken.pdf"
    not_a_pdf.write_bytes(b"%PDF-1.3\n%%EOF\n")
    with pytest.raises(Exception):  # noqa: B017 - any error is fine, silence is not
        parse_lgd_districts_pdf(not_a_pdf)
