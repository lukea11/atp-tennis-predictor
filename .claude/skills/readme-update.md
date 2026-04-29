# README Update Skill

## Purpose
Update README.md to showcase Claude Skills usage for company review.
Focus ONLY on skills — no pipeline details, no model metrics, 
no setup instructions.

## Rules
- Every skill must explain the first principles thinking behind it
- Every skill must show the command to invoke it
- Every skill must show a real sample output inside a `<details>` dropdown
- Always frame skills as guardrails against LLM pattern-matching
- Never include project technical details unless directly 
  relevant to explaining a skill
- Include a Pipeline Integration table immediately after the summary table,
  showing how each skill slots into the data pipeline (see README Structure)
- Do not include anything else beyond skills and pipeline integration:
  no project structure, no hyperparameter talk, no feature categories
- Table has no hyperlinks — plain text skill names only
- Table title is "Summary of Skills in Project"
- Each skill section is always fully visible — no dropdown wrapper
- Each skill header uses `##` (h2) — e.g. `## 1. Data Check`
- Only the sample output is wrapped in a `<details>` dropdown
- Each skill section may include additional labeled paragraphs (e.g. `**Standardised Output design:**`) between First principles and Invoke — preserve these if present in the current README

## README Structure

---

# {Project Name}

> {One-line description of what the project does and the model/data it uses.}

## What are Claude Skills?

A Claude Skill is a markdown file that orchestrates a repeatable workflow, allowing us to focus on core problem-solving while routine tasks execute consistently according to defined specifications.

Without a skill with specified structure, LLM outputs may be plausible but misaligned with the underlying data or context. In quantitative settings, this can lead to silent errors: results that run successfully but are incorrect.

**Skills can guardrail against this** by us encoding first-principles reasoning and explicit constraints into the workflow, ensuring outputs are reproducible, verifiable, and grounded in the correct data and logic.

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

**First principles:** {first principles reasoning}

**Invoke:** `{command}`

<details>
<summary><strong>Sample output</strong></summary>

```
{sample output}
```

</details>

---

## 2. Prediction Report

**First principles:** {first principles reasoning}

**Invoke:** `{command}`

<details>
<summary><strong>Sample output</strong></summary>

```
{sample output}
```

</details>

---

## 3. Player Tournament Prediction

**First principles:** {first principles reasoning}

**Invoke:** `{command}`

<details>
<summary><strong>Sample output</strong></summary>

```
{sample output}
```

</details>

---

## 4. Refactoring

**First principles:** {first principles reasoning}

**Invoke:** `{command}`

<details>
<summary><strong>Sample output</strong></summary>

```
{sample output}
```

</details>

---

## 5. README Update

**First principles:** This project is about showcasing the use of Claude AI Skills. Without a prescribed structure, README content drifts toward generic project conventions that do not communicate what is actually distinctive about the project: setup guides, architecture diagrams and hyperparameter tables.

This skill defines a fixed template so each invocation produces the same sections in the same order, and mandates that technical details are excluded unless they directly explain a skill.

**Invoke:** `{command}`

<details>
<summary><strong>Sample output</strong></summary>

```
{sample output}
```

</details>