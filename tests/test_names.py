"""District-name normalisation (worked example) and map_to_lgd (Sage's TODO)."""

import unicodedata

import pandas as pd
import pytest

from up_siting.common.names import map_to_lgd, normalise_name


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Bara Banki", "barabanki"),
        ("BARABANKI", "barabanki"),
        ("  Rae   Bareli ", "raebareli"),
        ("Gautam Buddha Nagar District", "gautambuddhanagar"),
        ("Distt. Kheri", "kheri"),
        ("Sant Ravidas Nagar (Bhadohi)", "santravidasnagarbhadohi"),
        ("J.P. Nagar", "jpnagar"),
        ("Ambedkar-Nagar", "ambedkarnagar"),
        ("Jammu & Kashmir", "jammuandkashmir"),
    ],
)
def test_normalise_name_english(raw: str, expected: str) -> None:
    assert normalise_name(raw) == expected


def test_normalise_name_keeps_devanagari_vowel_signs() -> None:
    # "मिर्ज़ापुर" (Mirzapur) has vowel signs (category Mc) and a nukta (Mn): none may be lost.
    mirzapur = "मिर्ज़ापुर"
    assert normalise_name(mirzapur) == unicodedata.normalize("NFKC", mirzapur)
    assert normalise_name("जिला आगरा") == "आगरा"  # "जिला" = district, dropped as noise


def test_normalise_name_unicode_forms_compare_equal() -> None:
    precomposed = "ज़"  # DEVANAGARI LETTER ZA (one code point)
    decomposed = "ज़"  # JA + NUKTA (two code points), looks identical
    assert normalise_name(precomposed) == normalise_name(decomposed)


@pytest.mark.parametrize("missing", [None, "", "   ", "District", float("nan"), pd.NA])
def test_normalise_name_missing_is_none(missing: object) -> None:
    assert normalise_name(missing) is None


@pytest.fixture
def name_map() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "alias_normalised": ["agra", "prayagraj", "allahabad", "barabanki"],
            "lgd_district_code": [118, 120, 120, 129],
        }
    )


def test_map_to_lgd_maps_and_keeps_rows(name_map: pd.DataFrame) -> None:
    src = pd.DataFrame(
        {"district": ["AGRA", "Allahabad", "Bara Banki", "Atlantis", None], "v": [1, 2, 3, 4, 5]}
    )
    mapped, _ = map_to_lgd(src, "district", name_map)

    assert len(mapped) == len(src)
    assert mapped["v"].tolist() == [1, 2, 3, 4, 5], "row order must not change"
    assert str(mapped["lgd_district_code"].dtype) == "Int64"
    assert mapped["lgd_district_code"].tolist()[:3] == [118, 120, 129]
    assert mapped["lgd_district_code"].iloc[3:].isna().all()
    assert "lgd_district_code" not in src.columns, "must not modify the input"


def test_map_to_lgd_unmatched_report(name_map: pd.DataFrame) -> None:
    src = pd.DataFrame({"district": ["Atlantis", "Lemuria", "Atlantis", None, "Agra"]})
    _, unmatched = map_to_lgd(src, "district", name_map)

    assert list(unmatched.columns) == ["district", "n_rows"]
    assert unmatched["district"].tolist() == ["Atlantis", "Lemuria"]
    assert unmatched["n_rows"].tolist() == [2, 1]


def test_map_to_lgd_rejects_ambiguous_name_map(name_map: pd.DataFrame) -> None:
    bad = pd.concat(
        [name_map, pd.DataFrame({"alias_normalised": ["agra"], "lgd_district_code": [999]})]
    )
    with pytest.raises(ValueError, match="agra"):
        map_to_lgd(pd.DataFrame({"district": ["Agra"]}), "district", bad)


# ------------------------------------------------------------------ map_to_lgd review (2026-11-24)
# Contract details found in review. strict=True: once fixed, these XPASS and pytest reports
# that as a failure, which is your cue to delete the xfail line.
@pytest.mark.xfail(strict=True, reason="review follow-up: map_to_lgd writes into name_map")
def test_map_to_lgd_does_not_modify_name_map() -> None:
    name_map = pd.DataFrame(
        {
            "alias_normalised": pd.Series(["agra", None], dtype=object),
            "lgd_district_code": [118, 999],
        }
    )
    before = name_map.copy()
    map_to_lgd(pd.DataFrame({"district": ["Agra"]}), "district", name_map)
    pd.testing.assert_frame_equal(name_map, before)


@pytest.mark.xfail(strict=True, reason="review follow-up: map_to_lgd drops the input's index")
def test_map_to_lgd_keeps_input_index(name_map: pd.DataFrame) -> None:
    # Sources are often filtered first (index 10, 20, ...); the result must still line up
    # with the input row-for-row so it can be joined or assigned back.
    src = pd.DataFrame({"district": ["Agra", "Lemuria"]}, index=[10, 20])
    mapped, _ = map_to_lgd(src, "district", name_map)
    assert mapped.index.tolist() == [10, 20]
