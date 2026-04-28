import numpy as np
import pandas as pd
from pathlib import Path

FEAT_DIR       = Path(__file__).parent.parent / "data" / "features"
AGG_DIR        = Path(__file__).parent.parent / "data" / "aggregated"
DAYS_PER_MONTH = 30.44

# Stat suffixes that map to w_<col> / l_<col> in the feature DataFrame.
# Raw cols may have values for RET/WO rows; feature cols are already NaN.
# Both are explicitly nulled for non-completed matches in the player view.
STAT_COLS_RAW  = ["ace", "df", "svpt", "1stIn", "1stWon", "2ndWon",
                  "SvGms", "bpSaved", "bpFaced"]
STAT_COLS_FEAT = ["SvGmsWon", "rtnWon", "rtnGms"]
STAT_COLS      = STAT_COLS_RAW + STAT_COLS_FEAT

FILL_ZERO_COLS = (
    ["start_rank", "end_rank", "rank_improvement",
     "win_rate", "strsets_rate", "completed_winrate", "tiebreaks_winrate"]
    + [f"total_{c}" for c in STAT_COLS]
)


# ── Player-perspective pivot ───────────────────────────────────────────────────

def _player_perspective(df: pd.DataFrame, role: str) -> pd.DataFrame:
    """Extract one row per match from either the winner or loser's viewpoint.

    All stat columns are set to NaN for retired/walkover matches since
    those matches were not completed and stats are unreliable.

    Args:
        df: Feature-enriched match DataFrame.
        role: 'winner' or 'loser'.
    Returns:
        Player-perspective DataFrame with unified column names.
    """
    p         = "w" if role == "winner" else "l"
    completed = df["loser_retired"] == 0
    tb_total  = df["w_tiebreaks_won"] + df["l_tiebreaks_won"]

    out = pd.DataFrame({
        "tourney_date":    df["tourney_date"].values,
        "surface":         df["surface"].values,
        "player_id":       df[f"{role}_id"].values,
        "player_name":     df[f"{role}_name"].values,
        "rank":            df[f"{role}_rank"].values,
        "won":             (1 if role == "winner" else 0),
        "player_retired":  (df["loser_retired"].values if role == "loser" else 0),
        "is_completed":    completed.astype(int).values,
        "win_completed":   (completed.astype(int).values if role == "winner" else 0),
        "straight_set":    (df["straight_sets_win"].values if role == "winner" else 0),
        "tiebreaks_won":   df[f"{p}_tiebreaks_won"].values,
        "tiebreaks_total": tb_total.values,
    })
    for col in STAT_COLS:
        out[col] = df[f"{p}_{col}"].where(completed).values
    return out


def _pivot_to_player_view(df: pd.DataFrame) -> pd.DataFrame:
    """Stack winner and loser perspectives into one row-per-player-per-match table.

    Args:
        df: Feature-enriched match DataFrame.
    Returns:
        Player-perspective DataFrame sorted chronologically, with year column.
    """
    pv = pd.concat(
        [_player_perspective(df, "winner"), _player_perspective(df, "loser")],
        ignore_index=True,
    )
    pv["tourney_date"] = pd.to_datetime(pv["tourney_date"])
    pv["year"] = pv["tourney_date"].dt.year
    return pv.sort_values(["year", "tourney_date"]).reset_index(drop=True)


# ── Injury table ──────────────────────────────────────────────────────────────

def build_injury_table(df: pd.DataFrame) -> pd.DataFrame:
    """Build a table of retirement events with comeback dates.

    For each match where the loser retired or walked over, records the
    retirement date and the player's next match date as their comeback.
    Used to compute the injured_during_swing metric.

    Args:
        df: Full feature DataFrame (all years, all surfaces).
    Returns:
        DataFrame: player_id, retirement_date, comeback_date, months_absent.
    """
    df = df.copy()
    df["tourney_date"] = pd.to_datetime(df["tourney_date"])

    all_dates = pd.concat([
        df[["winner_id", "tourney_date"]].rename(columns={"winner_id": "player_id"}),
        df[["loser_id",  "tourney_date"]].rename(columns={"loser_id":  "player_id"}),
    ]).sort_values("tourney_date")

    retirements = df[df["loser_retired"] == 1][["loser_id", "tourney_date"]].copy()
    retirements.columns = ["player_id", "retirement_date"]

    records = []
    for _, row in retirements.iterrows():
        pid, ret_date = row["player_id"], row["retirement_date"]
        nxt = all_dates[
            (all_dates["player_id"] == pid) & (all_dates["tourney_date"] > ret_date)
        ]
        if nxt.empty:
            continue
        comeback_date = nxt["tourney_date"].min()
        records.append({
            "player_id":       pid,
            "retirement_date": ret_date,
            "comeback_date":   comeback_date,
            "months_absent":   (comeback_date - ret_date).days / DAYS_PER_MONTH,
        })
    return pd.DataFrame(records) if records else pd.DataFrame(
        columns=["player_id", "retirement_date", "comeback_date", "months_absent"]
    )


def _injury_score(
    player_id: int, ref_date: pd.Timestamp, injury_table: pd.DataFrame
) -> float:
    """Compute injury compromise score at ref_date using Back-from-Absence.

    Formula: max(0, 1 - months_since_comeback / months_absent).
    Uses the most recent comeback on or before ref_date.
    Returns 0 if no injury history or player is fully recovered.

    Args:
        player_id: ATP player ID.
        ref_date: First match date for this player in the surface-year period.
        injury_table: Output of build_injury_table().
    Returns:
        Float in [0, 1]. 1 = just returned; 0 = fully recovered / no injury.
    """
    prior = injury_table[
        (injury_table["player_id"] == player_id)
        & (injury_table["comeback_date"] <= ref_date)
    ]
    if prior.empty:
        return 0.0
    latest = prior.sort_values("comeback_date").iloc[-1]
    if latest["months_absent"] == 0:
        return 0.0
    months_since = (ref_date - latest["comeback_date"]).days / DAYS_PER_MONTH
    return float(max(0.0, 1.0 - months_since / latest["months_absent"]))


# ── Aggregation helpers ───────────────────────────────────────────────────────

def _year_ranks(pv: pd.DataFrame) -> pd.DataFrame:
    """Compute start rank, end rank, and rank improvement per player-year.

    Rank is global ATP ranking (not surface-specific). Uses the player's
    first and last match of the year across all surfaces.

    Args:
        pv: Player-perspective DataFrame sorted by tourney_date.
    Returns:
        DataFrame: year, player_id, start_rank, end_rank, rank_improvement.
    """
    yr = (
        pv.sort_values(["year", "tourney_date"])
        .groupby(["year", "player_id"])
        .agg(start_rank=("rank", "first"), end_rank=("rank", "last"))
        .reset_index()
    )
    yr["rank_improvement"] = yr["start_rank"] - yr["end_rank"]
    return yr


def _base_aggregation(pv: pd.DataFrame) -> pd.DataFrame:
    """Aggregate player stats by (year, player_id, surface).

    Args:
        pv: Player-perspective DataFrame with year column.
    Returns:
        DataFrame with match counts and stat totals per composite key.
    """
    agg_dict = dict(
        player_name       = ("player_name",    "first"),
        matches_played    = ("won",            "count"),
        wins              = ("won",            "sum"),
        matches_completed = ("is_completed",   "sum"),
        wins_in_completed = ("win_completed",  "sum"),
        straight_set_wins = ("straight_set",   "sum"),
        tiebreaks_played  = ("tiebreaks_total","sum"),
        tiebreaks_won     = ("tiebreaks_won",  "sum"),
    )
    for col in STAT_COLS:
        agg_dict[f"total_{col}"] = (col, "sum")
    return (
        pv.sort_values(["year", "tourney_date"])
        .groupby(["year", "player_id", "surface"])
        .agg(**agg_dict)
        .reset_index()
    )


def _add_rates(agg: pd.DataFrame) -> pd.DataFrame:
    """Add win_rate, strsets_rate, completed_winrate, and tiebreaks_winrate.

    Args:
        agg: Aggregated DataFrame from _base_aggregation().
    Returns:
        agg with four rate columns appended.
    """
    wins      = agg["wins"].replace(0, np.nan)
    completed = agg["matches_completed"].replace(0, np.nan)
    tbs       = agg["tiebreaks_played"].replace(0, np.nan)

    agg["win_rate"]          = agg["wins"] / agg["matches_played"]
    agg["strsets_rate"]      = agg["straight_set_wins"] / wins
    agg["completed_winrate"] = agg["wins_in_completed"] / completed
    agg["tiebreaks_winrate"] = agg["tiebreaks_won"] / tbs
    return agg


def _add_injury_scores(
    agg: pd.DataFrame, pv: pd.DataFrame, injury_table: pd.DataFrame
) -> pd.DataFrame:
    """Add injured_during_swing using each player's first match in the period.

    Reference date is the first match for the player on that surface in that year,
    making the metric surface-specific (clay season starts later than hard).

    Args:
        agg: Aggregated DataFrame.
        pv: Player-perspective DataFrame.
        injury_table: Output of build_injury_table().
    Returns:
        agg with 'injured_during_swing' column appended.
    """
    first_match = (
        pv.groupby(["year", "player_id", "surface"])["tourney_date"]
        .min()
        .reset_index()
        .rename(columns={"tourney_date": "ref_date"})
    )
    agg = agg.merge(first_match, on=["year", "player_id", "surface"], how="left")
    agg["injured_during_swing"] = agg.apply(
        lambda r: _injury_score(r["player_id"], r["ref_date"], injury_table), axis=1
    )
    return agg.drop(columns=["ref_date"])


# ── Main pipeline ─────────────────────────────────────────────────────────────

def aggregate_all(dfs: list) -> tuple:
    """Run the full player-surface-year aggregation pipeline.

    Inner loop: per year × surface × player — match counts, stats, injury score.
    Outer loop: union across 2018–2024.

    Args:
        dfs: List of yearly feature-enriched match DataFrames.
    Returns:
        Tuple (aggregated_df, injury_table).
        aggregated_df primary key: (year, player_id, surface).
    """
    df = pd.concat(dfs, ignore_index=True)
    df["tourney_date"] = pd.to_datetime(df["tourney_date"])

    pv           = _pivot_to_player_view(df)
    injury_table = build_injury_table(df)
    year_ranks   = _year_ranks(pv)

    agg = _base_aggregation(pv)
    agg = _add_rates(agg)
    agg = _add_injury_scores(agg, pv, injury_table)
    agg = agg.merge(year_ranks, on=["year", "player_id"], how="left")

    name_parts = agg["player_name"].str.split(" ", n=1, expand=True)
    agg.insert(3, "player_first_name", name_parts[0])
    agg.insert(4, "player_last_name",  name_parts[1].fillna(""))
    agg = agg.drop(columns=["player_name"])

    agg[FILL_ZERO_COLS] = agg[FILL_ZERO_COLS].fillna(0)
    return agg, injury_table


def save_aggregation(agg: pd.DataFrame, injury_table: pd.DataFrame) -> None:
    """Save aggregated stats and injury table to data/aggregated/.

    Args:
        agg: Player-surface-year aggregated DataFrame.
        injury_table: Retirement/comeback events DataFrame.
    """
    AGG_DIR.mkdir(parents=True, exist_ok=True)
    agg.to_csv(AGG_DIR / "player_surface_year_stats.csv", index=False)
    injury_table.to_csv(AGG_DIR / "injury_table.csv", index=False)


if __name__ == "__main__":
    feat = pd.read_csv(FEAT_DIR / "atp_features.csv")
    agg, injury_table = aggregate_all([feat])
    save_aggregation(agg, injury_table)
    print(f"Aggregated: {len(agg):,} rows  ({agg['year'].nunique()} years × "
          f"{agg['surface'].nunique()} surfaces × {agg['player_id'].nunique()} players)")
    print(f"Injury table: {len(injury_table):,} retirement events")
