# ATP Tennis Predictor

> Predicts ATP match win probabilities and simulates full tournament draws using XGBoost trained on 2018–2024 historical match data.

---

## What are Claude Skills?

A Claude Skill is a markdown file that orchestrates a repeatable workflow — freeing us to focus on core problem-solving while routine tasks execute consistently according to defined specifications.

Without a skill, Claude pattern-matches to what the output *historically looked like* — not what is *correct for our specific context.* In quantitative and data-driven work, this is how silent errors happen: a plausible but slightly wrong formula runs without raising an exception, but produces wrong numbers.

**Skills guardrail against this** by encoding first principles thinking directly into the instruction set — so Claude cannot pattern-match its way into a plausible but incorrect answer.

---

## Summary of Skills in Project

| # | Skill | Purpose |
|---|-------|---------|
| 1 | Data Check | Validate incoming ATP CSV data before cleaning |
| 2 | Prediction Report | Generate a signal report from feature importance scores |
| 3 | Player Tournament Prediction | Run a full Monte Carlo simulation for a player in a tournament |
| 4 | Refactoring | Enforce loose coupling and single-source-of-truth |
| 5 | README Update | Maintain this document to a consistent standard |

---

## Pipeline Integration

| Step | Stage | Skill |
|------|-------|-------|
| 1 | Ingestion | Data Check Skill (blocking) |
| 2 | Feature Generation | Refactoring Skill enforced |
| 3 | Training | Prediction Report Skill auto-generated |
| 4 | Simulation | Player-Tournament Prediction Skill invoked |

---

## 1. Data Check

**First principles:** ATP match CSVs change silently between years — new columns appear, dtypes shift, columns are renamed.

Without an explicit check at ingestion compared to data from previous years, these changes propagate invisibly through a 5-step pipeline and corrupt features with no error message.

By the time the model produces a wrong prediction, the source of the error is buried 3 files deep.

**Invoke:** `run the data check skill`

<details>
<summary><strong>Sample output</strong></summary>

```
2024 ATP Matches Data Check

Columns received: 49
New columns:      None
Missing columns:  None
Data type changes: None

Status: PASS
```

</details>

---

## 2. Prediction Report

**First principles:** Model outputs are only useful if they are consistently structured and interpretable.

This skill enforces a fixed reporting structure so every model produces a decision-ready summary of both configuration and learned signals:
- a consistent set of core hyperparameters
- a standardised view of model performance
- a ranked list of top signals for interpretation

**Invoke:** `invoke the prediction report skill`

<details>
<summary><strong>Sample output</strong></summary>

```
ATP Match Prediction — Signal Report

Model: XGBoost | decay_rate=0.7 | max_depth=5 | min_child_weight=5
Val AUC (2024): 0.7180 | Val Accuracy: 65.54% | Best iteration: varies

Top 5 Signals (Paired):
 1. rank_pts_diff         11.80%  — Ranking Points Gap
 2. rank_diff              4.30%  — ATP Ranking Gap
 3. rank_pts (A+B)         3.97%  — Player Ranking Points
 4. wins_last5 (A+B)       3.65%  — Recent Form
 5. seed (A+B)             3.44%  — Tournament Seeding
```

</details>

---

## 3. Player Tournament Prediction

**First principles:** Tournament simulation must satisfy **Temporal validity**
- Predictions must be based only on information available at the time.
- A tournament in year Y must use a model trained on data up to year Y−1, otherwise future match outcomes leak into the prediction.
- The skill enforces this by ensuring the correct train–test split is applied during simulation, preventing any leakage of future information.

**Standardised Output design:**
The skill standardises how results are presented, ensuring outputs are interpretable and directly usable for decisions such as player selection and match outcome evaluation.

**Invoke:** `Medvedev Australian Open 2024` or `Simulate Djokovic Roland Garros 2023`

<details>
<summary><strong>Sample output</strong></summary>

```
Daniil Medvedev: Australian Open 2024 Chances
5000 simulations · Hard · Grand Slam

───────────────────────────────
Possible Path
───────────────────────────────
Round 128 : Terence Atmane                                              P(win): 87%
Round 64  : Emil Ruusuvuori (59%) or Patrick Kypson (28%)               P(win): 84%
Round 32  : Felix Auger-Aliassime (34%) or Hugo Grenier (17%)           P(win): 82%
Round 16  : Grigor Dimitrov (22%) or Alejandro Davidovich Fokina (13%)  P(win): 79%
QF        : Holger Rune (11%) or Hubert Hurkacz (10%)                   P(win): 74%
SF        : Carlos Alcaraz (14%) or Alexander Zverev (6%)               P(win): 58%
Final     : Novak Djokovic (8%) or Jannik Sinner (4%)                   P(win): 53%

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
Expected exit     : SF
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

---

## 4. Refactoring

**First principles:** In a multi-file pipeline (cleaning → features → aggregation → build_dataset → train), adding one new feature requires coordinated changes across 4–5 files.

Without a single source of truth, updates can be missed:
- features can exist in one file but not another
- column mismatches silently introduce NaNs
- errors only appear during model training

This skill enforces a single source of truth for features and shared logic, so that:
- each feature is defined in only one place
- all downstream components reference that definition
- adding or modifying a feature requires changing only one file

**Invoke:** `invoke the refactoring skill`

<details>
<summary><strong>Sample output</strong></summary>

```
Refactoring Report

What was refactored: H2H last-5 feature implementation

Files affected:
| File                 | Change                                                       | Reason                                             |
|----------------------|--------------------------------------------------------------|----------------------------------------------------|
| src/features.py      | _update_h2h now tracks last5 deque                          | Single source of truth for all H2H state           |
| src/simulator.py     | compute_h2h_lookup returns (surface_h2h, overall_h2h) tuple | Mirrors features.py convention; no duplication     |
| src/build_dataset.py | Added h2h_last5 / h2h_last5_surface to PLAYER_ATTRS         | One place defines what columns map to A/B          |
| models/train_xgb.py  | Added 4 new features after days_since_h2h                   | FEATURES list is the single source of column order |

Before vs After:
- Before: H2H state tracked surface-only wins; last-5 required re-scanning all history
- After: FIFO deque (maxlen=5) updated in-place; last5_sequence stored as space-separated
  string ("1 0 1 1 0") in both CSVs so future updates are a single append + drop

What this enables:
- Adding last-5 for a new match: append to last5_sequence, recompute A_wins_last5 only
- Adding a new H2H feature: extend the deque or add a new column to _update_h2h only
```

</details>

---

## 5. README Update

**First principles:** This project is about showcasing the use of Claude AI Skills. Without a prescribed structure, README content drifts toward generic project conventions that do not communicate what is actually distinctive about the project: setup guides, architecture diagrams and hyperparameter tables.

This skill defines a fixed template so each invocation produces the same sections in the same order, and mandates that technical details are excluded unless they directly explain a skill.

**Invoke:** `invoke the readme update skill`

<details>
<summary><strong>Sample output</strong></summary>

```
Invoked after: What are Claude Skills? description updated

Changes made:
  - Reframed skills description: "orchestrates a repeatable workflow —
    freeing us to focus on core problem-solving" replaces generic codifies
  - Silent errors made concrete: "a plausible but slightly wrong formula
    runs without raising an exception, but produces wrong numbers"
  - readme-update skill template updated to match
  - README refreshed to match updated template

Skills section verified: all 5 skills present with first principles,
invoke command, and sample output dropdown.
```

</details>
