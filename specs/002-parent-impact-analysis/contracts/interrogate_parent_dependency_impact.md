# Contract: interrogate_parent_dependency_impact

## Interface Type
Python library function exposed from `arcgis_dependency`.

## Location
- Implementation target: `src/arcgis_dependency/_main.py`
- Export target: `src/arcgis_dependency/__init__.py`

## Implemented Signature
```python
interrogate_parent_dependency_impact(
    target_item_ids: str | list[str] | None = None,
    gis: arcgis.gis.GIS | None = None,
    output_excel: str | Path | None = None,
) -> dict[str, pandas.DataFrame] | Path
```

## Inputs
- `target_item_ids`:
- Optional single target item ID or list of target IDs.
- If omitted, implementation resolves from config key `request_item_ids`.

- `gis`:
- Optional pre-built `arcgis.gis.GIS` instance.
- If provided, implementation uses it rather than building from config.

- `output_excel`:
- Optional workbook output path.
- If provided, implementation writes workbook and returns the written path.

## Output Contracts
### Default output (`output_excel` not provided)
Return type: `dict[str, pandas.DataFrame]` with keys:
- `impact_rows`: detailed rows with columns:
- `target_item_id`
- `target_item_name`
- `affected_item_id`
- `affected_item_name`
- `relationship_status`
- `reason`

- `target_decisions`: summary rows with columns:
- `target_item_id`
- `target_item_name`
- `decision`
- `affected_count`
- `unknown_count`
- `decision_reason`

### Export output (`output_excel` provided)
- Workbook is written to output path with sheets:
- `impact_rows`
- `target_decisions`
- Return type: `pathlib.Path`

## Behavioral Contracts
- Scans all items accessible to the authenticated user context for complete dependent discovery.
- Includes full recursive/transitive impacted dependencies.
- Deduplicates by (`target_item_id`, `affected_item_id`).
- Preserves best-effort behavior for mixed-validity target lists.
- Returns a decision summary row even when a target has no affected rows.
- Uses tri-state decisions:
- `safe_to_delete`
- `not_safe_to_delete`
- `unknown_requires_review`

## Error Contracts
- If no target IDs are available from input/config, raise actionable `ValueError`.
- If workbook path cannot be written, raise actionable error.
- Item-level and traversal-level failures are represented in detailed rows and reflected in summary decisions.
