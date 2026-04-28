# ATP Match Prediction — Signal Report

**Generated:** 2026-04-28  
**Model:** XGBoost | decay_rate=1.0 | max_depth=4 | min_child_weight=5 | learning_rate=0.05  
**Val AUC (2024):** 0.7126 | **Val Accuracy:** 63.98% | **Best iteration:** 78 trees

---

## What is Decision Weight?

Decision weight (%) measures how much of the model's total predictive power comes from each signal. Out of every 100 decisions the model makes about who wins, this is roughly how many were primarily driven by that feature. Technically it is the share of total XGBoost information gain — how much each feature narrows down the likely winner across all splits in all trees.

---

## Top 20 Signals

| Rank | Feature | Decision Weight | Category | What it means in tennis |
|------|---------|----------------|----------|--------------------------|
| 1 | `rank_pts_diff` | 10.26% | Matchup Comparison | The relative ranking points gap — more predictive than either player's absolute points alone |
| 2 | `rank_diff` | 4.71% | Matchup Comparison | The relative ATP ranking gap — the lower-ranked player wins ~35% of matches |
| 3 | `A_rank_pts` | 2.36% | Rankings & Seeding | Player A's rolling 12-month points — reflects recent results before the ranking number catches up |
| 4 | `sv_gms_won_pct_A` | 2.19% | Serve Performance | Player A service hold rate — the baseline that keeps a player in every set on this surface |
| 5 | `completed_winrate_A` | 2.07% | Win Rate Signals | Player A win rate in fully completed matches — removes free wins against retired opponents |
| 6 | `win_rate_A` | 2.02% | Win Rate Signals | Player A overall win rate on this surface the prior year |
| 7 | `B_h2h_last5` | 1.99% | Head-to-Head | Player B wins in last 5 H2H meetings (any surface) — recent rivalry momentum |
| 8 | `B_wins_last5` | 1.95% | Form & Momentum | Player B wins in last 5 matches — current form entering this match |
| 9 | `matches_played_B` | 1.78% | Form & Health | Player B matches played on this surface last year — experience and conditioning indicator |
| 10 | `A_tourney_win_rate` | 1.77% | Tournament History | Player A historical win rate at this tournament (2018+, Bayesian-smoothed) |
| 11 | `win_rate_B` | 1.73% | Win Rate Signals | Player B overall win rate on this surface the prior year |
| 12 | `A_h2h_last5` | 1.71% | Head-to-Head | Player A wins in last 5 H2H meetings (any surface) |
| 13 | `A_rank` | 1.70% | Rankings & Seeding | Player A's current ATP world ranking at match time |
| 14 | `rtn_win_pct_B` | 1.69% | Return Performance | Player B return-game win rate — how frequently B breaks serve on this surface |
| 15 | `B_rank_pts` | 1.68% | Rankings & Seeding | Player B's rolling 12-month ranking points |
| 16 | `A_wins_last5` | 1.67% | Form & Momentum | Player A wins in last 5 matches — current form entering this match |
| 17 | `B_seed` | 1.61% | Rankings & Seeding | Player B seeding in this draw — confirms elite placement and bracket position |
| 18 | `matches_played_A` | 1.61% | Form & Health | Player A matches played on this surface last year |
| 19 | `B_win_streak` | 1.61% | Form & Momentum | Player B's current consecutive win streak entering this match |
| 20 | `B_age` | 1.55% | Player Profile | Player B age — affects stamina and peak physical window, most pronounced in best-of-5 |

---

## All Signals

Ordered by decision weight descending. Features marked **0.00%** were present in the model but assigned zero importance — not used in any tree split (redundant given other features).

### Matchup Comparison

| Feature | Long Name | Decision Weight | Definition | Why It Matters |
|---------|-----------|----------------|------------|----------------|
| `rank_pts_diff` | Ranking Points Gap | **10.26%** | Player A's ranking points minus Player B's ranking points | The single most predictive signal — the relative points gap directly measures the quality difference; what matters is not a player's absolute points, but how many more they have than their opponent |
| `rank_diff` | ATP Ranking Gap | **4.71%** | Player A's ATP ranking minus Player B's ranking | The relative ranking gap is more predictive than either player's absolute rank alone — what matters is not that you're ranked 50, but that you're ranked 50 vs an opponent at 120 |

### Rankings & Seeding

| Feature | Long Name | Decision Weight | Definition | Why It Matters |
|---------|-----------|----------------|------------|----------------|
| `A_rank_pts` | Player A Ranking Points | **2.36%** | Player A's rolling 12-month ranking points total | Points reflect earned results continuously; a player who just won a major has high points before the ranking ladder moves, making this a more current form signal than rank alone |
| `A_rank` | Player A ATP Ranking | **1.70%** | Player A's current ATP world ranking at match time | The best objective summary of overall quality — aggregates results across all surfaces over 52 weeks |
| `B_rank_pts` | Player B Ranking Points | **1.68%** | Player B's rolling 12-month ranking points total | Same as A_rank_pts for the opponent — particularly useful for players on a hot run whose official rank hasn't caught up yet |
| `B_seed` | Player B Tournament Seed | **1.61%** | Player B's seeding in this tournament draw | Confirms elite status within this specific draw and determines placement — seeded players avoid each other until late rounds |
| `A_seed` | Player A Tournament Seed | **1.41%** | Player A's seeding in this tournament draw | Same as B_seed for Player A |
| `B_rank` | Player B ATP Ranking | **1.34%** | Player B's current ATP world ranking at match time | Same as A_rank for the opponent |

### Win Rate Signals (lagged — prior year, same surface)

| Feature | Long Name | Decision Weight | Definition | Why It Matters |
|---------|-----------|----------------|------------|----------------|
| `completed_winrate_A` | Player A Completed-Match Win Rate | **2.07%** | Player A's win rate in fully completed matches only | A cleaner quality signal — removes free wins where the opponent retired injured |
| `win_rate_A` | Player A Surface Win Rate | **2.02%** | % of matches Player A won on this surface the prior year | Overall surface-specific form over a full season |
| `win_rate_B` | Player B Surface Win Rate | **1.73%** | % of matches Player B won on this surface the prior year | Same for the opponent |
| `completed_winrate_B` | Player B Completed-Match Win Rate | **1.52%** | Player B's win rate in fully completed matches only | Same for the opponent |
| `strsets_rate_B` | Player B Straight-Sets Win Rate | **1.19%** | % of Player B's wins won in straight sets | A player who frequently drops sets even in wins is vulnerable — opponents who push them know there's a chance |
| `strsets_rate_A` | Player A Straight-Sets Win Rate | **1.15%** | % of Player A's wins won in straight sets | Dominance indicator — winning without dropping a set means the player was never in real danger |

### Serve Performance (lagged — prior year, same surface)

| Feature | Long Name | Decision Weight | Definition | Why It Matters |
|---------|-----------|----------------|------------|----------------|
| `sv_gms_won_pct_A` | Player A Service Hold Rate | **2.19%** | % of service games Player A held on this surface the prior year | The most direct measure of serve dominance — breaking serve happens only ~25% of the time in ATP tennis, so a reliable hold keeps a player in every set |
| `df_rate_A` | Player A Double-Fault Rate | **1.49%** | Double faults per serve point for Player A | Unforced serve errors — doubles are free gifts to the opponent and often appear under pressure |
| `sv_gms_won_pct_B` | Player B Service Hold Rate | **1.43%** | % of service games Player B held on this surface the prior year | Same for the opponent — a player who frequently loses serve is under constant pressure |
| `first_serve_win_pct_A` | Player A First-Serve Points Won | **1.41%** | % of points Player A won when first serve landed in | Quality of the first delivery — a high value means the first serve is a genuine weapon that forces a weak return |
| `ace_rate_A` | Player A Ace Rate | **1.41%** | Aces per serve point for Player A | Free point generation — aces win points without the opponent touching the ball |
| `first_serve_pct_B` | Player B First-Serve In Rate | **1.41%** | % of Player B's first serves that landed in | Consistency of the delivery — erratic first serves force repeated second balls |
| `first_serve_pct_A` | Player A First-Serve In Rate | **1.35%** | % of Player A's first serves that landed in | Same for Player A |
| `first_serve_win_pct_B` | Player B First-Serve Points Won | **1.25%** | % of points Player B won when first serve landed in | Same as first_serve_win_pct_A for the opponent |
| `df_rate_B` | Player B Double-Fault Rate | **1.23%** | Double faults per serve point for Player B | Same as df_rate_A for the opponent |
| `second_serve_win_pct_A` | Player A Second-Serve Points Won | **1.21%** | % of points Player A won on second serve | Resilience under pressure — players who still win second-serve points prevent opponents from teeing off |
| `bp_save_pct_B` | Player B Break-Point Save Rate | **1.16%** | % of break points Player B saved | Clutch performance under maximum serve pressure — saving break points in the biggest moments keeps sets alive |
| `second_serve_win_pct_B` | Player B Second-Serve Points Won | **1.14%** | % of points Player B won on second serve | Same for the opponent |
| `bp_save_pct_A` | Player A Break-Point Save Rate | **0.99%** | % of break points Player A saved | Same as bp_save_pct_B for Player A |
| `ace_rate_B` | Player B Ace Rate | **1.08%** | Aces per serve point for Player B | Facing a high-ace server forces the returner to take more risks |

### Return Performance (lagged — prior year, same surface)

| Feature | Long Name | Decision Weight | Definition | Why It Matters |
|---------|-----------|----------------|------------|----------------|
| `rtn_win_pct_B` | Player B Return-Game Win Rate | **1.69%** | % of return games Player B won (i.e. breaks secured) | Offensive pressure on the opponent's serve — great returners turn the most passive position in tennis into a weapon |
| `rtn_win_pct_A` | Player A Return-Game Win Rate | **1.31%** | % of return games Player A won | Same for Player A |
| `tiebreaks_winrate_A` | Player A Tiebreak Win Rate | **1.19%** | % of tiebreaks Player A won | Mental toughness at 6-6 — tiebreaks remove technical advantage and come down to nerve |
| `tiebreaks_winrate_B` | Player B Tiebreak Win Rate | **1.08%** | % of tiebreaks Player B won | Same for the opponent |

### Head-to-Head

| Feature | Long Name | Decision Weight | Definition | Why It Matters |
|---------|-----------|----------------|------------|----------------|
| `B_h2h_last5` | Player B H2H Last 5 (Overall) | **1.99%** | Player B wins in last 5 head-to-head meetings across all surfaces | Recent rivalry momentum — captures current-form matchup dynamics rather than a career total that may include years-old results |
| `A_h2h_last5` | Player A H2H Last 5 (Overall) | **1.71%** | Player A wins in last 5 head-to-head meetings across all surfaces | Same for Player A — both H2H last-5 features debuted in the top 15 by gain, outranking all cumulative H2H counts |
| `days_since_h2h` | Days Since Last Meeting | **0.95%** | Days since their last surface-specific meeting (-1 if never met) | Freshness of H2H information — a meeting last month is more informative than one five years ago |
| `B_h2h_last5_surface` | Player B H2H Last 5 (Surface) | **0.95%** | Player B wins in last 5 head-to-head meetings on this specific surface | Surface-filtered version — more precise but sparse for players who rarely meet on the same surface |
| `B_h2h` | Player B H2H Wins (Surface, Cumulative) | **0.51%** | Player B's total prior wins vs Player A on this surface | Career surface-specific total — now largely superseded by the last-5 features |
| `A_h2h` | Player A H2H Wins (Surface, Cumulative) | **0.00%** | Player A's total prior wins vs Player B on this surface | Assigned zero weight — information already captured by rank_diff and the h2h_last5 features |
| `A_h2h_last5_surface` | Player A H2H Last 5 (Surface) | **0.00%** | Player A wins in last 5 surface-specific meetings | Assigned zero weight — sparse for many pairs; B_h2h_last5_surface carries the surface signal |

### Form & Momentum

| Feature | Long Name | Decision Weight | Definition | Why It Matters |
|---------|-----------|----------------|------------|----------------|
| `B_wins_last5` | Player B Wins in Last 5 | **1.95%** | Player B wins in last 5 matches across all surfaces | Most immediate form indicator — confidence and physical readiness right now |
| `A_wins_last5` | Player A Wins in Last 5 | **1.67%** | Player A wins in last 5 matches across all surfaces | Same for Player A |
| `B_win_streak` | Player B Win Streak | **1.61%** | Player B's current consecutive overall win count | Momentum — a player on a 10-match run is in a different psychological state than one who just lost |
| `A_win_streak_surface` | Player A Surface Win Streak | **1.41%** | Player A's consecutive wins on this surface (resets on loss OR surface change) | Surface-specific hot streak — winning 8 straight on clay proves current mastery of these specific conditions |
| `B_win_streak_surface` | Player B Surface Win Streak | **1.22%** | Player B's consecutive wins on this surface | Same for the opponent |
| `A_win_streak` | Player A Win Streak | **0.93%** | Player A's current consecutive overall win count | Same as B_win_streak for Player A — ranked lower because A_win_streak_surface is more precise |

### Tournament History (cumulative, 2018 onward)

> **Data limitation:** titles and matches won before 2018 are not visible to the model. For players with long careers (Djokovic, Nadal, Federer), the model undercounts their true tournament mastery. Always note the 2018 cutoff when citing these features.

| Feature | Long Name | Decision Weight | Definition | Why It Matters |
|---------|-----------|----------------|------------|----------------|
| `A_tourney_win_rate` | Player A Tournament Win Rate | **1.77%** | Player A's Bayesian-smoothed match win rate at this specific tournament (2018+) | Deeper than titles — a player who consistently reaches the QF without winning still has high win rate, reflecting genuine venue affinity |
| `A_tourney_matches` | Player A Tournament Experience | **1.17%** | Total matches Player A has played at this tournament (2018+) | A player with 40+ matches here has handled the scheduling, courts, and crowd pressure many times |
| `B_tourney_matches` | Player B Tournament Experience | **1.17%** | Same as A_tourney_matches for the opponent | Particularly relevant for first-time Grand Slam participants facing logistical novelty |
| `A_tourney_titles` | Player A Tournament Titles | **1.16%** | Number of times Player A has won this tournament (2018+) | The clearest signal of venue-specific mastery — winning a tournament multiple times reflects genuine dominance of its unique conditions |
| `B_tourney_win_rate` | Player B Tournament Win Rate | **0.95%** | Player B's Bayesian-smoothed match win rate at this tournament (2018+) | Same as A_tourney_win_rate for the opponent |
| `B_tourney_titles` | Player B Tournament Titles | **0.00%** | Number of times Player B has won this tournament (2018+) | Assigned zero weight — B_tourney_win_rate captures the same information more continuously |

### Home Advantage

| Feature | Long Name | Decision Weight | Definition | Why It Matters |
|---------|-----------|----------------|------------|----------------|
| `B_is_home` | Player B Home Advantage | **0.97%** | 1 if Player B is playing in their home country, 0 otherwise | Home crowd support increases pressure on the away player, particularly in deciding moments — the model detects this on the opponent side |
| `A_is_home` | Player A Home Advantage | **0.00%** | 1 if Player A is playing in their home country, 0 otherwise | Assigned zero weight — when the home player is Player A (lower ID), the ranking advantage already absorbs most of the signal |

### Form & Health (lagged — prior year, same surface)

| Feature | Long Name | Decision Weight | Definition | Why It Matters |
|---------|-----------|----------------|------------|----------------|
| `matches_played_B` | Player B Matches Played | **1.78%** | Total matches Player B played on this surface the prior year | Experience and conditioning — a player with 40+ clay matches has deep surface-specific preparation vs someone with 8 |
| `rank_improvement_B` | Player B Ranking Improvement | **1.42%** | Player B's ranking improvement over the prior year | Trajectory — a rising player is gaining confidence and beating players they previously couldn't |
| `matches_played_A` | Player A Matches Played | **1.61%** | Total matches Player A played on this surface the prior year | Same for Player A |
| `injured_during_swing_B` | Player B Back-from-Absence Score | **1.35%** | Score 0–1: how recently Player B returned from a retirement/walkover | Injury recency penalty — a player returning within weeks may still be managing pain; notably the model weights opponent injury more than own injury |
| `rank_improvement_A` | Player A Ranking Improvement | **1.35%** | Player A's ranking improvement over the prior year | Same for Player A |
| `injured_during_swing_A` | Player A Back-from-Absence Score | **0.00%** | Score 0–1: how recently Player A returned from a retirement/walkover | Assigned zero weight — the model finds opponent injury (B side) more predictive than own injury (A side) |

### Player Profile

| Feature | Long Name | Decision Weight | Definition | Why It Matters |
|---------|-----------|----------------|------------|----------------|
| `B_age` | Player B Age | **1.55%** | Player B's age in years at time of match | Affects stamina and peak physical window — most pronounced in best-of-5 Grand Slams where older players fade in the fifth set |
| `A_ht` | Player A Height | **1.37%** | Player A's height in cm | Taller players generate more serve leverage (higher contact point, sharper angles), especially on faster surfaces |
| `hand_B_L` | Player B Left-Handed | **1.27%** | Binary: 1 if Player B is left-handed | Left-handers have a tactical advantage — their wide serve and spin patterns are unfamiliar to most opponents |
| `B_ht` | Player B Height | **1.25%** | Player B's height in cm | Same for the opponent |
| `A_age` | Player A Age | **1.13%** | Player A's age in years at time of match | Same as B_age for Player A |
| `hand_A_L` | Player A Left-Handed | **1.01%** | Binary: 1 if Player A is left-handed | Same as hand_B_L for Player A |

### Match Context

| Feature | Long Name | Decision Weight | Definition | Why It Matters |
|---------|-----------|----------------|------------|----------------|
| `best_of` | Best-of Format | **1.37%** | Best-of-3 or Best-of-5 matches | Longer matches disproportionately favour fitter, more consistent players — upsets are significantly rarer in best-of-5 |
| `round_ord` | Tournament Round | **1.12%** | Ordinal round (R128=1 … Final=7) | Later rounds mean stronger opponents and accumulated fatigue |
| `surface_enc` | Surface | **0.86%** | Encoded surface: Hard=0, Clay=1, Grass=2 | Low weight because surface is already captured implicitly in all lagged stats, which are surface-specific by design |
| `tourney_level_enc` | Tournament Level | **0.68%** | Encoded level: A=0, G=1, M=2, F=3 | Draw quality and best-of format vary by level — but lagged stats already partially encode tournament calibre |

---

## Interpretation

The ranking points gap (`rank_pts_diff`) is overwhelmingly the most decisive signal at 10.26% — more than double the second feature (`rank_diff` at 4.71%). Together these two derived features account for 15% of all model decisions, confirming that the relative quality gap between players is the dominant factor in ATP match outcomes. The remaining 85% is distributed remarkably evenly across 62 active features, with no single category dominating.

The new H2H last-5 features (`B_h2h_last5` at #7 with 1.99%, `A_h2h_last5` at #12 with 1.71%) debuted directly in the top 15 by gain and outrank every cumulative H2H feature (`B_h2h` at 0.51%, `A_h2h` at 0.00%). This validates the hypothesis that recent matchup history matters more than career totals — the last five meetings capture current-form matchup dynamics that get diluted when aggregated over many years. Form and momentum features (`B_wins_last5`, `A_wins_last5`, `B_win_streak`) similarly all rank in the top 20, reflecting that the model finds current hot/cold streaks genuinely predictive.

Two asymmetries in the zero-weight features are worth noting. First, `A_is_home` (0.00%) vs `B_is_home` (0.97%) — home advantage only appears on the B-player side. Since Player A is always the lower ATP player ID (typically the higher-ranked player in a pair), home advantage for the lower-ranked player (B) is more surprising and informative than home advantage for the favourite, which the ranking gap already explains. Second, `injured_during_swing_A` (0.00%) vs `injured_during_swing_B` (1.35%) — the model ignores the target player's own injury history but penalises the opponent's, suggesting that facing a compromised opponent is a more reliable signal than a player's own recovery trajectory. The five features with zero weight are not bad features — they are simply redundant given the other signals the model has access to.
