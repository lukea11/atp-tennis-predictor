import numpy as np
import pandas as pd
from pathlib import Path

from build_draw import ROUND_ORD

FEAT_DIR = Path(__file__).parent.parent / "data" / "features"
AGG_DIR  = Path(__file__).parent.parent / "data" / "aggregated"
PROC_DIR = Path(__file__).parent.parent / "data" / "processed"

SURFACE_ENC = {'Hard': 0, 'Clay': 1, 'Grass': 2}
LEVEL_ENC   = {'A': 0, 'G': 1, 'M': 2, 'F': 3}
HAND_ENC    = {'R': 0, 'L': 1, 'U': 0}

# (output_name, numerator_col, denominator_col) — computed from agg totals
AGG_RATE_TRIPLES = [
    ('ace_rate',             'total_ace',      'total_svpt'),
    ('df_rate',              'total_df',       'total_svpt'),
    ('first_serve_pct',      'total_1stIn',    'total_svpt'),
    ('first_serve_win_pct',  'total_1stWon',   'total_1stIn'),
    ('second_serve_win_pct', 'total_2ndWon',   'total_2ndIn'),
    ('bp_save_pct',          'total_bpSaved',  'total_bpFaced'),
    ('sv_gms_won_pct',       'total_SvGmsWon', 'total_SvGms'),
    ('rtn_win_pct',          'total_rtnWon',   'total_rtnGms'),
]

LAGGED_STAT_COLS = [
    'win_rate', 'completed_winrate', 'strsets_rate', 'tiebreaks_winrate',
    'rank_improvement', 'injured_during_swing', 'matches_played',
] + [name for name, *_ in AGG_RATE_TRIPLES]

PLAYER_ATTRS = {
    'id':       ('winner_id',          'loser_id'),
    'rank':     ('winner_rank',        'loser_rank'),
    'rank_pts': ('winner_rank_points', 'loser_rank_points'),
    'seed':     ('winner_seed',        'loser_seed'),
    'age':      ('winner_age',         'loser_age'),
    'ht':       ('winner_ht',          'loser_ht'),
    'hand':     ('winner_hand',        'loser_hand'),
    'h2h':      ('winner_h2h',         'loser_h2h'),
}


def _add_rates(agg: pd.DataFrame) -> pd.DataFrame:
    """Add normalised serve/return rate columns to the aggregation table.

    Args:
        agg: Player-surface-year aggregated DataFrame.
    Returns:
        agg with rate columns appended; zero denominator → NaN.
    """
    agg = agg.copy()
    agg['total_2ndIn'] = agg['total_svpt'] - agg['total_1stIn']
    for name, num, den in AGG_RATE_TRIPLES:
        agg[name] = agg[num] / agg[den].replace(0, np.nan)
    return agg


def _assign_ab(df: pd.DataFrame) -> pd.DataFrame:
    """Create player-A / player-B columns using lower-ID = A convention.

    label = 1 if player A (lower ID) wins. Consistent with H2H DB rule.

    Args:
        df: Feature-enriched match DataFrame.
    Returns:
        df with A_*/B_* columns and 'label' added.
    """
    df = df.copy()
    a_wins = df['winner_id'] < df['loser_id']
    for attr, (wcol, lcol) in PLAYER_ATTRS.items():
        df[f'A_{attr}'] = np.where(a_wins, df[wcol], df[lcol])
        df[f'B_{attr}'] = np.where(a_wins, df[lcol], df[wcol])
    df['label'] = a_wins.astype(int)
    return df


def _merge_lagged(
    matches: pd.DataFrame, agg: pd.DataFrame, id_col: str, suffix: str
) -> pd.DataFrame:
    """Left-join previous-year surface stats for one player onto match rows.

    Shifts agg year by +1 so that 2018 stats appear alongside 2019 matches.

    Args:
        matches: Match DataFrame with 'year', 'surface', and id_col columns.
        agg: Aggregated stats with rate columns added.
        id_col: Column holding the player ID to join on (e.g. 'A_id').
        suffix: Column suffix for merged stats ('_A' or '_B').
    Returns:
        matches with LAGGED_STAT_COLS merged in as <col><suffix>.
    """
    slim = agg[['year', 'player_id', 'surface'] + LAGGED_STAT_COLS].copy()
    slim = slim.rename(columns={c: f'{c}{suffix}' for c in LAGGED_STAT_COLS})
    slim['year'] = slim['year'] + 1       # prev-year stats join to next year's matches
    slim = slim.rename(columns={'player_id': id_col})
    return matches.merge(slim, on=['year', id_col, 'surface'], how='left')


def _add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add matchup-comparison features derived from A/B player columns.

    Args:
        df: Dataset DataFrame with A_rank, A_rank_pts, B_rank, B_rank_pts columns.
    Returns:
        df with rank_diff and rank_pts_diff columns appended.
    """
    df['rank_diff']     = df['A_rank']     - df['B_rank']
    df['rank_pts_diff'] = df['A_rank_pts'] - df['B_rank_pts']
    return df


def _encode(df: pd.DataFrame) -> pd.DataFrame:
    """Encode surface, tourney level, round, and player handedness.

    Args:
        df: Dataset DataFrame with A/B player columns.
    Returns:
        df with encoding columns added.
    """
    df['surface_enc']       = df['surface'].map(SURFACE_ENC)
    df['tourney_level_enc'] = df['tourney_level'].map(LEVEL_ENC)
    df['round_ord']         = df['round'].map(ROUND_ORD)
    df['hand_A_L']          = df['A_hand'].map(HAND_ENC)
    df['hand_B_L']          = df['B_hand'].map(HAND_ENC)
    return df


def build_dataset(feat_df: pd.DataFrame, agg_df: pd.DataFrame) -> pd.DataFrame:
    """Build the model-ready match dataset with lagged features for both players.

    Player A = lower player ID (label = 1 if A wins). Uses prev-year same-surface
    aggregated stats as lagged features; rows missing stats for either player are dropped.

    Args:
        feat_df: Feature-enriched match DataFrame (output of features.py).
        agg_df: Player-surface-year aggregated stats (output of aggregation.py).
    Returns:
        Model-ready DataFrame with match context, player A/B features, and label.
    """
    feat_df = feat_df.copy()
    feat_df['tourney_date'] = pd.to_datetime(feat_df['tourney_date'])
    feat_df['year'] = feat_df['tourney_date'].dt.year

    df = feat_df[feat_df['year'] >= 2019].copy()
    df = _assign_ab(df)

    agg_rated = _add_rates(agg_df)
    df = _merge_lagged(df, agg_rated, 'A_id', '_A')
    df = _merge_lagged(df, agg_rated, 'B_id', '_B')

    # Drop rows where either player lacks prev-year same-surface stats
    lag_check = [f'{c}_A' for c in LAGGED_STAT_COLS] + [f'{c}_B' for c in LAGGED_STAT_COLS]
    df = df.dropna(subset=[f'win_rate_A', f'win_rate_B']).reset_index(drop=True)

    df = _encode(df)
    df = _add_derived_features(df)
    return df


def save_dataset(df: pd.DataFrame, filename: str = 'model_dataset.csv') -> None:
    """Save the model-ready dataset to data/processed/.

    Args:
        df: Model-ready DataFrame.
        filename: Output filename.
    """
    PROC_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROC_DIR / filename, index=False)


if __name__ == '__main__':
    feat = pd.read_csv(FEAT_DIR / 'atp_features.csv')
    agg  = pd.read_csv(AGG_DIR  / 'player_surface_year_stats.csv')
    ds   = build_dataset(feat, agg)
    save_dataset(ds)
    print(f'Dataset: {len(ds):,} rows, {ds.shape[1]} columns')
    print(f'Label balance: {ds["label"].mean():.1%} player-A wins')
    print(f'Years: {sorted(ds["year"].unique())}')
