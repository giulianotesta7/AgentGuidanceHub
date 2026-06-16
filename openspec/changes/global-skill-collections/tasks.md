# Tasks: Global Skill Collections

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 500-700 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1: server + migrations + resolve/list API → PR 2: CLI global-skill flow + agent defaults + tests |
| Delivery strategy | ask-always |
| Chain strategy | feature-branch-chain |
| Issue | #97 |
| Tracker branch | `feat/global-skill-collections` |

Decision needed before apply: No — user selected chained PRs with a feature-branch-chain/tracker PR strategy for issue #97.
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Collection model, assignment rules, skill list/resolve endpoints | PR 1 | Base = tracker branch/PR; includes migration, auth, validator, API tests |
| 2 | Global skill install/remove, agent default selection, native path resolver | PR 2 | Base = PR 1; includes CLI/state tests and rollback |

## Phase 1: Foundation / Data Model

- [ ] 1.1 Add `agh/server/migrations/004_collections.sql` for `collections` and `collection_packages` plus ID prefix updates.
- [ ] 1.2 Extend `agh/server/db.py` schema helpers and repository types for collection CRUD and assignment records.
- [ ] 1.3 Add route/module wiring in `agh/server/app.py` for the new collections router.

## Phase 2: Core Server Behavior

- [ ] 2.1 Implement `agh/server/routes/collections.py` CRUD and package assignment endpoints with owner/admin authorization.
- [ ] 2.2 Add skill-only validation that rejects package artifacts containing `instructions/AGENTS.md` or `instructions/CLAUDE.md`.
- [ ] 2.3 Implement `GET /skills` and `GET /skills:resolve` for collection-backed skill discovery and concrete version resolution.

## Phase 3: CLI Global Skills

- [ ] 3.1 Add `agh/cli/global_skills.py` for resolve/download/cache/target/lock/remove flow under user AGH state.
- [ ] 3.2 Extend `agh/cli/agent_integrations.py` with `global_skill_dir(agent)` and separate global default-agent selection.
- [ ] 3.3 Add CLI commands for `skill list/install/remove` plus global-skill-scoped agent defaults such as `skill agent show/select/clear` in `agh/cli/main.py`.

## Phase 4: Strict TDD Verification

- [ ] 4.1 Write failing tests for collection auth, skill-only rejection, and resolve/list scenarios in `tests/`.
- [ ] 4.2 Write failing tests for global install/remove, checksum no-op, AGH-owned update, and untracked target `--force` behavior.
- [ ] 4.3 Verify CLI prompts and default-agent behavior, including `Select the agent for global skills:` wording.

## Phase 5: Cleanup / Documentation

- [ ] 5.1 Update CLI help/docs for global skill commands and agent-default behavior.
- [ ] 5.2 Keep the workspace prompt wording cleanup as a separate follow-up PR; do not include it in core implementation.
