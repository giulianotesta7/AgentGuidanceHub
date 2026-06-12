## Intent

PR1 makes project commands accept exact project names while keeping canonical `prj_...` IDs fully supported. User email refs and pack `name@version` refs remain planned follow-up slices, not required PR1 behavior.

## Scope

### In Scope for PR1
- Server project resolution endpoint: project by name
- CLI project input detection (`prj_...`, all-digit passthrough, exact name resolution) before project actions
- Project name global uniqueness + digit-only name rejection
- Visibility-scoped project lookup, exact matching only

### Out of Scope for PR1
- User email refs and `agh user show <email>`
- Pack version refs such as `name@version` / `packv_...` resolver behavior
- Assignment commands (`asn_...`), web UI, fuzzy search

## Future Slices

- PR2: user email resolution endpoint and CLI user ref handling.
- PR3: pack-version resolver/parser and CLI project-pack ref handling.

## Capabilities

### New PR1 Capabilities
- `project-name-resolution`: Resolve project name to `prj_...` ID. Exact match, visibility-scoped, 404 if not found. Project names are globally unique.
- `cli-name-identifiers`: Project command input format detection + project name resolution before action.

### Modified Capabilities
None — no existing specs.

## Approach

Approach A, narrowed for PR1: CLI-side project resolution via a dedicated server endpoint (`/projects/by-name/{name}`). CLI resolves project names before action and passes the canonical project ID to existing action routes. Action routes stay ID-only.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `agh/server/routes/projects.py` | New/Modified | Project resolution endpoint, validation, duplicate-name mapping |
| `agh/cli/project_refs.py`, `agh/cli/main.py` | New/Modified | Project input detection + resolution call |
| DB (projects.name) | Modified | UNIQUE constraint, reject digit-only |
| `tests/` | Modified | Project route, migration, CLI project-ref, and docs guidance coverage |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Project name collisions during uniqueness migration | Med | Clear error; user can fall back to ID |
| Race: rename between resolution and action | Low | Stale ref -> 404 at action time |
| Enumeration via resolution endpoint | Med | Scope lookups to project visibility |
| CLI latency from extra call | Low | Indexed lookup, negligible overhead |

## Rollback Plan

Revert CLI project-name resolution, remove project lookup endpoint, undo DB uniqueness change. Action routes remain untouched.

## Dependencies

- Project name global uniqueness migration (existing data deduplication)

## Success Criteria

- [ ] `agh project get <name>` returns unique project details
- [ ] Project update/delete/member/pack commands accept exact project names where they previously accepted `prj_...`
- [ ] `agh project get 123` is treated as numeric ID passthrough, not a name
- [ ] Digit-only project names are rejected at creation and rename
- [ ] All project ID-based commands remain unchanged
- [ ] Project name resolution respects auth scope
- [ ] Exact-only project name matching is enforced
