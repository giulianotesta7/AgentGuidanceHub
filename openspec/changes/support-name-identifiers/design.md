## Technical Approach

PR1 adds explicit project resolver helpers around the existing canonical-ID API. The server exposes a read-only, exact project-name lookup endpoint for visible projects. The CLI parses `<project-ref>`, resolves human-readable project names first, then calls existing action routes with canonical project IDs. `prj_...`, all-digit refs, and existing scripts remain passthrough.

User email refs and pack-version refs are future chained slices, not PR1 requirements.

## Architecture Decisions

| Concern | Options / tradeoff | Decision |
|---|---|---|
| Project names | Active-only uniqueness allows old inactive collisions; global uniqueness simplifies lookup. | Add global `UNIQUE` index on `projects.name`; reject digit-only names in shared validation. |
| API shape | Dual-use action routes save one request but blur auth and errors. | Keep action routes ID-only; add a dedicated project lookup endpoint before dynamic `/{id}` paths. |
| Visibility | Returning 403 leaks existence; returning 404 hides hidden resources. | Resolver queries apply project visibility scope and return 404 for out-of-scope targets; action routes still enforce canonical-ID auth checks. |
| CLI parsing | Per-command parsing duplicates rules. | Add a focused `agh/cli/project_refs.py` resolver and call it from affected project commands. |

## Data Flow

```text
CLI project arg -> classify ref -> project resolver endpoint -> canonical project ID -> existing action route
                         |                                               |
                         +-- prj_... / all-digit ------------------------+ passthrough
```

- Project: `prj_...` and all-digit refs pass through; otherwise call `GET /api/v1/projects/by-name/{name:path}`, then call `/projects/{id}` routes.

## File Changes

| File | Action | Description |
|---|---|---|
| `agh/common/validation.py` | Modify | Add `validate_project_name()`. |
| `agh/server/migrations/002_unique_project_names.sql` | Create | Add `ux_projects_name` unique index. |
| `agh/server/routes/projects.py` | Modify | Use shared project-name validation, map duplicate names to 409, add `GET /projects/by-name/{name:path}` before `/{project_id}`. |
| `agh/cli/project_refs.py` | Create | Add focused project ref classifier/resolver. |
| `agh/cli/main.py` | Modify | Call project ref resolution from affected project commands. |
| `tests/` | Modify | Add DB migration, project route, project CLI resolution, error mapping, and docs guidance tests. |

## Interfaces / Contracts

- `GET /api/v1/projects/by-name/{name:path}` -> `200 {"id","name"}`, `401`, `404`.

CLI maps malformed local project refs to exit code 2, auth failures to existing code 4 with re-login guidance, and 404 to not-found.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit | project-name validation | pytest focused helper tests |
| API | project resolver status codes, exact/case-sensitive lookup, visibility, duplicate-name conflicts on create/update | FastAPI `TestClient` route tests |
| CLI | project ID passthrough, project-name resolution order, error mapping, backward compatibility | `CliRunner` plus local HTTP test server |
| Migration | unique project-name index and duplicate-data failure mode | SQLite migration tests |

## Migration / Rollout

Add a forward migration for `ux_projects_name`. Operators must deduplicate existing duplicate project names before deploying; otherwise SQLite will reject the index and startup migration will fail. No feature flag required because ID-based action routes remain unchanged.

## Future Slices

- PR2: add `GET /api/v1/users/by-email/{email:path}`, `agh user show`, and email resolution for user-related CLI commands with exact, visibility-scoped lookup.
- PR3: add pack-version ref parsing/resolution for `packv_...`, `<domain>/<name>@<version>`, and `<name>@<version>`, including ambiguity handling for no-domain refs.

## Open Questions

None.
