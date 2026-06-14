# Apply Progress: Fix Workspace Pull Atomicity

## PR1 Scope
Stacked-to-main PR1: cache staging + rollback helpers only. Target/skill promotion and lock-last stay in PR2.

## Completed Tasks
- [x] 1.1 Cache staging helpers.
- [x] 1.2 AGH-owned rollback/stale cleanup with cache-boundary proof.
- [x] 1.3 Stage safety tests, including second-write failure and symlink/boundary cleanup.

## TDD Cycle Evidence
| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|---|---|---|---|---|---|---|---|
| PR1 review fixes | `tests/test_workspace_pull.py` | Unit | ✅ 46/46 | ✅ Boundary misuse test failed before helper signature/code | ✅ 49/49 focused; 290/290 full | ✅ second write failure + symlink cleanup | ✅ ruff format/check |

## Remaining
- [ ] PR2 target/skill promotion + lock-last flow.
- [ ] PR3 CLI regressions/proof points.
