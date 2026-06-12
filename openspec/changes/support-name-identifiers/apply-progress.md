## PR 1 / Slice 1: Project refs only

- Branch: `feat/project-name-refs`
- Chain strategy: `stacked-to-main`
- Target: `main`
- Scope: project identifiers only; user email refs and pack `name@version` refs are intentionally out of scope for PR1.
- Mode: Standard (`strict_tdd: false`); tests were updated alongside behavior.

## Completed

- Added shared `validate_project_name()` validation for required, trimmed, non-digit-only project names.
- Added migration `002_unique_project_names.sql` with global `ux_projects_name` uniqueness.
- Mapped duplicate project names to `409` and digit-only project names to `400` on create/update.
- Added `GET /api/v1/projects/by-name/{name:path}` with exact, active, visibility-scoped single-row lookup.
- Resolved CLI project refs by exact project name through `agh/cli/project_refs.py` for project get/update/delete/member/pack commands while preserving `prj_...` and all-digit passthrough.
- Updated English README/CLI help guidance for project refs.

## Verification

- `uv run pytest tests/test_common_helpers.py tests/test_db_migrations.py tests/test_project_routes.py tests/test_cli_admin_commands.py tests/test_cli_pack_commands.py tests/test_docs_guidance.py` — passed (75 tests, 1 existing Starlette/httpx warning).
- `uv run pytest` — passed (244 tests, 1 existing Starlette/httpx warning).

## Remaining Future Slices

- PR2 user email refs: endpoint, CLI user show/resolution, and tests.
- PR3 pack version refs: resolver endpoint/parser, CLI pack-ref resolution, and tests.
