# Data Model: ArcGIS Web GIS Item Dependency Interrogation

## Entity: DependencyInterrogationRequest
- Description: Normalized request context for one invocation.
- Fields:
- `requested_item_ids`: `list[str]` (resolved from parameter or config)
- `source`: `str` (`parameter` or `config`)
- `output_excel_path`: `Path | None`
- `recursive`: `bool` (always `True` for this feature)

Validation rules:
- `requested_item_ids` must be non-empty after normalization.
- Item IDs must be non-empty strings after trimming.
- `output_excel_path`, if provided, must target a writable location.

## Entity: DependencyTraversalNode
- Description: Internal representation of a discovered item for traversal.
- Fields:
- `item_id`: `str`
- `item_name`: `str | None`
- `depth`: `int`
- `parent_item_id`: `str | None`

Validation rules:
- `depth >= 0`
- `item_id` must be present for valid nodes.

## Entity: DependencyRelationshipRow
- Description: One output row in the default DataFrame.
- Fields:
- `parent_item_id`: `str`
- `parent_item_name`: `str`
- `dependent_item_id`: `str`
- `dependent_item_name`: `str`

Validation rules:
- All four fields are always present in the result schema.
- Failure rows must use `dependent_item_id="__ERROR__"`.
- Failure reason text must be stored in `dependent_item_name`.

## Entity: FailureRecord
- Description: Captured per-item failure details represented in-band in output rows.
- Fields:
- `requested_item_id`: `str`
- `failure_reason`: `str`
- `failure_type`: `str` (e.g., invalid ID, inaccessible item, traversal error)

Validation rules:
- Failure records must map deterministically to emitted failure rows.

## Relationships
- One `DependencyInterrogationRequest` resolves to many `DependencyTraversalNode` entries.
- Traversal nodes produce many `DependencyRelationshipRow` entries.
- Zero or more `FailureRecord` entries may be produced for a request.

## State Transitions
1. Input received -> IDs resolved (parameter/config)
2. IDs resolved -> Traversal started (per ID)
3. Traversal started -> Relationship rows accumulated
4. Traversal started -> Failure records captured (if needed)
5. Rows accumulated -> Dedup applied by `(parent_item_id, dependent_item_id)`
6. Dedup complete -> Return DataFrame or write workbook and return `Path`