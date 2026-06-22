---
name: agh-cli-validation
description: "Trigger: AGH CLI validation, manual CLI check, agh command, workspace pull, config file. Safely verify AGH CLI behavior during development."
license: Apache-2.0
metadata:
  author: "giulianotesta7"
  version: "1.0"
---

# AGH — CLI Validation Skill

## Activation Contract

Load this skill when a change touches AGH CLI commands, local config behavior, workspace pull/sync, package installation, or PR validation needs manual CLI evidence.

This skill is for agents validating AGH during development. It is not end-user usage documentation.

## Hard Rules

1. **Do not expose real tokens.** Never print, copy, or commit values from `.agh-cli-dev.toml`, `.agh-cli-test.toml`, `~/.config/agh/config.toml`, or API responses that include secrets.
2. **Use isolated config.** Prefer `AGH_CONFIG_FILE=<temp-file>` for local validation instead of the user's real config.
3. **Use isolated data/workspaces.** Prefer temp directories or disposable worktrees when testing workspace pull/sync behavior.
4. **Start with read-only commands.** Use `agh --help`, command `--help`, `config show`, and dry-run modes before mutating state.
5. **Do not hit a real server unless the user explicitly approves it.** Mocked tests or local test servers are preferred.
6. **Report exact commands.** Include env vars and flags that affect config/data isolation, but redact tokens.

## Decision Gates

| Change | CLI validation |
| --- | --- |
| CLI help, command wiring, Typer options | `uv run agh --help` and affected command `--help`. |
| Config loading/saving | Use `AGH_CONFIG_FILE=$(mktemp)` or a temp path; verify `agh config show` masks tokens. |
| Login/auth behavior | Prefer pytest with mocked API; only use real server with explicit approval. |
| Workspace pull/sync | Use temp workspace and isolated `AGH_CONFIG_FILE`; prefer `--dry-run` first. |
| Pack/package install behavior | Use test server/fixtures when possible; avoid global user skill dirs unless explicitly testing global install. |
| Packaging/install behavior | `uv build`, `uv tool install --force dist/*.whl`, then `agh --help`. |

## Execution Steps

1. Identify the affected CLI command and whether it reads config, writes files, calls the server, or touches workspace state.
2. Choose the safest validation target: unit test, focused pytest, help command, dry-run, temp workspace, or installed wheel check.
3. Set `AGH_CONFIG_FILE` to a temp config when command behavior needs config.
4. Redact tokens from commands, logs, screenshots, and PR bodies.
5. Run the smallest command that proves the behavior.
6. If validating mutation, inspect only the temp workspace/data paths.
7. Report exact commands, expected result, actual result, and cleanup state.

## Safe Command Patterns

```bash
# Help and command discovery
uv run agh --help
uv run agh <command> --help

# Isolated config path
tmp_config="$(mktemp)"
AGH_CONFIG_FILE="$tmp_config" uv run agh config show

# Package install validation
uv build
uv tool install --force dist/*.whl
agh --help
```

For workspace tests, run inside a temp directory and prefer dry-run first:

```bash
tmp_dir="$(mktemp -d)"
cd "$tmp_dir"
AGH_CONFIG_FILE="/path/to/temp-config.toml" uv run agh pull --dry-run
```

## Output Contract

Return:
- CLI command or workflow validated.
- Whether validation used unit tests, local command, installed CLI, or server-backed flow.
- Config/data isolation used (`AGH_CONFIG_FILE`, temp dir, dry-run, fixture, or mock).
- Exact commands run with secrets redacted.
- Expected result and actual result.
- Cleanup performed or remaining local state.

## References

- `agh/cli/main.py` — Typer command wiring and command behavior.
- `agh/cli/config.py` — `AGH_CONFIG_FILE`, config loading, and token masking.
- `tests/test_cli_*.py` — focused CLI tests using `typer.testing.CliRunner`.
- `skills/agh-testing-coverage/SKILL.md` — choose focused vs broad validation.
- `skills/agh-docs-alignment/SKILL.md` — keep documented CLI examples aligned.
