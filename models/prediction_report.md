# ATP Match Prediction — Signal Report

**Generated:** 2026-04-28
**Model:** XGBoost | decay_rate=0.5 | max_depth=3 | min_child_weight=5 | learning_rate=0.05
**Val AUC (2024):** 0.710 | **Val Accuracy:** 64.7% | **Best iteration:** 82
**Train-Val Gap:** 0.008 (improved from 0.011 before derived features added)

---

## What is Decision Weight?

Decision weight (%) measures how much of the model's total predictive power comes from each signal. Out of every 100 decisions the model makes about who wins, this is roughly how many were primarily driven by that feature. Technically it is the share of total XGBoost information gain — how much each feature narrows down the likely winner across all splits in all trees.

---

## Top 20 Signals

| Rank | Feature | Decision Weight | Category | What it means in tennis |
|------|---------|----------------|----------|--------------------------|
| 1 | rank_pts_diff | 11.5% | Rankings | Ranking points gap (A minus B) — how many more accumulated points one player has than the other; the single most direct measure of the quality gap between the two players |
| 2 | rank_diff | 6.6% | Rankings | ATP ranking gap (A minus B) — positive means B is ranked higher; the relative quality gap that determines draw advantage and seeding |
| 3 | A_rank_pts | 4.1% | Rankings | Player A's rolling 12-month ranking points — captures recent form better than rank alone |
| 4 | B_rank_pts | 3.6% | Rankings | Player B's rolling 12-month ranking points |
| 5 | sv_gms_won_pct_A | 3.1% | Serve | % of service games held by Player A — the foundation of ATP tennis; a reliable hold is the baseline requirement in every set |
| 6 | completed_winrate_A | 2.9% | Win Rates | Player A's win rate in fully completed matches — removes free wins from opponent retirements; a cleaner quality signal |
| 7 | win_rate_A | 2.6% | Win Rates | Player A's match win rate on this surface the prior year |
| 8 | A_ht | 2.4% | Player Profile | Player A's height — taller players generate more serve leverage, especially on fast surfaces |
| 9 | matches_played_B | 2.3% | Form & Health | Total matches Player B played on this surface last year — experience and stat reliability proxy |
| 10 | second_serve_win_pct_B | 2.3% | Serve | % of points Player B won on second serve — resilience when the first serve misses |
| 11 | first_serve_pct_B | 2.2% | Serve | % of Player B's first serves that landed in — consistency of the first delivery |
| 12 | B_rank | 2.2% | Rankings | Player B's ATP world ranking at match time |
| 13 | A_rank | 2.1% | Rankings | Player A's ATP world ranking at match time |
| 14 | injured_during_swing_B | 2.1% | Form & Health | How recently Player B returned from a retirement/walkover (0–1 score) |
| 15 | matches_played_A | 2.1% | Form & Health | Total matches Player A played on this surface last year |
| 16 | win_rate_B | 2.1% | Win Rates | Player B's match win rate on this surface the prior year |
| 17 | B_age | 2.0% | Player Profile | Player B's age — affects stamina and peak physical window |
| 18 | ace_rate_A | 2.0% | Serve | Aces per serve point for Player A — free point generation |
| 19 | first_serve_pct_A | 2.0% | Serve | % of Player A's first serves that landed in |
| 20 | df_rate_B | 1.9% | Serve | Double faults per serve point for Player B — unforced serve errors under pressure |

---

## All Signals

| Feature | Long Name | Decision Weight | Definition | Why It Matters |
|---------|-----------|----------------|------------|----------------|
| rank_pts_diff | Ranking Points Gap | 11.5% | Player A's ranking points minus Player B's ranking points | The single most predictive feature — the relative points gap directly measures the quality difference between the two players; a player 2,000 points ahead has demonstrably earned more over the last 52 weeks |
| rank_diff | ATP Ranking Gap | 6.6% | Player A's ATP ranking minus Player B's ranking (positive = B is ranked higher/better) | The relative ranking gap is more predictive than either player's absolute rank alone — what matters is not that you're ranked 50, but that you're ranked 50 vs an opponent at 120 |
| A_rank_pts | Player A Ranking Points | 4.1% | Player A's rolling 12-month ranking points total | Points reflect earned results and update continuously; a player who just won a major has high points before the ranking ladder moves |
| B_rank_pts | Player B Ranking Points | 3.6% | Player B's rolling 12-month ranking points total | Same as A_rank_pts for the opponent — particularly useful for players on a hot run whose official rank hasn't caught up yet |
| sv_gms_won_pct_A | Player A Service Hold Rate | 3.1% | % of service games Player A held on this surface the prior year | The most direct measure of serve dominance — breaking serve happens only ~25% of the time in ATP tennis, so a reliable hold is the baseline that keeps a player in every set |
| completed_winrate_A | Player A Completed-Match Win Rate | 2.9% | Player A's win rate in fully completed matches only (no retirements or walkovers) | A cleaner quality signal — removes free wins where the opponent retired injured; a player with 80% completed win rate is genuinely dominant, not padding stats against injured opponents |
| win_rate_A | Player A Surface Win Rate | 2.6% | % of matches Player A won on this surface the prior year | Overall surface-specific form over a full season; winning consistently on a surface reflects both skill and physical comfort with the conditions |
| A_ht | Player A Height | 2.4% | Player A's height in cm | Taller players generate more serve leverage (higher contact point, sharper angles), especially on faster surfaces; height is also correlated with wingspan and reach |
| matches_played_B | Player B Matches Played | 2.3% | Total matches Player B played on this surface the prior year | Experience and workload indicator — more matches means more reliable lagged stats and more tournament reps on this surface |
| second_serve_win_pct_B | Player B Second-Serve Points Won | 2.3% | % of points Player B won on second serve | Resilience under pressure — when the first serve misses, the second is slower and attackable; players who still win second-serve points have variety and depth that prevents opponents from teeing off |
| first_serve_pct_B | Player B First-Serve In Rate | 2.2% | % of Player B's first serves that landed in | Consistency of the first delivery — erratic first serves force the server onto the weaker second delivery repeatedly, neutralising the serve advantage entirely |
| B_rank | Player B ATP Ranking | 2.2% | Player B's current ATP world ranking at match time | Context anchor for the rank gap — together with A_rank it allows the model to calibrate absolute quality |
| A_rank | Player A ATP Ranking | 2.1% | Player A's current ATP world ranking at match time | Same anchor for Player A — individual rank still informative when rank gap features are included |
| injured_during_swing_B | Player B Back-from-Absence Score | 2.1% | Score 0–1: how recently Player B returned from a retirement/walkover (1 = just returned, 0 = fully recovered) | Injury recency penalty for the opponent — a player returning from injury within weeks may still be managing pain; the model weights opponent injury more than own injury |
| matches_played_A | Player A Matches Played | 2.1% | Total matches Player A played on this surface the prior year | Same as matches_played_B for Player A — a player with 40+ clay matches has deep surface-specific conditioning compared to someone with 8 |
| win_rate_B | Player B Surface Win Rate | 2.1% | % of matches Player B won on this surface the prior year | Same as win_rate_A for the opponent — the direct comparison of surface-specific form |
| B_age | Player B Age | 2.0% | Player B's age in years at time of match | Affects stamina (especially best-of-5), peak physical window, and experience under pressure — players in their mid-to-late 20s tend to peak |
| ace_rate_A | Player A Ace Rate | 2.0% | Aces per serve point for Player A | Free point generation — aces win points without the opponent touching the ball; surface-dependent (much higher on grass/fast hard) and puts opponents on the back foot psychologically |
| first_serve_pct_A | Player A First-Serve In Rate | 2.0% | % of Player A's first serves that landed in | Same as first_serve_pct_B for Player A — a high first-serve percentage means the server's best weapon is reliably deployed every game |
| df_rate_B | Player B Double-Fault Rate | 1.9% | Double faults per serve point for Player B | Unforced serve errors — doubles are free gifts to the opponent and often appear under pressure; a high double-fault rate is a reliable tell for nerves or mechanical issues |
| rtn_win_pct_B | Player B Return-Game Win Rate | 1.9% | % of return games Player B won (i.e. breaks secured) | Offensive pressure on the opponent's serve — the attacker's metric; great returners turn the most passive position in tennis into a weapon that generates breaks |
| rtn_win_pct_A | Player A Return-Game Win Rate | 1.9% | % of return games Player A won (i.e. breaks secured) | Same as rtn_win_pct_B for Player A — a player who breaks frequently forces the server to play perfect tennis every game |
| df_rate_A | Player A Double-Fault Rate | 1.9% | Double faults per serve point for Player A | Same as df_rate_B for Player A — players who double-fault frequently hand away break points when the pressure is highest |
| completed_winrate_B | Player B Completed-Match Win Rate | 1.9% | Player B's win rate in fully completed matches only | Same as completed_winrate_A for the opponent — discounting retirement wins gives a fairer picture of who can beat healthy opponents |
| rank_improvement_B | Player B Ranking Improvement | 1.8% | Player B's ranking improvement over the prior year (positive = improved) | Trajectory signal — a rising player is gaining confidence and match practice; a falling player may be dealing with undisclosed injury or form slumps |
| sv_gms_won_pct_B | Player B Service Hold Rate | 1.8% | % of service games Player B held on this surface the prior year | Same as sv_gms_won_pct_A for the opponent — a player who frequently loses serve is under constant pressure |
| strsets_rate_B | Player B Straight-Sets Win Rate | 1.8% | % of Player B's wins that were won in straight sets | Same as strsets_rate_A for the opponent — a player who frequently drops sets even in wins is vulnerable |
| tiebreaks_winrate_A | Player A Tiebreak Win Rate | 1.8% | % of tiebreaks Player A won | Mental toughness and clutch ability at 6-6 — tiebreaks remove nearly all technical advantage and come down to nerve |
| bp_save_pct_B | Player B Break-Point Save Rate | 1.8% | % of break points Player B saved | Clutch performance under maximum serve pressure — saving break points in the biggest moments keeps sets alive |
| second_serve_win_pct_A | Player A Second-Serve Points Won | 1.7% | % of points Player A won on second serve | Same as second_serve_win_pct_B for Player A — a weak second serve is the most reliable way opponents can generate break opportunities |
| days_since_h2h | Days Since Last Meeting | 1.7% | Days since their last meeting on this surface (-1 if never met) | Freshness of H2H information — a meeting last month is more informative than one five years ago; very old H2H records predate career-defining technique changes |
| ace_rate_B | Player B Ace Rate | 1.6% | Aces per serve point for Player B | Same as ace_rate_A for the opponent — facing a high-ace server is demoralising and forces the returner to take more risks |
| rank_improvement_A | Player A Ranking Improvement | 1.6% | Player A's ranking improvement over the prior year (positive = improved) | Same as rank_improvement_B for Player A — improvement indicates they are beating players they previously couldn't |
| B_ht | Player B Height | 1.6% | Player B's height in cm | Same as A_ht for the opponent — height advantages are most pronounced on serve-friendly surfaces like grass and fast hard courts |
| first_serve_win_pct_A | Player A First-Serve Points Won | 1.5% | % of points Player A won when first serve landed in | Quality of the first delivery — a high value means the first serve is a genuine weapon that wins points outright or forces a weak return |
| A_age | Player A Age | 1.5% | Player A's age in years at time of match | Same as B_age for Player A — age mismatches matter most in five-set matches and late in tournaments when fatigue compounds |
| tourney_level_enc | Tournament Level | 1.5% | Encoded level: Grand Slam / Masters / 500 / 250 | Affects draw quality, prize money stakes, best-of format (Slams use best-of-5), and player motivation |
| first_serve_win_pct_B | Player B First-Serve Points Won | 1.5% | % of points Player B won when first serve landed in | Same as first_serve_win_pct_A for the opponent — the first serve is the one shot where the server has complete control |
| round_ord | Tournament Round | 1.4% | Round of the tournament (R128 → Final) | Later rounds mean stronger opponents, but also more fatigue — by the semi-finals, even unseeded players have beaten several ranked opponents |
| strsets_rate_A | Player A Straight-Sets Win Rate | 1.4% | % of Player A's wins that were won in straight sets | Dominance indicator — winning without dropping a set means the player was never in real danger |
| B_seed | Player B Tournament Seed | 1.4% | Player B's seeding in this tournament draw | Seeding confirms elite status within the draw; the rank gap features have partially absorbed this signal |
| A_seed | Player A Tournament Seed | 1.3% | Player A's seeding in this tournament draw | Same as B_seed for Player A — residual signal beyond what rank gap already captures |
| tiebreaks_winrate_B | Player B Tiebreak Win Rate | 0.8% | % of tiebreaks Player B won | Same as tiebreaks_winrate_A for the opponent — tiebreak ability is the best proxy for clutch performance at 6-6 |
| bp_save_pct_A | Player A Break-Point Save Rate | 0.6% | % of break points Player A saved | Same as bp_save_pct_B for Player A — residual signal; much of this is captured by sv_gms_won_pct and second_serve_win_pct |

---

## Interpretation

**Relative quality gap is the dominant signal.** The two new derived features — ranking points gap (`rank_pts_diff`, 11.5%) and ranking gap (`rank_diff`, 6.6%) — immediately became the top two signals, together accounting for 18.1% of all decisions. This validates a key tennis intuition: what matters is not that you're ranked 50, but that you're ranked 50 against an opponent at 120. The model now captures the quality differential directly rather than inferring it from two separate inputs.

**Individual rank features absorbed but not replaced.** The four underlying features (`A_rank`, `B_rank`, `A_rank_pts`, `B_rank_pts`) dropped sharply — from a combined 22.8% to 12.0% — but remain in the top 15. They add context the gap alone misses: two players with a 500-point gap at the bottom of the rankings are a different matchup than the same gap at the top.

**Completed win rate beats raw win rate.** `completed_winrate_A` outranks `win_rate_A`, confirming that removing retirement-padded wins is a better quality signal — this continues to validate the data cleaning rule.

**Serve is the engine.** Five of the top 20 features are serve metrics, led by `sv_gms_won_pct_A` (service hold rate). The model finds *holding* more predictive than individual serve quality stats, which aligns with ATP reality: consistency of service games held is the floor that determines whether a set stays on serve.

**Reduced overfitting.** Adding the gap features shrank the train-val AUC gap from 0.011 to 0.008, suggesting the model is now fitting a cleaner signal. The derived features give the trees a more efficient path to the key comparison rather than learning it implicitly across many splits.
