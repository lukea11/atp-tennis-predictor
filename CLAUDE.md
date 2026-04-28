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
- Skills: data-check, prediction-report, readme-update
- Model: XGBoost (Player A win probability)

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