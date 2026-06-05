# Research: ArcGIS Web GIS Item Dependency Interrogation

## Decision 1: Input Resolution Priority
- Decision: Resolve item IDs in this order: explicit function parameter, then config `request_item_ids`.
- Rationale: Keeps call-site overrides deterministic while supporting config-driven batch runs.
- Alternatives considered:
- Config-first resolution
- Merge parameter and config lists by default

## Decision 2: Recursive Traversal Strategy
- Decision: Use recursive dependency graph traversal with cycle protection via visited edge set.
- Rationale: Clarified requirement is full recursive dependency coverage with no infinite loops.
- Alternatives considered:
- Direct dependencies only
- Fixed-depth traversal

## Decision 3: Mixed-Validity Error Handling
- Decision: Best-effort processing across item IDs; continue valid IDs when some fail.
- Rationale: Prevents unnecessary data loss in batch analyses and aligns with clarified behavior.
- Alternatives considered:
- Fail-fast on first invalid/inaccessible item
- Strict mode only with no best-effort path

## Decision 4: Failure Row Encoding in Default Table
- Decision: Encode failures in-band as rows using `dependent_item_id="__ERROR__"` and
  `dependent_item_name="<failure reason>"`.
- Rationale: Preserves required return schema while retaining machine-detectable failure signals.
- Alternatives considered:
- Separate companion error object
- Logging-only failure reporting

## Decision 5: Dedupe Semantics
- Decision: Deduplicate rows by `(parent_item_id, dependent_item_id)`.
- Rationale: Prevents recursive overlap inflation while preserving distinct relationships.
- Alternatives considered:
- No dedupe
- Dedupe scoped per requested root item only

## Decision 6: Export Behavior and Return Type
- Decision: Default return is DataFrame; when output workbook path is provided and write succeeds,
  return `pathlib.Path`.
- Rationale: Matches explicit feature requirement and supports reporting workflows.
- Alternatives considered:
- Always return DataFrame with optional side-effect export
- Always return tuple `(dataframe, path|None)`

## Decision 7: Logging Pattern
- Decision: Use project logger and record item-level processing milestones and failures.
- Rationale: Satisfies constitution requirements for diagnosable error handling.
- Alternatives considered:
- Sparse logging
- Exception-only logging at outer boundaries