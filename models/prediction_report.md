# ATP Match Prediction — Signal Report

**Generated:** 2026-04-28  
**Model:** XGBoost | decay_rate=0.7 | max_depth=5 | min_child_weight=5 | learning_rate=0.05  
**Val AUC (2024):** 0.7180 | **Val Accuracy:** 65.54% | **Best iteration:** varies

---

## What is Decision Weight?

Decision weight (%) measures how much of the model's total predictive power comes from each signal. Out of every 100 decisions the model makes about who wins, this is roughly how many were primarily driven by that feature. Technically it is the share of total XGBoost information gain — how much each feature narrows down the likely winner across all splits in all trees.

**A/B pairing:** Since Player A (lower ATP ID) and Player B (higher ATP ID) are an arbitrary assignment, each player's version of the same stat is paired and their weights summed. This gives the true signal weight for that concept, free of the ID-assignment artifact.

---

## Top 20 Signals (Paired)

| Rank | Feature | Decision Weight | What it measures |
|------|---------|----------------|-----------------|
| 1 | `rank_pts_diff` | 11.80% | Ranking points gap — how many more points one player has than the other |
| 2 | `rank_diff` | 4.30% | ATP ranking gap — lower-ranked player wins ~35% of matches |
| 3 | `rank_pts` (A+B) | 3.97% | Player ranking points — absolute points level, not just the gap |
| 4 | `wins_last5` (A+B) | 3.65% | Recent form — wins in last 5 matches entering this match |
| 5 | `seed` (A+B) | 3.44% | Tournament seeding — confirms elite placement and bracket position |
| 6 | `completed_winrate` (A+B) | 3.36% | Completed-match win rate — removes free wins against retired opponents |
| 7 | `hand_L` (A+B) | 3.23% | Left-handed player — left-handers generate atypical spin angles on all surfaces |
| 8 | `age` (A+B) | 2.87% | Player age — affects stamina and peak window, most pronounced in best-of-5 |
| 9 | `matches_played` (A+B) | 2.83% | Matches played on surface (prior year) — experience and conditioning indicator |
| 10 | `win_rate` (A+B) | 2.75% | Surface win rate (prior year) — overall winning percentage on this surface |
| 11 | `tourney_titles` (A+B) | 2.72% | Tournament titles (2018+) — proven ability to win this specific event |
| 12 | `rank` (A+B) | 2.65% | ATP world ranking at match time |
| 13 | `sv_gms_won_pct` (A+B) | 2.64% | Service hold rate — the baseline that keeps a player in every set |
| 14 | `ht` (A+B) | 2.59% | Player height — taller players generally hold serve more easily |
| 15 | `rtn_win_pct` (A+B) | 2.57% | Return game win rate — how frequently a player breaks serve |
| 16 | `h2h_last5` (A+B) | 2.55% | H2H last 5 meetings (any surface) — recent head-to-head momentum |
| 17 | `rank_improvement` (A+B) | 2.50% | Ranking trajectory — how many places gained in the prior year |
| 18 | `injured_during_swing` (A+B) | 2.47% | Injury during tournament swing (prior year) — durability signal |
| 19 | `is_home` (A+B) | 2.43% | Home advantage — player's IOC country vs tournament host country |
| 20 | `h2h_last5_surface` (A+B) | 2.39% | H2H last 5 on this surface — surface-specific rivalry momentum |

---

## All Signals (Paired, 38 total)

A/B feature pairs are merged into a single row. Match-context and diff features are unpaired by nature.

| Rank | Feature | Decision Weight | Category |
|------|---------|----------------|----------|
| 1 | `rank_pts_diff` | 11.80% | Matchup Comparison |
| 2 | `rank_diff` | 4.30% | Matchup Comparison |
| 3 | `rank_pts` (A+B) | 3.97% | Rankings & Seeding |
| 4 | `wins_last5` (A+B) | 3.65% | Form & Momentum |
| 5 | `seed` (A+B) | 3.44% | Rankings & Seeding |
| 6 | `completed_winrate` (A+B) | 3.36% | Win Rates |
| 7 | `hand_L` (A+B) | 3.23% | Player Profile |
| 8 | `age` (A+B) | 2.87% | Player Profile |
| 9 | `matches_played` (A+B) | 2.83% | Form & Health |
| 10 | `win_rate` (A+B) | 2.75% | Win Rates |
| 11 | `tourney_titles` (A+B) | 2.72% | Tournament History |
| 12 | `rank` (A+B) | 2.65% | Rankings & Seeding |
| 13 | `sv_gms_won_pct` (A+B) | 2.64% | Serve Performance |
| 14 | `ht` (A+B) | 2.59% | Player Profile |
| 15 | `rtn_win_pct` (A+B) | 2.57% | Return Performance |
| 16 | `h2h_last5` (A+B) | 2.55% | Head-to-Head |
| 17 | `rank_improvement` (A+B) | 2.50% | Form & Health |
| 18 | `injured_during_swing` (A+B) | 2.47% | Form & Health |
| 19 | `is_home` (A+B) | 2.43% | Home Advantage |
| 20 | `h2h_last5_surface` (A+B) | 2.39% | Head-to-Head |
| 21 | `first_serve_pct` (A+B) | 2.30% | Serve Performance |
| 22 | `first_serve_win_pct` (A+B) | 2.29% | Serve Performance |
| 23 | `tourney_win_rate` (A+B) | 2.27% | Tournament History |
| 24 | `win_streak` (A+B) | 2.27% | Form & Momentum |
| 25 | `second_serve_win_pct` (A+B) | 2.22% | Serve Performance |
| 26 | `df_rate` (A+B) | 2.21% | Serve Performance |
| 27 | `h2h` (A+B) | 2.12% | Head-to-Head |
| 28 | `ace_rate` (A+B) | 2.12% | Serve Performance |
| 29 | `win_streak_surface` (A+B) | 2.08% | Form & Momentum |
| 30 | `bp_save_pct` (A+B) | 2.02% | Serve Performance |
| 31 | `tourney_matches` (A+B) | 1.99% | Tournament History |
| 32 | `strsets_rate` (A+B) | 1.86% | Win Rates |
| 33 | `tiebreaks_winrate` (A+B) | 1.86% | Win Rates |
| 34 | `best_of` | 1.49% | Match Context |
| 35 | `days_since_h2h` | 0.97% | Head-to-Head |
| 36 | `round_ord` | 0.79% | Match Context |
| 37 | `tourney_level_enc` | 0.72% | Match Context |
| 38 | `surface_enc` | 0.70% | Match Context |
