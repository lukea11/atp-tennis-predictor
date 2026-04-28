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
| 2 | B_rank_pts | 5.3% | Rankings | Player B's rolling 12-month ranking points — captures recent form better than rank alone; a player who just won a major has high points before the ranking updates |
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

## All Signals

| Feature | Long Name | Decision Weight | Definition | Why It Matters |
|---------|-----------|----------------|------------|----------------|
| A_rank | Player A ATP Ranking | 8.3% | Player A's current ATP world ranking at match time | The single best objective summary of overall quality — it aggregates results across all surfaces over 52 weeks and is updated weekly, so it reflects a player's standing in the world right now |
| B_rank_pts | Player B Ranking Points | 5.3% | Player B's rolling 12-month ranking points total | Points reflect earned results and update continuously; a player who just won a major has high points before the ranking ladder moves, making this a more current form signal than rank alone |
| A_rank_pts | Player A Ranking Points | 5.2% | Player A's rolling 12-month ranking points total | Same as B_rank_pts for Player A — particularly useful for players on a hot run whose official rank hasn't caught up yet |
| A_seed | Player A Tournament Seed | 4.6% | Player A's seeding in this tournament draw | Seeding confirms elite status within this specific draw and determines placement — seeded players avoid each other until late rounds, meaning they face progressively harder opponents as they advance |
| win_rate_B | Player B Surface Win Rate | 4.2% | % of matches Player B won on this surface the prior year | Overall surface-specific form over a full season; winning consistently on a surface reflects both skill and physical comfort with the conditions |
| B_rank | Player B ATP Ranking | 3.9% | Player B's current ATP world ranking at match time | Same as A_rank for the opponent — the direct quality comparison between the two players; the lower-ranked player wins roughly 35% of matches |
| B_seed | Player B Tournament Seed | 3.7% | Player B's seeding in this tournament draw | Same as A_seed for the opponent — unseeded players face tougher early-round draws and have less favourable bracket positions |
| completed_winrate_A | Player A Completed-Match Win Rate | 3.0% | Player A's win rate in fully completed matches only (no retirements or walkovers) | A cleaner quality signal — removes free wins where the opponent retired injured; a player with 80% completed win rate is genuinely dominant, not padding stats against injured opponents |
| sv_gms_won_pct_A | Player A Service Hold Rate | 2.7% | % of service games Player A held on this surface the prior year | The most direct measure of serve dominance — breaking serve happens only ~25% of the time in ATP tennis, so a reliable hold is the baseline that keeps a player in every set |
| matches_played_B | Player B Matches Played | 2.7% | Total matches Player B played on this surface the prior year | Experience and workload indicator — more matches means more reliable lagged stats and more tournament reps on this surface; very few matches either means a new player, injury, or selective scheduling |
| completed_winrate_B | Player B Completed-Match Win Rate | 2.7% | Player B's win rate in fully completed matches only | Same as completed_winrate_A for the opponent — discounting retirement wins and losses gives a fairer picture of who can actually beat healthy opponents |
| matches_played_A | Player A Matches Played | 2.3% | Total matches Player A played on this surface the prior year | Same as matches_played_B for Player A — a player with 40+ clay matches has deep surface-specific conditioning and tactical library compared to someone with 8 |
| B_age | Player B Age | 2.1% | Player B's age in years at time of match | Affects stamina (especially best-of-5), peak physical window, and experience under pressure — players in their mid-to-late 20s tend to peak, while younger players can be inconsistent and older players fade physically |
| rtn_win_pct_B | Player B Return-Game Win Rate | 2.1% | % of return games Player B won (i.e. breaks secured) | Offensive pressure on the opponent's serve — the attacker's metric; great returners turn the most passive position in tennis into a weapon that generates breaks |
| B_h2h | Player B Head-to-Head Wins | 2.0% | Player B's prior wins vs Player A on this surface | Captures player-specific matchup dynamics that aggregate stats miss — certain playing styles are awkward for certain opponents regardless of ranking |
| strsets_rate_A | Player A Straight-Sets Win Rate | 2.0% | % of Player A's wins that were won in straight sets | Dominance indicator — winning without dropping a set means the player was never in real danger; players with high straight-set rates rarely go to deciding sets where upsets happen |
| win_rate_A | Player A Surface Win Rate | 2.0% | % of matches Player A won on this surface the prior year | Overall surface-specific form; the direct head-to-head comparison of how well each player performs on this specific surface |
| first_serve_win_pct_A | Player A First-Serve Points Won | 1.9% | % of points Player A won when first serve landed in | Quality of the first delivery — a high value means the first serve is a genuine weapon that wins points outright or forces a weak return; great first serves reduce break point exposure entirely |
| first_serve_win_pct_B | Player B First-Serve Points Won | 1.9% | % of points Player B won when first serve landed in | Same as first_serve_win_pct_A for the opponent — the first serve is the one shot where the server has complete control; strong first-serve winners keep opponents passive |
| days_since_h2h | Days Since Last Meeting | 1.8% | Days since their last meeting on this surface (-1 if never met) | Freshness of H2H information — a meeting last month is more informative than one five years ago; very old H2H records predate career-defining technique changes and may be misleading |
| A_ht | Player A Height | 1.8% | Player A's height in cm | Taller players generate more serve leverage (higher contact point, sharper angles), especially on faster surfaces; height is also correlated with wingspan and reach for volleys |
| second_serve_win_pct_B | Player B Second-Serve Points Won | 1.7% | % of points Player B won on second serve | Resilience under pressure — when the first serve misses, the second is slower and attackable; players who still win second-serve points have variety and depth that prevents opponents from teeing off |
| rank_improvement_B | Player B Ranking Improvement | 1.7% | Player B's ranking improvement over the prior year (positive = improved) | Trajectory signal — a rising player is gaining confidence, match practice, and is physically peaking; a falling player may be dealing with undisclosed injury or form slumps not yet reflected in current ranking |
| rtn_win_pct_A | Player A Return-Game Win Rate | 1.7% | % of return games Player A won (i.e. breaks secured) | Same as rtn_win_pct_B for Player A — a player who breaks frequently forces the server to play perfect tennis every game; one slip and they're down a break |
| first_serve_pct_A | Player A First-Serve In Rate | 1.7% | % of Player A's first serves that landed in | Consistency of the first delivery — erratic first serves force the server onto the weaker second delivery repeatedly, neutralising the serve advantage entirely |
| bp_save_pct_B | Player B Break-Point Save Rate | 1.6% | % of break points Player B saved | Clutch performance under maximum serve pressure — saving break points in the biggest moments keeps sets alive; the best servers in the world excel here not just through power but composure |
| df_rate_B | Player B Double-Fault Rate | 1.5% | Double faults per serve point for Player B | Unforced serve errors — doubles are free gifts to the opponent and often appear under pressure; a high double-fault rate is a reliable tell for nerves or mechanical issues under match pressure |
| injured_during_swing_B | Player B Back-from-Absence Score | 1.5% | Score 0–1: how recently Player B returned from a retirement/walkover (1 = just returned, 0 = fully recovered) | Injury recency penalty for the opponent — a player returning from injury within weeks may still be managing pain, physically underprepared, or mentally cautious; the model weights opponent injury more than own injury |
| ace_rate_A | Player A Ace Rate | 1.5% | Aces per serve point for Player A | Free point generation — aces win points without the opponent touching the ball; surface-dependent (much higher on grass/fast hard) and puts opponents on the back foot psychologically |
| strsets_rate_B | Player B Straight-Sets Win Rate | 1.5% | % of Player B's wins that were won in straight sets | Same as strsets_rate_A for the opponent — a player who frequently drops sets even in wins is vulnerable; opponents who push them to three or five sets know there's a chance |
| first_serve_pct_B | Player B First-Serve In Rate | 1.4% | % of Player B's first serves that landed in | Same as first_serve_pct_A for the opponent — a high first-serve percentage means the server's best weapon is reliably deployed every game |
| ace_rate_B | Player B Ace Rate | 1.4% | Aces per serve point for Player B | Same as ace_rate_A for the opponent — facing a high-ace server is demoralising and forces the returner to take more risks |
| rank_improvement_A | Player A Ranking Improvement | 1.4% | Player A's ranking improvement over the prior year (positive = improved) | Same as rank_improvement_B for Player A — improvement indicates they are beating players they previously couldn't; decline signals potential hidden issues |
| sv_gms_won_pct_B | Player B Service Hold Rate | 1.4% | % of service games Player B held on this surface the prior year | Same as sv_gms_won_pct_A for the opponent — a player who frequently loses serve is under constant pressure and cannot dictate the match |
| A_age | Player A Age | 1.4% | Player A's age in years at time of match | Same as B_age for Player A — age mismatches matter most in five-set matches and late in tournaments when fatigue compounds |
| bp_save_pct_A | Player A Break-Point Save Rate | 1.4% | % of break points Player A saved | Same as bp_save_pct_B for Player A — a low break-point save rate means opponents can capitalise when they do create opportunities |
| B_ht | Player B Height | 1.4% | Player B's height in cm | Same as A_ht for the opponent — height advantages are most pronounced on serve-friendly surfaces like grass and fast hard courts |
| tiebreaks_winrate_A | Player A Tiebreak Win Rate | 1.4% | % of tiebreaks Player A won | Mental toughness and clutch ability at 6-6 — tiebreaks remove nearly all technical advantage and come down to nerve; players who win tiebreaks consistently have the mental game to handle the highest pressure moments |
| second_serve_win_pct_A | Player A Second-Serve Points Won | 1.3% | % of points Player A won on second serve | Same as second_serve_win_pct_B for Player A — a weak second serve is the most reliable way opponents can generate break opportunities |
| df_rate_A | Player A Double-Fault Rate | 1.3% | Double faults per serve point for Player A | Same as df_rate_B for Player A — players who double-fault frequently hand away break points when the pressure is highest |
| tourney_level_enc | Tournament Level | 1.3% | Encoded level: Grand Slam / Masters / 500 / 250 | Affects draw quality, prize money stakes, best-of format (Slams use best-of-5), and player motivation — top players prioritise Slams and Masters, meaning upsets are rarer there despite longer formats |
| best_of | Best-of Format | 1.2% | Best-of-3 or Best-of-5 matches | Longer matches disproportionately favour fitter, more consistent players — upsets are significantly rarer in best-of-5 because the better player has more chances to correct a bad start |
| hand_B_L | Player B Left-Handed | 1.2% | Binary: 1 if Player B is left-handed | Left-handers have a natural tactical advantage — their wide serve lands in an unusual quadrant that right-handers rarely practice against; statistically they punch above their weight in win rates because opponents see them infrequently |
| A_h2h | Player A Head-to-Head Wins | 0.9% | Player A's prior wins vs Player B on this surface | Same as B_h2h for Player A — a lower-ranked player can dominate H2H due to a favourable stylistic matchup; career-long patterns reflect tactical and physical mismatches that persist |
| tiebreaks_winrate_B | Player B Tiebreak Win Rate | 0.8% | % of tiebreaks Player B won | Same as tiebreaks_winrate_A for the opponent — tiebreak ability is the single best proxy for how a player performs when one bad point can end a set |

---

## Interpretation

**Rankings dominate but not alone.** Rankings and seeding collectively account for ~31% of the model's decisions — unsurprising given that ATP rankings are a direct measure of accumulated quality. However, that leaves ~69% driven by other signals, confirming that rank alone is insufficient and the lagged surface stats add meaningful lift.

**Completed win rate beats raw win rate.** `completed_winrate` outranks `win_rate` for both players — the model learned to discount wins that came via opponent retirement. This validates the data cleaning rule: excluding retirements from stats wasn't just data hygiene, it improved predictive signal.

**Serve hold rate edges out first-serve quality.** Service game hold rate (`sv_gms_won_pct`) ranks higher than first-serve point win rate — the model finds *holding* more predictive than *how* you hold. This aligns with ATP reality: breaking serve is rare (~25% of games), so a reliable hold is the baseline requirement.

**Matches played is top-10, but worth monitoring.** Volume of matches on a surface last year ranks 10th — partly because it proxies experience, but also because players with more matches have more reliable lagged stats. This could be a spurious correlation for players who played many matches but lost most of them.

**Injury signal is asymmetric.** `injured_during_swing_B` (1.5%) appears in the top 30 but `injured_during_swing_A` does not crack the top 35. The model weights an *opponent's* injury history more than the player's own — plausibly because a healthy player benefits when facing a compromised opponent, and the compromised player may still play through injury without being fully penalised by the model.
