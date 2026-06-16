# Proposal: Global Skill Collections

## Intent

Introduce admin-curated `Collection` catalogs so members can discover and install approved skills into their selected agent's native global skill directory, while preserving repo/workspace-scoped `Project`, `agh sync`, and `agh pull`.

## Scope

### In Scope
- Add server-side collections, package assignments, authorization, and skill-only package validation.
- Add `agh collection` admin commands for collection CRUD and package assignment.
- Add `agh skill list/install/remove` for collection-backed global skills with local cache/lock state.
- Add global-skill-scoped agent default selection plus conflict/update rules.

### Out of Scope
- Git-backed collections or collection participation in `agh sync` / `agh pull`.
- Workspace-local `agh skill install`; `agh pull` remains the workspace install path.
- Existing workspace prompt wording follow-up.

## Capabilities

### New Capabilities
- `global-skill-collections`: Collection management, skill availability, global installation, local lock/cache, and agent-default UX.

### Modified Capabilities
- None; no existing `global-skill-collections` OpenSpec capability is present.

## Approach

Create a dedicated collection/global-install flow. Owners/admins manage collections and assignments; members list available collection skills and install explicit package refs, e.g. `agh skill install acme/commenting@latest comment-writer`. Assignments reject packages containing `instructions/AGENTS.md` or `instructions/CLAUDE.md`. Installs resolve concrete version/checksum, write AGH-owned global cache/lock under user AGH state (`XDG_STATE_HOME/agh` or `~/.local/state/agh`), and copy skills to the selected agent's native global skills path. Same checksum is a no-op; AGH-owned installs update; different-package same-name installs conflict; untracked target files require force.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `agh/server/db.py` | Modified | Collection and assignment tables/migrations. |
| `agh/server/routes/collections.py` | New | CRUD, assignment, available-skill endpoints. |
| `agh/cli/main.py` | Modified | `collection` admin commands, `skill` commands, and global-skill-scoped agent default commands. |
| `agh/cli/agent_integrations.py` | Modified | Global default and native path mapping. |
| `agh/cli/workspace_pull.py` | Reference | Reuse cache/lock patterns only. |
| `tests/` | Modified | Authorization, validation, CLI UX, lock/cache, install/remove. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Native global paths differ by agent/version. | Med | Confirm OpenCode/Claude paths before implementation; keep mapping isolated. |
| Workspace/global semantics blur. | Med | Separate commands, state, locks, and tests from pull flow. |
| Overwriting user files. | Med | Require explicit force for untracked target files. |

## Rollback Plan

Disable collection routes/CLI commands, leave project/package/pull tables untouched, and delete local AGH global cache/lock plus AGH-owned installed skill files if needed.

## Dependencies

- Existing package publishing and artifact validation.
- Native global skill path confirmation for OpenCode and Claude before implementation.

## Success Criteria

- [ ] Owner/admin can manage collections and assignments; members cannot mutate them.
- [ ] Instruction-bearing packages are rejected for collections.
- [ ] Members can list collection skills and install/remove global skills with deterministic lock records.
- [ ] `agh sync` and `agh pull` behavior remains workspace-scoped and unchanged.
