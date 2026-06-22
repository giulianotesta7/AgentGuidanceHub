---
name: agh-skill-manager
description: "Trigger: AGH skill creation, audit, improvement, normalization, or validation. Create and audit AGH-local skills under skills/<name>/SKILL.md."
license: Apache-2.0
metadata:
  author: "giulianotesta7"
  version: "1.0"
---

# AGH — Skill Manager Skill

## Activation Contract

Load this skill when creating, auditing, improving, normalizing, or validating AGH-local skills under `skills/<name>/SKILL.md`. Create a skill only when the workflow is reusable and an agent needs runtime guidance. Audit existing AGH skills when the user asks to review quality, triggers, structure, frontmatter, or rule clarity.

Do not use this for one-off prompts, README-style docs, non-reusable instructions, or broad agent configuration unrelated to skills.

Load `agh-docs-alignment` alongside this skill whenever a change touches `AGENTS.md`, `README.md`, or notices.

## Hard Rules

1. **Create skills only for reusable AGH workflows where an agent needs runtime guidance.** If the guidance is human-facing or one-off, prefer normal documentation.
2. **Use `skills/<skill-name>/SKILL.md` with lowercase hyphenated names.** One `SKILL.md` per skill.
3. **`SKILL.md` is a runtime instruction contract for an LLM, not human documentation.** Write imperative instructions.
4. **Update `AGENTS.md` for every local skill added, removed, or renamed** — the Skills table always, and the Composition section when the skill should load alongside other skills.
5. **Use `agh-docs-alignment` for any `README.md` / `AGENTS.md` / notice change.** That skill owns README structure, bilingual mirror policy, and docs-test validation.
6. **Do not add `assets/`, `references/`, or `scripts/` unless they solve a real reusable need.** Default to a self-contained `SKILL.md`.
7. **Preserve author intent, activation semantics, critical rules, and output requirements** when auditing. Do not invent triggers, policies, or domain rules; mark ambiguous cases for human review.
8. **Generated technical artifacts stay in English** — identifiers, comments, examples, and frontmatter.
9. **Do not invent repo policy during audits.** Report missing or unclear policy as an ambiguity instead of filling the gap yourself.
10. **Default to report-only audits.** Modify existing skills only when the user explicitly asks to apply changes.

## Decision Gates

| Situation | Action |
| --- | --- |
| Reusable AGH workflow needs runtime guidance | Create or update a skill |
| Human-facing explanation or one-off prompt | Recommend normal docs instead |
| Missing/invalid frontmatter | Fix `name`, quoted one-line `description`, `license`, `metadata` |
| Skill reads like a tutorial | Convert to imperative runtime instructions |
| Branching logic hidden in prose | Use a compact decision table |
| Long examples/templates/schemas | Move to `assets/` or `references/` only if reusable; otherwise trim |
| Skill added, removed, or renamed | Update `AGENTS.md` Skills table (and Composition when relevant) |
| Intent or rules conflict | Report the ambiguity; do not rewrite automatically |

## Execution Steps

1. Identify mode: create, audit-only, or apply-improvements.
2. Confirm the pattern is reusable and an agent needs runtime guidance; otherwise recommend docs.
3. For create or normalize, write frontmatter first, then sections in this order: Activation Contract, Hard Rules, Decision Gates, Execution Steps, Validation, Output Contract, References.
4. Write frontmatter with lowercase hyphenated `name`, a quoted one-line `description` with essential triggers first, `license`, and `metadata` (`author`, `version`).
5. Keep the main skill concise; move long examples or schemas to `assets/` or `references/` only when reusable.
6. Update `AGENTS.md` (Skills table; Composition when the skill composes with others) for every add, remove, or rename.
7. For audit mode, review metadata, trigger clarity, negative triggers, section order, actionability, decision gates, output contract, and AGH alignment; report findings grouped by severity.
8. Apply changes only when the user asked for apply mode.

## Validation

Run after `AGENTS.md`, `README.md`, or template changes:

```bash
# Whitespace/conflict sanity
git diff --check

# README / AGENTS / template drift checks
uv run pytest tests/test_docs_guidance.py -q
```

Notes:

- When README user-facing content changes, mirror `README.es.md` (load `agh-docs-alignment`).
- A skill-only change with no `AGENTS.md` / README / notice edit needs only `git diff --check`.

## Output Contract

Return:

- Mode used and skills/directories inspected.
- Files created or modified, if any.
- Whether `AGENTS.md` was updated, and why (or why not).
- Audit findings grouped by severity when auditing.
- Validation commands run and their pass/fail results.
- Ambiguities or residual risks requiring human review.

## References

- `AGENTS.md` — AGH-local skill index; must reflect every add, remove, and rename.
- `skills/agh-docs-alignment/SKILL.md` — README H2 rules, bilingual mirror policy, docs-test validation.
- `skills/agh-testing-coverage/SKILL.md` — focused validation targets for skill-adjacent changes.
- `tests/test_docs_guidance.py` — asserts README H2 structure and docs drift.
