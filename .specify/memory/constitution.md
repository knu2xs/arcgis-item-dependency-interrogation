<!--
Sync Impact Report
- Version change: unversioned template -> 1.0.0
- Modified principles:
	- Template Principle 1 -> I. Configuration and Secrets First
	- Template Principle 2 -> II. CRS Integrity and Spatial Correctness
	- Template Principle 3 -> III. Logging and Error Transparency
	- Template Principle 4 -> IV. Testable, Incremental Delivery
	- Template Principle 5 -> V. SQL Safety and Data Handling Discipline
- Added sections:
	- Implementation Constraints
	- Delivery Workflow and Quality Gates
- Removed sections:
	- None
- Templates requiring updates:
	- ✅ .specify/templates/plan-template.md
	- ✅ .specify/templates/spec-template.md
	- ✅ .specify/templates/tasks-template.md
	- ✅ .specify/templates/commands/*.md (no files present)
	- ✅ README.md (no update required; no constitution references)
- Deferred TODOs:
	- None
-->

# ArcGIS Item Dependency Interrogation Constitution

## Core Principles

### I. Configuration and Secrets First
All runtime behavior that can vary by environment MUST be sourced from project configuration.
Credentials and sensitive values MUST reside in local secrets files and MUST NOT be committed.
Hardcoded credentials, hardcoded environment-specific URLs, and hardcoded output paths are forbidden.
This reduces deployment risk and prevents credential leaks.

### II. CRS Integrity and Spatial Correctness
Spatial inputs MUST have an explicit CRS before processing.
Reprojection MUST be explicit for every source-to-target CRS transformation.
Distance, area, and length calculations MUST run in an appropriate projected CRS.
WKIDs or EPSG codes MUST be configuration-driven rather than hardcoded in code.
This protects analytical correctness and prevents silent spatial corruption.

### III. Logging and Error Transparency
Production and script code MUST use project logging utilities instead of print statements.
Exception handling MUST follow build-message -> log -> raise so failures are visible and consistent.
Important processing milestones and branch decisions SHOULD be logged at informative levels.
This ensures failures are diagnosable from logs alone.

### IV. Testable, Incremental Delivery
New behavior MUST include tests in the testing tree that mirror source structure.
Each feature SHOULD be implementable and verifiable as an independently valuable increment.
ArcPy and external system interactions MUST use fixtures, controlled test data, or mocks where appropriate.
This preserves quality while enabling safe iteration.

### V. SQL Safety and Data Handling Discipline
Non-trivial SQL MUST be externalized into SQL files under the package SQL directory.
Queries MUST use bind parameters for user or runtime-supplied values.
Source data in data/raw MUST be treated as immutable.
Generated outputs MUST be written to approved interim or processed locations.
This reduces injection risk and protects raw data provenance.

## Implementation Constraints

- Python code MUST follow project style guidance: explicit type hints and Google-style docstrings.
- Public APIs MUST NOT be renamed or signature-changed without explicit approval.
- New dependencies require explicit review before they are added to dependency manifests.
- Module and script paths MUST use pathlib.Path rather than os.path string concatenation.

## Delivery Workflow and Quality Gates

- Plans MUST include a constitution check before implementation starts.
- Pull requests MUST document how changed code satisfies applicable principles.
- Tests and formatting checks MUST pass before merge.
- Constitution compliance review is required for all feature specifications, plans, and task lists.

## Governance

This constitution supersedes conflicting local workflow habits for this repository.

Amendment process:
- Propose changes in a documented update that includes rationale and impact.
- Update affected templates and guidance files in the same change when applicable.
- Record a Sync Impact Report at the top of the constitution file.

Versioning policy:
- MAJOR: Principle removals, incompatible governance changes, or redefinition of mandatory rules.
- MINOR: New principle or materially expanded mandatory guidance.
- PATCH: Clarifications, wording, and non-semantic edits.

Compliance review expectations:
- Every implementation plan MUST pass a constitution gate before execution.
- Every task list MUST preserve testing, logging, and data-safety requirements.
- Reviews MUST block merges when principle violations are unresolved.

**Version**: 1.0.0 | **Ratified**: 2026-06-05 | **Last Amended**: 2026-06-05
