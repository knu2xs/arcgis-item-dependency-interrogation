# Implementation Plan: ArcGIS Web GIS Item Dependency Interrogation

**Branch**: `001-execute-feature-hook` | **Date**: 2026-06-05 | **Spec**: `/specs/001-webgis-item-dependencies/spec.md`

**Input**: Feature specification from `/specs/001-webgis-item-dependencies/spec.md`

## Summary

Add a package-level function in `arcgis_dependency` (implemented in `_main.py`, exposed in
`__init__.py`) that interrogates ArcGIS Online and ArcGIS Enterprise item dependencies using
item IDs provided directly (single string or list) or from config (`request_item_ids`).

The feature returns a dependency `pandas.DataFrame` by default with required columns
`parent_item_id`, `parent_item_name`, `dependent_item_id`, and `dependent_item_name`.
When an output workbook path is provided, write the result to Excel and return `pathlib.Path`.

Traversal is recursive, cycle-safe, best-effort for mixed-validity batches, deduplicated by
`(parent_item_id, dependent_item_id)`, and per-item failures are represented in-band using
`dependent_item_id="__ERROR__"` and failure text in `dependent_item_name`.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.14 in project environment (project requirement: `>=3.9`)

**Primary Dependencies**: `arcgis` (ArcGIS Python API), `pandas`, project `config` singleton,
project `get_logger` utility, `pathlib`

**Storage**: N/A (in-memory processing) + optional Excel workbook output path

**Testing**: `pytest` under `testing/`

**Target Platform**: Python library usage in ArcGIS Pro/Conda environments (Windows-first)

**Project Type**: Python library/package

**Performance Goals**: Meet spec outcomes (single-item interrogation practical within ~2 minutes;
batch of at least 25 IDs completes without data loss for valid items)

**Constraints**: No hardcoded credentials or site URLs; recursive traversal must be cycle-safe;
best-effort batch handling with in-table failure rows; dedupe by parent-dependent pair; preserve
required output schema

**Scale/Scope**: One library function + exports + tests for single-item, multi-item, and
optional workbook output; typical batch size at least 25 IDs

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Configuration and secrets: PASS
- Plan uses config-driven item IDs and existing GIS/profile configuration.
- No hardcoded credentials, secrets, or environment URLs required.

- CRS integrity: PASS (N/A for tabular dependency interrogation)
- Feature does not compute spatial metrics or reprojection operations.

- Logging and errors: PASS
- Design includes project logger usage and explicit per-item failure messaging.

- Testing strategy: PASS
- Plan includes independent tests for single-item, multi-item, mixed-validity, recursion safety,
  dedupe behavior, and workbook return behavior.

- SQL and data handling: PASS
- No non-trivial SQL planned; raw data immutability unaffected.

Post-Design Re-check: PASS (no constitution violations introduced by design artifacts)

## Project Structure

### Documentation (this feature)

```text
specs/001-webgis-item-dependencies/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── interrogate_item_dependencies.md
└── tasks.md             # Created later by /speckit.tasks
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
src/
└── arcgis_dependency/
  ├── __init__.py
  ├── _main.py
  ├── config.py
  └── utils/
    ├── __init__.py
    ├── _gis.py
    └── _logging.py

testing/
├── conftest.py
├── test_arcgis_dependency.py
└── test_dependency_interrogation.py
```

**Structure Decision**: Use the existing single-package project layout under
`src/arcgis_dependency` and `testing/`, with focused updates to `_main.py`,
`__init__.py`, and new feature tests.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
