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
- Do not talk about anything else other than skills — no pipelines, 
  no project structure, no hyperparameter talk, no feature categories

## Sample Output Format
Wrap every sample output in a `<details>` dropdown:

```
<details>
<summary><strong>Sample output</strong></summary>

\`\`\`
...output here...
\`\`\`

</details>
```

---

## README Structure (always produce exactly this)

---

# {Project Name}

<details>
<summary><strong>What are Claude Skills?</strong></summary>

A Claude Skill is a markdown file that codifies a repeatable
workflow — instructions an agent references to produce
consistent, standardized output.

**The skill is a bridge:**
> Closing the gap between what Claude produces by default
  and what our standards actually require.

Without a skill, Claude pattern-matches to what the output
*historically looked like* — not what is *correct for our
specific context.* This is dangerous in quantitative and
data-driven work, where a convincing but slightly wrong
formula still runs without errors, but produces wrong numbers.

**Skills guardrail against this** by encoding first principles
thinking directly into the instruction set — so Claude cannot
pattern-match its way into a plausible but incorrect answer.

| | Without Skill | With Skill |
|---|---|---|
| Output | Varies, generic | Consistent, standardized |
| Quality | Claude's default standard | Your standard |
| Errors | Plausible but wrong | Caught by guardrails |
| Repeated work | Re-explain every time | Codified once |

> **Rule:** Systematize the known so human judgment
  is reserved for the unknown.

</details>

---

## Skills in this Project

---

### 1. {Skill Name}

**Why this skill exists — first principles:**
> {Explain what goes wrong WITHOUT this skill.
  What does Claude pattern-match to incorrectly?
  What is the first principles reasoning that 
  the skill encodes?}

**What it enforces:**
- {Rule 1}
- {Rule 2}
- {Rule 3}

**To invoke:**
```
"{exact command to call this skill in Claude Code}"
```

<details>
<summary><strong>Sample output</strong></summary>

```
{real sample output here}
```

</details>

---

### 2. {Skill Name}

**Why this skill exists — first principles:**
> {Explain what goes wrong WITHOUT this skill.}

**What it enforces:**
- {Rule 1}
- {Rule 2}

**To invoke:**
```
"{exact command}"
```

<details>
<summary><strong>Sample output</strong></summary>

```
{real sample output here}
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

> **Rule:** Computation is always fixed code.
  Communication is always a skill.

</details>

<details>
<summary><strong>Why skills catch what code cannot</strong></summary>

Code catches syntax errors and runtime errors.
Skills catch reasoning errors — where the code runs
perfectly but produces the wrong answer because the
underlying logic violates first principles.

**Example from this project:**
Without the data check skill, Claude pattern-matches
to "missing values = fill with 0" — a reasonable default.
But first principles says: missing data in a financial/
sports dataset is often itself a signal, not noise.
A player missing from rankings may be injured.
Filling with 0 destroys that information.

The skill encodes this reasoning so it is applied
consistently — not left to Claude's default judgment.

</details>

---

*Built with Claude Code — Anthropic's AI coding agent*
*Skills framework: systematize the known,
 reserve judgment for the unknown.*