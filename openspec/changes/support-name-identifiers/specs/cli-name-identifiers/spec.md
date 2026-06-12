## Purpose

For PR1, CLI project commands accepting project refs MUST resolve exact project names to canonical project IDs before action. Prefixed project IDs and all-digit project refs bypass name resolution.

User email refs and pack-version refs are future chained slices, not PR1 requirements.

## Requirements

### Requirement: Project Input Format Detection

The CLI MUST detect `prj_...`, all-digit project refs, and project names before routing project commands.

#### Scenario: Prefixed project ID passes through

- GIVEN an argument starting with `prj_`
- WHEN the project command runs
- THEN the ID MUST pass directly without resolution

#### Scenario: All-digit project ref passes through

- GIVEN `agh project get 12345`
- WHEN the argument is entirely digits
- THEN the CLI MUST pass it directly without name resolution

### Requirement: Project Reference by Name

The CLI MUST treat non-prefixed, non-all-digit project arguments as project names.

#### Scenario: Name resolves

- GIVEN `agh project get my-project`
- WHEN the argument does not start with `prj_` and is not all digits
- THEN the CLI MUST pass the resolved ID to the action

#### Scenario: Name not found

- GIVEN `agh project get nonexistent`
- WHEN resolution returns 404
- THEN the CLI MUST print not-found and exit non-zero

### Requirement: Numeric-Safe Project Names

Project names MUST NOT consist entirely of digits. The CLI/server behavior MUST prevent ambiguous project refs by rejecting digit-only project names at creation and rename.

#### Scenario: Digit-only name rejected at create

- GIVEN `agh project create 12345`
- WHEN the command runs
- THEN the CLI MUST report a validation error

#### Scenario: Digit-only name rejected at rename

- GIVEN `agh project update prj_... --name 12345`
- WHEN the command runs
- THEN the CLI MUST report a validation error

### Requirement: Project Resolution Before Action

The CLI MUST resolve human-readable project names to canonical project IDs before server mutation/detail calls.

#### Scenario: Resolution precedes delete

- GIVEN `agh project delete my-project`
- WHEN the CLI runs
- THEN it MUST resolve the name to a `prj_...` ID before calling the delete endpoint

### Requirement: Project Backward Compatibility

Existing project ID-based scripts MUST continue to work unchanged.

#### Scenario: Existing project ID script

- GIVEN `agh project get prj_abc123def456`
- WHEN the command runs
- THEN behavior MUST be identical to the current release

### Requirement: Unauthorized Project Resolution

When the project resolution endpoint returns 401, the CLI MUST surface the auth error.

#### Scenario: Expired token

- GIVEN `agh project get my-project`
- AND the auth token is expired
- WHEN resolution returns 401
- THEN the CLI MUST print an auth error and suggest re-login
