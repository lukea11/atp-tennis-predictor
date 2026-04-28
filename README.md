# ATP Tennis Predictor

> Predicts ATP match win probabilities and simulates full tournament draws using XGBoost trained on 2018–2024 historical match data.

---

<details>
<summary><strong>What are Claude Skills?</strong></summary>

A Claude Skill is a markdown file that codifies a repeatable workflow — instructions an agent references to produce consistent, standardized output.

Without a skill, Claude pattern-matches to what the output *historically looked like* — not what is *correct for our specific context.* This is dangerous in quantitative and data-driven work, where a convincing but slightly wrong formula still runs without errors, but produces wrong numbers.

**Skills guardrail against this** by encoding first principles thinking directly into the instruction set — so Claude cannot pattern-match its way into a plausible but incorrect answer.

| | Without Skill | With Skill |
|---|---|---|
| Output | Varies, generic | Consistent, standardized |
| Quality | Claude's default standard | Your standard |
| Errors | Plausible but wrong | Caught by guardrails |
| Repeated work | Re-explain every time | Codified once |

> **Rule:** Systematize the known so human judgment is reserved for the unknown.

</details>

---

## Skills in this Project

---

### 1. Data Check

**Why this skill exists — first principles:**
> ATP match CSVs change silently between years — new columns appear, dtypes shift, columns are renamed. Without an explicit check at ingestion, these changes propagate invisibly through a 5-step pipeline and corrupt features with no error message. By the time the model produces a wrong prediction, the source of the error is buried 3 files deep. Claude's default is to fill missing values with 0 or drop rows — which destroys signal (a missing rank means unranked, not rank 0).

**What it enforces:**
- Compare every column name against the expected 49-column schema
- Verify dtypes match expected types (with accepted variations for seed/entry columns)
- Block the pipeline with FAIL status if any deviation is found — never silently proceed

**To invoke:**
```
"run the data check skill"
```

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

### 2. Prediction Report

**Why this skill exists — first principles:**
> Feature importance numbers exist in `feature_importance.csv` — they are the ground truth. Without a skill, an LLM will pattern-match to what a "typical" feature importance report looks like and invent plausible-sounding weights and feature names that do not match the actual file. In a 69-feature model, a fabricated number is undetectable without cross-referencing the source. Without explicit rules, Claude also defaults to generic ML language ("high gain feature") rather than domain-specific tennis interpretation.

**What it enforces:**
- Read directly from `feature_importance.csv` — no estimation or invention
- Compute decision weight as each feature's exact share of total XGBoost information gain
- Map every code name to a human-readable tennis description

**To invoke:**
```
"invoke the prediction report skill"
```

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

---

### 3. Player Tournament Prediction

**Why this skill exists — first principles:**
> A tournament bracket has hard structural constraints — each player occupies exactly one section of the draw relative to the target player, so the same opponent cannot appear in two different rounds. Without explicit rules, an LLM generates probability estimates and opponent lists that look realistic but violate these constraints (e.g. the same player in QF, SF, and Final — physically impossible). The skill also enforces a model cutoff rule: a tournament in year Y must use a model trained only through year Y−1, otherwise future match outcomes leak into the prediction.

**What it enforces:**
- Cross-round deduplication: a player can appear in at most one round row
- Model cutoff: tournament in year Y uses only a model trained through year Y−1
- Conditional win probability per round = P(reach next round) / P(reach this round)
- Cite at least 2 feature values by code name and long name in every report

**To invoke:**
```
"Medvedev Australian Open 2024"  or  "simulate Djokovic Roland Garros 2023"
```

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

---

### 4. Refactoring

**Why this skill exists — first principles:**
> In a multi-file pipeline (cleaning → features → aggregation → build_dataset → train), adding one new feature requires coordinated changes across 4–5 files. Without a single source of truth, updates are missed silently: a feature added to `features.py` but not to `train_xgb.py` produces a NaN column with no error; a column renamed in `cleaning.py` but not in `build_dataset.py` breaks the join only at training time. Claude's default is to add the feature wherever it's needed — duplicating the definition and creating future inconsistency.

**What it enforces:**
- All column names, feature lists, and constants defined once (single source of truth)
- Each file has exactly one responsibility — no feature engineering inside training code
- Adding a new feature requires touching only one file

**To invoke:**
```
"invoke the refactoring skill"
```

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

### 5. README Update

**Why this skill exists — first principles:**
> Without a prescribed structure, README content drifts toward generic project conventions — setup guides, architecture diagrams, hyperparameter tables — none of which communicate what is distinctive about the project. Claude's default for a data science README is to document the model, the features, and the pipeline. This skill overrides that default entirely: the README exists to showcase the skills framework, not the model.

**What it enforces:**
- Skills-only content: no pipeline diagrams, model metrics, feature tables, or setup instructions
- Every skill section includes first principles reasoning, an enforces list, an invoke command, and a sample output in a dropdown

**To invoke:**
```
"invoke the readme update skill"
```

<details>
<summary><strong>Sample output</strong></summary>

```
Invoked after: readme-update skill restored and regenerated README
               from scratch following updated skill structure

Changes made:
  - "What are Claude Skills?" moved into <details> dropdown
  - All 5 skill sections converted to numbered ### headings
  - Added "Why this skill exists" blockquote per skill
  - Added "What it enforces" bullets per skill
  - Added "To invoke" code block per skill
  - Added "The Thinking Behind Skills" section

Skills section verified: all 5 skills present with first principles
reasoning, enforces list, invoke command, and sample output dropdown.
```

</details>

---

## The Thinking Behind Skills

<details>
<summary><strong>Skills vs Fixed Code — when to use each</strong></summary>

| | Fixed Code | Skill |
|---|---|---|
| When | Pure computation, deterministic | Needs judgment, narrative, varies |
| Examples | Cleaning, feature engineering, model training | Reports, validation, documentation |
| Output | Same every time | Adapts to context |

> **Rule:** Computation is always fixed code. Communication is always a skill.

</details>

<details>
<summary><strong>Why skills catch what code cannot</strong></summary>

Code catches syntax errors and runtime errors. Skills catch reasoning errors — where the code runs perfectly but produces the wrong answer because the underlying logic violates first principles.

**Example from this project:**
Without the data check skill, Claude pattern-matches to "missing values = fill with 0" — a reasonable default. But first principles says: missing data in a sports dataset is often itself a signal, not noise. A player missing from rankings may be injured or unranked. Filling with 0 destroys that information.

The skill encodes this reasoning so it is applied consistently — not left to Claude's default judgment.

</details>

---

*Built with Claude Code — Anthropic's AI coding agent*
*Skills framework: systematize the known, reserve judgment for the unknown.*
