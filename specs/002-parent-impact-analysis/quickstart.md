# Quickstart: Parent Dependency Impact Analysis

## Prerequisites
- Project environment is active and includes ArcGIS Python API dependencies.
- Authenticated GIS access is available by profile/config or supplied `GIS` object.
- Feature branch `002-webgis-item-dependencies` is checked out.

## Setup
1. Activate the project environment.
2. Confirm feature imports from `arcgis_dependency`.
3. Ensure config fallback key `request_item_ids` is set when omitting direct inputs.

## Validation Scenario 1: Single Target (Detailed + Summary)
1. Call `interrogate_parent_dependency_impact(target_item_ids="<valid_target>")`.
2. Verify return object is a dictionary with keys `impact_rows` and `target_decisions`.
3. Verify `impact_rows` includes explicit target/affected columns.
4. Verify `target_decisions` includes tri-state decision fields.

Expected outcome:
- Full recursive affected items are returned for the target.
- One summary decision row is present for the target.

## Validation Scenario 2: Mixed-Validity Batch
1. Call with a list containing valid and invalid/inaccessible target IDs.
2. Verify valid targets still produce impact rows.
3. Verify failure rows are present in `impact_rows` for unresolved targets.
4. Verify unresolved evidence yields `unknown_requires_review` in `target_decisions`.

Expected outcome:
- Best-effort behavior preserves valid results.
- Failures are visible without aborting the batch.

## Validation Scenario 3: Full-Scope Completeness
1. Use a fixture where affected items exist outside an initial small candidate subset.
2. Execute parent-impact interrogation.
3. Verify returned impacted rows include out-of-subset affected items.

Expected outcome:
- Full-scope discovery returns complete affected-item coverage.

## Validation Scenario 4: Recursive/Transitive Coverage
1. Use a fixture graph with dependency depth > 1.
2. Execute parent-impact interrogation.
3. Verify transitive affected items at all reachable depths are returned.

Expected outcome:
- Recursion terminates safely and returns transitive impacts.

## Validation Scenario 5: No-Dependents Target
1. Use a fixture target item with no inbound dependents.
2. Execute parent-impact interrogation for that target.
3. Verify no resolved rows are returned for that target.
4. Verify the target decision is `safe_to_delete` when there is no unresolved evidence.

Expected outcome:
- Targets without dependents are represented by decision summary rows without false impacted rows.

## Validation Scenario 6: Workbook Export
1. Call with `output_excel=<writable_path>`.
2. Verify returned object is a `Path`.
3. Verify workbook exists and contains sheets `impact_rows` and `target_decisions`.

Expected outcome:
- Workbook export succeeds and preserves both detailed and summary outputs.

## Suggested Test Commands
```powershell
pytest -q testing/test_parent_impact_single.py testing/test_parent_impact_batch.py testing/test_parent_impact_export.py
```

For broader confidence:
```powershell
pytest -q
```
