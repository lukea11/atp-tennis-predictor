# Data Check Report Skill

## When to use
When new ATP CSV Match data is loaded for any year

## Process
1. Compare received columns against expected column list
2. Check data types match expected types
3. Flag any missing or new columns
4. Flag any data type changes

## Dtype Rules
- `str` and `object` are equivalent — never flag this as a change
- `winner_seed` and `loser_seed` may be `str` due to non-numeric entries (WC, Q, LL, etc.) — accepted as-is; cleaning.py is responsible for coercing to float

## Expected Columns
[For Match Data]:
1. tourney_id, tourney_name (city played)
2. surface
3. draw_size
4. tourney_level:
- A: ATP 250, 500, United Cup, Tour Finals
- M: ATP Masters 1000s
- G: Grand Slams
- D: Davis Cup
- F: Exhibition Matches
5. tourney_date: Date when the tournament started
6. winner_id, loser_id
7. winner_seed, loser_seed
8. winner_entry, loser_entry
9. winner_name, loser_name
10. winner_hand, loser_hand
11. winner_ht,loser_ht:heightofplayers
12. winner_ioc, loser_ioc: country they represent
13. winner_age, loser_age
14. score
15. best_of: 3 or 5 (only in grand slams)
16. round
17. minutes: duration of match
18. w_ace, l_ace: number of aces
19. w_df, l_df: number of double faults
20. w_svpt, l_svpt: number of points played on serve
21. w_1stIn, l_1stIn: number of first serves in
22. w_1stWon, l_1stWon: number of points won when the first
serve is in
23. w_2ndWon, l_2ndWon: number of points won when the
2nd serve is in
24. w_SvGms, l_SvGms: number of service games played
25. w_bpSaved, l_bpSaved: number of breakpoints saved
26. w_bpFaced, l_bpFaced: number of breakpoints faced
27. winner_rank, loser_rank: world ranking at the time of that
match
28. winner_rank_points, loser_rank_points: number of ranking
points at the time of that match

## Accepted dtype variations
- All text columns (tourney_id, tourney_name, surface, tourney_level, winner/loser entry/name/hand/ioc, score, round): str or object — both accepted
- winner_seed, loser_seed: float64 or str — both accepted (str expected when non-numeric seeds like WC, Q, LL are present)

## Output Format
[For Match Data]:
Title: {YEAR} ATP Matches Data Check

Columns received: {n}
New columns: {column (dtype)} OR None
Missing columns: {column (expected dtype)} OR None
Data type changes: {column (expected dtype → actual dtype)} OR None

Status: PASS / FAIL
If FAIL: state clearly what needs to be resolved before cleaning.