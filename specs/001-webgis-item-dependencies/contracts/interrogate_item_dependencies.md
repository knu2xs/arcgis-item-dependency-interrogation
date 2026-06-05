# Contract: interrogate_item_dependencies

## Interface Type
Python library function exposed from `arcgis_dependency`.

## Location
- Implementation target: `src/arcgis_dependency/_main.py`
- Export target: `src/arcgis_dependency/__init__.py`

## Proposed Signature
```python
interrogate_item_dependencies(
    item_ids: str | list[str] | None = None,
  gis: arcgis.gis.GIS | None = None,
    output_excel: str | Path | None = None,
) -> pandas.DataFrame | Path
```

## Inputs
- `item_ids`:
- Optional single item ID string or list of item ID strings.
- If omitted, implementation resolves IDs from config key `request_item_ids`.

- `gis`:
- Optional pre-built `arcgis.gis.GIS` instance.
- If provided, implementation uses this object instead of building a GIS from config.

- `output_excel`:
- Optional workbook output path.
- If provided and write succeeds, function returns `Path` to written workbook.

## Output Contracts
### Default output (`output_excel` not provided)
- Return type: `pandas.DataFrame`
- Required columns:
- `parent_item_id`
- `parent_item_name`
- `dependent_item_id`
- `dependent_item_name`

### Export output (`output_excel` provided)
- Write workbook with dependency rows.
- Return type: `pathlib.Path`
- Returned path points to the written workbook.

## Behavioral Contracts
- Supports ArcGIS Online and ArcGIS Enterprise sites.
- Performs recursive dependency traversal.
- Must be cycle-safe.
- Must process mixed-validity batches in best-effort mode.
- Must deduplicate by `(parent_item_id, dependent_item_id)`.
- Must encode failure rows in-band using:
- `dependent_item_id="__ERROR__"`
- `dependent_item_name="<failure reason>"`

## Error Contracts
- If no IDs are available from parameter or config, raise actionable error.
- If workbook output path is not writable, raise actionable error.
- Item-level failures in mixed batches are represented as failure rows instead of aborting
  the full operation.