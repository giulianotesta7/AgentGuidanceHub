# Apply Progress: Global Skill Collections — PR 1A

## Scope

PR 1A collection foundation for feature-branch-chain issue #97. Base branch: `feat/global-skill-collections` / tracker PR #98. Excludes collection package assignments, skill-only validation, `GET /skills`, `GET /skills:resolve`, CLI global skills, workspace prompt wording, and PR creation.

## Mode

Strict TDD evidence was produced during the original oversized server slice. This split keeps only PR 1A foundation tests and implementation. Test runner: `uv run pytest`.

## Completed Tasks

- [x] 1.1 Add `agh/server/migrations/004_collections.sql` for `collections` plus `col_` ID prefix updates.
- [x] 1.3 Add route/module wiring in `agh/server/app.py` for the new collections router.
- [x] 2.1A Implement collection CRUD endpoints with owner/admin mutation and member read/list behavior.
- [x] 4.1A Write focused tests for collection migration, auth, CRUD/list/get/update/delete, and active/inactive behavior.

## TDD Cycle Evidence

| Task | Test File | RED | GREEN | REFACTOR |
|------|-----------|-----|-------|----------|
| 1.1 | `tests/test_db_migrations.py` | Migration/prefix assertions failed before support | `uv run pytest tests/test_db_migrations.py tests/test_collection_routes.py` → 12 passed | Collection table, migration version, and `col_` prefix covered |
| 1.3 | `tests/test_collection_routes.py` | `/api/v1/collections` returned 404 before router wiring | Focused tests and full suite passed | Existing app include pattern reused |
| 2.1A | `tests/test_collection_routes.py` | Owner/admin/member CRUD tests failed before routes | Focused tests and full suite passed | Route module contains only collection foundation behavior |
| 4.1A | `tests/test_collection_routes.py`, `tests/test_db_migrations.py` | Foundation tests introduced before production code in original slice | Focused tests and full suite passed | PR 1B tests were removed and preserved externally |

## Verification Commands

- `uv run pytest tests/test_db_migrations.py tests/test_collection_routes.py` → 12 passed.
- `uv run pytest` → 358 passed, 1 skipped.

## Files Changed

- `agh/common/ids.py` — added the `col_` ID prefix.
- `agh/server/migrations/004_collections.sql` — added the `collections` table.
- `agh/server/routes/collections.py` — added collection CRUD routes only.
- `agh/server/app.py` — registered the collections router under `/api/v1`.
- `tests/test_db_migrations.py` — added collection schema and ID prefix coverage.
- `tests/test_collection_routes.py` — added foundation route coverage.
- `openspec/changes/global-skill-collections/tasks.md` — marked only PR 1A tasks complete and deferred PR 1B.

## Remaining / Risks

- PR 1B must add `collection_packages` storage, `casn_` ID prefix, assignment endpoints, skill-only validation, and skill list/resolve tests.
- CLI global skill work remains for PR 2.
