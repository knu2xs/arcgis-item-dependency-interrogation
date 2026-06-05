# Tasks: ArcGIS Web GIS Item Dependency Interrogation

**Input**: Design documents from `/specs/001-webgis-item-dependencies/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included because the feature specification requires independently testable slices for single-item, multi-item, and workbook export behavior.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 [P] Add an `item_ids` default entry to `config/config.yml` so config-driven dependency interrogation has a documented fallback source
- [X] T002 [P] Replace the placeholder package export surface in `src/arcgis_dependency/__init__.py` so the dependency interrogation function is exposed from the package root
- [X] T003 [P] Replace the placeholder entrypoint scaffolding in `src/arcgis_dependency/_main.py` with the public `interrogate_item_dependencies` function signature and module docstring
- [X] T004 [P] Replace the smoke-test stub in `testing/test_arcgis_dependency.py` with package import assertions for `arcgis_dependency`
- [X] T005 [P] Create a focused feature test module scaffold in `testing/test_dependency_interrogation.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Implement item ID normalization, config fallback resolution, and no-input validation in `src/arcgis_dependency/_main.py`
- [X] T007 Implement recursive dependency traversal with cycle protection and deduplication by `(parent_item_id, dependent_item_id)` in `src/arcgis_dependency/_main.py`
- [X] T008 Implement best-effort mixed-validity handling and in-band failure row encoding using `dependent_item_id="__ERROR__"` and failure text in `dependent_item_name` in `src/arcgis_dependency/_main.py`
- [X] T009 Implement workbook export branching and `Path` return handling in `src/arcgis_dependency/_main.py`
- [X] T010 Add logging for traversal progress, item-level failures, and export outcomes in `src/arcgis_dependency/_main.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Query Dependencies for One Item (Priority: P1) 🎯 MVP

**Goal**: A developer can pass one item ID and get the recursive dependency rows back as a DataFrame with the required columns.

**Independent Test**: Can be verified by calling the function with a single valid item ID and checking the returned DataFrame schema and recursive dependency rows.

### Tests for User Story 1

- [X] T011 [US1] Add a single-item DataFrame schema test in `testing/test_dependency_interrogation.py`
- [X] T012 [US1] Add a recursive traversal test for one valid item ID in `testing/test_dependency_interrogation.py`

### Implementation for User Story 1

- [X] T013 [US1] Wire the explicit one-item call path through `src/arcgis_dependency/_main.py` so it returns recursive dependency rows for a single item

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Query Dependencies for Multiple Items (Priority: P2)

**Goal**: A developer can pass multiple item IDs or rely on config `item_ids` and get combined best-effort results with valid rows preserved.

**Independent Test**: Can be verified by calling the function with a list of IDs and by omitting the parameter when config `item_ids` is populated, then confirming dedupe and failure rows behave as specified.

### Tests for User Story 2

- [X] T014 [US2] Add a config-driven item ID resolution test in `testing/test_dependency_interrogation.py`
- [X] T015 [US2] Add a mixed-validity best-effort and dedupe test in `testing/test_dependency_interrogation.py`

- [X] T016 [US2] Add a 25-item batch regression test in `testing/test_dependency_interrogation.py` to verify SC-003 coverage without loss of valid rows

### Implementation for User Story 2

- [X] T017 [US2] Extend the batching logic in `src/arcgis_dependency/_main.py` to process lists, config fallback, valid-row preservation, and in-table failure rows

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Export Dependencies to Workbook (Priority: P3)

**Goal**: A developer can optionally write dependency results to an Excel workbook and receive the output path.

**Independent Test**: Can be verified by calling the function with a writable workbook path, confirming a workbook is created, and verifying the return type is `Path`.

### Tests for User Story 3

- [X] T018 [US3] Add a workbook export return-type test in `testing/test_dependency_interrogation.py`
- [X] T019 [US3] Add a workbook content test for exported dependency rows in `testing/test_dependency_interrogation.py`

### Implementation for User Story 3

- [X] T020 [US3] Implement the workbook writing branch and `Path` return value in `src/arcgis_dependency/_main.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T021 [P] Update usage examples and feature notes in `README.md` and `specs/001-webgis-item-dependencies/quickstart.md`
- [ ] T022 [P] Clean up docstrings and smoke-test assertions in `src/arcgis_dependency/_main.py` and `testing/test_arcgis_dependency.py`
- [X] T023 [P] Run the focused regression suite and resolve any failures in `testing/test_dependency_interrogation.py`
- [ ] T024 [P] Verify the 25-item batch threshold in `testing/test_dependency_interrogation.py` and record any performance observations

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests MUST be written and should fail before implementation where practical
- Shared traversal, normalization, and dedupe logic should be completed before the story-specific wiring
- Workbook export should be implemented after the tabular dependency result path is stable
- Story complete before moving to next priority

### Parallel Opportunities

- Setup tasks T001 through T005 can run in parallel because they touch different files
- After Foundation is complete, different user stories can proceed in parallel by different developers
- T011 and T012 can be worked in parallel with each other if test boundaries are separated cleanly
- T014, T015, and T016 can be worked in parallel with each other if test boundaries are separated cleanly
- T018 and T019 can be worked in parallel with each other if test boundaries are separated cleanly

---

## Parallel Example: User Story 1

```bash
# Launch the two tests for User Story 1 together:
Task: "Add a single-item DataFrame schema test in testing/test_dependency_interrogation.py"
Task: "Add a recursive traversal test for one valid item ID in testing/test_dependency_interrogation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Demo the single-item dependency interrogation behavior

### Incremental Delivery

1. Complete Setup + Foundational → core engine ready
2. Add User Story 1 → test independently → demo single-item interrogation
3. Add User Story 2 → test independently → demo batch/config-driven interrogation
4. Add User Story 3 → test independently → demo workbook export
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing where practical
- Commit after each logical group of tasks if you want smaller checkpoints
- Stop at the MVP checkpoint if you only need the core single-item behavior
