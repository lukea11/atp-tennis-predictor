# Player Tournament Prediction Report Skill

## When to trigger
When the user asks for a prediction or simulation for a specific player in a
specific tournament, e.g. "Alcaraz 2024 Australian Open" or "simulate Djokovic
Roland Garros 2023".

## Arguments (parse from user message)
- `player_name` — full or partial name, case-insensitive
- `tournament_name` — partial tournament name, case-insensitive
- `year` — 4-digit year
- `n_sims` — number of simulations (default 1500)

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

## Process
1. Run the simulation:
   ```
   python3 src/simulator.py "<player_name>" "<tournament_name>" <year> --n-sims <n_sims>
   ```
   Parse the JSON output.

2. Get per-round win probabilities by calling `build_feature_row` for the
   likely opponent in each round and using `predict_proba` from the model.
   For the actual R128 opponent (known from the draw): compute exact win prob.
   For subsequent rounds: use the simulation opponent counts to find the top 2
   most frequent opponents.

3. Format the report as described below.

## Opponent display rules
- **R128**: Show actual draw opponent (or BYE). Always 1 opponent — it's fixed by the draw.
- **R64**: Show top 2 most likely opponents from simulation with their frequency %.
- **R32 onward**: Show top 2 most likely opponents by occurrence count in simulations.
- Format frequency as: `[Name] (seen in X% of simulations)`

## Report format

```
<Player Full Name>: <Tournament Name> <Year> Chances
<n_sims> simulations · <Surface> · <Level>

───────────────────────────────
Possible Path
───────────────────────────────
Round 128 : <Opponent Name> [or BYE]                          P(win): XX%
Round 64  : <Name A> (X%) or <Name B> (Y%)                   P(reach): XX%
Round 32  : <Name A> (X%) or <Name B> (Y%)                   P(reach): XX%
Round 16  : <Name A> (X%) or <Name B> (Y%)                   P(reach): XX%
QF        : <Name A> (X%) or <Name B> (Y%)                   P(reach): XX%
SF        : <Name A> (X%) or <Name B> (Y%)                   P(reach): XX%
Final     : <Name A> (X%) or <Name B> (Y%)                   P(reach): XX%

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
Expected exit     : <Round> (most common exit in simulations, X% of runs)
P(win <round>)    : XX%  ← probability of winning the expected exit round
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
  - Player rank / rank points
- Retrieve feature values from the simulation's `draw_attrs` and `lagged_stats`
  for the specific tournament year/surface.

## Maximum round for a tournament
Determine the correct round labels from the draw size:
- 128-draw (Grand Slams): R128 → R64 → R32 → R16 → QF → SF → F
- 96/64-draw (Masters): R64 → R32 → R16 → QF → SF → F (some players start R64, some R128)
- 32-draw (250/500): R32 → R16 → QF → SF → F
Omit rounds that do not exist for the tournament. Check `tourney_info['first_round']`
from the simulation output to determine the starting round.
