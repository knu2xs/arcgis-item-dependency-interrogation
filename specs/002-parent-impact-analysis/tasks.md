# Tasks: Parent Dependency Impact Analysis

**Input**: Design documents from `/specs/002-parent-impact-analysis/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are included because the specification requires independently testable slices for single-item, multi-item, and export workflows.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish test modules and implementation scaffolding for the new parent-impact workflow.

- [X] T001 Create parent-impact single-target test module scaffold in testing/test_parent_impact_single.py
- [X] T002 [P] Create parent-impact batch test module scaffold in testing/test_parent_impact_batch.py
- [X] T003 [P] Create parent-impact export test module scaffold in testing/test_parent_impact_export.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement shared core helpers that all user stories depend on.

**CRITICAL**: No user story implementation starts before this phase is complete.

- [X] T004 Implement target ID normalization with config fallback request_item_ids in src/arcgis_dependency/_main.py
- [X] T005 Implement all-accessible-items discovery helper for full-scope dependent search in src/arcgis_dependency/_main.py
- [X] T006 Implement cycle-safe recursive traversal helper for transitive affected items in src/arcgis_dependency/_main.py
- [X] T007 Implement relationship deduplication keyed by target_item_id and affected_item_id in src/arcgis_dependency/_main.py
- [X] T008 Implement tri-state decision aggregation helper for safe_to_delete, not_safe_to_delete, and unknown_requires_review in src/arcgis_dependency/_main.py
- [X] T009 Implement failure-row construction helper with explicit reason text and error status in src/arcgis_dependency/_main.py
- [X] T010 Implement two-sheet workbook writer support for impact_rows and target_decisions in src/arcgis_dependency/_main.py
- [X] T030 Implement structured logging for item resolution, traversal milestones, and export outcomes in src/arcgis_dependency/_main.py
- [X] T031 Implement build-message -> log -> raise handling for top-level parent-impact failures in src/arcgis_dependency/_main.py
- [X] T032 [P] Add logging visibility tests for failure paths in testing/test_parent_impact_batch.py

**Checkpoint**: Foundational graph traversal, dedupe, decisioning, and export primitives are complete.

---

## Phase 3: User Story 1 - Assess Deletion Impact for One Item (Priority: P1) 🎯 MVP

**Goal**: Return complete recursive impact rows and a per-target decision summary for one target item.

**Independent Test**: Call parent-impact analysis with one valid target and verify explicit target/affected columns plus a tri-state decision row.

### Tests for User Story 1

- [X] T011 [US1] Add single-target recursive impact acceptance tests in testing/test_parent_impact_single.py
- [X] T012 [US1] Add unresolved-dependency to unknown_requires_review decision tests in testing/test_parent_impact_single.py
- [X] T033 [US1] Add caller-supplied GIS passthrough tests in testing/test_parent_impact_single.py

### Implementation for User Story 1

- [X] T013 [US1] Implement interrogate_parent_dependency_impact single-target execution path in src/arcgis_dependency/_main.py
- [X] T014 [US1] Implement explicit impact row schema with target_* and affected_* columns in src/arcgis_dependency/_main.py
- [X] T015 [US1] Export interrogate_parent_dependency_impact from package API in src/arcgis_dependency/__init__.py
- [X] T034 [US1] Implement caller-supplied GIS passthrough path that skips config-built GIS in src/arcgis_dependency/_main.py

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Assess Deletion Impact for Multiple Items (Priority: P2)

**Goal**: Process mixed-validity target batches with complete coverage, dedupe, and per-target decisions.

**Independent Test**: Run a mixed-validity target list and verify valid rows are preserved, failures are captured in-table, and each target gets a decision summary.

### Tests for User Story 2

- [X] T016 [US2] Add mixed-validity batch processing tests in testing/test_parent_impact_batch.py
- [X] T017 [US2] Add duplicate-path deduplication tests in testing/test_parent_impact_batch.py
- [X] T018 [US2] Add full-scope discovery tests for dependents outside initial candidate subsets in testing/test_parent_impact_batch.py
- [X] T036 [US2] Add partial-failure progress and continuation tests for large-scan runs in testing/test_parent_impact_batch.py

### Implementation for User Story 2

- [X] T019 [US2] Implement multi-target execution loop with best-effort continuation in src/arcgis_dependency/_main.py
- [X] T020 [US2] Implement in-table failure-row emission for unresolved or inaccessible targets in src/arcgis_dependency/_main.py
- [X] T021 [US2] Implement per-target decision summary DataFrame assembly with rationale fields in src/arcgis_dependency/_main.py
- [X] T035 [US2] Implement large-scan progress milestone logging during full-scope discovery in src/arcgis_dependency/_main.py

**Checkpoint**: User Stories 1 and 2 both run independently with correct batch semantics.

---

## Phase 5: User Story 3 - Export Impact Results (Priority: P3)

**Goal**: Support workbook export for detailed and summary outputs while preserving in-memory defaults.

**Independent Test**: Provide a writable output path and verify workbook creation, expected sheet names, and path return value.

### Tests for User Story 3

- [X] T022 [US3] Add workbook export acceptance tests for dual-sheet outputs in testing/test_parent_impact_export.py

### Implementation for User Story 3

- [X] T023 [US3] Implement export branch that writes impact_rows and target_decisions sheets in src/arcgis_dependency/_main.py
- [X] T024 [US3] Implement Path return behavior for successful workbook export in src/arcgis_dependency/_main.py
- [X] T025 [US3] Update export usage and validation scenarios for parent-impact outputs in specs/002-parent-impact-analysis/quickstart.md

**Checkpoint**: All user stories are independently functional and export behavior is verified.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, regression protection, and documentation hardening across stories.

- [X] T026 [P] Add package-level regression import test for interrogate_parent_dependency_impact in testing/test_arcgis_dependency.py
- [X] T027 Update parent-impact contract details to match implemented behavior in specs/002-parent-impact-analysis/contracts/interrogate_parent_dependency_impact.md
- [X] T028 Add beginner-friendly Google-style docstring refinements for parent-impact helpers in src/arcgis_dependency/_main.py
- [X] T029 Validate quickstart scenarios against finalized tests and decisions in specs/002-parent-impact-analysis/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): No dependencies.
- Foundational (Phase 2): Depends on Setup and blocks all user stories.
- User Story phases (Phase 3-5): Depend on Foundational completion.
- Polish (Phase 6): Depends on selected user stories being complete.

### User Story Dependencies

- US1 (P1): Starts after Phase 2; no dependency on other stories.
- US2 (P2): Starts after Phase 2; functionally independent from US1 but builds on the same foundational helpers.
- US3 (P3): Starts after Phase 2 and depends on shared export primitives from Phase 2.

### Within Each User Story

- Tests are written before implementation and should fail before coding.
- Core implementation in src/arcgis_dependency/_main.py follows test creation.
- Public API export and story documentation updates complete each story.

---

## Parallel Opportunities

- T002 and T003 can run in parallel with T001 because they touch different test files.
- T026 can run in parallel with T027-T029 because it touches a different file.
- After Phase 2 completes, different team members can take US1, US2, and US3 in parallel if merge sequencing on src/arcgis_dependency/_main.py is coordinated.

---

## Parallel Example: User Story 1

- Task T011 in testing/test_parent_impact_single.py
- Task T015 in src/arcgis_dependency/__init__.py

## Parallel Example: User Story 2

- Task T016 in testing/test_parent_impact_batch.py
- Task T019 in src/arcgis_dependency/_main.py

## Parallel Example: User Story 3

- Task T022 in testing/test_parent_impact_export.py
- Task T025 in specs/002-parent-impact-analysis/quickstart.md

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 setup tasks.
2. Complete Phase 2 foundational tasks.
3. Complete Phase 3 (US1) and validate independent test criteria.
4. Demo or checkpoint after US1 passes.

### Incremental Delivery

1. Deliver US1 for single-target impact decisions.
2. Deliver US2 for batch and mixed-validity handling.
3. Deliver US3 for workbook export and final documentation alignment.

### Parallel Team Strategy

1. Shared completion of Phases 1 and 2.
2. Assign US1, US2, and US3 to separate developers after foundation is stable.
3. Use Phase 6 for integration hardening and final regression verification.

---

## Notes

- All tasks follow strict checklist format with task ID, optional parallel marker, optional story label, and explicit file path.
- Story labels are only used in user-story phases.
- Priority order is preserved as P1 -> P2 -> P3.
