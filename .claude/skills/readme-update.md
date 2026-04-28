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
- Do not talk about anything else other than skills, only focus on skills,
  so no need to talk about pipelines, project structure, no hyperparameter 
  talk, no need feature categories, no need top features
- Table has no hyperlinks — plain text skill names only
- Table title is "Summary of Skills in Project"
- Each skill section is always fully visible — no dropdown wrapper
- Only the sample output is wrapped in a `<details>` dropdown

## Sample Output Format
Only the sample output gets a dropdown:

```
**N. Skill Name**

**First principles:** ...

**Invoke:** `command here`

<details>
<summary><strong>Sample output</strong></summary>

\`\`\`
...output here...
\`\`\`

</details>

---
```

---

## README Structure

---

# {Project Name}

## What are Claude Skills?

A Claude Skill is a markdown file that codifies a repeatable
workflow — instructions an agent references to produce
consistent, standardized output.

Without a skill, Claude pattern-matches to what the output
*historically looked like* — not what is *correct for our
specific context.* This is dangerous in quantitative and
data-driven work, where a convincing but slightly wrong
formula still runs without errors, but produces wrong numbers.

**Skills guardrail against this** by encoding first principles
thinking directly into the instruction set — so Claude cannot
pattern-match its way into a plausible but incorrect answer.

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

**1. Data Check**

**First principles:** {first principles reasoning}

**Invoke:** `{command}`

<details>
<summary><strong>Sample output</strong></summary>

```
{sample output}
```

</details>

---

**2. Prediction Report**

**First principles:** {first principles reasoning}

**Invoke:** `{command}`

<details>
<summary><strong>Sample output</strong></summary>

```
{sample output}
```

</details>

---

**3. Player Tournament Prediction**

**First principles:** {first principles reasoning}

**Invoke:** `{command}`

<details>
<summary><strong>Sample output</strong></summary>

```
{sample output}
```

</details>

---

**4. Refactoring**

**First principles:** {first principles reasoning}

**Invoke:** `{command}`

<details>
<summary><strong>Sample output</strong></summary>

```
{sample output}
```

</details>

---

**5. README Update**

**First principles:** {first principles reasoning}

**Invoke:** `{command}`

<details>
<summary><strong>Sample output</strong></summary>

```
{sample output}
```

</details>