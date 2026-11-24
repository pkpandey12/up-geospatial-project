"""District-name normalisation and mapping to LGD codes.

Every source spells districts its own way ("Bara Banki", "Barabanki", "BARABANKI",
"Rae Bareli", "Raebareli", "Allahabad" for Prayagraj ...). The project joins on the LGD
district code, never on names. Names are only used once, at the edge, to *find* the code:

    raw name --normalise_name()--> key --lookup in district_name_map.csv--> lgd_district_code

`normalise_name` is deliberately conservative: it removes differences that never change
meaning (case, spaces, punctuation, the word "district"). Real spelling differences
("Kabeer" vs "Kabir") and renames ("Allahabad" -> "Prayagraj") are listed explicitly in
dbt/seeds/district_aliases.csv, so every match can be explained. Fuzzy matching is used
only to *suggest* new aliases for a human to review, never to match automatically.
Learn: notebooks/eda/01_spine.ipynb, section 5.
"""

import unicodedata

import pandas as pd

# Words that sources add around a district name but that never distinguish two districts.
_NOISE_TOKENS = frozenset(
    {
        "district",
        "distt",
        "dist",
        "zila",
        "zilla",
        "jila",
        "janpad",
        "जिला",
        "जनपद",
    }
)


def _is_kept_char(ch: str) -> bool:
    """Keep letters (L*), combining marks (M*) and digits (N*); everything else is a separator.

    Marks matter for Hindi: Devanagari vowel signs such as "ि" are category Mc/Mn, and
    Python's regex \\w would drop them and corrupt the word.
    """
    return unicodedata.category(ch)[0] in {"L", "M", "N"}


def normalise_name(name: object) -> str | None:
    """Turn a district name into a join key.

    Steps: Unicode NFKC (so look-alike code points compare equal), casefold, "&" -> "and",
    split on anything that isn't a letter/mark/digit, drop noise words such as "district",
    and glue the remaining tokens together with no spaces.

    >>> normalise_name("Bara Banki")
    'barabanki'
    >>> normalise_name("  GAUTAM BUDDHA NAGAR District ")
    'gautambuddhanagar'
    >>> normalise_name("Sant Ravidas Nagar (Bhadohi)")
    'santravidasnagarbhadohi'
    >>> normalise_name(None) is None
    True

    Returns None for missing or empty input, so callers can treat "no name" as missing data.
    """
    if name is None or (not isinstance(name, str) and pd.isna(name)):
        return None
    text = unicodedata.normalize("NFKC", str(name)).casefold().replace("&", " and ")
    cleaned = "".join(ch if _is_kept_char(ch) else " " for ch in text)
    tokens = [t for t in cleaned.split() if t not in _NOISE_TOKENS]
    key = "".join(tokens)
    return key or None


def map_to_lgd(
    df: pd.DataFrame, name_col: str, name_map: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Attach `lgd_district_code` to every row of a source table, using its district-name column.

    Inputs:  df, any source table; name_col, the column holding raw district names;
             name_map, the table in dbt/seeds/district_name_map.csv with at least the columns
             `alias_normalised` and `lgd_district_code`.
    Returns: (mapped, unmatched)
             mapped    = df with a new nullable-integer column `lgd_district_code` ("Int64"),
                         SAME number of rows and SAME row order as df.
             unmatched = one row per distinct raw name that found no code, with columns
                         [name_col, "n_rows"], sorted by n_rows descending then name.
    Edge cases:
      - Null / empty names stay unmatched (code <NA>) but are NOT listed in `unmatched`.
      - If name_map has the same alias_normalised twice, raise ValueError: a left join
        would silently duplicate source rows.
      - Do not modify df in place.
    Practises: left joins, anti-joins, row-count invariants (validate= in pandas merge).
    """
    # 1. Check name_map is unique on alias_normalised; raise ValueError naming the duplicates.
    name_map["alias_normalised"] = name_map["alias_normalised"].astype(str)
    duplicates = name_map["alias_normalised"].duplicated(keep=False)
    if duplicates.any():
        dupes = name_map.loc[duplicates, "alias_normalised"].unique()
        raise ValueError(f"name_map has duplicate alias_normalised: {dupes}")
    # 2. Copy df and add a temporary key column: df[name_col] passed through normalise_name.
    df_copy = df.copy()
    df_copy["_key"] = df_copy[name_col].apply(normalise_name)
    # 3. Left-join the key to name_map[["alias_normalised", "lgd_district_code"]].
    #    Hint: pandas merge has a `validate=` argument that enforces "many_to_one".
    df_merged = df_copy.merge(
        name_map[["alias_normalised", "lgd_district_code"]],
        how="left",
        left_on="_key",
        right_on="alias_normalised",
        validate="many_to_one",
    )
    # 4. Cast lgd_district_code to "Int64", drop the temporary key, check the row count
    #    did not change.
    df_merged["lgd_district_code"] = df_merged["lgd_district_code"].astype("Int64")
    if len(df_merged) != len(df):
        raise ValueError(f"row count changed after merge: before={len(df)}, after={len(df_merged)}")
    # 5. Build `unmatched`: rows with a non-null key but no code, grouped by the raw name,
    #    counted, sorted.
    unmatched = (
        df_merged[df_merged["lgd_district_code"].isna() & df_merged["_key"].notna()]
        .groupby(name_col)
        .size()
        .reset_index(name="n_rows")
        .sort_values(by=["n_rows", name_col], ascending=[False, True])
    )
    df_merged.drop(columns=["_key", "alias_normalised"], inplace=True)
    # 6. Return (mapped, unmatched).
    return df_merged, unmatched
