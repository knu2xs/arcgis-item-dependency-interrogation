# Implementation Plan: Parent Dependency Impact Analysis

**Branch**: `002-webgis-item-dependencies` | **Date**: 2026-06-05 | **Spec**: `specs/002-parent-impact-analysis/spec.md`

**Input**: Feature specification from `/specs/002-parent-impact-analysis/spec.md`

## Summary

Add a new parent-impact interrogation capability that determines what would be affected by deleting one or more target items.
The feature returns explicit beginner-friendly columns (`target_*`, `affected_*`) and a per-target tri-state decision summary
(`safe_to_delete`, `not_safe_to_delete`, `unknown_requires_review`). It scans all accessible items for complete coverage,
includes full recursive/transitive impact, and prioritizes correctness over runtime performance.

## Technical Context

**Language/Version**: Python 3.14 (project requires Python >=3.9)

**Primary Dependencies**: `arcgis`, `pandas`, `openpyxl`, project config/logging utilities

**Storage**: N/A (in-memory graph traversal with optional `.xlsx` workbook output)

**Testing**: `pytest` with fake GIS/item fixtures and focused feature tests under `testing/`

**Target Platform**: ArcGIS Pro / ArcGIS API for Python runtime (Windows developer environment)

**Project Type**: Python library package (`src/arcgis_dependency`)

**Performance Goals**: Correctness-first full-scope dependency impact; no hard latency target

**Constraints**: Must not omit valid dependents; tri-state decision output required for unresolved dependencies

**Scale/Scope**: Organization-wide scan of all accessible items; recursive transitive traversal per target

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gate

- Configuration and secrets: PASS - planned changes keep authentication/config through `config` and optional caller-supplied `GIS`; no hardcoded credentials.
- CRS integrity: PASS - no spatial CRS transformations are introduced by this feature.
- Logging and errors: PASS - plan preserves explicit logging and build-message -> log -> raise patterns with in-table failure encoding.
- Testing strategy: PASS - plan defines independent tests for single target, batch, tri-state summary, and workbook export.
- SQL and data handling: PASS - no SQL additions; no writes to `data/raw`.

### Post-Design Re-Check

- Configuration and secrets: PASS - contract and quickstart keep config-driven auth and optional supplied GIS.
- CRS integrity: PASS - data model and contracts confirm non-spatial behavior.
- Logging and errors: PASS - design specifies failure rows and summary rationale fields.
- Testing strategy: PASS - quickstart includes independent validation for each user story.
- SQL and data handling: PASS - no SQL/data-location violations introduced.

## Project Structure

### Documentation (this feature)

```text
specs/002-parent-impact-analysis/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── interrogate_parent_dependency_impact.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── arcgis_dependency/
    ├── __init__.py
    ├── _main.py
    ├── config.py
    └── utils/

testing/
├── conftest.py
├── test_arcgis_dependency.py
└── test_dependency_interrogation.py
```

**Structure Decision**: Keep a single-library structure and implement parent-impact behavior in `src/arcgis_dependency/_main.py`
with accompanying tests in `testing/test_parent_impact_single.py`, `testing/test_parent_impact_batch.py`, and
`testing/test_parent_impact_export.py`. No new top-level packages are needed.

## Complexity Tracking

No constitution violations identified; no complexity exemptions required.
