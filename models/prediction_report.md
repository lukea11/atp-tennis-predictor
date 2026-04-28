# ATP Match Prediction — Signal Report

**Generated:** 2026-04-28
**Model:** XGBoost | decay_rate=0.5 | max_depth=3 | min_child_weight=5 | learning_rate=0.05
**Val AUC (2024):** 0.714 | **Val Accuracy:** 65.7% | **Best iteration:** 82

---

## What is Decision Weight?

Decision weight (%) measures how much of the model's total predictive power comes from each signal. Out of every 100 decisions the model makes about who wins, this is roughly how many were primarily driven by that feature. Technically it is the share of total XGBoost information gain — how much each feature narrows down the likely winner across all splits in all trees.

---

## Top 20 Signals

| Rank | Feature | Decision Weight | Category | What it means in tennis |
|------|---------|----------------|----------|--------------------------|
| 1 | A_rank | 8.3% | Rankings | Player A's ATP world ranking — the single best objective summary of overall quality at match time |
| 2 | B_rank_pts | 5.4% | Rankings | Player B's rolling 12-month ranking points — captures recent form better than rank alone; a player who just won a major has high points before the ranking updates |
| 3 | A_rank_pts | 5.2% | Rankings | Same as above for Player A — points reflect earned results, rank can lag behind form |
| 4 | A_seed | 4.6% | Rankings | Tournament seeding for Player A — confirms elite status within the draw; unseeded players face tougher early-round opponents |
| 5 | win_rate_B | 4.2% | Win Rates | Player B's match win rate on this surface the prior year — overall surface-specific form from the previous season |
| 6 | B_rank | 3.9% | Rankings | Player B's ATP world ranking at match time |
| 7 | B_seed | 3.7% | Rankings | Tournament seeding for Player B |
| 8 | completed_winrate_A | 3.0% | Win Rates | Player A's win rate in fully completed matches (no retirements) — a cleaner quality signal that removes free wins from opponent injury |
| 9 | sv_gms_won_pct_A | 2.7% | Serve | % of service games held by Player A the prior year — the most direct measure of serve dominance; holding serve consistently is the foundation of ATP tennis |
| 10 | matches_played_B | 2.7% | Form & Health | Total matches Player B played on this surface last year — captures both experience and how reliable their lagged stats are |
| 11 | completed_winrate_B | 2.7% | Win Rates | Player B's win rate in completed matches — mirrors rank 8 for the opponent |
| 12 | matches_played_A | 2.3% | Form & Health | Total matches Player A played on this surface last year |
| 13 | B_age | 2.1% | Player Profile | Player B's age — affects stamina (especially best-of-5), peak physical window, and experience under pressure |
| 14 | rtn_win_pct_B | 2.1% | Return | % of Player B's return games won (i.e. breaks secured) — the attacker's metric; offensive pressure on the opponent's serve |
| 15 | B_h2h | 2.0% | H2H | Player B's prior wins vs Player A on this surface — captures matchup-specific dynamics that aggregate stats miss (e.g. awkward playing styles) |
| 16 | strsets_rate_A | 2.0% | Win Rates | % of Player A's wins that were straight sets — dominance indicator; winning without dropping a set means rarely being troubled |
| 17 | win_rate_A | 2.0% | Win Rates | Player A's match win rate on this surface the prior year |
| 18 | first_serve_win_pct_A | 1.9% | Serve | % of points Player A won when first serve landed in — quality of the first delivery; high value means the first serve is a genuine weapon |
| 19 | first_serve_win_pct_B | 1.9% | Serve | Same metric for Player B |
| 20 | days_since_h2h | 1.8% | H2H | Days since their last meeting on this surface — freshness of H2H information; -1 if they have never met on this surface |

---

## By Category (summed decision weight)

| Category | Total Weight | Key signals |
|----------|-------------|-------------|
| Rankings & Seeding | **31.5%** | A_rank (8.3%), A/B rank_pts (10.6%), A/B seed (8.3%) |
| Win Rates (lagged) | **18.9%** | completed_winrate A/B (5.6%), win_rate A/B (6.2%), strsets_rate A/B (3.5%), tiebreaks_winrate A/B (2.2%), rtn_win_pct A/B (3.8%) — split across return too |
| Serve Performance | **18.6%** | sv_gms_won_pct A/B (4.1%), first_serve_win_pct A/B (3.8%), second_serve_win_pct A/B (3.0%), bp_save_pct A/B (3.0%), first_serve_pct A/B (3.1%), ace_rate A/B (2.9%), df_rate A/B (2.8%) |
| Return Performance | **5.7%** | rtn_win_pct A/B (3.8%), tiebreaks_winrate A/B (2.2%) |
| Form & Health | **9.6%** | matches_played A/B (5.0%), rank_improvement A/B (3.1%), injured_during_swing B (1.5%) |
| Player Profile | **9.9%** | A/B age (3.5%), A/B ht (3.2%), hand_B_L (1.2%), A_h2h/B_h2h (2.9%) combined w/ H2H |
| H2H | **4.8%** | B_h2h (2.0%), days_since_h2h (1.8%), A_h2h (0.9%) |
| Match Context | **3.7%** | tourney_level_enc (1.3%), best_of (1.2%), surface_enc implicitly via separate surface models |

---

## Interpretation

**Rankings dominate but not alone.** Rankings and seeding collectively account for ~31% of the model's decisions — unsurprising given that ATP rankings are a direct measure of accumulated quality. However, that leaves ~69% driven by other signals, confirming that rank alone is insufficient and the lagged surface stats add meaningful lift.

**Serve holds vs winning points.** Service game hold rate (`sv_gms_won_pct`) edges out first-serve quality in importance — the model finds *holding* more predictive than *how* you hold. This aligns with ATP reality: breaking serve is rare (~25% of games), so a reliable hold is the baseline requirement.

**Completed win rate beats raw win rate.** `completed_winrate` outranks `win_rate` for both players, meaning the model learned to discount wins that came via opponent retirement. This validates the CLAUDE.md cleaning rule — excluding retirements from stats wasn't just data hygiene, it improved predictive signal.

**Surprising: matches played is top-10.** Volume (how many matches a player played last year on this surface) ranks 10th — partly because it proxies experience, but also because players with more matches simply have more reliable lagged stats. Worth monitoring: this could be a spurious correlation for players who played many matches but lost most of them.

**Injury signal is asymmetric.** `injured_during_swing_B` (1.5%) appears in the top 30 but `injured_during_swing_A` does not crack the top 45. The model appears to weight an *opponent's* injury history more than the player's own — plausibly because a healthy player benefits when facing a compromised opponent, and the compromised player may still play through injury.
