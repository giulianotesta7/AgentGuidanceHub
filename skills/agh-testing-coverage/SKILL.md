---
name: agh-testing-coverage
description: "Trigger: AGH tests, pytest, coverage, validation, bug fix, behavior change. Choose focused AGH validation and report it clearly."
license: Apache-2.0
metadata:
  author: "giulianotesta7"
  version: "1.0"
---

# AGH — Testing & Coverage Skill

## Activation Contract

Load this skill when adding behavior, fixing bugs, refactoring logic, changing validation commands, or preparing PR validation for Agent Guidance Hub.

Use it with `agh-work-unit-commits` so each work unit includes the validation that proves it. Prefer focused validation while developing; run broader validation before PRs that touch runtime behavior.

Do not use this skill for docs consistency alone; load `agh-docs-alignment`. Do not use it to split commits or PRs; load `agh-work-unit-commits` or `agh-chained-pr`.

## Hard Rules

1. **Test behavior, not implementation details.** Prefer CLI/API/runtime-visible outcomes over private call expectations.
2. **Bug fixes need regression coverage** unless the bug is docs-only or impossible to automate; state the reason when no test is added.
3. **Use focused tests first.** Run the smallest relevant pytest target while iterating, then broaden as risk grows.
4. **Keep tests deterministic.** Avoid sleeps, network dependencies, and shared global state when a local fixture or temp path works.
5. **Pair validation with the work unit.** Docs, tests, fixtures, and examples belong with the change they prove.
6. **Do not fake full validation.** PR bodies must list the exact commands run, not the commands you intended to run.

## Validation Decision Gates

| Change | Minimum validation |
| --- | --- |
| Runtime Python behavior | Focused pytest target, then `uv run pytest -q` before PR when practical. |
| Bug fix | A failing regression test first, then focused pytest target proving the fix. |
| CLI behavior | Focused CLI tests or closest pytest module, plus `agh --help` only when installed CLI behavior changes. |
| Server/API behavior | Focused server/API tests; include error-path tests for validation/auth/IO changes. |
| Docker/runtime | `docker build --check .` and `AGH_STRICT_DOCKER_RUNTIME=1 uv run pytest tests/test_docker_runtime.py -q`. |
| Docs/workflow/templates | `uv run pytest tests/test_docs_guidance.py -q` and `git diff --check`. |
| Formatting/lint-sensitive change | `uv run --with ruff ruff check .` and/or `uv run --with ruff ruff format --check .`. |
| Typing/API surface change | `uv run --with pyright pyright agh tests`. |
| Package/release behavior | `uv build`, `uv tool install --force dist/*.whl`, then `agh --help`. |

## Regression Test Loop

1. Reproduce the bug or missing behavior.
2. Add the smallest failing test that captures user-visible behavior.
3. Implement the smallest fix.
4. Run the focused test until green.
5. Run any broader validation required by the touched area.
6. Report exact commands and results in the PR.

## Coverage Rules

- Cover happy path, error path, and edge cases for new behavior.
- Prefer fixtures and temp directories over persistent `.agh-data*` state.
- Avoid adding test seams that change runtime behavior.
- For command examples, verify documented commands through docs tests or direct command checks.
- When skipping automation, state why and include manual verification.

## Commands

```bash
# Focused tests while iterating
uv run pytest tests/<module>.py -q
uv run pytest tests/<module>.py::test_name -q

# Full CI-equivalent validation pieces
uv lock --locked
uv run pytest -q
uv run --with ruff ruff check .
uv run --with ruff ruff format --check .
uv run --with pyright pyright agh tests
docker build --check .
AGH_STRICT_DOCKER_RUNTIME=1 uv run pytest tests/test_docker_runtime.py -q
uv build
uv tool install --force dist/*.whl
agh --help
```

## PR Validation Reporting

Use exact commands and outcomes:

```markdown
## Validation

- [x] `uv run pytest tests/test_docs_guidance.py -q` — 13 passed
- [x] `git diff --check` — passed
```

If validation is intentionally narrow, add one sentence explaining why it is enough for the change.

## Output Contract

Return:
- Behavior or risk being validated.
- Focused test target chosen and why.
- Broader validation required before PR, if any.
- Exact commands run and results.
- Regression coverage added or reason it was not added.
- Any manual verification and its scope.

## References

- `.github/workflows/ci.yml` — CI source of truth.
- `pyproject.toml` — pytest and package configuration.
- `CONTRIBUTING.md` — validation commands for contributors.
- `skills/agh-work-unit-commits/SKILL.md` — pair validation with work units.
- `skills/agh-docs-alignment/SKILL.md` — docs-specific validation and drift checks.

## Notices

Adapted from `skills/testing-coverage/SKILL.md` in
[`Gentleman-Programming/engram`](https://github.com/Gentleman-Programming/engram/tree/main/skills/testing-coverage),
licensed under Apache-2.0. This version was modified for Agent Guidance Hub's
Python/uv, FastAPI/Typer, Docker, docs-guidance, and package-validation workflow.
