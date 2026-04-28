# Prediction Report Skill

## When to trigger
After every training and evaluation run — whenever models/feature_importance.csv
and models/best_params.json have been updated.

## Process
1. Read models/feature_importance.csv
2. Read models/best_params.json
3. Compute Decision Weight (%) = each feature's gain / total gain × 100
4. Write the report to models/prediction_report.md using the Output Format

## Terminology
**Decision weight (%)** — the percentage of the model's total information gain
contributed by this signal. Think of it as: out of every 100 decisions the model
makes about who wins, how many were primarily driven by this signal?
This is more precise than "explains variance" — it reflects how much each feature
narrows down the likely winner across all splits in all trees.

## Feature reference table
Used to populate the "All Signals" table in the report.
Each row: Feature code | Long name | Definition | Why it matters

### Matchup Comparison (derived)
| Feature | Long Name | Definition | Why It Matters |
|---------|-----------|------------|----------------|
| rank_pts_diff | Ranking Points Gap | Player A's ranking points minus Player B's ranking points | The single most predictive signal — the relative points gap directly measures the quality difference; what matters is not a player's absolute points, but how many more they have than their opponent |
| rank_diff | ATP Ranking Gap | Player A's ATP ranking minus Player B's ranking (positive = B ranked higher/better) | The relative ranking gap is more predictive than either player's absolute rank alone — what matters is not that you're ranked 50, but that you're ranked 50 vs an opponent at 120 |

### Rankings & Seeding
| Feature | Long Name | Definition | Why It Matters |
|---------|-----------|------------|----------------|
| A_rank | Player A ATP Ranking | Player A's current ATP world ranking at match time | The single best objective summary of overall quality — it aggregates results across all surfaces over 52 weeks and is updated weekly, so it reflects a player's standing in the world right now |
| B_rank | Player B ATP Ranking | Player B's current ATP world ranking at match time | Same as A_rank for the opponent — the direct quality comparison between the two players; the lower-ranked player wins roughly 35% of matches |
| A_rank_pts | Player A Ranking Points | Player A's rolling 12-month ranking points total | Points reflect earned results and update continuously; a player who just won a major has high points before the ranking ladder moves, making this a more current form signal than rank alone |
| B_rank_pts | Player B Ranking Points | Player B's rolling 12-month ranking points total | Same as A_rank_pts for the opponent — particularly useful for players on a hot run whose official rank hasn't caught up yet |
| A_seed | Player A Tournament Seed | Player A's seeding in this tournament draw | Seeding confirms elite status within this specific draw and determines placement — seeded players avoid each other until late rounds, meaning they face progressively harder opponents as they advance |
| B_seed | Player B Tournament Seed | Player B's seeding in this tournament draw | Same as A_seed for the opponent — unseeded players face tougher early-round draws and have less favourable bracket positions |

### Win Rate Signals (lagged — prior year, same surface)
| Feature | Long Name | Definition | Why It Matters |
|---------|-----------|------------|----------------|
| win_rate_A | Player A Surface Win Rate | % of matches Player A won on this surface the prior year | Overall surface-specific form over a full season; winning consistently on a surface reflects both skill and physical comfort with the conditions |
| win_rate_B | Player B Surface Win Rate | % of matches Player B won on this surface the prior year | Same for the opponent — the direct head-to-head comparison of how well each player performs on this specific surface |
| completed_winrate_A | Player A Completed-Match Win Rate | Player A's win rate in fully completed matches only (no retirements or walkovers) | A cleaner quality signal — removes free wins where the opponent retired injured; a player with 80% completed win rate is genuinely dominant, not padding stats against injured opponents |
| completed_winrate_B | Player B Completed-Match Win Rate | Player B's win rate in fully completed matches only | Same for the opponent — discounting retirement wins and losses gives a fairer picture of who can actually beat healthy opponents |
| strsets_rate_A | Player A Straight-Sets Win Rate | % of Player A's wins that were won in straight sets | Dominance indicator — winning without dropping a set means the player was never in real danger; players with high straight-set rates rarely go to deciding sets where upsets happen |
| strsets_rate_B | Player B Straight-Sets Win Rate | % of Player B's wins that were won in straight sets | Same for the opponent — a player who frequently drops sets even in wins is vulnerable; opponents who push them to three or five sets know there's a chance |

### Serve Performance (lagged — prior year, same surface)
| Feature | Long Name | Definition | Why It Matters |
|---------|-----------|------------|----------------|
| sv_gms_won_pct_A | Player A Service Hold Rate | % of service games Player A held on this surface the prior year | The most direct measure of serve dominance — breaking serve happens only ~25% of the time in ATP tennis, so a reliable hold is the baseline that keeps a player in every set |
| sv_gms_won_pct_B | Player B Service Hold Rate | % of service games Player B held on this surface the prior year | Same for the opponent — a player who frequently loses serve is under constant pressure and cannot dictate the match |
| first_serve_win_pct_A | Player A First-Serve Points Won | % of points Player A won when first serve landed in | Quality of the first delivery — a high value means the first serve is a genuine weapon that wins points outright or forces a weak return; great first serves reduce break point exposure entirely |
| first_serve_win_pct_B | Player B First-Serve Points Won | % of points Player B won when first serve landed in | Same for the opponent — the first serve is the one shot where the server has complete control; strong first-serve winners keep opponents passive |
| second_serve_win_pct_A | Player A Second-Serve Points Won | % of points Player A won on second serve | Resilience under pressure — when the first serve misses, the second is slower and attackable; players who still win second-serve points have variety and depth that prevents opponents from teeing off |
| second_serve_win_pct_B | Player B Second-Serve Points Won | % of points Player B won on second serve | Same for the opponent — a weak second serve is the most reliable way opponents can generate break opportunities |
| bp_save_pct_A | Player A Break-Point Save Rate | % of break points Player A saved | Clutch performance under maximum serve pressure — saving break points in the biggest moments keeps sets alive; the best servers in the world excel here not just through power but composure |
| bp_save_pct_B | Player B Break-Point Save Rate | % of break points Player B saved | Same for the opponent — a low break-point save rate means the opponent can capitalise when they do create opportunities |
| first_serve_pct_A | Player A First-Serve In Rate | % of Player A's first serves that landed in | Consistency of the first delivery — erratic first serves force the server onto the weaker second delivery repeatedly, neutralising the serve advantage entirely |
| first_serve_pct_B | Player B First-Serve In Rate | % of Player B's first serves that landed in | Same for the opponent — a high first-serve percentage means the server's best weapon is reliably deployed every game |
| ace_rate_A | Player A Ace Rate | Aces per serve point for Player A | Free point generation — aces win points without the opponent touching the ball; surface-dependent (much higher on grass/fast hard) and puts opponents on the back foot psychologically |
| ace_rate_B | Player B Ace Rate | Aces per serve point for Player B | Same for the opponent — facing a high-ace server is demoralising and forces the returner to take more risks |
| df_rate_A | Player A Double-Fault Rate | Double faults per serve point for Player A | Unforced serve errors — doubles are free gifts to the opponent and often appear under pressure; players who double-fault frequently hand away break points when the pressure is highest |
| df_rate_B | Player B Double-Fault Rate | Double faults per serve point for Player B | Same for the opponent — a high double-fault rate is a reliable tell for nerves or mechanical issues under match pressure |

### Return Performance (lagged — prior year, same surface)
| Feature | Long Name | Definition | Why It Matters |
|---------|-----------|------------|----------------|
| rtn_win_pct_A | Player A Return-Game Win Rate | % of return games Player A won (i.e. breaks secured) | Offensive pressure on the opponent's serve — the attacker's metric; great returners turn the most passive position in tennis (receiving) into a weapon that generates breaks |
| rtn_win_pct_B | Player B Return-Game Win Rate | % of return games Player B won (i.e. breaks secured) | Same for the opponent — a player who breaks frequently forces the server to play perfect tennis every game; one slip and they're down a break |
| tiebreaks_winrate_A | Player A Tiebreak Win Rate | % of tiebreaks Player A won | Mental toughness and clutch ability at 6-6 — tiebreaks remove nearly all technical advantage and come down to nerve; players who win tiebreaks consistently have the mental game to handle the highest pressure moments |
| tiebreaks_winrate_B | Player B Tiebreak Win Rate | % of tiebreaks Player B won | Same for the opponent — tiebreak ability is the single best proxy for how a player performs when one bad point can end a set |

### Head-to-Head
| Feature | Long Name | Definition | Why It Matters |
|---------|-----------|------------|----------------|
| A_h2h | Player A Head-to-Head Wins | Player A's prior wins vs Player B on this surface | Captures player-specific matchup dynamics that aggregate stats miss — certain playing styles are awkward for certain opponents regardless of ranking; a lower-ranked player can dominate H2H due to a favourable matchup |
| B_h2h | Player B Head-to-Head Wins | Player B's prior wins vs Player A on this surface | Same for the opponent — if one player has a 5-0 H2H record on clay, that pattern is a real signal, not noise; it reflects tactical and physical mismatches that persist over careers |
| days_since_h2h | Days Since Last Meeting | Days since their last meeting on this surface (-1 if never met) | Freshness of H2H information — a meeting last month is more informative than one five years ago; very old H2H records predate career-defining technique changes and may be misleading |

### Player Profile
| Feature | Long Name | Definition | Why It Matters |
|---------|-----------|------------|----------------|
| A_age | Player A Age | Player A's age in years at time of match | Affects stamina (especially best-of-5), peak physical window, and experience under pressure — players in their mid-to-late 20s tend to peak, while younger players can be inconsistent and older players fade physically |
| B_age | Player B Age | Player B's age in years at time of match | Same for the opponent — age mismatches matter most in five-set matches and late in tournaments when fatigue compounds |
| A_ht | Player A Height | Player A's height in cm | Taller players generate more serve leverage (higher contact point, sharper angles), especially on faster surfaces; height is also correlated with wingspan and reach for volleys |
| B_ht | Player B Height | Player B's height in cm | Same for the opponent — height advantages are most pronounced on serve-friendly surfaces like grass and fast hard courts |
| hand_A_L | Player A Left-Handed | Binary: 1 if Player A is left-handed | Left-handers have a natural tactical advantage — their wide serve lands in an unusual quadrant that right-handers rarely practice against; the spin patterns and angles from left-handed groundstrokes are also unfamiliar |
| hand_B_L | Player B Left-Handed | Binary: 1 if Player B is left-handed | Same for the opponent — statistically, about 10% of players are left-handed but they punch above their weight in win rates precisely because opponents see them infrequently |

### Form & Health (lagged)
| Feature | Long Name | Definition | Why It Matters |
|---------|-----------|------------|----------------|
| rank_improvement_A | Player A Ranking Improvement | Player A's ranking improvement over the prior year (positive = improved) | Trajectory signal — a rising player is gaining confidence, match practice, and is physically peaking; improvement indicates they are beating players they previously couldn't |
| rank_improvement_B | Player B Ranking Improvement | Player B's ranking improvement over the prior year (positive = improved) | Same for the opponent — a falling player may be dealing with undisclosed injury, form slumps, or motivational issues not yet reflected in current ranking |
| matches_played_A | Player A Matches Played | Total matches Player A played on this surface the prior year | Experience and workload indicator — more matches means more reliable lagged stats and more tournament reps on this surface; very few matches either means a new player, injury, or selective scheduling |
| matches_played_B | Player B Matches Played | Total matches Player B played on this surface the prior year | Same for the opponent — a player with 40+ clay matches has deep surface-specific conditioning and tactical library compared to someone with 8 |
| injured_during_swing_A | Player A Back-from-Absence Score | Score 0–1: how recently Player A returned from a retirement/walkover (1 = just returned, 0 = fully recovered) | Injury recency penalty — a player returning from injury within weeks may still be managing pain, physically underprepared, or mentally cautious; the score decays as months pass without incident |
| injured_during_swing_B | Player B Back-from-Absence Score | Score 0–1: how recently Player B returned from a retirement/walkover (1 = just returned, 0 = fully recovered) | Same for the opponent — interestingly the model weights opponent injury more than own injury, suggesting a healthy player benefits more from facing a compromised opponent than the injured player is penalised |

### Match Context
| Feature | Long Name | Definition | Why It Matters |
|---------|-----------|------------|----------------|
| surface_enc | Surface | Encoded surface: Hard / Clay / Grass | Surface changes the game so fundamentally that specialists exist for each — Nadal's clay dominance and Federer's grass record illustrate how surface-specific skills can override overall ranking |
| tourney_level_enc | Tournament Level | Encoded level: Grand Slam / Masters / 500 / 250 | Affects draw quality, prize money stakes, best-of format (Slams use best-of-5), and player motivation — top players prioritise Slams and Masters, meaning upsets are rarer there despite longer formats |
| round_ord | Tournament Round | Round of the tournament (R128 → Final) | Later rounds mean stronger opponents, but also more fatigue — the model learns that by the semi-finals, even unseeded players have beaten several ranked opponents to get there |
| best_of | Best-of Format | Best-of-3 or Best-of-5 matches | Longer matches disproportionately favour fitter, more consistent players — upsets are significantly rarer in best-of-5 because the better player has more chances to correct a bad start |

## Output Format

Write to models/prediction_report.md:

```
# ATP Match Prediction — Signal Report

**Generated:** {date}
**Model:** XGBoost | decay_rate={x} | max_depth={x} | min_child_weight={x} | learning_rate={x}
**Val AUC (2024):** {x} | **Val Accuracy:** {x}% | **Best iteration:** {x}

---

## What is Decision Weight?

Decision weight (%) measures how much of the model's total predictive power
comes from each signal. Out of every 100 decisions the model makes about who
wins, this is roughly how many were primarily driven by that feature.
Technically it is the share of total XGBoost information gain — how much each
feature narrows down the likely winner across all splits in all trees.

---

## Top 20 Signals

| Rank | Feature | Decision Weight | Category | What it means in tennis |
|------|---------|----------------|----------|--------------------------|
| 1 | ... | x.x% | ... | ... |
...

---

## All Signals

| Feature | Long Name | Decision Weight | Definition | Why It Matters |
|---------|-----------|----------------|------------|----------------|
| A_rank | Player A ATP Ranking | x.x% | ... | ... |
...
(list ALL features from feature_importance.csv, ordered by decision weight descending)

---

## Interpretation

3-5 sentences on what the signal breakdown reveals about what drives
match outcomes in ATP tennis. Flag any surprising findings.
```
