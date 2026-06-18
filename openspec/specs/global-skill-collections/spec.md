# global-skill-collections Specification

## Purpose

Provide admin-curated global skill collections that members can discover and install into their selected agent’s native global skill directory without changing repo/workspace-scoped project behavior.

## Requirements

### Requirement: Collection governance

The system MUST treat collections as global tooling catalogs, separate from repo-backed projects. Only owners and admins MAY create, edit, or assign collections; members MAY list available collection skills.
Collections and collection package assignments MUST support active/inactive state. Available skill listing and install resolution MUST include only active collections and active collection package assignments.

#### Scenario: Admin manages a collection

- GIVEN an authenticated owner or admin
- WHEN they create or update a collection or assign a package to it
- THEN the change is accepted

#### Scenario: Member lists collections

- GIVEN an authenticated member
- WHEN they request available collection skills
- THEN the system returns readable collection listings

#### Scenario: Inactive collection is excluded

- GIVEN a collection is inactive
- WHEN a member lists or resolves available skills
- THEN skills from that collection are not returned

#### Scenario: Inactive collection package assignment is excluded

- GIVEN an active collection has an inactive package assignment
- WHEN a member lists or resolves available skills
- THEN skills from that package assignment are not returned

### Requirement: Skill-only package assignment

The system MUST accept only skill-only packages for collection assignment. Packages containing `instructions/AGENTS.md` or `instructions/CLAUDE.md` MUST be rejected.

#### Scenario: Valid skill package is assigned

- GIVEN a package that contains only skill artifacts
- WHEN an owner or admin assigns it to a collection
- THEN the assignment succeeds

#### Scenario: Instruction-bearing package is rejected

- GIVEN a package that contains `instructions/AGENTS.md` or `instructions/CLAUDE.md`
- WHEN it is assigned to a collection
- THEN the system rejects the assignment

### Requirement: Global skill install, list, and remove

The `agh skill install <package-ref> <skill-name>` command MUST install collection-backed skills globally for the selected agent, `agh skill list` MUST show skills available from active collections, and `agh skill remove <skill-name>` MUST remove the local global installation for the selected or default agent.

#### Scenario: Install resolves a concrete package version

- GIVEN an available collection package ref such as `@latest`
- WHEN a member installs a skill
- THEN the system records the resolved version and checksum in local AGH state

#### Scenario: Remove clears the local installation record

- GIVEN a previously installed global skill
- WHEN the user removes it
- THEN the local installation is removed and the local lock is updated

### Requirement: Global skill target and conflict rules

The system MUST install to the selected agent’s native global skill directory, maintain AGH-owned cache and lock state under user AGH state, and enforce update rules: same checksum is a no-op, AGH-owned version or checksum changes update automatically, same skill name from a different package conflicts, and untracked targets require `--force`.

#### Scenario: AGH-owned install updates cleanly

- GIVEN an AGH-owned installed skill with a changed checksum or version
- WHEN the user installs again
- THEN the installation updates automatically

#### Scenario: Untracked target requires force

- GIVEN an existing local target not tracked by AGH
- WHEN the user installs without `--force`
- THEN the system rejects the overwrite

### Requirement: Agent selection and defaults

The system MUST use the configured default global-skills agent when present. Otherwise it MUST prompt with the wording `Select the agent for global skills:` and allow the user to save a new default after selection.

#### Scenario: Default agent is used

- GIVEN a configured default global-skills agent
- WHEN the user runs a global skill command
- THEN that agent is selected automatically

#### Scenario: User selects and saves a default

- GIVEN no saved default agent
- WHEN the user is prompted and selects an agent
- THEN the command proceeds and the user MAY save that choice as the default
