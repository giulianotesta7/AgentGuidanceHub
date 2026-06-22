---
name: agh-docs-alignment
description: "Trigger: AGH docs alignment, README drift, docs test, example or command mismatch. Keep AGH code, docs, examples, templates, and docs tests consistent."
license: Apache-2.0
metadata:
  author: "giulianotesta7"
  version: "1.0"
---

# AGH — Docs Alignment Skill

## Activation Contract

Load this skill when an AGH change touches user-facing docs, examples, commands, contributor flow, skill attribution, or anything a docs test asserts. It complements `cognitive-doc-design`: that skill governs prose style and cognitive load; this one governs **consistency and validation** — keeping code, docs, examples, templates, and docs tests from drifting.

## Hard Rules

1. **README.md is the landing page and the usage guide.** Keep user-facing docs there.
2. **Do not add new `## ` sections to README.md.** `tests/test_docs_guidance.py` asserts the exact README H2 list. Prefer `### ` for supplemental sections (e.g. `### Third-party notices`). Only change the H2 structure when intentionally redesigning the guide, and update `tests/test_docs_guidance.py` in the same change.
3. **Mirror user-facing README changes in `README.es.md`** in the same change.
4. **Docs describe current behavior, not intended behavior.** Update docs in the same change as the code.
5. **Keep documented commands aligned with real AGH validation** — when docs mention validation, compare them against `CONTRIBUTING.md` and `.github/workflows/ci.yml`. Do not run the full validation set unless the change itself requires it.
6. **Remove references to deprecated files, endpoints, commands, or scripts** when they go away.
7. **Generated technical artifacts stay in English.** Identifiers, comments, UI copy, and command examples are not translated by the conversation language.

## Decision Gates

| Change | Check and update |
| --- | --- |
| README structure, H2/H3 sections, or bookmarks | `tests/test_docs_guidance.py`; keep the H2 list; mirror `README.es.md` |
| User-facing README content | `README.md` and `README.es.md` in the same change |
| Examples, CLI commands, validation commands | Compare against real commands in `CONTRIBUTING.md` and `.github/workflows/ci.yml`; run only the relevant docs/examples check |
| Contribution flow, labels, PR/issue templates | `CONTRIBUTING.md`, `.github/pull_request_template.md`, `.github/ISSUE_TEMPLATE/*`, `AGENTS.md`, local `skills/` |
| Skill attribution or license | The skill's own `## Notices` and README `### Third-party notices` |
| Add or remove a skill | `AGENTS.md` skills table (and Composition when useful) and README notice |

## Alignment Checklist

- [ ] README H2 list unchanged, or docs test updated to match.
- [ ] `README.es.md` mirrors the user-facing change.
- [ ] Endpoint, script, and command names match the repo.
- [ ] Example commands match the current repo docs or CI source of truth.
- [ ] Deprecated references removed.
- [ ] Skill attribution updated in both the skill and README notices when applicable.

## Commands

```bash
# H2 list is asserted by docs tests — verify it before touching README structure
grep -E '^## ' README.md

# Run only the docs-guidance tests after README/template/contributing/notice changes
uv run pytest tests/test_docs_guidance.py -q

# Inspect documented validation commands without running the full validation set
rg "uv run|ruff|pyright|docker build" README.md README.es.md CONTRIBUTING.md .github/workflows
```

## Output Contract

Return:
- Files checked or updated and why.
- Whether the README H2 structure changed, with the matching docs-test update.
- Whether `README.es.md` was mirrored.
- Examples/commands checked against the repo source of truth.
- Any drift found and how it was resolved.
- Test scope run (full vs narrow) and rationale.

## References

- `README.md` — landing page and usage guide.
- `README.es.md` — Spanish mirror.
- `CONTRIBUTING.md` — PR-first policy, labels, validation commands, docs mirror policy.
- `tests/test_docs_guidance.py` — asserts README structure, bookmarks, templates, and validation commands.
- `.github/pull_request_template.md`, `.github/ISSUE_TEMPLATE/*` — contributor flow contract.
- `AGENTS.md` — AGH-local skill index.

## Notices

Adapted from `skills/docs-alignment/SKILL.md` in
[`Gentleman-Programming/engram`](https://github.com/Gentleman-Programming/engram/tree/main/skills/docs-alignment),
licensed under Apache-2.0. This version was modified for Agent Guidance Hub's
README-as-guide model, bilingual mirror policy, docs-test validation, and
PR-first contribution flow.
