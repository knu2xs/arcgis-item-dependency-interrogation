# Feature Specification: Parent Dependency Impact Analysis

**Feature Branch**: `002-webgis-item-dependencies`

**Created**: 2026-06-05

**Status**: Draft

**Input**: User description: "Create a function to interrogate parent dependencies to efficiently answer the first question with the same output options as the existing iterrogate_item_dependencies function. This package is still in pre-alpha, so refactor as much as is needed to efficiently accomplish this. Also, please keep in mind to be explicit over implicit since this code needs to be fairly easily understood by beginner-intermediate pythonistas"

## Clarifications

### Session 2026-06-05

- Q: What scope should parent-impact analysis run against when identifying dependents? → A: Always scan all accessible items in the organization/workspace.
- Q: How should output columns be named for parent-impact results? → A: Use explicit beginner-friendly names with `target_*` and `affected_*` fields.
- Q: Should delete-impact include direct dependents only or full transitive dependents? → A: Full recursive/transitive dependents; complete information and accuracy are prioritized over performance.
- Q: How should unresolved or inaccessible dependencies affect delete decisions? → A: Use explicit tri-state outcomes: `safe_to_delete`, `not_safe_to_delete`, and `unknown_requires_review`.
- Q: Should output include detailed rows, summary decisions, or both? → A: Include both detailed impact rows and per-target decision summary output.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Assess Deletion Impact for One Item (Priority: P1)

A user provides one candidate item for deletion and receives a dependency impact table showing which other items would be affected if that item is removed.

**Why this priority**: This is the core decision workflow that prevents accidental breakage and directly answers the highest-priority user need.

**Independent Test**: Can be fully tested by submitting one valid item identifier and verifying that affected dependent items are returned in the required output schema.

**Acceptance Scenarios**:

1. **Given** a valid candidate item, **When** the user runs parent dependency impact analysis, **Then** the system returns the full recursive set of affected dependent items linked to that candidate item using explicit target and affected column names.
2. **Given** an inaccessible or missing candidate item, **When** the user runs analysis, **Then** the system returns an in-table failure record without aborting unrelated processing.
3. **Given** unresolved or inaccessible dependencies, **When** decision output is produced, **Then** the target is marked `unknown_requires_review` rather than forced to safe/unsafe.

---

### User Story 2 - Assess Deletion Impact for Multiple Items (Priority: P2)

A user provides multiple candidate items and receives combined impact results so they can compare deletion risk across a batch.

**Why this priority**: Batch analysis improves triage speed and supports practical cleanup workflows.

**Independent Test**: Can be tested by providing a mixed-validity list and verifying successful rows are preserved while failures are represented in-table.

**Acceptance Scenarios**:

1. **Given** multiple candidates including at least one invalid item, **When** analysis runs, **Then** valid impact rows are returned and failures are captured per-item.
2. **Given** duplicate relationship paths in the dependency graph, **When** analysis runs, **Then** duplicate impact rows are not repeated.
3. **Given** batch analysis output, **When** results are returned, **Then** both detailed impact rows and per-target decision summaries are available.

---

### User Story 3 - Export Impact Results (Priority: P3)

A user optionally writes the impact table to a workbook and receives the written file path as output.

**Why this priority**: Export supports review, approval, and archival outside interactive sessions.

**Independent Test**: Can be tested by supplying a writable output path and verifying a workbook is created and the return value is that path.

**Acceptance Scenarios**:

1. **Given** a writable workbook path, **When** analysis is executed with export enabled, **Then** a workbook containing the impact table is written and the output path is returned.

---

### Edge Cases

- What happens when the target item has no dependents?
- How does the system handle cyclic dependency graphs where items indirectly reference each other?
- How are external or inaccessible dependent items represented when metadata cannot be fully resolved?
- What happens when both direct input and config-driven item inputs are omitted?
- How does the system communicate progress and partial failures when full-scope organization scans are large?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support parent dependency impact interrogation for a single candidate item.
- **FR-002**: System MUST support parent dependency impact interrogation for multiple candidate items in one request.
- **FR-003**: System MUST return a default tabular result using explicit columns: `target_item_id`, `target_item_name`, `affected_item_id`, and `affected_item_name`.
- **FR-004**: System MUST support optional workbook export and return the written file path when export is requested.
- **FR-005**: System MUST preserve best-effort processing for mixed-validity item sets and represent failures in-table.
- **FR-006**: System MUST prevent duplicate relationship rows for the same parent/dependent relationship pair in the returned results.
- **FR-007**: System MUST ensure graph traversal is cycle-safe and terminates for cyclic dependency structures.
- **FR-008**: System MUST allow callers to provide an existing authenticated GIS session object and use it when supplied.
- **FR-009**: System MUST keep parent-impact workflow explicit and beginner-intermediate friendly by:
	- using descriptive `target_*` and `affected_*` naming in all result schemas,
	- adding Google-style docstrings on new public functions and new helper functions,
	- keeping each new helper focused on one clear responsibility,
	- avoiding implicit behavior where explicit parameters or named helpers make intent clearer.
- **FR-010**: System MUST identify affected dependents by scanning all items accessible to the authenticated user context rather than limiting discovery to only explicitly supplied candidate IDs.
- **FR-011**: System MUST include full recursive/transitive dependents (not only direct one-hop dependents) when computing delete-impact results.
- **FR-012**: System MUST prioritize completeness and correctness of dependency impact results over performance optimizations that could omit valid dependent items, even when runtime or complexity increases.
- **FR-013**: System MUST expose a tri-state delete decision for each target item: `safe_to_delete`, `not_safe_to_delete`, or `unknown_requires_review`.
- **FR-014**: System MUST classify targets as `unknown_requires_review` when dependency resolution is incomplete due to inaccessible, missing, or indeterminate upstream data.
- **FR-015**: System MUST return both detailed impact relationship rows and a per-target decision summary in the same analysis workflow.

### Constitution Alignment *(mandatory)*

- **CA-001**: Configuration and secret handling MUST continue to use project configuration and local secrets workflows; no credentials are hardcoded.
- **CA-002**: CRS handling is not materially changed by this feature; no new spatial transformation behavior is introduced.
- **CA-003**: Workflow and failure-path logging MUST remain explicit for item resolution, traversal, and export outcomes.
- **CA-004**: Feature delivery MUST include independently testable slices for single-item impact, multi-item impact, and export behavior.
- **CA-005**: No new SQL behavior is introduced; existing SQL/data location safety constraints remain unchanged.

### Key Entities *(include if feature involves data)*

- **Impact Analysis Request**: User-provided candidate item identifiers, optional GIS session, and optional export path.
- **Impact Relationship Row**: One relationship row with explicit columns `target_item_id`, `target_item_name`, `affected_item_id`, and `affected_item_name`.
- **Failure Row**: In-table record capturing per-item resolution or traversal failure without stopping batch execution.
- **Target Decision**: Per-target outcome value in `{safe_to_delete, not_safe_to_delete, unknown_requires_review}` with supporting reasoning rows.
- **Target Decision Summary**: Aggregated per-target decision output that pairs each target item with one tri-state outcome and decision rationale.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can identify affected dependent items for a single delete candidate in one run with no manual graph tracing.
- **SC-002**: For a mixed-validity batch, 100% of valid candidates produce impact rows while failures are reported per-item without aborting the batch.
- **SC-003**: Duplicate impact rows for the same parent/dependent pair are reduced to zero in final outputs.
- **SC-004**: Users can produce a workbook export of impact results in the same run and receive a usable output path.
- **SC-005**: For a target item known to have dependents outside an initial candidate list, full-scope analysis still returns those dependents.
- **SC-006**: For dependency chains with depth greater than one, returned results include all transitive affected items in the chain.
- **SC-007**: Targets with unresolved dependency evidence are never labeled `safe_to_delete`; they are labeled `unknown_requires_review`.
- **SC-008**: For every analyzed target item, the result set includes both at least one decision summary record and, when applicable, detailed affected-item relationship rows.

## Assumptions

- Users provide item identifiers they are authorized to inspect in the target organization.
- Consumers of this feature can adopt explicit parent-impact column names that differ from legacy dependency output schema.
- This feature remains library-focused and does not introduce new UI surfaces.
- Refactoring within existing module boundaries is acceptable because the package is pre-alpha.
- Longer runtimes and higher algorithmic complexity are acceptable when required to preserve complete and accurate impact discovery.
