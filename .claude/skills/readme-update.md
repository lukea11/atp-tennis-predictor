# README Update Skill

## Purpose
Update README.md after any meaningful change to the project.
Priority: showcase Claude Skills usage clearly for company review.

## When to invoke
- After adding/modifying a skill
- After completing a pipeline stage
- After hyperparameter tuning
- After any new fixed code module is added

## Rules
- Plain English first — no jargon without explanation
- Skills section must always come BEFORE technical details
- Every skill must show a real sample output
- Never list a skill without explaining WHY it exists
- Show the before/after of having the skill vs not

---

## README Structure (always follow this order)

---

# {Project Name}

> One sentence: what this project predicts and why it matters.

---

## The Role of Claude AI Skills

> This section comes FIRST — before setup, before models,
  before anything technical. It is the most important section.

This project is built around the principle of **systematizing 
the known so human judgment is reserved for the unknown.**

Claude Skills are markdown instruction files that Claude Code
references to produce consistent, standardized outputs for
repeatable workflows — eliminating the need to re-explain
processes and ensuring quality every time.

### Skills in this project:

| Skill | File | Purpose |
|-------|------|---------|
| Data Check | .claude/skills/data-check.md | Validate incoming ATP data before cleaning |
| Prediction Report | .claude/skills/prediction-report.md | Generate player tournament predictions |
| Refactoring | .claude/skills/refactoring.md | Enforce loose coupling and single source of truth |
| README Update | .claude/skills/readme-update.md | Maintain this document to company standard |

### Why skills and not just prompts?

Without a skill:
> "Hey Claude, check this data for me"
→ Different output every time, inconsistent quality

With a skill:
> "Run the data check skill"
→ Same structured report every time, 
  catches the same issues every time,
  in the same format every time

### Workflow diagram