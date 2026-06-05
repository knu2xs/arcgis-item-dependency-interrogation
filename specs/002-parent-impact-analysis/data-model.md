# Data Model: Parent Dependency Impact Analysis

## Entity: ImpactAnalysisRequest
- Description: Input payload controlling parent-impact interrogation execution.
- Fields:
- `target_item_ids: list[str]` (required after normalization)
- `gis: arcgis.gis.GIS | None` (optional authenticated session)
- `output_excel: Path | None` (optional workbook destination)
- Validation:
- `target_item_ids` must be non-empty after normalization from input/config.
- If `gis` is omitted, configuration must provide valid connection settings.

## Entity: ImpactRelationshipRow
- Description: Detailed relationship edge showing one affected item tied to a target deletion candidate.
- Fields:
- `target_item_id: str`
- `target_item_name: str`
- `affected_item_id: str`
- `affected_item_name: str`
- `relationship_status: str` (`resolved` or `error`)
- `reason: str | None` (present for unresolved/error rows)
- Validation:
- Uniqueness key: (`target_item_id`, `affected_item_id`)
- Error rows use explicit status and reason text.

## Entity: TargetDecisionSummary
- Description: Aggregated per-target deletion recommendation.
- Fields:
- `target_item_id: str`
- `target_item_name: str`
- `decision: str` in `{safe_to_delete, not_safe_to_delete, unknown_requires_review}`
- `affected_count: int`
- `unknown_count: int`
- `decision_reason: str`
- Decision rules:
- `not_safe_to_delete`: at least one resolved affected dependency exists.
- `unknown_requires_review`: no resolved blockers but unresolved/indeterminate evidence exists.
- `safe_to_delete`: no resolved blockers and no unresolved evidence.

## Entity: FailureRecord
- Description: In-table failure capture for item-resolution/traversal issues.
- Fields:
- `target_item_id: str`
- `target_item_name: str`
- `affected_item_id: str` (uses error sentinel value)
- `affected_item_name: str` (human-readable failure message)
- `relationship_status: str` (`error`)
- Validation:
- Failure capture must not abort unrelated target processing.

## Relationships
- One `ImpactAnalysisRequest` produces many `ImpactRelationshipRow` entries.
- One `ImpactAnalysisRequest` produces one `TargetDecisionSummary` per target item.
- `FailureRecord` is represented as a specialized `ImpactRelationshipRow` with `relationship_status=error`.
