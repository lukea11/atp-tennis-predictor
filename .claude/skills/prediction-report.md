# Prediction Report Skill

## When to trigger
After every training and evaluation run — whenever models/feature_importance.csv
and models/best_params.json have been updated.

## Process
1. Read models/feature_importance.csv
2. Read models/best_params.json
3. Compute Decision Weight (%) = each feature's gain / total gain × 100
4. Group features into categories (see mapping below)
5. Write the report to models/prediction_report.md using the Output Format

## Terminology
**Decision weight (%)** — the percentage of the model's total information gain
contributed by this signal. Think of it as: out of every 100 decisions the model
makes about who wins, how many were primarily driven by this signal?
This is more precise than "explains variance" — it reflects how much each feature
narrows down the likely winner across all splits in all trees.

## Feature → Tennis meaning mapping

### Rankings & Seeding
| Feature | Tennis meaning |
|---------|----------------|
| A_rank / B_rank | ATP world ranking — the single best objective summary of a player's quality at the time of the match |
| A_rank_pts / B_rank_pts | Ranking points accumulated over the rolling 12 months — captures recent form better than raw rank; a player who just won a major has high points before the ranking updates |
| A_seed / B_seed | Tournament seeding — confirms elite status within the draw; unseeded players face tougher early draws |

### Win Rate Signals (lagged — prior year, same surface)
| Feature | Tennis meaning |
|---------|----------------|
| win_rate_A / win_rate_B | % of matches won on this surface the prior year — overall surface-specific form |
| completed_winrate_A / B | Win rate in fully completed matches only (no retirements) — cleaner quality signal, removes free wins from opponent injury |
| strsets_rate_A / B | % of wins that were straight sets — dominance indicator; winning without dropping a set means the player was rarely troubled |

### Serve Performance (lagged — prior year, same surface)
| Feature | Tennis meaning |
|---------|----------------|
| sv_gms_won_pct_A / B | % of service games held — the most direct measure of serve dominance; holding serve consistently is the foundation of ATP tennis |
| first_serve_win_pct_A / B | % of points won when first serve lands in — quality of the first delivery; a high value means the first serve is a genuine weapon |
| second_serve_win_pct_A / B | % of points won on second serve — resilience when first serve misses; exposes vulnerability under pressure |
| bp_save_pct_A / B | % of break points saved — clutch performance under the highest serve pressure |
| first_serve_pct_A / B | % of first serves in — consistency; erratic first serves force a player onto the weaker second delivery repeatedly |
| ace_rate_A / B | Aces per serve point — free point generation; surface-dependent (higher on grass/fast hard) |
| df_rate_A / B | Double faults per serve point — unforced serve errors; doubles under pressure signal nerves |

### Return Performance (lagged — prior year, same surface)
| Feature | Tennis meaning |
|---------|----------------|
| rtn_win_pct_A / B | % of return games won (i.e., breaks secured) — offensive pressure on the opponent's serve; the attacker's metric |
| tiebreaks_winrate_A / B | % of tiebreaks won — mental toughness and clutch ability at 6-6; often separates players of similar rank |

### Head-to-Head
| Feature | Tennis meaning |
|---------|----------------|
| A_h2h / B_h2h | Prior wins vs this specific opponent on this surface — captures player-specific matchup dynamics that aggregate stats miss (e.g. awkward playing styles) |
| days_since_h2h | Days since their last meeting on this surface — freshness of H2H information; -1 if they have never met on this surface |

### Player Profile
| Feature | Tennis meaning |
|---------|----------------|
| A_age / B_age | Player age — affects stamina (especially best-of-5), peak physical window, and experience handling pressure |
| A_ht / B_ht | Height — taller players generate more serve leverage, especially on faster surfaces |
| hand_A_L / hand_B_L | Left-handedness — lefties have a natural tactical advantage: wide serve to the deuce court, and opponents rarely practice against left-handed spin patterns |

### Form & Health (lagged)
| Feature | Tennis meaning |
|---------|----------------|
| rank_improvement_A / B | Ranking improvement over the prior year — trajectory signal; a rising player is gaining confidence and match practice |
| matches_played_A / B | Total matches played on this surface the prior year — experience and workload; more matches also means more reliable lagged stats |
| injured_during_swing_A / B | Back-from-absence score (0–1) — how recently the player returned from a retirement/walkover; 1 = just came back, 0 = fully recovered |

### Match Context
| Feature | Tennis meaning |
|---------|----------------|
| surface_enc | Surface (Hard / Clay / Grass) — surface changes the game so fundamentally that specialists exist for each; Simpson's paradox applies (a player can have a better overall record but lose on a specific surface) |
| tourney_level_enc | Tournament level (Grand Slam / Masters / 500 / 250) — affects draw quality, prize money stakes, and best-of format |
| round_ord | Round of the tournament (R128 → Final) — later rounds mean stronger opponents and higher-stakes pressure |
| best_of | Best-of-3 vs best-of-5 — longer matches disproportionately favour fitter, more consistent players; upsets are rarer in best-of-5 |

## Output Format

Write to models/prediction_report.md:

```
# ATP Match Prediction — Signal Report

**Generated:** {date}
**Model:** XGBoost | decay_rate={x} | max_depth={x} | min_child_weight={x}
**Val AUC (2024):** {x} | **Val Accuracy:** {x}% | **Best iteration:** {x}

---

## What is Decision Weight?

Decision weight (%) measures how much of the model's total predictive power
comes from each signal. Out of every 100 decisions the model makes about who
wins, this is roughly how many were primarily driven by each feature.

---

## Top 20 Signals

| Rank | Feature | Decision Weight | Category | What it means in tennis |
|------|---------|----------------|----------|--------------------------|
| 1 | ... | x.x% | Rankings | ... |
...

---

## By Category (summed decision weight)

| Category | Total Weight | Key signals |
|----------|-------------|-------------|
| Rankings & Seeding | x.x% | ... |
| Serve Performance | x.x% | ... |
...

---

## Interpretation

3-5 sentences on what the category breakdown reveals about what drives
match outcomes in ATP tennis. Flag any surprising findings.
```
