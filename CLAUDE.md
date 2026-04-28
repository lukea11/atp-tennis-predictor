# ATP Tennis Predictor

## Project Goal
Predict player performance in upcoming ATP tournaments using
historical match data (2018-2024). Output: win probability 
per match, tournament simulation, player prediction reports.

## Data
- Source: ATP match CSVs (2018-2024)
- Location: /data/raw/
- Key columns (atp_matches_YYYY.csv):
  - tourney_id, tourney_name, surface, draw_size, tourney_level, tourney_date, match_num
  - winner_id, winner_seed, winner_entry, winner_name, winner_hand, winner_ht, winner_ioc, winner_age
  - loser_id, loser_seed, loser_entry, loser_name, loser_hand, loser_ht, loser_ioc, loser_age
  - score, best_of, round, minutes
  - w_ace, w_df, w_svpt, w_1stIn, w_1stWon, w_2ndWon, w_SvGms, w_bpSaved, w_bpFaced
  - l_ace, l_df, l_svpt, l_1stIn, l_1stWon, l_2ndWon, l_SvGms, l_bpSaved, l_bpFaced
  - winner_rank, winner_rank_points, loser_rank, loser_rank_points

## Architecture
- Fixed code: cleaning.py, features.py, aggregation.py, simulator.py
- Skills (in .claude/skills/): data-check, prediction-report, player-tournament-prediction-report, refactoring, readme-update
- Model: XGBoost (Player A win probability)

## Model Design Decisions
- **Mirror augmentation**: Training data is doubled by swapping all A/B feature pairs and flipping labels. Forces the model to learn symmetric weights — a feature's importance must be the same regardless of which player is arbitrarily assigned as A or B. `A_B_PAIRS` and `NEGATE_ON_MIRROR` in `models/train_xgb.py` define which columns are swapped vs negated.
- **Paired A/B feature importance**: In prediction reports, A and B versions of the same stat are merged (e.g. `A_rank_pts` + `B_rank_pts` → `rank_pts (A+B)`) to show true signal weight free of the ID-assignment artifact. Implemented in `models/prediction_report.md`.
- **Player A convention**: Player A is always the player with the lower ATP ID. This is arbitrary — mirror augmentation corrects for any bias this would otherwise introduce.
- **Recency decay**: Training rows are weighted by `decay_rate ^ (max_year - year)`. Best params: decay_rate=0.7, max_depth=5, min_child_weight=5. Val AUC: 0.7180, Val Accuracy: 65.54% (2024 holdout).

## Rules (always follow)
- NEVER use random train/test split — always time-based
- NEVER include Davis Cup matches (no points, causes NA values)
- ALWAYS exclude W/O and RET matches from match stats calculation
- ALWAYS lag features by at least 1 period before correlation
- player_A ID must always be < player_B ID in H2H database

## Commit Rules
Commit after every meaningful unit of work:
git add <specific files>
git commit -m "description of what changed and why"
git push

Never use git add -A without checking git status first.

## Code Style
- Python only
- Functions should be under 30 lines
- Every function needs a docstring explaining inputs/outputs
- No magic numbers — use named constants