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
- Wrap each individual skill section in a `<details>` dropdown
- Number each skill in both the table and the dropdown header
- Table of contents has no hyperlinks — plain numbered list only
- Every skill is collapsed by default
- Sample output is a nested `<details>` dropdown inside the skill dropdown

## Sample Output Format
Wrap every skill in a `<details>` dropdown:
Wrap every sample output in a nested `<details>` dropdown:

```
<details>
<summary><strong>N. Skill Name</strong></summary>

**First principles:** ...

**Invoke:** `command here`

<details>
<summary><strong>Sample output</strong></summary>

\`\`\`
...output here...
\`\`\`

</details>
</details>
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

## Skills in this project

| # | Skill | Purpose |
|---|-------|---------|
| 1 | Data Check | Validate incoming ATP CSV data before cleaning |
| 2 | Prediction Report | Generate a signal report from feature importance scores |
| 3 | Player Tournament Prediction | Run a full Monte Carlo simulation for a player in a tournament |
| 4 | Refactoring | Enforce loose coupling and single-source-of-truth |
| 5 | README Update | Maintain this document to a consistent standard |

---

<details>
<summary><strong>1. Data Check</strong></summary>

**First principles:** {first principles reasoning}

**Invoke:** `{command}`

<details>
<summary><strong>Sample output</strong></summary>

```
{sample output}
```

</details>
</details>

---

<details>
<summary><strong>2. Prediction Report</strong></summary>

**First principles:** {first principles reasoning}

**Invoke:** `{command}`

<details>
<summary><strong>Sample output</strong></summary>

```
{sample output}
```

</details>
</details>

---

<details>
<summary><strong>3. Player Tournament Prediction</strong></summary>

**First principles:** {first principles reasoning}

**Invoke:** `{command}`

<details>
<summary><strong>Sample output</strong></summary>

```
{sample output}
```

</details>
</details>

---

<details>
<summary><strong>4. Refactoring</strong></summary>

**First principles:** {first principles reasoning}

**Invoke:** `{command}`

<details>
<summary><strong>Sample output</strong></summary>

```
{sample output}
```

</details>
</details>

---

<details>
<summary><strong>5. README Update</strong></summary>

**First principles:** {first principles reasoning}

**Invoke:** `{command}`

<details>
<summary><strong>Sample output</strong></summary>

```
{sample output}
```

</details>
</details>