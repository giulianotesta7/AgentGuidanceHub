# Project Name Resolution Specification

## Purpose

Resolve a globally unique project name to its canonical `prj_...` identifier via a dedicated server endpoint.

## Requirements

### Requirement: Name-to-ID Resolution

The system MUST provide `GET /api/v1/projects/by-name/{name}` returning the project's `{id, name}` on unique match.

#### Scenario: Unique name resolves

- GIVEN an authenticated request to the project name resolution endpoint
- AND exactly one active project matches the name within the requester's visibility scope
- WHEN the request is processed
- THEN the response MUST be 200 with the project's canonical ID and name

#### Scenario: Name not found

- GIVEN an authenticated request to the project name resolution endpoint
- AND no active project matches the name within scope
- WHEN the request is processed
- THEN the response MUST be 404

#### Scenario: Unauthenticated request

- GIVEN an unauthenticated request
- WHEN the request is processed
- THEN the response MUST be 401

### Requirement: Visibility-Scoped Lookup

The system MUST scope project name resolution to projects the requester can see, returning 404 for out-of-scope names.

#### Scenario: Out-of-scope name returns not found

- GIVEN an authenticated user
- AND a project name exists but outside the user's visibility scope
- WHEN the user requests resolution of that name
- THEN the response MUST be 404

### Requirement: Name Uniqueness

Project names MUST be globally unique across all projects. The system MUST enforce a UNIQUE constraint on project names.

#### Scenario: Duplicate name rejected at creation

- GIVEN an existing project with name `my-project`
- WHEN a user attempts to create a new project with the same name
- THEN the creation MUST fail with a conflict error

### Requirement: Non-Numeric Name Validation

Project names MUST NOT consist entirely of digits. The system MUST reject digit-only names at creation and rename.

#### Scenario: Digit-only name rejected at creation

- GIVEN a creation request with project name `12345`
- WHEN the request is processed
- THEN the response MUST be 400 with a validation error

#### Scenario: Digit-only name rejected at rename

- GIVEN a rename request with project name `12345`
- WHEN the request is processed
- THEN the response MUST be 400 with a validation error

### Requirement: Exact Match Only

The system MUST perform exact, case-sensitive matching on project names.

#### Scenario: Case variance returns not found

- GIVEN a project with name `MyProject`
- WHEN a resolution request uses `myproject`
- THEN the response MUST be 404
