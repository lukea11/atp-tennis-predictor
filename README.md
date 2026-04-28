# ATP Tennis Predictor

> Predicts ATP match win probabilities and simulates full tournament draws using XGBoost trained on 2018–2024 historical match data.

---

## What are Claude Skills?

A Claude Skill is a markdown file that codifies a repeatable workflow — instructions an agent references to produce consistent, standardized output.

**The skill is a bridge:**
> Closing the gap between what Claude produces by default and what our standards actually require.

Without a skill, Claude pattern-matches to what the output *historically looked like* — not what is *correct for our specific context.* This is dangerous in quantitative and data-driven work, where a convincing but slightly wrong formula still runs without errors, but produces wrong numbers.

**Skills guardrail against this** by encoding first principles thinking directly into the instruction set — so Claude cannot pattern-match its way into a plausible but incorrect output.

---

## Skills in this project

| # | Skill | Purpose |
|---|-------|---------|
| 1 | [Data Check](#data-check) | Validate incoming ATP CSV data before cleaning |
| 2 | [Prediction Report](#prediction-report) | Generate a signal report from feature importance scores |
| 3 | [Player Tournament Prediction](#player-tournament-prediction) | Run a full Monte Carlo simulation for a player in a tournament |
| 4 | [Refactoring](#refactoring) | Enforce loose coupling and single-source-of-truth |
| 5 | [README Update](#readme-update) | Maintain this document to a consistent standard |

---

<details>
<summary><strong>1. Data Check</strong></summary>

**First principles:** ATP match CSVs change silently between years — new columns appear, dtypes shift, columns are renamed. Without an explicit check at ingestion, these changes propagate invisibly through a 5-step pipeline and corrupt features with no error message. By the time the model produces a wrong prediction, the source of the error is buried 3 files deep.

The skill enforces a fixed contract: compare every column name and dtype against the expected schema, flag any deviation, and block the pipeline until the issue is resolved.

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

</details>

---

<details>
<summary><strong>2. Prediction Report</strong></summary>

**First principles:** Feature importance numbers exist in `feature_importance.csv` — they are the ground truth. Without a skill, an LLM will pattern-match to what a "typical" feature importance report looks like and invent plausible-sounding weights and feature names that do not match the actual file. In a 69-feature model, this error is undetectable without cross-referencing the source.

The skill reads directly from `feature_importance.csv`, computes each feature's share of total XGBoost information gain, and maps code names to human-readable tennis descriptions. No estimation — every number is derived from the file.

**Invoke:** `invoke the prediction report skill`

<details>
<summary><strong>Sample output</strong></summary>

```
ATP Match Prediction — Signal Report

Model: XGBoost | decay_rate=0.7 | max_depth=5 | min_child_weight=5
Val AUC (2024): 0.7180 | Val Accuracy: 65.54% | Best iteration: varies

Top 5 Signals:
 1. rank_pts_diff         11.80%  — Ranking Points Gap
 2. rank_diff              4.30%  — ATP Ranking Gap
 3. hand_A_L               2.29%  — Player A Left-Handed
 4. A_rank_pts             2.21%  — Player A Ranking Points
 5. B_seed                 2.09%  — Player B Seeding
```

</details>

</details>

---

<details>
<summary><strong>3. Player Tournament Prediction</strong></summary>

**First principles:** A tournament bracket has hard structural constraints — each player occupies exactly one section of the draw relative to the target player, so the same opponent cannot appear in two different rounds. Without explicit rules, an LLM generates probability estimates and opponent lists that look realistic but violate these constraints. The skill also enforces a model cutoff rule: a tournament in year Y must use a model trained only on data through year Y−1, otherwise the simulation leaks future match outcomes into the prediction.

**Invoke:** Natural language trigger — e.g. `Medvedev Australian Open 2024` or `simulate Djokovic Roland Garros 2023`

<details>
<summary><strong>Sample output</strong></summary>

```
Daniil Medvedev: Australian Open 2024 Chances
5000 simulations · Hard · Grand Slam

───────────────────────────────
Possible Path
───────────────────────────────
Round 128 : Terence Atmane                                         P(win): 87%
Round 64  : Emil Ruusuvuori (59%) or Patrick Kypson (28%)          P(win): 84%
Round 32  : Felix Auger-Aliassime (34%) or Hugo Grenier (17%)      P(win): 82%
Round 16  : Grigor Dimitrov (22%) or Alejandro Davidovich Fokina   P(win): 79%
QF        : Holger Rune (11%) or Hubert Hurkacz (10%)              P(win): 74%
SF        : Carlos Alcaraz (14%) or Alexander Zverev (6%)          P(win): 58%
Final     : Novak Djokovic (8%) or Jannik Sinner (4%)              P(win): 53%

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

</details>

---

<details>
<summary><strong>4. Refactoring</strong></summary>

**First principles:** In a multi-file pipeline (cleaning → features → aggregation → build_dataset → train), adding one new feature requires coordinated changes across 4–5 files. Without a single source of truth, updates are missed: a feature added to `features.py` but not to `train_xgb.py` causes a silent NaN column; a column renamed in `cleaning.py` but not in `build_dataset.py` breaks the join with no error until model training. The skill enforces one rule: every shared constant lives in one place so adding a feature touches one file.

**Invoke:** `invoke the refactoring skill`

<details>
<summary><strong>Sample output</strong></summary>

```
Refactoring Report

What was refactored: H2H last-5 feature implementation

Files affected:
| File                | Change                                              | Reason                                      |
|---------------------|-----------------------------------------------------|---------------------------------------------|
| src/features.py     | _update_h2h now tracks last5 deque                  | Single source of truth for all H2H state    |
| src/simulator.py    | compute_h2h_lookup returns (surface_h2h, overall_h2h) tuple | Mirrors features.py convention; no logic duplication |
| src/build_dataset.py | Added h2h_last5 / h2h_last5_surface to PLAYER_ATTRS | One place defines what columns map to A/B   |
| models/train_xgb.py | Added 4 new features after days_since_h2h           | FEATURES list is the single source of column order |

Before vs After:
- Before: H2H state tracked surface-only wins; last-5 required re-scanning all history
- After: FIFO deque (maxlen=5) updated in-place; last5_sequence stored as space-separated
  string ("1 0 1 1 0") in both CSVs so future updates are a single append + drop

What this enables:
- Adding last-5 for a new match: append to last5_sequence, recompute A_wins_last5 only
- Adding a new H2H feature: extend the deque or add a new column to _update_h2h only
```

</details>

</details>

---

<details>
<summary><strong>5. README Update</strong></summary>

**First principles:** Without a prescribed structure, README content drifts toward generic project conventions — setup guides, architecture diagrams, hyperparameter tables — none of which communicate what is actually distinctive about the project. The skill defines a fixed template so each invocation produces the same sections in the same order, and mandates that technical details are excluded unless they directly explain a skill.

**Invoke:** `invoke the readme update skill`

<details>
<summary><strong>Sample output</strong></summary>

```
Invoked after: readme-update skill updated with per-skill dropdowns
               and visible table of contents

Changes made:
  - Table of contents kept always visible with skill numbers
  - Each skill section wrapped in a numbered <details> dropdown
  - Sample output remains as nested <details> inside each skill
  - "What are Claude Skills?" section kept as plain visible text

Skills section verified: all 5 skills present with first principles,
invoke command, and sample output — TOC visible, content collapsed.
```

</details>

</details>
