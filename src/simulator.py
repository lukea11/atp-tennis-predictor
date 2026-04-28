"""ATP tournament simulator using XGBoost match probabilities."""

import argparse
import json
import sys
import numpy as np
import pandas as pd
import xgboost as xgb
from collections import Counter
from difflib import get_close_matches
from pathlib import Path

from build_draw import (
    Match, ROUND_ORD, ROUND_LABELS,
    build_bracket_tree, extract_player_attrs, find_tournament,
    get_actual_path, load_cleaned, tournament_info,
)
from build_dataset import SURFACE_ENC, LEVEL_ENC, AGG_RATE_TRIPLES, LAGGED_STAT_COLS, _add_rates

AGG_DIR   = Path(__file__).parent.parent / "data" / "aggregated"
MODEL_DIR = Path(__file__).parent.parent / "models"

# Must match train_xgb.py FEATURES exactly — model expects this column order.
FEATURES = [
    'surface_enc', 'tourney_level_enc', 'round_ord', 'best_of',
    'A_rank', 'A_rank_pts', 'A_seed', 'A_age', 'A_ht', 'A_h2h', 'hand_A_L',
    'B_rank', 'B_rank_pts', 'B_seed', 'B_age', 'B_ht', 'B_h2h', 'hand_B_L',
    'days_since_h2h',
    'rank_diff', 'rank_pts_diff',
    'A_tourney_titles', 'A_tourney_win_rate', 'A_tourney_matches',
    'B_tourney_titles', 'B_tourney_win_rate', 'B_tourney_matches',
    'win_rate_A', 'completed_winrate_A', 'strsets_rate_A', 'tiebreaks_winrate_A',
    'rank_improvement_A', 'injured_during_swing_A', 'matches_played_A',
    'ace_rate_A', 'df_rate_A', 'first_serve_pct_A', 'first_serve_win_pct_A',
    'second_serve_win_pct_A', 'bp_save_pct_A', 'sv_gms_won_pct_A', 'rtn_win_pct_A',
    'win_rate_B', 'completed_winrate_B', 'strsets_rate_B', 'tiebreaks_winrate_B',
    'rank_improvement_B', 'injured_during_swing_B', 'matches_played_B',
    'ace_rate_B', 'df_rate_B', 'first_serve_pct_B', 'first_serve_win_pct_B',
    'second_serve_win_pct_B', 'bp_save_pct_B', 'sv_gms_won_pct_B', 'rtn_win_pct_B',
]


# ── Model and data loading ─────────────────────────────────────────────────────

def load_model(model_path: Path = None) -> xgb.XGBClassifier:
    """Load the pre-trained XGBoost model from disk.

    Args:
        model_path: Override default (models/xgb_model.json).
    Returns:
        Loaded XGBClassifier.
    """
    path  = model_path or MODEL_DIR / 'xgb_model.json'
    model = xgb.XGBClassifier()
    model.load_model(str(path))
    return model


def build_lagged_stats(agg_df: pd.DataFrame, year: int, surface: str) -> dict:
    """Extract prior-year surface stats for every player.

    Args:
        agg_df: Aggregated player stats DataFrame.
        year: Tournament year (stats from year-1 are used).
        surface: Tournament surface.
    Returns:
        Dict: {player_id: {stat_name: float}}.
    """
    prior = agg_df[(agg_df['year'] == year - 1) & (agg_df['surface'] == surface)]
    prior = _add_rates(prior)
    return {
        int(row['player_id']): {
            col: float(row[col]) if pd.notna(row[col]) else np.nan
            for col in LAGGED_STAT_COLS
        }
        for _, row in prior.iterrows()
    }


def merge_player_attrs(draw_attrs: dict, lagged: dict,
                       tourney_history: dict = None) -> dict:
    """Combine draw-time attributes with lagged stats and tournament history.

    Args:
        draw_attrs: From extract_player_attrs() — rank, seed, ht, etc.
        lagged: From build_lagged_stats() — win_rate, ace_rate, etc.
        tourney_history: From compute_tourney_history_lookup() — optional;
            keys tourney_titles, tourney_wins, tourney_matches per player.
    Returns:
        Merged dict: {player_id: combined_feature_attrs}.
    """
    merged = {pid: dict(attrs) for pid, attrs in draw_attrs.items()}
    for pid in merged:
        lag = lagged.get(pid, {})
        for col in LAGGED_STAT_COLS:
            merged[pid][col] = lag.get(col, np.nan)
        th = (tourney_history or {}).get(pid, {})
        wins    = th.get('tourney_wins',    0)
        matches = th.get('tourney_matches', 0)
        merged[pid]['tourney_titles']   = th.get('tourney_titles', 0)
        merged[pid]['tourney_matches']  = matches
        merged[pid]['tourney_win_rate'] = wins / matches if matches > 0 else 0.0
    return merged


def compute_tourney_history_lookup(
    cleaned_df: pd.DataFrame, player_ids: set,
    tourney_name: str, before_date: pd.Timestamp,
) -> dict:
    """Compute each draw player's prior match history at this tournament.

    Args:
        cleaned_df: Full cleaned match DataFrame.
        player_ids: Set of player IDs in the tournament draw.
        tourney_name: Exact tournament name (as it appears in the data).
        before_date: Tournament start date (exclusive cutoff).
    Returns:
        Dict: {player_id: {tourney_wins, tourney_titles, tourney_matches}}.
    """
    prior = cleaned_df[
        (cleaned_df['tourney_date'] < before_date)
        & (cleaned_df['tourney_name'] == tourney_name)
    ].sort_values('tourney_date')

    db: dict = {}
    for _, row in prior.iterrows():
        w_id = int(row['winner_id'])
        l_id = int(row['loser_id'])
        for pid in (w_id, l_id):
            if pid not in db:
                db[pid] = {'tourney_wins': 0, 'tourney_titles': 0, 'tourney_matches': 0}
        db[w_id]['tourney_wins']    += 1
        db[w_id]['tourney_matches'] += 1
        db[l_id]['tourney_matches'] += 1
        if row['round'] == 'F':
            db[w_id]['tourney_titles'] += 1

    return {pid: db[pid] for pid in player_ids if pid in db}


# ── H2H lookup ─────────────────────────────────────────────────────────────────

def compute_h2h_lookup(
    cleaned_df: pd.DataFrame, player_ids: set,
    surface: str, before_date: pd.Timestamp,
) -> dict:
    """Compute pairwise H2H records for all draw players before the tournament.

    Only same-surface prior meetings are counted (surface-specific H2H,
    consistent with how H2H features were built in features.py).

    Args:
        cleaned_df: Full cleaned match DataFrame.
        player_ids: Set of player IDs in the tournament draw.
        surface: Tournament surface.
        before_date: Tournament start date (exclusive cutoff).
    Returns:
        Dict: {(player_A_id, player_B_id): {A_wins, B_wins, last_date}}.
        All keys have player_A_id < player_B_id.
    """
    prior = cleaned_df[
        (cleaned_df['tourney_date'] < before_date)
        & (cleaned_df['surface'] == surface)
        & cleaned_df['winner_id'].isin(player_ids)
        & cleaned_df['loser_id'].isin(player_ids)
    ]
    if prior.empty:
        return {}

    w     = prior['winner_id'].astype(int)
    l     = prior['loser_id'].astype(int)
    tmp   = prior.assign(a_id=np.minimum(w, l), b_id=np.maximum(w, l),
                         a_won=(w < l).astype(int))
    grp   = tmp.groupby(['a_id', 'b_id'])

    a_wins_s    = grp['a_won'].sum()
    count_s     = grp.size()
    last_date_s = grp['tourney_date'].max()

    return {
        (int(idx[0]), int(idx[1])): {
            'A_wins':    int(a_wins),
            'B_wins':    int(count_s[idx] - a_wins),
            'last_date': last_date_s[idx],
        }
        for idx, a_wins in a_wins_s.items()
    }


def _h2h_values(h2h: dict, a_id: int, b_id: int,
                tourney_date: pd.Timestamp) -> tuple:
    """Return (A_wins, B_wins, days_since) for one player pair.

    Args:
        h2h: H2H lookup dict (a_id < b_id as keys).
        a_id: Lower player ID (player A).
        b_id: Higher player ID (player B).
        tourney_date: Tournament start date.
    Returns:
        Tuple (A_wins, B_wins, days_since). days_since = -1 if never met.
    """
    rec = h2h.get((a_id, b_id))
    if rec is None:
        return (0, 0, -1)
    last = rec['last_date']
    days = int((tourney_date - pd.to_datetime(last)).days) if last is not None else -1
    return (rec['A_wins'], rec['B_wins'], days)


# ── Feature construction ───────────────────────────────────────────────────────

def build_feature_row(
    a_id: int, b_id: int, round_label: str,
    info: dict, player_attrs: dict, h2h: dict,
) -> list:
    """Build one feature vector in FEATURES column order.

    a_id must be < b_id (lower ATP player ID = Player A, per project convention).

    Args:
        a_id: Player A ID (lower).
        b_id: Player B ID (higher).
        round_label: Current round (e.g. 'QF').
        info: Tournament info dict with surface_enc and level_enc added.
        player_attrs: Combined attrs dict from merge_player_attrs().
        h2h: H2H lookup from compute_h2h_lookup().
    Returns:
        List of feature values matching FEATURES order.
    """
    a        = player_attrs[a_id]
    b        = player_attrs[b_id]
    ah, bh, days = _h2h_values(h2h, a_id, b_id, info['date'])
    row = [
        info['surface_enc'], info['level_enc'],
        ROUND_ORD[round_label], info['best_of'],
        a['rank'], a['rank_pts'], a['seed'], a['age'], a['ht'], ah, a['hand_L'],
        b['rank'], b['rank_pts'], b['seed'], b['age'], b['ht'], bh, b['hand_L'],
        days,
        a['rank'] - b['rank'],
        a['rank_pts'] - b['rank_pts'],
        a.get('tourney_titles', 0),   a.get('tourney_win_rate', 0.0), a.get('tourney_matches', 0),
        b.get('tourney_titles', 0),   b.get('tourney_win_rate', 0.0), b.get('tourney_matches', 0),
    ]
    for col in LAGGED_STAT_COLS:
        row.append(a.get(col, np.nan))
    for col in LAGGED_STAT_COLS:
        row.append(b.get(col, np.nan))
    return row


# ── Simulation engine ──────────────────────────────────────────────────────────

def _simulate_collect(node, player_attrs: dict, predict_fn, rng,
                       matches: list):
    """Recursively simulate a bracket subtree and collect match results.

    Args:
        node: Match node, int (player_id), or 'BYE'.
        player_attrs: Combined player attrs dict.
        predict_fn: Callable(a_id, b_id, round_label) → P(a wins), a_id < b_id.
        rng: numpy random Generator.
        matches: Output list; each played match appends (round_label, winner, loser).
    Returns:
        Winner player_id or 'BYE'.
    """
    if node == 'BYE':
        return 'BYE'
    if isinstance(node, (int, np.integer)):
        return int(node)

    lw = _simulate_collect(node.left,  player_attrs, predict_fn, rng, matches)
    rw = _simulate_collect(node.right, player_attrs, predict_fn, rng, matches)

    if lw == 'BYE': return rw
    if rw == 'BYE': return lw

    a_id, b_id = (min(lw, rw), max(lw, rw))
    p_a        = predict_fn(a_id, b_id, node.round_label)
    a_wins     = rng.random() < p_a
    winner     = a_id if a_wins else b_id
    loser      = b_id if a_wins else a_id
    matches.append((node.round_label, winner, loser))
    return winner


def simulate_once(tree: Match, player_attrs: dict, predict_fn, rng) -> list:
    """Run one complete tournament simulation.

    Args:
        tree: Root bracket Match node.
        player_attrs: Combined player feature attrs dict.
        predict_fn: Callable(a_id, b_id, round_label) → P(a wins).
        rng: numpy random Generator.
    Returns:
        List of (round_label, winner_id, loser_id) for every match played.
    """
    matches = []
    champion = _simulate_collect(tree, player_attrs, predict_fn, rng, matches)
    if champion != 'BYE':
        matches.append(('W', champion, None))
    return matches


def _make_predict_fn(model, info: dict, player_attrs: dict, h2h: dict):
    """Return a memoised predict function scoped to this tournament.

    The cache avoids recomputing the same matchup in different rounds across
    multiple simulations.

    Args:
        model: Loaded XGBClassifier.
        info: Tournament info dict (must already contain surface_enc and level_enc).
        player_attrs: Combined player attrs dict.
        h2h: H2H lookup dict.
    Returns:
        Callable(a_id, b_id, round_label) → float.
    """
    cache = {}

    def predict(a_id: int, b_id: int, round_label: str) -> float:
        key = (a_id, b_id, round_label)
        if key not in cache:
            row = build_feature_row(a_id, b_id, round_label, info, player_attrs, h2h)
            X   = np.array(row, dtype=np.float32).reshape(1, -1)
            cache[key] = float(model.predict_proba(X)[0, 1])
        return cache[key]

    return predict


# ── Result compilation ─────────────────────────────────────────────────────────

def _resolve_player(name: str, draw_attrs: dict) -> int:
    """Find a player ID by case-insensitive substring or fuzzy name match.

    Args:
        name: Player name or partial name.
        draw_attrs: {player_id: {name: ...}} from extract_player_attrs().
    Returns:
        Matched player_id.
    Raises:
        ValueError: No match, or multiple matches with suggestions.
    """
    name_lower = name.lower()
    all_names  = {pid: attrs['name'] for pid, attrs in draw_attrs.items()}
    exact      = [pid for pid, n in all_names.items() if name_lower in n.lower()]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        raise ValueError(
            f"Multiple players match '{name}': "
            f"{[all_names[p] for p in exact]}"
        )
    name_list = list(all_names.values())
    close     = get_close_matches(name, name_list, n=3, cutoff=0.5)
    if close:
        raise ValueError(f"No player named '{name}'. Did you mean: {close}?")
    raise ValueError(
        f"No player named '{name}' found in this tournament draw. "
        "Check spelling and try again."
    )


def _compile_results(
    target_id: int, draw_attrs: dict, info: dict,
    sim_match_lists: list, n_sims: int,
) -> dict:
    """Aggregate per-simulation match records into summary statistics.

    Args:
        target_id: Target player ID.
        draw_attrs: Player attrs dict from extract_player_attrs().
        info: Tournament info dict.
        sim_match_lists: List of n_sims match-record lists from simulate_once().
        n_sims: Total simulations run.
    Returns:
        Dict with keys: target_id, target_name, tourney_info, round_probs,
        win_probability, opponent_counts, expected_exit, exit_distribution,
        draw_attrs, n_sims.
    """
    exit_counts    = Counter()
    round_reached  = Counter()
    opp_counts     = {r: Counter() for r in ROUND_LABELS}

    for sim in sim_match_lists:
        exit_rl = 'W'
        for rl, winner, loser in sim:
            if rl == 'W':
                continue
            if winner == target_id or loser == target_id:
                opp = loser if winner == target_id else winner
                opp_counts[rl][opp] += 1
            if loser == target_id:
                exit_rl = rl
        exit_counts[exit_rl] += 1
        exit_ord = ROUND_ORD.get(exit_rl, max(ROUND_ORD.values()) + 1)
        for rl in ROUND_LABELS:
            if ROUND_ORD[rl] <= exit_ord:
                round_reached[rl] += 1

    return {
        'target_id':        target_id,
        'target_name':      draw_attrs[target_id]['name'],
        'tourney_info':     info,
        'round_probs':      {r: round_reached[r] / n_sims for r in ROUND_LABELS},
        'win_probability':  exit_counts['W'] / n_sims,
        'opponent_counts':  opp_counts,
        'expected_exit':    exit_counts.most_common(1)[0][0],
        'exit_distribution': dict(exit_counts),
        'draw_attrs':       draw_attrs,
        'n_sims':           n_sims,
    }


# ── Main entry point ───────────────────────────────────────────────────────────

def run_simulation(
    tourney_name: str,
    year: int,
    target_name: str,
    n_sims: int = 5000,
    cleaned_path: Path = None,
    agg_path: Path = None,
    model_path: Path = None,
) -> dict:
    """Run N tournament simulations and return statistics for a target player.

    The model used was trained on seasons prior to the tournament year, so no
    future information leaks into predictions. The draw structure is taken from
    the actual historical match data for that tournament.

    Args:
        tourney_name: Partial tournament name (case-insensitive).
        year: Tournament year.
        target_name: Player name or partial name (case-insensitive).
        n_sims: Number of Monte Carlo simulations (default 5000).
        cleaned_path: Override cleaned matches CSV path.
        agg_path: Override aggregated stats CSV path.
        model_path: Override model JSON path.
    Returns:
        Dict of simulation results (see _compile_results).
    Raises:
        ValueError: Tournament or player not found, or name is ambiguous.
    """
    cleaned_df = load_cleaned(cleaned_path)
    agg_df     = pd.read_csv(agg_path or AGG_DIR / 'player_surface_year_stats.csv')
    model      = load_model(model_path)

    tourney_df = find_tournament(cleaned_df, tourney_name, year)
    info       = tournament_info(tourney_df)
    tree       = build_bracket_tree(tourney_df)
    draw_attrs = extract_player_attrs(tourney_df)
    target_id  = _resolve_player(target_name, draw_attrs)

    info['surface_enc'] = SURFACE_ENC.get(info['surface'], 0)
    info['level_enc']   = LEVEL_ENC.get(info['level'], 0)

    lagged       = build_lagged_stats(agg_df, year, info['surface'])
    tourney_hist = compute_tourney_history_lookup(
        cleaned_df, tree.all_players(), info['name'], info['date']
    )
    attrs   = merge_player_attrs(draw_attrs, lagged, tourney_hist)
    h2h     = compute_h2h_lookup(
        cleaned_df, tree.all_players(), info['surface'], info['date']
    )

    predict_fn = _make_predict_fn(model, info, attrs, h2h)
    rng        = np.random.default_rng(42)
    sim_lists  = [simulate_once(tree, attrs, predict_fn, rng) for _ in range(n_sims)]

    results = _compile_results(target_id, draw_attrs, info, sim_lists, n_sims)
    results['actual_path'] = get_actual_path(tourney_df, target_id)
    return results


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run ATP tournament simulation for a player.'
    )
    parser.add_argument('player',       help='Player name (partial ok)')
    parser.add_argument('tournament',   help='Tournament name (partial ok)')
    parser.add_argument('year',         type=int, help='Tournament year')
    parser.add_argument('--n-sims',     type=int, default=5000,
                        help='Number of simulations (default 5000)')
    parser.add_argument('--model-path', type=str, default=None,
                        help='Override model JSON path')
    args = parser.parse_args()

    try:
        results = run_simulation(
            tourney_name=args.tournament,
            year=args.year,
            target_name=args.player,
            n_sims=args.n_sims,
            model_path=Path(args.model_path) if args.model_path else None,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(results, indent=2, default=str))
