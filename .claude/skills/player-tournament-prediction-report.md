# Player Tournament Prediction Report Skill

## When to trigger
When the user asks for a prediction or simulation for a specific player in a
specific tournament, e.g. "Alcaraz 2024 Australian Open" or "simulate Djokovic
Roland Garros 2023".

## Arguments (parse from user message)
- `player_name` — full or partial name, case-insensitive
- `tournament_name` — partial tournament name, case-insensitive
- `year` — 4-digit year
- `n_sims` — number of simulations (default 5000)

## Error handling before running simulation

### Wrong player name
If `_resolve_player` raises ValueError with "Did you mean":
→ Reply: "Do you mean **[suggested name]**? Re-run with the correct name."

If it raises "No player named":
→ Reply: "There are no players with this name in the [Tournament Name] draw. Try again."

### Wrong tournament name
If `find_tournament` raises ValueError with "No tournament found":
→ Reply: "No tournament matching '[name]' found for [year]. Try the full or partial tournament name (e.g. 'Australian Open', 'Roland Garros', 'Wimbledon', 'US Open')."

If it raises "Ambiguous":
→ Reply: "Multiple tournaments match '[name]': [list]. Be more specific."

## Temporal validity (no leakage)

Every data source is cut off at the tournament start date — no future information enters the simulation:

| Data source | Cutoff |
|---|---|
| Model training | All matches with `tourney_date < tournament start date` |
| Lagged serve/win stats | Full prior-year surface aggregates (year Y−1) |
| H2H record | All matches with `tourney_date < tournament start date` |
| Form (streak, wins_last5) | All matches with `tourney_date < tournament start date` |
| Tournament history | All editions with `tourney_date < tournament start date` |

The simulator enforces all cutoffs automatically. For model training, it
checks for a date-specific model (`xgb_model_thruYYYYMMDD.json`) and trains
one if absent — so results from the tournament immediately before (e.g. Rome)
are included when predicting the next (e.g. Roland Garros). Tournaments
beyond the default training window use the default model.

Note: lagged serve/win stats remain full prior-year aggregates (year Y−1),
consistent with how the model was trained — a known limitation.

## Process
1. Run the simulation (model selection is automatic):
   ```
   python3 src/simulator.py "<player_name>" "<tournament_name>" <year> \
       --n-sims <n_sims>
   ```

2. Parse the JSON output. Extract:
   - `actual_path` — use `actual_path['R128']` (or the first round) for the fixed draw opponent
   - `opponent_counts` — for top-2 opponents per round (by simulation frequency)
   - `round_probs` — compute P(win) for each round as a conditional probability:
     `P(win round R) = round_probs[next_round] / round_probs[R]`
     For the final round: `P(win) = win_probability`
   - `win_probability` — overall tournament win probability
   - `expected_exit` — expected exit round
   - `draw_attrs` — player feature values for citation in commentary

4. Format the report as described below.

## Opponent display rules
- **R128**: Show actual draw opponent (or BYE). Always 1 opponent — it's fixed by the draw.
- **R64**: Show top 2 most likely opponents from simulation with their frequency %.
- **R32 onward**: Show top 2 most likely opponents by occurrence count in simulations.
- Format frequency as: `[Name] (seen in X% of simulations)`

## Cross-round deduplication (CRITICAL)
The bracket structure guarantees that each player occupies exactly one section
relative to the target player — a player who could be the QF opponent cannot
also be an SF or Final opponent, because meeting them in the QF eliminates one
of them. Therefore:

**A player's name must NEVER appear in more than one round row.**

When selecting top-2 opponents for each round, process rounds in order
(R128 → Final) and exclude any player already shown in an earlier round.
In practice the simulation already enforces this (bracket sections are
disjoint), but always verify the output before displaying.

## Report format

```
<Player Full Name>: <Tournament Name> <Year> Chances
<n_sims> simulations · <Surface> · <Level>

───────────────────────────────
Possible Path
───────────────────────────────
Round 128 : <Opponent Name> [or BYE]                          P(win): XX%
Round 64  : <Name A> (X%) or <Name B> (Y%)                   P(win): XX%
Round 32  : <Name A> (X%) or <Name B> (Y%)                   P(win): XX%
Round 16  : <Name A> (X%) or <Name B> (Y%)                   P(win): XX%
QF        : <Name A> (X%) or <Name B> (Y%)                   P(win): XX%
SF        : <Name A> (X%) or <Name B> (Y%)                   P(win): XX%
Final     : <Name A> (X%) or <Name B> (Y%)                   P(win): XX%

───────────────────────────────
Toughest Round
───────────────────────────────
The toughest expected obstacle is the <Round> against <most frequent high-rank
opponent at that round>. The model gives <Player> a <X%> chance in that matchup.
[Cite 2 features: e.g. "Alcaraz's sv_gms_won_pct (service hold rate) of 87% on
hard courts vs Djokovic's bp_save_pct (break-point save rate) of 68% suggests
the serve battle will be decisive. Alcaraz's rank_improvement (+45 places) over
2023 shows upward trajectory, but Djokovic's completed_winrate of 83% on hard
courts sets the bar."]

───────────────────────────────
Summary
───────────────────────────────
Expected exit     : <Round>
P(win <round>)    : XX%  ← conditional win probability in that round (P(win next round) / P(win this round))
Toughest match    : <Round> vs <Opponent> (X% win probability)
P(win tournament) : XX%

[Plain-English paragraph: 3–4 sentences explaining the overall outlook.
Use full feature names in parentheses when citing stats — e.g.
"service hold rate (sv_gms_won_pct)" — so the report is self-contained.
Cite at least 2 supporting features for the overall assessment. Avoid
hedging language like "might" or "could potentially"; state probabilities
directly.]
```

## Feature citation rules
- Always cite features by both code name and long name:
  `service hold rate (sv_gms_won_pct)`
- Minimum 2 features cited per report (required for every report)
- Preferred features to cite (use whichever are most decisive):
  - `sv_gms_won_pct` (service hold rate)
  - `completed_winrate` (completed-match win rate)
  - `rank_improvement` (ranking trajectory)
  - `first_serve_win_pct` (first-serve points won)
  - `rtn_win_pct` (return-game win rate)
  - `bp_save_pct` (break-point save rate)
  - `win_rate` (surface win rate)
  - `tourney_titles` (prior titles at this tournament)
  - `tourney_win_rate` (historical win rate at this tournament)
  - Player rank / rank points
- Retrieve feature values from the simulation's `draw_attrs` and `lagged_stats`
  for the specific tournament year/surface.

## Tournament history data limitation
Tournament history features (`tourney_titles`, `tourney_win_rate`, `tourney_matches`)
are computed from match data starting in **2018 only**. Titles won before 2018 are
invisible to the model. When citing these features, always note the 2018 cutoff:

  Example: "Djokovic's tournament title count (tourney_titles) of 4 at Wimbledon
  reflects his wins in 2018, 2019, 2021, and 2022 — the model does not see his
  earlier titles (2011, 2014, 2015). His true total entering 2023 was 7."

This matters most for legends with long careers (Djokovic, Federer, Nadal, Serena).
Always cross-reference against the player's actual career record when writing the
Toughest Round or Summary commentary.

## Maximum round for a tournament
Determine the correct round labels from the draw size:
- 128-draw (Grand Slams): R128 → R64 → R32 → R16 → QF → SF → F
- 96/64-draw (Masters): R64 → R32 → R16 → QF → SF → F (some players start R64, some R128)
- 32-draw (250/500): R32 → R16 → QF → SF → F
Omit rounds that do not exist for the tournament. Check `tourney_info['first_round']`
from the simulation output to determine the starting round.
