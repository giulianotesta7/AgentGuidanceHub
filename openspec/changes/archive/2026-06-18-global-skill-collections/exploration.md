## Exploration: global-skill-collections

### Current State
AGH already supports global package publishing and workspace-local pull/install behavior. Packages can contain `instructions/AGENTS.md`, `instructions/CLAUDE.md`, and `skills/<name>/SKILL.md`; pull manifests already map skill artifacts to native agent folders (`.claude/skills/...` and `.opencode/skills/...`) based on the selected workspace agent. Workspace agent choice is stored locally in `.agh-cache/preferences.toml`, while `agh sync` remains repo-scoped via `.agh/project.toml`.

There is no collection model yet. Server state is currently centered on `users`, `projects`, `packages`, `package_versions`, and `project_packages` only. Collection/global-skill installation will need new server entities and local global-skill state separate from workspace pull state.

### Affected Areas
- `agh/server/db.py` — add collection and package-assignment tables plus migrations.
- `agh/server/routes/*.py` — add collection CRUD, package assignment, and list endpoints; likely new route module.
- `agh/cli/main.py` — add `skill` commands and global-agent selection UX.
- `agh/cli/agent_integrations.py` — likely extend preference storage to support global-skill defaults/state.
- `agh/cli/workspace_pull.py` — must stay workspace-local; use as a reference for skill target placement and cache/lock patterns.
- `agh/cli/package_publish.py` — reuse package artifact validation rules for skill-only package acceptance/rejection.
- `agh/server/routes/packages.py` — reuse artifact/file validation and published package lookup patterns for collection assignment.
- `tests/` — coverage for server authorization, CLI prompting, install/remove/list, and validation errors.

### Approaches
1. **Collection-backed global install with local lock/cache** — server stores curated collections and assignments; CLI resolves active collection skills, installs them into the selected agent’s native global skills dir, and records a local AGH lock/cache.
   - Pros: Matches the product decision set; clean separation from workspace sync/pull; easy to list “available” vs “installed”.
   - Cons: More moving parts (collection CRUD, assignment rules, local lock state, per-agent global paths).
   - Effort: High

2. **Treat global skills as a special workspace pull** — reuse pull manifests and workspace cache/lock logic, but point at a global destination.
   - Pros: Reuses existing artifact download and placement flow.
   - Cons: Violates the explicit repo/workspace boundary; muddles `agh pull` semantics; makes global installs depend on workspace state.
   - Effort: Medium

### Recommendation
Use a dedicated collection/global-install flow, not a workspace-pull variant. Keep `agh sync`/`agh pull` repo-scoped, and introduce separate global-skill state plus native-agent destination mapping. Reuse existing package manifest validation and skill placement patterns, but do not reuse workspace pull semantics.

### Risks
- Global install path differences between Claude and OpenCode may require per-agent path discovery rather than a hardcoded assumption.
- Collection assignment must reject instruction-bearing packages (`AGENTS.md`/`CLAUDE.md`) explicitly, not silently skip them.
- CLI agent-selection UX must avoid confusing workspace selection with the new global-skill default agent.

### Ready for Proposal
Yes. The codebase has clear reuse points, but the collection model, authorization, local global lock/cache, and agent-path resolution still need proposal/spec decisions.
