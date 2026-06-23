# Apply Progress: add-scoop-windows-installer

## PR 1: Windows Release Assets and Frozen Version Gate

Status: implemented; CI feasibility gate 1.11 is pending.

## TDD Cycle Evidence

### RED

- [x] 1.1 `tests/test_cli_version.py` first failed because root
  `--version` did not exist.
- [x] 1.2 `tests/test_release_workflow.py` first failed because
  `build-windows`, Windows assets, and zip validation did not exist.
- [x] 1.3 Release dependency assertions first failed because PyInstaller was
  not declared or locked.

### GREEN

- [x] 1.4 Added root `--version` callback to `agh/cli/main.py`.
- [x] 1.5 Left `agh/__init__.py` unchanged; PyInstaller copies `agh`
  metadata with `--copy-metadata agh`.
- [x] 1.6 Added `release = ["pyinstaller>=6.0"]` to `pyproject.toml` and
  updated `uv.lock`.
- [x] 1.7 Added `build-windows` with native `amd64` and `arm64` matrix legs,
  PyInstaller build, frozen version check, zip creation, root `agh.exe` check,
  and artifact upload.
- [x] 1.8 Made PyPI/GHCR depend on `build-windows`; `github-release`
  downloads, verifies, and attaches both Windows zips.

### TRIANGULATE

- [x] 1.9 Added assertions for complete Windows delivery, `fail-fast: false`,
  and `if-no-files-found: error`.
- [x] 1.10 Re-ran focused tests and lockfile checks.
- [ ] 1.11 Pending CI: verify `build-windows (amd64)` and
  `build-windows (arm64)` schedule and pass on GitHub Actions.

### REFACTOR

- [x] 1.12 Kept release YAML scoped to Windows artifacts and existing
  dependency updates. No unrelated release refactors were added.

## Files Changed

- `agh/cli/main.py` — imports `agh.__version__` and adds root `--version`.
- `pyproject.toml` — adds a non-runtime `release` dependency group.
- `uv.lock` — locks PyInstaller 6.21.0 and transitive dependencies.
- `.github/workflows/release.yml` — adds `build-windows`, publication
  dependency updates, and GitHub Release asset attachment.
- `tests/test_cli_version.py` — covers root `--version` behavior.
- `tests/test_release_workflow.py` — covers release workflow structure and
  PyInstaller dependency expectations.
- `changelog.d/+windows-release-assets.added.md` — keeps PR 1 CI-compatible
  by documenting the new Windows release asset behavior.

## Test Commands Run

```bash
# RED phase confirmation
uv run pytest tests/test_cli_version.py tests/test_release_workflow.py -q
# → 24 failed, 2 passed

# GREEN phase
uv run pytest tests/test_cli_version.py -q
# → 3 passed
uv run pytest tests/test_cli_version.py tests/test_release_workflow.py -q
# → 26 passed

# Lockfile
uv lock --locked
# → Resolved 44 packages (in sync)

# Full suite
uv run pytest -q
# → 505 passed, 1 skipped

# Lint/format/type checks from subagent
uv run --with ruff ruff check agh tests
# → All checks passed
uv run --with ruff ruff format --check .
# → 63 files already formatted
uv run --with pyright pyright agh/cli/main.py
# → 0 errors, 0 warnings

# Parent revalidation after reviewer fix
uv run pytest tests/test_release_workflow.py tests/test_cli_version.py -q
# → 27 passed
uv run pytest -q
# → 506 passed, 1 skipped
uv run towncrier check
# → passed
```

## Validation Output

- Focused release and CLI tests pass.
- Full pytest suite passes.
- Towncrier check passes with the PR 1 Windows release asset fragment.
- Lockfile is in sync.
- LSP diagnostics for changed Python/test files report no diagnostics.
- Lens diagnostics are clean after markdown cleanup.

## Diff Size

```text
.github/workflows/release.yml | 117 +++++
agh/cli/main.py               |  12 +-
pyproject.toml                |   1 +
uv.lock                       |  92 ++++
4 files changed, 219 insertions(+), 3 deletions(-)
```

There are also two new test files. PR 1 is near the 400-line review budget
when tests and lockfile are counted. The full SDD artifact set is larger and
should be reviewed separately from the implementation slice.

## Reviewer Fixes

- Fixed GitHub Release asset paths by defining job-level `VERSION` for the
  `github-release` job.
- Strengthened `tests/test_release_workflow.py` so undefined version
  expressions cannot pass by substring alone.

## Deviations from Design

- `SETUPTOOLS_SCM_PRETEND_VERSION_FOR_AGH` is set inside the PowerShell step
  instead of job-level `env:` to avoid long YAML lines.
- `agh/__init__.py` was not modified. Existing importlib metadata behavior is
  retained and paired with PyInstaller `--copy-metadata agh`.
- PR 1 now includes a narrow changelog fragment for Windows release assets so
  CI can pass without relying on a `no-changelog-needed` label. PR 2 still owns
  Scoop install-channel docs and the Scoop-specific release note.

## Remaining Tasks (PR 1)

- [ ] 1.11 Push to CI and verify both Windows matrix legs schedule and pass.
  If `windows-11-arm`, ARM64 Python, PyInstaller, or AGH dependencies fail,
  stop as blocked.

## Remaining Tasks (PR 2)

All PR 2 tasks remain unchecked and blocked by task 1.11.

## PR Boundary

This slice implements PR 1 only: Windows release assets, frozen version gate,
PyInstaller dependency, and paired tests. PR 2 is blocked until CI feasibility
is proven.
