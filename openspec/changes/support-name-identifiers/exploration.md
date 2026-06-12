## PR1 Scope Note

This exploration is historical context from before the work was split. It is not PR1 acceptance criteria. PR1 required behavior is project refs only; user email refs and pack-version refs are future chained slices.

# Exploration: Support Name/Email Identifiers in CLI

## Current State

The `agh` CLI currently requires prefixed opaque IDs for most mutation and detail commands. Server-side resource identifiers (generated via `agh/common/ids.py`) use 16-hex-char suffixes under prefixes `usr_`, `prj_`, `pack_`, `packv_`, `asn_`, `tok_`.

### Commands requiring IDs today

**User commands (require `usr_...`):**
- `agh user update <user_id>` — `user_id` positional arg
- `agh user delete <user_id>` — `user_id` positional arg
- `agh token rotate <user_id>` — `user_id` positional arg
- `agh token reset <user_id>` — `user_id` positional arg

**Project commands (require `prj_...`):**
- `agh project get <project_id>` — `project_id` positional arg
- `agh project update <project_id>` — `project_id` positional arg
- `agh project delete <project_id>` — `project_id` positional arg
- `agh project member add <project_id> <user_id>` — both positional
- `agh project member remove <project_id> <user_id>` — both positional
- `agh project pack list <project_id>` — `project_id` positional arg
- `agh project pack add <project_id> <pack_ref>` — `project_id` positional
- `agh project pack update <project_id> <assignment_id>` — both positional
- `agh project pack remove <project_id> <assignment_id>` — both positional

**Pack commands:**
- Already accept domain/name@version (`acme/name@1.0.0`) — human-readable by design. No change needed.

**Assignment commands:**
- Require `asn_...` assignment IDs. No natural human-readable name exists for assignments. Out of scope for this change.

### Server-side ID validation

Routes in `agh/server/routes/users.py`, `projects.py`, and `packs.py` validate IDs through helpers like `_get_user()`, `_get_project()`, and `_validate_project_id()` which call `is_valid_prefixed_id()` from `agh/common/ids.py`. These helpers enforce the prefix and format before DB lookup. If the ID format does not match, a `404` is returned (not `400`), which prevents probing valid vs invalid IDs.

### Database schema highlights

- **users**: `id TEXT PK` (prefixed), `email TEXT UNIQUE NOT NULL`. Email is unique and validated via `is_valid_email()`.
- **projects**: `id TEXT PK` (prefixed), `name TEXT NOT NULL`. Name is NOT unique — only the active repo URL has a unique constraint (`ux_projects_active_repo_url_normalized`).
- **project_members**: `(project_id, user_id)` composite PK.
- **project_packs**: `id TEXT PK` (prefixed `asn_`), no natural name field.

### Existing resolution-like patterns

- `pack_ref` (domain/name@version) already serves as a human-readable identifier in pack publish, assignment, and pull-manifest flow.
- Email is the primary user identifier for login (`agh login --email`) and user creation (`agh user create <email>`).
- Project `name` is already accepted for creation (`agh project create <name>`).

## Affected Areas

### Direct changes needed

| Area | Impact | Commands affected |
|------|--------|-------------------|
| `agh/cli/main.py` | All commands with `user_id` or `project_id` positional args | `user update`, `user delete`, `token rotate`, `token reset`, `project get/update/delete`, `project member add/remove`, `project pack list/add/update/remove` |
| `agh/server/routes/users.py` | Need resolution endpoint(s) for email to user_id | `GET /api/v1/users/by-email/{email}` or `GET /api/v1/users?email=...` |
| `agh/server/routes/projects.py` | Need resolution endpoint(s) for project name to project_id | `GET /api/v1/projects/by-name/{name}` or `GET /api/v1/projects?name=...` |
| `agh/common/ids.py` | No change — ID format stays canonical | — |
| `agh/common/validation.py` | No change | — |
| `openspec/specs/` (CLI + API) | New requirements for name/email acceptance | Spec updates in `specs/cli/spec.md` and `specs/api/spec.md` |

### No changes needed

| Area | Rationale |
|------|-----------|
| Pack routes (`/packs`) | Already human-readable via domain/name@version |
| Assignment routes (project_packs) | No natural human-readable name for assignments |
| Auth middleware (`auth.py`) | Resolution happens before auth check, not during |
| DB schema | IDs remain canonical; resolution is a query, not a storage change |
| `agh pull`, `agh sync`, `agh agent` | These commands use repo URLs or local filesystem state, not IDs |
| `agh login` | Already uses email — no change |

## Approaches

### Approach A: CLI-only resolution via dedicated API endpoints

Add `GET /api/v1/users/by-email/{email}` and `GET /api/v1/projects/by-name/{name}` server endpoints. The CLI calls these before the action command (e.g., `user update` first calls the lookup endpoint, gets the `usr_...` ID, then calls `PATCH /api/v1/users/{id}`).

**Pros:**
- API stays clean — action routes continue to accept only canonical IDs
- Resolution logic is centralized, reusable (e.g., for future web UI)
- CLI can clearly distinguish "not found" from "ambiguous"
- Exact match enforcement is natural with `WHERE email = ?` or `WHERE name = ?`

**Cons:**
- Every affected CLI command makes two API calls instead of one (added latency)
- CLI must handle resolution errors (not found, ambiguous matches) before the action
- New API surface to document and maintain

**Ambiguity handling for projects:** `name` is not unique; multiple projects can share the same name (only active repo URL is unique). Resolution by name MUST reject ambiguous matches (>1 active project with same name). Resolution by email is safe because email is UNIQUE.

### Approach B: Server-side dual-acceptance

Modify action routes to accept either the prefixed ID OR the name/email in the URL path. The server detects the format and performs the lookup transparently.

**Pros:**
- Single API call per CLI command
- Resolution is transparent to the CLI

**Cons:**
- URL paths become complex (e.g., `/users/{user_or_email}`)
- Server must guess whether the input is an ID, email, or name — error-prone
- `400 vs 404` semantics blur; error messages become confusing
- Ambiguity detection is harder to surface to the user
- Violates "IDs remain canonical" direction — the API stops being ID-only

### Approach C: CLI sidecar resolution via existing list endpoints

The CLI fetches the full list (`GET /api/v1/users`, `GET /api/v1/projects`), filters client-side to find the matching name/email, extracts the ID, then calls the action route with the ID.

**Pros:**
- No new API endpoints needed
- CLI has full context for disambiguation

**Cons:**
- `list` endpoints may return many results; filtering client-side is wasteful
- Requires sufficient API permission to list all users/projects (admin role for users)
- New data on every action command; scales poorly
- Race conditions if a resource is renamed between resolution and action

### Approach D: Server-side batch resolution endpoint

Single endpoint `POST /api/v1/resolve` that accepts a map of logical identifiers and returns canonical IDs. CLI calls once before action.

**Pros:**
- Single resolution endpoint for all resource types
- Future-proof for additional resource types

**Cons:**
- Over-engineered for two resource types
- Extra abstraction layer adds cognitive overhead
- Still requires two API calls per CLI command

## Recommendation

**Approach A** — CLI resolution via dedicated per-resource lookup endpoints.

**Rationale:**
1. Aligns with "IDs remain canonical; names/emails are CLI convenience" — the API stays ID-only for mutations.
2. "Resolve name/email to ID before action" is explicitly called out.
3. Dedicated endpoints (`by-email`, `by-name`) make resolution semantics unambiguous.
4. Exact match enforcement is natural in SQL (`WHERE email = ?`).
5. Ambiguity handling is straightforward: if `COUNT(*) > 1` for a project name, return a clear error.

**Specific design points:**
- **Users**: `GET /api/v1/users/by-email/{email}` — returns `{"id": "usr_...", "email": "..."}` or 404. Email is unique, so no ambiguity.
- **Projects**: `GET /api/v1/projects/by-name/{name}` — returns `{"id": "prj_...", "name": "..."}` if exactly one active project matches; returns `409 CONFLICT` (or `422`) with `{"detail": "multiple projects match name ...", "matches": [...]}` if ambiguous; returns `404` if none match.
- **Email preference for users**: The CLI, when given an input that does NOT match `usr_` prefix format, tries email resolution first. This matches "prefer email over display name" from the product direction.
- **Input format detection in CLI**: If the argument starts with `usr_`, treat as ID (passthrough). Otherwise, treat as email (call lookup). Same for `prj_` prefix for projects.
- **Scripts should keep using IDs**: No behavior change for prefixed-ID input paths.

**Out of scope for resolution:**
- Pack assignments (`asn_...`) — no natural human-readable identifier.
- Pack references — already human-readable.

## Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Project name collisions cause CLI frustration | Medium | Return clear error message listing colliding project IDs/names; user can fall back to ID |
| CLI becomes chatty with extra API calls | Low | Resolution is a lightweight DB query; latency impact minimal |
| Race: project renamed between resolution and action | Low | Action route receives target ID; rename between calls is unlikely and only causes a 404 at action time |
| Users type email for `user delete` and project name is matched instead | Low | Input format detection (`usr_` prefix vs email format) disambiguates; email contains `@` |
| Admin calls `user update` with email and expects to change email of the matched user | Medium | The resolved ID is passed to the action; `--email` option still sets the new email. This is correct behavior — the arg is the identifier, the option is the field to update. Document clearly. |

## Ready for Proposal

Yes. The scope is well-defined: CLI-side resolution for users (email) and projects (name) via dedicated server lookup endpoints. Pack operations, assignments, sync, pull, and agent commands are unaffected. The existing API and ID contracts remain unchanged.
