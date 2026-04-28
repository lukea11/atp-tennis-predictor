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
- Do not talk about anything else other than skills, only focus on skills, so no need to talk about pipelines, project structure, no hyperparameter talk, no need feature categories, no need top features

## Sample Output Format
Wrap every skill in a `<details>` dropdown:
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
pattern-match its way into a plausible but incorrect