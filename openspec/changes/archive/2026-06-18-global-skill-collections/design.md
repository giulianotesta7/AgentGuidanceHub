# Design: Global Skill Collections

## Technical Approach

Add a collection-specific server flow and a separate user-global CLI install flow. Collections curate published skill-only package versions; workspace `sync`/`pull` remains unchanged. The CLI resolves collection availability, downloads a single `skills/<name>/SKILL.md` artifact through existing authenticated package file routes, then stages cache, target, and lock updates under user AGH state.

## Architecture Decisions

| Decision | Options / tradeoff | Choice and rationale |
|---|---|---|
| Collection model | Reuse projects vs new tables | New `collections` and `collection_packages`; keeps repo membership and global tooling catalogs separate. |
| Install source | Reuse pull manifest vs skill resolver | New skill availability/resolve endpoint; avoids leaking workspace instructions and keeps installs per-skill. |
| Native paths | Hardcode everywhere vs isolated resolver | Extend `agent_integrations.py` with `global_skill_dir(agent)`: candidate paths are Claude `~/.claude/skills` and OpenCode `~/.config/opencode/skills`. Local `~/.opencode/skills` exists but may be legacy. Confirm current agent behavior with a smoke check before implementation and keep the mapping isolated. |
| `@latest` | Store mutable local ref vs concrete lock | Server may expose `version_ref=latest`, but install records resolved SemVer, package version id, and checksum for deterministic updates. |
| Force | Broad override vs narrow safety valve | `--force` only overwrites an untracked local target for the selected agent. It does not bypass auth, server validation, or AGH-tracked same-name/different-package conflicts. |

## Data Flow

    admin -> /collections -> collection_packages -> skill-only validator
    member -> agh skill list -> /skills -> collection skill rows
    agh skill install -> /skills:resolve -> package file download
        -> user AGH cache -> native global skills dir -> global lock

## File Changes

| File | Action | Description |
|---|---|---|
| `agh/server/migrations/004_collections.sql` | Create | `collections(id col_*, name unique, description, active, created_by, timestamps)` and `collection_packages(id casn_*, collection_id, package_id, version_ref, position, active, timestamps, unique(collection_id, package_id))`; extend valid id prefixes. |
| `agh/server/routes/collections.py` | Create | Collection CRUD, package assignment, `GET /skills`, `GET /skills:resolve`; owner/admin mutate, active users list/resolve. |
| `agh/server/app.py` | Modify | Include collections router. |
| `agh/cli/main.py` | Modify | Add `collection` admin commands, `skill list/install/remove`, and global-skill-scoped agent defaults such as `skill agent show/select/clear`; add `--agent`, `--force`, and default-save flags. |
| `agh/cli/global_skills.py` | Create | Resolve agent, fetch skills, stage cache/target/lock writes, remove installs, rollback on failures. |
| `agh/cli/agent_integrations.py` | Modify | Add global skill default preference and native global path resolver separate from workspace selection. |
| `tests/` | Modify | Add strict TDD coverage for migrations, routes, CLI, state, conflicts, rollback. |

## Interfaces / Contracts

Server routes:
- `GET/POST /api/v1/collections`, `GET/PATCH/DELETE /api/v1/collections/{id}`.
- `GET/POST /api/v1/collections/{id}/packages`, `PATCH/DELETE /api/v1/collections/{id}/packages/{assignment_id}`.
- `GET /api/v1/skills[?collection_id=...]` returns collection, skill name, requested `package_ref`, resolved ref, checksum, description. It includes only active collections and active collection package assignments.
- `GET /api/v1/skills:resolve?package_ref=...&skill_name=...` requires the resolved package to be active in an active collection and returns `package_version_id`, concrete `package_ref`, checksum, artifact path, and existing package `download_url`.

Assignment validation resolves the requested version, rejects `instructions/AGENTS.md` or `instructions/CLAUDE.md`, requires `skills/*/SKILL.md`, and reuses safe storage reads. `latest` is revalidated during list/resolve so later instruction-bearing versions fail closed.

Local state under `XDG_STATE_HOME/agh` or `~/.local/state/agh`:
- `global-skills/defaults.toml`: `global_agent`, `selected_at`.
- `global-skills/lock.toml`: `version`, then `[[skills]] agent, skill_name, package_ref_requested, package_ref_resolved, package_version_id, checksum, artifact_path, target_path, source, mode, installed_at`.
- `global-skills/cache/<domain>/<name>/<version>/skills/<skill>/SKILL.md` stores verified content. Same checksum is noop; AGH-owned same package updates; different package same skill conflicts; remove deletes target and lock entry, then prunes unreferenced cache.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit | validation, SemVer latest, state parsing, target conflict matrix | pytest with temp dirs and direct functions. |
| Integration | migrations, auth, CRUD, assignment rejection, resolve/download | FastAPI `TestClient` plus real SQLite/filesystem. |
| CLI | command mapping, prompts, defaults, install/remove, force, rollback | `CliRunner`, fake HTTP server, isolated home/state env. |

## Migration / Rollout

Forward-only migration. No data migration for existing projects/packages. Rollback disables routes/CLI and removes user-global AGH state plus AGH-owned target files. Workspace prompt wording cleanup is a separate follow-up PR.

## Open Questions

- [ ] Before apply, run a smoke check against current Claude/OpenCode versions to confirm global path behavior, especially OpenCode legacy `~/.opencode/skills` vs documented `~/.config/opencode/skills`.
