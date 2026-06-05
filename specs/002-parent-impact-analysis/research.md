# Research: Parent Dependency Impact Analysis

## Decision 1: Full-Scope Discovery Strategy
- Decision: Discover impacted dependents by scanning all items accessible to the authenticated user context.
- Rationale: The feature is accuracy-first and must not miss dependents outside an initial candidate list.
- Alternatives considered:
- Restrict discovery to only explicitly supplied candidate IDs.
- Use pre-filtered subsets from config for faster scans.

## Decision 2: Recursive Impact Semantics
- Decision: Include full recursive/transitive dependent chains rather than only direct one-hop dependents.
- Rationale: Delete-risk analysis requires complete blast-radius visibility across dependency chains.
- Alternatives considered:
- Direct dependents only.
- Configurable depth with shallow default.

## Decision 3: Output Model
- Decision: Return both detailed impact rows and per-target tri-state summary decisions.
- Rationale: Detailed rows preserve traceability; summary decisions provide actionable outcomes for non-experts.
- Alternatives considered:
- Detailed rows only.
- Summary decisions only.

## Decision 4: Decision State Handling
- Decision: Use tri-state decision outcomes: `safe_to_delete`, `not_safe_to_delete`, `unknown_requires_review`.
- Rationale: Incomplete dependency evidence must be visible and must not be silently downgraded to binary safe/unsafe.
- Alternatives considered:
- Conservative binary (anything unresolved => not safe).
- Optimistic binary (ignore unresolved dependencies).

## Decision 5: Column Naming
- Decision: Use explicit columns `target_item_id`, `target_item_name`, `affected_item_id`, `affected_item_name`.
- Rationale: Beginner-intermediate users need explicit labels that describe deletion target vs affected item without inference.
- Alternatives considered:
- Reuse legacy `parent_*` / `dependent_*` naming.
- Mixed naming with compatibility aliases only.

## Decision 6: Export Behavior
- Decision: Keep the same output options as existing workflow: in-memory default output and optional workbook export path.
- Rationale: Maintains familiarity and consistent calling style while supporting richer parent-impact content.
- Alternatives considered:
- New export-specific function.
- Force workbook output for all runs.
