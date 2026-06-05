# Feature Specification: ArcGIS Web GIS Item Dependency Interrogation

**Feature Branch**: `001-execute-feature-hook`

**Created**: 2026-06-05

**Status**: Draft

**Input**: User description: "Using the ArcGIS Python API's functionality, I want a function in arcgis_dependency (lives in _main and exposed through __init__) to interrogate an ArcGIS Web GIS (ArcGIS Online and ArcGIS Enterprise) site to determine dependencies for a provided item (using item id) or multiple items. The items are provided as a parameter (single string item id or list of item ids) or read from the config (`request_item_ids`). The default returned result should be a pandas data frame with parent_item_id, parent_item_name,dependent_item_id and dependent_item_name columns. Another optional parameter should enable a path to an output excel workbook, which, if populated will be written, and the return object will the a pathlib.Path to the excel workbook."

## Clarifications

### Session 2026-06-05

- Q: How should mixed-validity batch input behave when some item IDs are invalid or inaccessible? -> A: Best-effort processing; continue valid item IDs and record per-item failures.
- Q: What dependency traversal depth should interrogation return? -> A: Full recursive dependency graph.
- Q: How should per-item failures be returned? -> A: Include failure rows in the same dependency table using placeholder dependency values.
- Q: How should duplicate dependency rows be handled? -> A: Deduplicate by `(parent_item_id, dependent_item_id)`.
- Q: What placeholder format should be used for failure rows in the dependency table? -> A: `dependent_item_id="__ERROR__"` and `dependent_item_name="<failure reason>"`.
- Q: What should the parent fields contain for failure rows? -> A: Use the requested item's identifier and best-available item name (or `__ERROR__` if unavailable).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Query Dependencies for One Item (Priority: P1)

A developer provides one item identifier and receives that item's dependency relationships from a target Web GIS site.

**Why this priority**: Single-item interrogation is the smallest useful unit and provides immediate value for troubleshooting and dependency discovery.

**Independent Test**: Can be fully tested by providing one valid item identifier and confirming dependency rows are returned with required columns.

**Acceptance Scenarios**:

1. **Given** a valid item identifier and valid Web GIS access, **When** the function is called, **Then** it returns a tabular result containing dependency relationships for that item.
2. **Given** a valid item identifier with no dependencies, **When** the function is called, **Then** it returns a tabular result with the required columns and zero dependency rows.
3. **Given** an item with multi-level dependencies, **When** the function is called, **Then** returned relationships include recursively discovered downstream dependencies.

---

### User Story 2 - Query Dependencies for Multiple Items (Priority: P2)

A developer provides multiple item identifiers directly or through configuration and receives combined dependency relationships across all requested items.

**Why this priority**: Batch interrogation reduces manual effort and enables broader impact analysis for releases and migration planning.

**Independent Test**: Can be fully tested by supplying a list of valid item identifiers and then by relying on configured identifiers, confirming both paths return combined results.

**Acceptance Scenarios**:

1. **Given** a list of valid item identifiers, **When** the function is called, **Then** dependencies for all requested items are returned in one tabular result.
2. **Given** no explicit item parameter but configured item identifiers are present, **When** the function is called, **Then** dependencies are returned for configured identifiers.
3. **Given** requested items whose dependencies overlap at deeper levels, **When** the function is called, **Then** recursive dependencies are included without losing parent-to-dependent relationship rows.

---

### User Story 3 - Export Dependencies to Workbook (Priority: P3)

A developer optionally requests workbook export and receives a created spreadsheet file containing dependency results.

**Why this priority**: Export supports handoff and reporting workflows, but dependency retrieval itself remains the primary value.

**Independent Test**: Can be tested by requesting output file creation and verifying the file path returned points to a readable workbook with dependency rows.

**Acceptance Scenarios**:

1. **Given** valid dependency results and a writable workbook output path, **When** export is requested, **Then** a workbook is written and the function returns the written file path.
2. **Given** export is not requested, **When** the function is called, **Then** it returns the default tabular result instead of a file path.

### Edge Cases

- What happens when both the function parameter and configured identifiers are empty?
- How does the system handle duplicate item identifiers in the provided list or config?
- What happens when one identifier is invalid but others are valid in a batch request?
- How does the system behave when the target site is reachable but the current user cannot access one or more requested items?
- What happens when workbook export is requested to a non-writable location?
- For mixed-validity batches, system continues valid identifiers and records per-item failure details for invalid or inaccessible identifiers.
- How does the system prevent infinite loops when recursive traversal encounters cyclical dependency relationships?
- For per-item failures, system emits rows in the main dependency table and uses placeholder values for dependency fields.
- Duplicate rows are removed using the pair `(parent_item_id, dependent_item_id)` as the uniqueness key.
- Failure rows use `dependent_item_id="__ERROR__"` and place the reason text in `dependent_item_name`.
- Failure rows preserve the requested item in the parent fields, using the resolved item name when available and `__ERROR__` when it is not.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept item identifiers from a direct function parameter supporting either one identifier or multiple identifiers.
- **FR-002**: System MUST use configured item identifiers when explicit item identifiers are not provided.
- **FR-003**: System MUST support interrogation against ArcGIS Online and ArcGIS Enterprise Web GIS sites.
- **FR-004**: System MUST retrieve dependency relationships for each resolved requested item identifier using recursive traversal across dependency levels.
- **FR-005**: Default response MUST be a tabular result with columns `parent_item_id`, `parent_item_name`, `dependent_item_id`, and `dependent_item_name`.
- **FR-006**: System MUST deduplicate results by the pair `(parent_item_id, dependent_item_id)`.
- **FR-007**: When optional workbook output is requested, system MUST write dependency results to a workbook file.
- **FR-008**: When workbook output is requested and written successfully, function MUST return the written workbook file path.
- **FR-009**: When workbook output is not requested, function MUST return the default tabular result.
- **FR-010**: System MUST provide actionable failure feedback when no item identifiers are supplied from either parameter or configuration.
- **FR-011**: System MUST process mixed-validity batch input in best-effort mode without losing valid-item dependency results.
- **FR-012**: System MUST record per-item failure details for invalid or inaccessible identifiers encountered during mixed-validity batch runs.
- **FR-013**: System MUST safely handle cyclical dependency graphs during recursive traversal without infinite processing.
- **FR-014**: System MUST represent per-item interrogation failures as rows in the same dependency table using `dependent_item_id="__ERROR__"`.
- **FR-015**: System MUST store per-item failure reason text in `dependent_item_name` for failure rows.
- **FR-016**: System MUST preserve the requested item identifier in `parent_item_id` for failure rows and use the resolved item name when available.

### Constitution Alignment *(mandatory)*

- **CA-001**: Configuration usage MUST rely on existing project configuration patterns and MUST NOT introduce hardcoded credentials or site URLs.
- **CA-002**: Any spatial reference assumptions in dependency-derived geometry handling (if present) MUST be explicit and configuration-driven.
- **CA-003**: Dependency interrogation failures and partial-result conditions MUST be logged with actionable context.
- **CA-004**: Implementation MUST include tests for single-item, multi-item, and optional export behaviors as independently testable increments.
- **CA-005**: Any non-trivial query logic added during implementation MUST follow SQL externalization and parameterization rules when applicable.

### Key Entities *(include if feature involves data)*

- **Requested Item**: An input identifier representing a Web GIS item selected for dependency interrogation; includes source (parameter or configuration).
- **Dependency Relationship**: A discovered linkage between a parent item and a dependent item, represented by parent and dependent identifiers and names.
- **Interrogation Result Set**: The full collection of dependency relationships returned for one or more requested items.
- **Workbook Export Artifact**: A generated spreadsheet file containing the dependency relationship result set.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of successful default interrogations return all required dependency columns.
- **SC-002**: Users can complete a single-item dependency interrogation and inspect results in under 2 minutes.
- **SC-003**: Batch interrogation over at least 25 item identifiers completes without data loss for valid identifiers.
- **SC-004**: 100% of successful export requests produce a readable workbook and return its path.
- **SC-005**: At least 95% of invalid-input runs provide error feedback that clearly states what input is missing or unusable.

## Assumptions

- Callers are already authenticated to the target Web GIS site through existing project configuration and profile setup.
- Configuration key `request_item_ids` is available for workflows that omit explicit item parameters.
- Workbook export uses a standard spreadsheet format accepted by business users.
- Dependency interrogation scope is limited to relationships discoverable through the ArcGIS Python API for the authenticated user.
- Initial feature scope focuses on dependency extraction and optional export, not on visualization or graph analytics.
