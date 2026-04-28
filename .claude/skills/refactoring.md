# Refactoring Skill

## Purpose
Ensure code is loosely coupled and absorbs change 
without cascading updates across multiple files.

## When to invoke
- Before writing any new feature or column
- When a file exceeds 150 lines
- When the same variable/list appears in 2+ files
- When adding a new data source or model

## Rules to enforce

### 1. Single Source of Truth
- All column names defined ONCE in config.py
- All feature lists defined ONCE in config.py
- All year ranges, surfaces, file paths in config.py
- If a value appears in 2+ files → move to config.py

### 2. Single Responsibility
Each file does exactly ONE thing:
- cleaning.py    → clean data only
- features.py    → build features only
- aggregation.py → aggregate stats only
- model.py       → train and predict only
- simulator.py   → simulate tournament only
- report.py      → format output only
If a file is doing 2 things → split it

### 3. Loose Coupling
- Files communicate via function inputs/outputs only
- No file imports logic from another file's internals
- No feature engineering inside model training code
- No cleaning logic inside aggregation code

### 4. Open for Extension
- Adding a new feature = update config.py only
- Adding a new surface = update config.py only
- Adding a new year = update config.py only
- No other files should need to change

### 5. No Magic Numbers
- No hardcoded years, column names, thresholds in code
- Every constant has a named variable in config.py
- Example: ANNUALIZE_FACTOR = 252, not just 252

## Validation Checklist
Before finishing any refactor:
- [ ] Does adding a new feature require touching 
      only config.py?
- [ ] Does each file have exactly one responsibility?
- [ ] Are any column names duplicated across files?
- [ ] Are there any magic numbers in non-config files?
- [ ] Can simulator.py run without knowing how 
      features were built?

## Report Format
Produce a refactoring report:

### Refactoring Report

**What was refactored:** {description}

**Files affected:**
| File | Change | Reason |
|------|--------|--------|
| config.py | Added MATCH_STATS list | Single source of truth |
| cleaning.py | Replaced hardcoded columns with MATCH_STATS | Loose coupling |

**Before vs After:**
- Before: {describe tightly coupled code}
- After: {describe loosely coupled code}

**What this enables:**
- Adding new feature now requires: {only config.py}
- Adding new surface now requires: {only config.py}

**SOLID principles applied:**
- S: {which files had single responsibility enforced}
- O: {what is now open for extension}
- L/I/D: {if applicable}