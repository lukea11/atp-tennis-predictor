import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
CLEAN_DIR = Path(__file__).parent.parent / "data" / "cleaned"
YEARS = range(2018, 2025)
DATE_FORMAT = "%Y%m%d"
DAVIS_CUP_LEVEL = "D"


def load_raw(year: int) -> pd.DataFrame:
    """Load raw ATP match CSV for a given year.

    Args:
        year: Calendar year (e.g. 2022).
    Returns:
        Raw DataFrame with all original columns.
    """
    path = RAW_DIR / f"atp_matches_{year}.csv"
    return pd.read_csv(path)


def remove_davis_cup(df: pd.DataFrame) -> pd.DataFrame:
    """Drop all Davis Cup matches (tourney_level == 'D').

    Davis Cup matches carry no ranking points and are the source of
    all NA values in minutes and serve statistics.

    Args:
        df: Raw match DataFrame.
    Returns:
        DataFrame with Davis Cup rows removed.
    """
    return df[df["tourney_level"] != DAVIS_CUP_LEVEL].copy()


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert tourney_date from YYYYMMDD integer to datetime.

    Args:
        df: Match DataFrame with tourney_date as int.
    Returns:
        DataFrame with tourney_date as datetime64.
    """
    df["tourney_date"] = pd.to_datetime(df["tourney_date"], format=DATE_FORMAT)
    return df


def coerce_seeds(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce winner_seed and loser_seed to float.

    Non-numeric seed values (WC, Q, LL, etc.) become NaN.

    Args:
        df: Match DataFrame.
    Returns:
        DataFrame with seed columns as float64.
    """
    df["winner_seed"] = pd.to_numeric(df["winner_seed"], errors="coerce")
    df["loser_seed"] = pd.to_numeric(df["loser_seed"], errors="coerce")
    return df


def fill_entry(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing winner_entry and loser_entry values.

    - Seeded players (seed is not NaN) with no entry → 'seeded'
    - Unseeded players (seed is NaN) with no entry → 'unseeded'
    - 'Alt' normalised to 'ALT'; all other existing entries preserved.

    Args:
        df: Match DataFrame with coerced seed columns.
    Returns:
        DataFrame with no NaN values in winner_entry or loser_entry.
    """
    for role in ("winner", "loser"):
        seed_col = f"{role}_seed"
        entry_col = f"{role}_entry"
        is_seeded = df[seed_col].notna()
        missing_entry = df[entry_col].isna()
        df.loc[is_seeded & missing_entry, entry_col] = "seeded"
        df.loc[~is_seeded & missing_entry, entry_col] = "unseeded"
        df[entry_col] = df[entry_col].replace("Alt", "ALT")
    return df


def clean_year(year: int) -> pd.DataFrame:
    """Run the full cleaning pipeline for a single year.

    Args:
        year: Calendar year to clean.
    Returns:
        Cleaned DataFrame.
    """
    df = load_raw(year)
    df = remove_davis_cup(df)
    df = parse_dates(df)
    df = coerce_seeds(df)
    df = fill_entry(df)
    return df


def clean_all() -> pd.DataFrame:
    """Clean and concatenate all years into a single DataFrame.

    Returns:
        Combined cleaned DataFrame sorted by tourney_date.
    """
    frames = [clean_year(y) for y in YEARS]
    combined = pd.concat(frames, ignore_index=True)
    return combined.sort_values("tourney_date").reset_index(drop=True)


def save_cleaned(df: pd.DataFrame, filename: str = "atp_matches_cleaned.csv") -> None:
    """Save the cleaned DataFrame to data/cleaned/.

    Args:
        df: Cleaned DataFrame.
        filename: Output filename.
    """
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_DIR / filename, index=False)


if __name__ == "__main__":
    df = clean_all()
    save_cleaned(df)
    print(f"Saved {len(df):,} rows to data/cleaned/atp_matches_cleaned.csv")
