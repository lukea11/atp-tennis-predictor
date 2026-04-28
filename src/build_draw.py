"""Reconstruct ATP tournament bracket trees from historical match data."""

import numpy as np
import pandas as pd
from pathlib import Path

CLEAN_DIR  = Path(__file__).parent.parent / "data" / "cleaned"

ROUND_ORD  = {'R128': 1, 'BR': 1, 'R64': 2, 'RR': 3, 'R32': 3,
              'R16': 4, 'QF': 5, 'SF': 6, 'F': 7}
PREV_ROUND = {'F': 'SF', 'SF': 'QF', 'QF': 'R16',
              'R16': 'R32', 'R32': 'R64', 'R64': 'R128'}
# Ordered elimination rounds only. BR (bye-round) and RR (round-robin) are
# excluded: the bracket model never simulates those round types.
ROUND_LABELS = ['R128', 'R64', 'R32', 'R16', 'QF', 'SF', 'F']


class Match:
    """A node in the bracket tree — one match between two contestants."""

    __slots__ = ('left', 'right', 'round_label')

    def __init__(self, left, right, round_label: str):
        """
        Args:
            left:  Match node, player_id (int), or 'BYE'.
            right: Match node, player_id (int), or 'BYE'.
            round_label: e.g. 'R128', 'R64', ..., 'F'.
        """
        self.left        = left
        self.right       = right
        self.round_label = round_label

    def all_players(self) -> set:
        """Return the set of all player_ids contained in this subtree."""
        def _collect(node) -> set:
            if node == 'BYE':
                return set()
            if isinstance(node, (int, np.integer)):
                return {int(node)}
            return node.all_players()
        return _collect(self.left) | _collect(self.right)


# ── Data loading ───────────────────────────────────────────────────────────────

def load_cleaned(path: Path = None) -> pd.DataFrame:
    """Load the cleaned match CSV and attach a numeric round_ord column.

    Args:
        path: Override default (data/cleaned/atp_matches_cleaned.csv).
    Returns:
        DataFrame with tourney_date as datetime and round_ord added.
    """
    p  = path or CLEAN_DIR / 'atp_matches_cleaned.csv'
    df = pd.read_csv(p, parse_dates=['tourney_date'], low_memory=False)
    df['round_ord'] = df['round'].map(ROUND_ORD)
    return df


def find_tournament(df: pd.DataFrame, name: str, year: int) -> pd.DataFrame:
    """Return all matches for a tournament by partial name and year.

    Args:
        df: Cleaned match DataFrame with tourney_date parsed.
        name: Case-insensitive partial tournament name.
        year: Tournament year.
    Returns:
        DataFrame sorted by round_ord, match_num.
    Raises:
        ValueError: No matches found or name is ambiguous.
    """
    mask = (
        df['tourney_name'].str.contains(name, case=False, na=False)
        & (df['tourney_date'].dt.year == year)
    )
    t = df[mask].copy()
    if t.empty:
        raise ValueError(f"No tournament found: '{name}' {year}")
    names = t['tourney_name'].unique()
    if len(names) > 1:
        raise ValueError(f"Ambiguous name '{name}' matches: {names.tolist()}")
    return t.sort_values(['round_ord', 'match_num']).reset_index(drop=True)


def tournament_info(tourney_df: pd.DataFrame) -> dict:
    """Extract metadata for a tournament.

    Args:
        tourney_df: All matches for one tournament.
    Returns:
        Dict with keys: name, surface, level, best_of, date.
    """
    row = tourney_df.iloc[0]
    return {
        'name':    row['tourney_name'],
        'surface': row['surface'],
        'level':   row['tourney_level'],
        'best_of': int(row['best_of']),
        'date':    pd.to_datetime(row['tourney_date']),
    }


# ── Bracket tree construction ──────────────────────────────────────────────────

def _prev_winner_row(tourney_df: pd.DataFrame, player_id: int,
                     round_label: str):
    """Return the match row where player_id won in round_label, or None.

    None means the player received a BYE in that round.

    Args:
        tourney_df: Tournament match DataFrame.
        player_id: Player to look up.
        round_label: Round to search (e.g. 'SF').
    Returns:
        pd.Series or None.
    """
    m = tourney_df[
        (tourney_df['round'] == round_label)
        & (tourney_df['winner_id'] == player_id)
    ]
    return m.iloc[0] if len(m) else None


def _build_subtree(tourney_df: pd.DataFrame, winner_id: int, loser_id: int,
                   round_label: str) -> Match:
    """Recursively build the bracket subtree rooted at one match.

    Traces both players backward through prior rounds. A player with no
    prior win row (BYE) produces a leaf Match(player, 'BYE', prev_round).

    Args:
        tourney_df: Tournament match DataFrame.
        winner_id: ID of the actual match winner.
        loser_id:  ID of the actual match loser.
        round_label: Round this match was played in.
    Returns:
        Match node for this match and all prior matches in the subtree.
    """
    prev = PREV_ROUND.get(round_label)
    if prev is None:
        return Match(winner_id, loser_id, round_label)

    w_row = _prev_winner_row(tourney_df, winner_id, prev)
    l_row = _prev_winner_row(tourney_df, loser_id, prev)

    left  = (
        _build_subtree(tourney_df, int(w_row['winner_id']), int(w_row['loser_id']), prev)
        if w_row is not None else Match(winner_id, 'BYE', prev)
    )
    right = (
        _build_subtree(tourney_df, int(l_row['winner_id']), int(l_row['loser_id']), prev)
        if l_row is not None else Match(loser_id, 'BYE', prev)
    )
    return Match(left, right, round_label)


def build_bracket_tree(tourney_df: pd.DataFrame) -> Match:
    """Build the full bracket tree from the Final backward.

    Reconstructs every match in the draw by tracing winner/loser paths.
    BYE players appear as Match(player_id, 'BYE', prev_round) leaf nodes.

    Args:
        tourney_df: All matches for one tournament, sorted by round_ord, match_num.
    Returns:
        Root Match node representing the Final.
    Raises:
        ValueError: No Final match found (incomplete data).
    """
    finals = tourney_df[tourney_df['round'] == 'F']
    if finals.empty:
        raise ValueError("No Final match found — tournament may be incomplete")
    f = finals.iloc[0]
    return _build_subtree(tourney_df, int(f['winner_id']), int(f['loser_id']), 'F')


# ── Player attributes ──────────────────────────────────────────────────────────

# Default fallback values used when a player attribute is missing from match data.
_ATTR_DEFAULTS = {'rank': 500.0, 'rank_points': 0.0, 'age': 25.0, 'ht': 185.0}


def _float_or(row, col: str, default: float) -> float:
    """Return float(row[col]) if the value is non-null, else default.

    Args:
        row: pandas Series (one match row).
        col: Column name.
        default: Fallback value.
    Returns:
        Parsed float or default.
    """
    val = row.get(col)
    return float(val) if pd.notna(val) else default


def extract_player_attrs(tourney_df: pd.DataFrame) -> dict:
    """Extract match-time attributes for every player from the tournament draw.

    Collects rank, rank_pts, seed, age, height, and hand from each player's
    first appearance in the match data. Missing values fall back to safe defaults
    so the model always receives a complete feature vector.

    Args:
        tourney_df: All matches for one tournament.
    Returns:
        Dict: {player_id: {name, rank, rank_pts, seed, age, ht, hand_L}}.
    """
    attrs = {}
    for _, row in tourney_df.iterrows():
        for role in ('winner', 'loser'):
            pid = int(row[f'{role}_id'])
            if pid in attrs:
                continue
            seed = row.get(f'{role}_seed')
            try:
                seed = float(seed) if pd.notna(seed) else np.nan
            except (TypeError, ValueError):
                seed = np.nan
            attrs[pid] = {
                'name':     row[f'{role}_name'],
                'rank':     _float_or(row, f'{role}_rank',        _ATTR_DEFAULTS['rank']),
                'rank_pts': _float_or(row, f'{role}_rank_points', _ATTR_DEFAULTS['rank_points']),
                'seed':     seed,
                'age':      _float_or(row, f'{role}_age',         _ATTR_DEFAULTS['age']),
                'ht':       _float_or(row, f'{role}_ht',          _ATTR_DEFAULTS['ht']),
                'hand_L':   1 if row.get(f'{role}_hand') == 'L' else 0,
            }
    return attrs


def get_actual_path(tourney_df: pd.DataFrame, target_id: int) -> dict:
    """Extract the actual round-by-round path for one player.

    Args:
        tourney_df: All matches for one tournament.
        target_id: Player ID to trace.
    Returns:
        Dict: {round_label: {opponent_id, opponent_name, won}}.
        R128 entry will be {'opponent_name': 'BYE', 'won': True} if player had a bye.
    """
    first_round_ord = tourney_df['round_ord'].min()
    # Use the actual round label present in the data rather than reverse-mapping
    # the ordinal — multiple labels share the same ordinal (e.g. R128 and BR = 1).
    first_round_rows = tourney_df[tourney_df['round_ord'] == first_round_ord]
    first_round      = first_round_rows.iloc[0]['round']
    r1_players       = (set(first_round_rows['winner_id'])
                        | set(first_round_rows['loser_id']))

    path = {}
    if first_round == 'R128' and target_id not in r1_players:
        path['R128'] = {'opponent_id': None, 'opponent_name': 'BYE', 'won': True}

    for _, row in tourney_df.iterrows():
        rl = row['round']
        if rl not in ROUND_ORD:
            continue
        if row['winner_id'] == target_id:
            path[rl] = {'opponent_id': int(row['loser_id']),
                        'opponent_name': row['loser_name'], 'won': True}
        elif row['loser_id'] == target_id:
            path[rl] = {'opponent_id': int(row['winner_id']),
                        'opponent_name': row['winner_name'], 'won': False}
    return path
