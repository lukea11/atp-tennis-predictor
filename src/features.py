import re
from collections import deque
import pandas as pd
from pathlib import Path

CLEAN_DIR = Path(__file__).parent.parent / "data" / "cleaned"
FEAT_DIR = Path(__file__).parent.parent / "data" / "features"
STRAIGHT_SETS_NEEDED = {3: 2, 5: 3}
MIN_SET_GAMES = 6          # minimum games won to count as a completed set
NO_STATS_RE = re.compile(r"RET|W/O")

# Tournament name (lowercase, stripped) → host country IOC code.
# None means no fixed host country (team events, rotating venues).
TOURNEY_COUNTRY = {
    'atp rio de janeiro':    'BRA',
    'rio de janeiro':        'BRA',
    'rio de janeiro':        'BRA',
    'acapulco':              'MEX',
    'adelaide':              'AUS',
    'adelaide 1':            'AUS',
    'adelaide 2':            'AUS',
    'antalya':               'TUR',
    'antwerp':               'BEL',
    'astana':                'KAZ',
    'atlanta':               'USA',
    'atp cup':               'AUS',
    'auckland':              'NZL',
    'australian open':       'AUS',
    'banja luka':            'BIH',
    'barcelona':             'ESP',
    'basel':                 'SUI',
    'bastad':                'SWE',
    'beijing':               'CHN',
    'belgrade':              'SRB',
    'belgrade 2':            'SRB',
    'brisbane':              'AUS',
    'bucharest':             'ROU',
    'budapest':              'HUN',
    'buenos aires':          'ARG',
    'cagliari':              'ITA',
    'canada masters':        'CAN',
    'chengdu':               'CHN',
    'cincinnati masters':    'USA',
    'cologne 1':             'GER',
    'cologne 2':             'GER',
    'cordoba':               'ARG',
    'dallas':                'USA',
    'delray beach':          'USA',
    'doha':                  'QAT',
    'dubai':                 'UAE',
    'eastbourne':            'GBR',
    'estoril':               'POR',
    'florence':              'ITA',
    'geneva':                'SUI',
    'gijon':                 'ESP',
    'great ocean road open': 'AUS',
    'gstaad':                'SUI',
    'halle':                 'GER',
    'hamburg':               'GER',
    'hong kong':             'HKG',
    'houston':               'USA',
    'indian wells masters':  'USA',
    'istanbul':              'TUR',
    'kitzbuhel':             'AUT',
    'laver cup':             None,
    'los cabos':             'MEX',
    'lyon':                  'FRA',
    'madrid masters':        'ESP',
    'mallorca':              'ESP',
    'marbella':              'ESP',
    'marrakech':             'MAR',
    'marseille':             'FRA',
    'melbourne':             'AUS',
    'metz':                  'FRA',
    'miami masters':         'USA',
    'monte carlo masters':   'MON',
    'montpellier':           'FRA',
    'moscow':                'RUS',
    'munich':                'GER',
    'murray river open':     'AUS',
    'naples':                'ITA',
    'new york':              'USA',
    'newport':               'USA',
    'nextgen finals':        'ITA',
    'nur-sultan':            'KAZ',
    'paris masters':         'FRA',
    'parma':                 'ITA',
    'pune':                  'IND',
    "queen's club":          'GBR',
    'quito':                 'ECU',
    'roland garros':         'FRA',
    'rome masters':          'ITA',
    'rotterdam':             'NED',
    'san diego':             'USA',
    'santiago':              'CHI',
    'sao paulo':             'BRA',
    'sardinia':              'ITA',
    'seoul':                 'KOR',
    'shanghai masters':      'CHN',
    'shenzhen':              'CHN',
    'singapore':             'SGP',
    'sofia':                 'BUL',
    'st petersburg':         'RUS',
    'st. petersburg':        'RUS',
    'stockholm':             'SWE',
    'stuttgart':             'GER',
    'sydney':                'AUS',
    'tel aviv':              'ISR',
    'tokyo':                 'JPN',
    'tokyo olympics':        'JPN',
    'tour finals':           'GBR',
    'us open':               'USA',
    'umag':                  'CRO',
    'united cup':            'AUS',
    'vienna':                'AUT',
    'washington':            'USA',
    'wimbledon':             'GBR',
    'winston-salem':         'USA',
    'zhuhai':                'CHN',
    's hertogenbosch':       'NED',
}


# ── Service / return game metrics ─────────────────────────────────────────────

def add_service_return_games(df: pd.DataFrame) -> pd.DataFrame:
    """Add per-match service and return game counts.

    RET and W/O matches are set to NaN (match not completed).
    New columns: w_rtnWon, l_rtnWon, w_rtnGms, l_rtnGms, w_SvGmsWon, l_SvGmsWon.

    Args:
        df: Match DataFrame.
    Returns:
        DataFrame with 6 new columns appended.
    """
    retired = df["score"].str.contains(NO_STATS_RE, na=False)
    df["w_rtnWon"]   = (df["l_bpFaced"] - df["l_bpSaved"]).where(~retired)
    df["l_rtnWon"]   = (df["w_bpFaced"] - df["w_bpSaved"]).where(~retired)
    df["w_rtnGms"]   = df["l_SvGms"].where(~retired)
    df["l_rtnGms"]   = df["w_SvGms"].where(~retired)
    df["w_SvGmsWon"] = (df["w_SvGms"] - df["l_rtnWon"]).where(~retired)
    df["l_SvGmsWon"] = (df["l_SvGms"] - df["w_rtnWon"]).where(~retired)
    return df


# ── Tiebreaks ─────────────────────────────────────────────────────────────────

def count_tiebreaks(score: str) -> tuple:
    """Count tiebreaks won by winner and loser from a score string.

    '7-6' in score → winner won that tiebreak.
    '6-7' in score → loser won that tiebreak.

    Args:
        score: Raw score string (e.g. '7-6(5) 6-4 7-6(3)').
    Returns:
        Tuple (winner_tiebreaks, loser_tiebreaks).
    """
    if not isinstance(score, str):
        return (0, 0)
    return (len(re.findall(r"7-6", score)), len(re.findall(r"6-7", score)))


def add_tiebreaks(df: pd.DataFrame) -> pd.DataFrame:
    """Add w_tiebreaks_won and l_tiebreaks_won columns.

    Args:
        df: Match DataFrame with a 'score' column.
    Returns:
        DataFrame with two new tiebreak columns.
    """
    tbs = df["score"].apply(count_tiebreaks)
    df["w_tiebreaks_won"] = tbs.apply(lambda x: x[0])
    df["l_tiebreaks_won"] = tbs.apply(lambda x: x[1])
    return df


# ── Sets played ───────────────────────────────────────────────────────────────

def count_sets(score: str, best_of: int) -> int:
    """Count completed sets in a match score string.

    A set is complete when at least one player reached MIN_SET_GAMES games.
    Partial sets (e.g. '2-0', '0-0') and non-score tokens are excluded.

    Args:
        score: Raw score string (e.g. '6-1 2-6 7-6 5-7 0-0 RET').
        best_of: Maximum sets in the match (3 or 5).
    Returns:
        Number of completed sets, capped at best_of.
    """
    if not isinstance(score, str):
        return 0
    clean = re.sub(r"\(\d+\)", "", score)
    completed = 0
    for token in clean.split():
        m = re.match(r"^(\d+)-(\d+)$", token)
        if m and max(int(m.group(1)), int(m.group(2))) >= MIN_SET_GAMES:
            completed += 1
    return min(completed, best_of)


def add_sets_played(df: pd.DataFrame) -> pd.DataFrame:
    """Add sets_played column derived from the score string.

    Args:
        df: Match DataFrame with 'score' and 'best_of' columns.
    Returns:
        DataFrame with 'sets_played' column added.
    """
    df["sets_played"] = df.apply(
        lambda r: count_sets(r["score"], r["best_of"]), axis=1
    )
    return df


# ── Straight sets / retirement ────────────────────────────────────────────────

def add_loser_retired(df: pd.DataFrame) -> pd.DataFrame:
    """Add loser_retired column: 1 if match ended via RET or W/O, else 0.

    Args:
        df: Match DataFrame with a 'score' column.
    Returns:
        DataFrame with 'loser_retired' column added.
    """
    df["loser_retired"] = df["score"].str.contains(NO_STATS_RE, na=False).astype(int)
    return df


def add_straight_sets(df: pd.DataFrame) -> pd.DataFrame:
    """Add straight_sets_win: 1 if winner won without dropping a set.

    Retirement/walkover matches are never counted as straight-set wins.
    Requires 'sets_played', 'best_of', and 'loser_retired' columns.

    Args:
        df: Enriched match DataFrame.
    Returns:
        DataFrame with 'straight_sets_win' column added.
    """
    sets_needed = df["best_of"].map(STRAIGHT_SETS_NEEDED)
    completed = df["loser_retired"] == 0
    df["straight_sets_win"] = (
        (df["sets_played"] == sets_needed) & completed
    ).astype(int)
    return df


# ── H2H helpers ───────────────────────────────────────────────────────────────

def _lookup_h2h(db: dict, key: tuple, match_date: pd.Timestamp) -> tuple:
    """Return prior H2H record for a (player_A, player_B, surface) key.

    Args:
        db: H2H state dict keyed by (player_A, player_B, surface).
        key: Lookup key.
        match_date: Date of the current match.
    Returns:
        Tuple (A_wins, B_wins, days_since_last_h2h).
        days = -1 if no prior head-to-head exists.
    """
    if key not in db:
        return (0, 0, -1)
    rec = db[key]
    return (rec["A_wins"], rec["B_wins"], (match_date - rec["last_date"]).days)


def _update_h2h(
    db: dict, key: tuple, winner_is_a: bool, match_date: pd.Timestamp
) -> None:
    """Update H2H database with the result of a completed match.

    Args:
        db: H2H state dict keyed by (player_A, player_B, surface).
        key: (player_A, player_B, surface) tuple.
        winner_is_a: True if player_A (lower ID) won.
        match_date: Date of the match.
    """
    if key not in db:
        db[key] = {"matches": 0, "A_wins": 0, "B_wins": 0, "last_date": None}
    rec = db[key]
    rec["matches"] += 1
    rec["A_wins" if winner_is_a else "B_wins"] += 1
    rec["last_date"] = match_date


# ── H2H main ──────────────────────────────────────────────────────────────────

def compute_h2h(dfs: list) -> tuple:
    """Compute time-aware, surface-specific H2H features for all matches.

    Records the H2H state *before* each match (true look-back, no leakage).
    Matches are sorted by tourney_date then match_num so within-tournament
    order is respected. H2H is surface-specific: only prior meetings on the
    same surface count.

    Args:
        dfs: List of yearly cleaned match DataFrames.
    Returns:
        Tuple (enriched_df, h2h_database_df).
        enriched_df gains: winner_h2h, loser_h2h, days_since_h2h.
        h2h_database_df columns:
            player_A, player_B, surface, matches, A_wins, B_wins, last_match_date.
    """
    df = (
        pd.concat(dfs, ignore_index=True)
        .assign(tourney_date=lambda d: pd.to_datetime(d["tourney_date"]))
        .sort_values(["tourney_date", "match_num"])
        .reset_index(drop=True)
    )
    db = {}
    w_h2h, l_h2h, days_list = [], [], []

    for _, row in df.iterrows():
        w_id, l_id = int(row["winner_id"]), int(row["loser_id"])
        a_id, b_id = (w_id, l_id) if w_id < l_id else (l_id, w_id)
        winner_is_a = w_id < l_id
        key = (a_id, b_id, row["surface"])
        date = row["tourney_date"]

        a_wins, b_wins, days = _lookup_h2h(db, key, date)
        w_h2h.append(a_wins if winner_is_a else b_wins)
        l_h2h.append(b_wins if winner_is_a else a_wins)
        days_list.append(days)
        _update_h2h(db, key, winner_is_a, date)

    df["winner_h2h"]    = w_h2h
    df["loser_h2h"]     = l_h2h
    df["days_since_h2h"] = days_list

    h2h_db = pd.DataFrame([
        {
            "player_A": k[0], "player_B": k[1], "surface": k[2],
            "matches": v["matches"], "A_wins": v["A_wins"], "B_wins": v["B_wins"],
            "last_match_date": v["last_date"],
        }
        for k, v in db.items()
    ])
    return df, h2h_db


# ── Tournament history ────────────────────────────────────────────────────────

def compute_tourney_history(df: pd.DataFrame) -> pd.DataFrame:
    """Add per-player prior tournament history features (no leakage).

    For each match, records how many matches the player has won, how many
    titles they have won, and how many total matches they have played at
    this specific tournament in prior appearances. State is captured BEFORE
    the match so there is no leakage.

    Requires df to be sorted by (tourney_date, match_num) — this is already
    guaranteed when called after compute_h2h.

    Args:
        df: Match DataFrame sorted by tourney_date, match_num.
    Returns:
        df copy with 6 new columns:
            winner/loser × tourney_wins / tourney_titles / tourney_matches.
    """
    db = {}   # {(player_id, tourney_name): {wins, titles, matches}}
    w_wins, l_wins       = [], []
    w_titles, l_titles   = [], []
    w_matches, l_matches = [], []

    for _, row in df.iterrows():
        t    = row['tourney_name']
        w_id = int(row['winner_id'])
        l_id = int(row['loser_id'])
        wk, lk = (w_id, t), (l_id, t)

        ws = db.get(wk, {'wins': 0, 'titles': 0, 'matches': 0})
        ls = db.get(lk, {'wins': 0, 'titles': 0, 'matches': 0})

        w_wins.append(ws['wins']);    l_wins.append(ls['wins'])
        w_titles.append(ws['titles']); l_titles.append(ls['titles'])
        w_matches.append(ws['matches']); l_matches.append(ls['matches'])

        if wk not in db:
            db[wk] = {'wins': 0, 'titles': 0, 'matches': 0}
        if lk not in db:
            db[lk] = {'wins': 0, 'titles': 0, 'matches': 0}

        db[wk]['wins']    += 1
        db[wk]['matches'] += 1
        db[lk]['matches'] += 1
        if row['round'] == 'F':
            db[wk]['titles'] += 1

    df = df.copy()
    df['winner_tourney_wins']    = w_wins
    df['loser_tourney_wins']     = l_wins
    df['winner_tourney_titles']  = w_titles
    df['loser_tourney_titles']   = l_titles
    df['winner_tourney_matches'] = w_matches
    df['loser_tourney_matches']  = l_matches
    return df


# ── Home advantage ────────────────────────────────────────────────────────────

def compute_home_advantage(df: pd.DataFrame) -> pd.DataFrame:
    """Add binary home-advantage columns using player nationality vs host country.

    Looks up each tournament's host IOC code from TOURNEY_COUNTRY and compares
    against winner_ioc / loser_ioc. 1 = player is playing in their home country.
    Unknown or neutral-venue tournaments produce 0 for both players.

    Args:
        df: Match DataFrame with tourney_name, winner_ioc, loser_ioc columns.
    Returns:
        df copy with winner_is_home and loser_is_home columns added.
    """
    host = df['tourney_name'].str.strip().str.lower().map(TOURNEY_COUNTRY)
    df = df.copy()
    df['winner_is_home'] = (df['winner_ioc'] == host).astype(int)
    df['loser_is_home']  = (df['loser_ioc']  == host).astype(int)
    return df


# ── Form / momentum ───────────────────────────────────────────────────────────

def compute_form_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add rolling pre-match form features for both players (no leakage).

    Tracks three signals for each player before each match:
      win_streak         — overall consecutive wins (resets on any loss)
      win_streak_surface — consecutive wins on this surface (resets on loss
                           OR when the player switches to a different surface)
      wins_last5         — wins in last 5 matches regardless of surface (0–5)

    Requires df sorted by (tourney_date, match_num) — already guaranteed
    when called after compute_h2h.

    Args:
        df: Match DataFrame sorted by tourney_date, match_num.
    Returns:
        df copy with 6 new columns:
            winner/loser × win_streak / win_streak_surface / wins_last5.
    """
    db = {}   # {player_id: {streak, last_surface, streak_surface, last5}}

    w_streak,   l_streak   = [], []
    w_streak_s, l_streak_s = [], []
    w_last5,    l_last5    = [], []

    for _, row in df.iterrows():
        w_id    = int(row['winner_id'])
        l_id    = int(row['loser_id'])
        surface = row['surface']

        for pid in (w_id, l_id):
            if pid not in db:
                db[pid] = {
                    'streak':         0,
                    'last_surface':   None,
                    'streak_surface': 0,
                    'last5':          deque(maxlen=5),
                }

        ws = db[w_id]
        ls = db[l_id]

        # Record pre-match state (leakage-free)
        w_streak.append(ws['streak'])
        l_streak.append(ls['streak'])
        w_streak_s.append(ws['streak_surface'] if ws['last_surface'] == surface else 0)
        l_streak_s.append(ls['streak_surface'] if ls['last_surface'] == surface else 0)
        w_last5.append(sum(ws['last5']))
        l_last5.append(sum(ls['last5']))

        # Update winner
        ws['streak'] += 1
        ws['streak_surface'] = (ws['streak_surface'] + 1) if ws['last_surface'] == surface else 1
        ws['last_surface'] = surface
        ws['last5'].append(1)

        # Update loser (loss resets both streaks; surface still recorded)
        ls['streak']         = 0
        ls['streak_surface'] = 0
        ls['last_surface']   = surface
        ls['last5'].append(0)

    df = df.copy()
    df['winner_win_streak']         = w_streak
    df['loser_win_streak']          = l_streak
    df['winner_win_streak_surface'] = w_streak_s
    df['loser_win_streak_surface']  = l_streak_s
    df['winner_wins_last5']         = w_last5
    df['loser_wins_last5']          = l_last5
    return df


# ── Pipeline ──────────────────────────────────────────────────────────────────

def add_features(dfs: list) -> tuple:
    """Run all feature engineering steps on a list of yearly DataFrames.

    Order: H2H → tourney history → home advantage → form features
           → loser_retired → service/return games → tiebreaks → sets played
           → straight sets.

    Args:
        dfs: List of yearly cleaned match DataFrames (2018–2024).
    Returns:
        Tuple (feature_df, h2h_database_df).
    """
    df, h2h_db = compute_h2h(dfs)
    df = compute_tourney_history(df)
    df = compute_home_advantage(df)
    df = compute_form_features(df)
    df = add_loser_retired(df)
    df = add_service_return_games(df)
    df = add_tiebreaks(df)
    df = add_sets_played(df)
    df = add_straight_sets(df)
    return df, h2h_db


def save_features(df: pd.DataFrame, h2h_db: pd.DataFrame) -> None:
    """Save feature DataFrame and H2H database to data/features/.

    Args:
        df: Enriched match DataFrame.
        h2h_db: H2H database DataFrame.
    """
    FEAT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(FEAT_DIR / "atp_features.csv", index=False)
    h2h_db.to_csv(FEAT_DIR / "h2h_database.csv", index=False)


if __name__ == "__main__":
    clean = pd.read_csv(CLEAN_DIR / "atp_matches_cleaned.csv")
    df, h2h_db = add_features([clean])
    save_features(df, h2h_db)
    print(f"Features: {df.shape[0]:,} rows, {df.shape[1]} columns")
    print(f"H2H database: {len(h2h_db):,} player-pair-surface combinations")
