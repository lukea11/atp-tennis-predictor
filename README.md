# ATP Tennis Predictor

> Predicts ATP match win probabilities and simulates full tournament draws using XGBoost trained on 2018–2024 historical match data.

---

## The Role of Claude AI Skills

This project is built around the principle of **systematising the known so human judgment is reserved for the unknown.**

Claude Skills are markdown instruction files that Claude Code references to produce consistent, standardised outputs for repeatable workflows — eliminating the need to re-explain processes and ensuring quality every time.

### Why skills and not just prompts?

Without a skill:
> "Hey Claude, check this data for me"  
→ Different output every time, inconsistent quality

With a skill:
> "Run the data check skill"  
→ Same structured report every time, catches the same issues every time, in the same format every time

### Skills in this project

| Skill | File | Purpose |
|-------|------|---------|
| Data Check | `.claude/skills/data-check.md` | Validate incoming ATP CSV data before cleaning — catches missing columns, dtype changes, and data quality issues |
| Prediction Report | `.claude/skills/prediction-report.md` | Generate a signal report from `feature_importance.csv` showing each feature's decision weight and what it means in tennis terms |
| Player Tournament Prediction | `.claude/skills/player-tournament-prediction-report.md` | Run a full Monte Carlo simulation for a player in a specific tournament and produce a structured prediction report with round-by-round probabilities |
| Refactoring | `.claude/skills/refactoring.md` | Enforce loose coupling and single-source-of-truth — ensures adding a new feature only requires touching one place |
| README Update | `.claude/skills/readme-update.md` | Maintain this document to a consistent standard after any meaningful project change |

### Sample skill outputs

<details>
<summary><strong>Data Check</strong> — run when a new year's CSV is loaded</summary>

```
2024 ATP Matches Data Check

Columns received: 49
New columns:      None
Missing columns:  None
Data type changes: None

Status: PASS
```
</details>

<details>
<summary><strong>Player Tournament Prediction</strong> — "Simulate Medvedev Australian Open 2024"</summary>

```
Daniil Medvedev: Australian Open 2024 Chances
5000 simulations · Hard · Grand Slam

───────────────────────────────
Possible Path
───────────────────────────────
Round 128 : Terence Atmane                                          P(win): 87%
Round 64  : Emil Ruusuvuori (59%) or Patrick Kypson (28%)          P(reach): 87%
Round 32  : Felix Auger-Aliassime (34%) or Hugo Grenier (17%)      P(reach): 73%
Round 16  : Grigor Dimitrov (22%) or Alejandro Davidovich Fokina   P(reach): 60%
QF        : Holger Rune (11%) or Hubert Hurkacz (10%)              P(reach): 47%
SF        : Carlos Alcaraz (14%) or Alexander Zverev (6%)          P(reach): 35%
Final     : Novak Djokovic (8%) or Jannik Sinner (4%)              P(reach): 20%

───────────────────────────────
Toughest Round
───────────────────────────────
The toughest expected obstacle is the Final against Novak Djokovic.
Djokovic's service hold rate (sv_gms_won_pct) of 91% on hard courts
and break-point save rate (bp_save_pct) of 74% make him the hardest
wall to get through — the model gives Medvedev a 53% conditional win
probability in that matchup.

───────────────────────────────
Summary
───────────────────────────────
Expected exit     : SF (last round with P(reach) ≥ 25% — P(reach) = 35%)
P(win SF)         : 58%
Toughest match    : Final vs Djokovic (53% win probability)
P(win tournament) : 11%

Medvedev is the model's pick to reach the SF on his best surface,
with a 35% chance of getting there and a 58% chance of winning once
he does. His service hold rate (sv_gms_won_pct) drives his high
win probabilities in early rounds, but the Final draw — likely
Djokovic — drops his tournament win ceiling to 11%.
```
</details>

<details>
<summary><strong>Prediction Report</strong> — top signals after training</summary>

```
# ATP Match Prediction — Signal Report

Model: XGBoost | decay_rate=1.0 | max_depth=4 | min_child_weight=5
Val AUC (2024): 0.7126 | Val Accuracy: 63.98% | Best iteration: varies

Top 5 Signals:
 1. rank_pts_diff         10.3%  — Ranking Points Gap
 2. rank_diff              4.7%  — ATP Ranking Gap
 3. A_rank_pts             2.4%  — Player A Ranking Points
 4. sv_gms_won_pct_A       2.2%  — Player A Service Hold Rate
 5. completed_winrate_A    2.1%  — Player A Completed-Match Win Rate
```
</details>

<details>
<summary><strong>Refactoring</strong> — after adding H2H last-5 features</summary>

```
### Refactoring Report

**What was refactored:** H2H last-5 feature implementation

**Files affected:**
| File | Change | Reason |
|------|--------|--------|
| src/features.py | _update_h2h now tracks last5 deque; compute_h2h maintains db_surface + db_overall | Single source of truth for all H2H state |
| src/simulator.py | compute_h2h_lookup returns (surface_h2h, overall_h2h) tuple | Mirrors features.py convention; no logic duplication |
| src/build_dataset.py | Added h2h_last5 / h2h_last5_surface to PLAYER_ATTRS | One place defines what columns map to A/B |
| models/train_xgb.py | Added 4 new features after days_since_h2h | FEATURES list is the single source of column order |

**Before vs After:**
- Before: H2H state tracked surface-only wins; last-5 required re-scanning all history
- After: FIFO deque (maxlen=5) updated in-place; last5_sequence stored as space-separated
  string ("1 0 1 1 0") in both CSVs so future updates are a single append + drop

**What this enables:**
- Adding last-5 for a new match: append to last5_sequence, recompute A_wins_last5 only
- Adding a new H2H feature: extend the deque or add a new column to _update_h2h only
```
</details>

<details>
<summary><strong>README Update</strong> — this document is the output</summary>

```
Invoked after: H2H last-5 feature addition, model retrain, bug fix
                in player tournament prediction sample output

Changes made:
  - Added H2H last-5 to feature categories table
  - Updated top-10 decision weight table (B_h2h_last5 now #7)
  - Replaced fabricated prediction sample with real simulation output
    for Medvedev AO 2024 (no duplicate players across rounds)
  - Added Refactoring and README Update skill sample outputs

Skills section verified: all 5 skills listed with purpose and sample.
```
</details>

---

## Pipeline

```
data/raw/                       ← ATP match CSVs (2018–2024)
    │
    ▼
src/cleaning.py                 → data/cleaned/atp_matches_cleaned.csv
    │   Remove Davis Cup, fix dtypes, standardise columns
    ▼
src/features.py                 → data/features/atp_features.csv
    │   H2H (surface + overall + last-5), tourney history,
    │   home advantage, form/momentum, serve/return stats
    ▼
src/aggregation.py              → data/aggregated/player_surface_year_stats.csv
    │   Per-player, per-surface, per-year stat aggregation
    ▼
src/build_dataset.py            → data/processed/model_dataset.csv
    │   Lag features by 1 year, assign player A/B (lower ID = A),
    │   Bayesian-smooth tournament win rates, encode surface/round
    ▼
models/train_xgb.py             → models/xgb_model.json
    │   XGBoost grid search with exponential recency decay weights
    ▼
src/simulator.py                ← Monte Carlo tournament simulation
```

### Data rules (always enforced)
- Davis Cup matches excluded — no ranking points, causes NaN cascades
- RET / W/O matches excluded from serve & return stat calculations
- Train/val split is always time-based — never random
- All rolling features computed as pre-match state (zero leakage)
- Player A is always the lower ATP player ID; H2H database uses the same convention

---

## Features (69 total)

All lagged stats use each player's prior-year same-surface stats to prevent data leakage.

### Top 10 by decision weight (share of model's total information gain)

| Rank | Feature | Decision Weight | What it measures |
|------|---------|----------------|-----------------|
| 1 | `rank_pts_diff` | 10.3% | Ranking points gap between the two players |
| 2 | `rank_diff` | 4.7% | ATP ranking gap |
| 3 | `A_rank_pts` | 2.4% | Player A's rolling 12-month ranking points |
| 4 | `sv_gms_won_pct_A` | 2.2% | Player A service hold rate (prior year, same surface) |
| 5 | `completed_winrate_A` | 2.1% | Player A win rate in fully completed matches |
| 6 | `win_rate_A` | 2.0% | Player A overall surface win rate (prior year) |
| 7 | `B_h2h_last5` | 2.0% | Player B wins in last 5 H2H meetings (any surface) |
| 8 | `B_wins_last5` | 1.9% | Player B wins in last 5 matches overall |
| 9 | `matches_played_B` | 1.8% | Player B matches played on this surface (prior year) |
| 10 | `A_tourney_win_rate` | 1.8% | Player A historical win rate at this tournament (2018+) |

### Feature categories

| Category | Features | Notes |
|----------|----------|-------|
| Matchup comparison | `rank_diff`, `rank_pts_diff` | Derived from player A/B ranks at match time |
| Rankings & seeding | `A/B_rank`, `A/B_rank_pts`, `A/B_seed` | Match-time values from the draw |
| H2H — cumulative | `A/B_h2h`, `days_since_h2h` | Surface-specific prior win counts |
| H2H — last 5 | `A/B_h2h_last5`, `A/B_h2h_last5_surface` | Overall and surface-specific last-5 win counts; raw FIFO sequence stored in `h2h_database.csv` (surface) and `h2h_database_overall.csv` (all surfaces) for easy future updates |
| Form & momentum | `A/B_win_streak`, `A/B_win_streak_surface`, `A/B_wins_last5` | Pre-match rolling state; surface streak resets on loss or surface change |
| Tournament history | `A/B_tourney_titles`, `A/B_tourney_win_rate`, `A/B_tourney_matches` | Bayesian-smoothed win rate (prior = 3 pseudo-matches); data from 2018 only — titles before 2018 are not visible to the model |
| Home advantage | `A/B_is_home` | Player IOC country code vs tournament host country |
| Serve performance | ace rate, df rate, 1st serve %, 1st/2nd serve win %, bp save %, sv games won % | Prior year, same surface |
| Return performance | return game win %, tiebreak win % | Prior year, same surface |
| Win rates | `win_rate`, `completed_winrate`, `strsets_rate` | Prior year, same surface |
| Health / trajectory | `rank_improvement`, `injured_during_swing`, `matches_played` | Prior year, same surface |
| Match context | `surface_enc`, `tourney_level_enc`, `round_ord`, `best_of` | Encoded at match time |
| Player profile | `A/B_age`, `A/B_ht`, `hand_A/B_L` | From the draw |

---

## Model

**Algorithm:** XGBoost binary classification — predicts P(player A wins), where player A = lower ATP player ID.

**Training:** Time-based splits only. Default model trains on 2019–2023 and validates on 2024. For simulating past tournaments, retroactive models (`xgb_model_thru{year}.json`) are trained to avoid future leakage.

**Recency weighting:** Exponential decay by year — `weight = decay_rate ^ (max_year − year)`. `decay_rate = 1.0` weights all years equally; lower values upweight recent seasons.

### Current best hyperparameters

| Parameter | Value |
|-----------|-------|
| `max_depth` | 4 |
| `min_child_weight` | 5 |
| `decay_rate` | 1.0 |
| `learning_rate` | 0.05 |
| `subsample` | 0.8 |
| `colsample_bytree` | 0.7 |
| `reg_lambda` | 3 |

### Validation performance (held-out 2024 season)

| Metric | Value |
|--------|-------|
| Accuracy | 63.98% |
| AUC | 0.7126 |
| Log-loss | 0.6193 |
| Brier score | 0.2155 |

---

## Usage

### Build the full pipeline

```bash
python3 src/cleaning.py
python3 src/features.py
python3 src/aggregation.py
python3 src/build_dataset.py
python3 models/train_xgb.py
```

### Simulate a tournament

```bash
python3 src/simulator.py "Alcaraz" "Roland Garros" 2024 --n-sims 5000
```

Output is JSON: round-by-round reach probabilities, opponent frequencies by round, expected exit, and tournament win probability.

### Train a retroactive model (leakage-free for past tournaments)

```bash
# Train through 2022 to simulate any 2023 tournament
python3 models/train_xgb.py --train-through 2022

python3 src/simulator.py "Djokovic" "Australian Open" 2023 \
    --n-sims 5000 \
    --model-path models/xgb_model_thru2022.json
```

---

## Project Structure

```
atp-tennis-predictor/
├── data/
│   ├── raw/                        ATP match CSVs (2018–2024)
│   ├── cleaned/                    Cleaned match data
│   ├── features/                   Feature-enriched matches + H2H databases
│   ├── aggregated/                 Per-player surface-year stats
│   └── processed/                  Model-ready dataset
├── models/
│   ├── train_xgb.py                Grid search + training script
│   ├── xgb_model.json              Default model (trained through 2023)
│   ├── xgb_model_thru2022.json     Retroactive model for 2023 simulations
│   ├── feature_importance.csv      Feature gain scores
│   └── best_params.json            Best hyperparameters
├── src/
│   ├── cleaning.py                 Raw CSV cleaning
│   ├── features.py                 Feature engineering (H2H, form, home advantage)
│   ├── aggregation.py              Per-player stat aggregation
│   ├── build_dataset.py            Model dataset construction
│   ├── build_draw.py               Tournament bracket builder
│   └── simulator.py                Monte Carlo tournament simulator
└── .claude/
    └── skills/                     Claude AI skill definitions
```

---

## Data Source

[Jeff Sackmann's tennis_atp repository](https://github.com/JeffSackmann/tennis_atp) — ATP tour matches 2018–2024.  
~16,000 raw matches → ~10,800 model rows (after year-lag filtering).
