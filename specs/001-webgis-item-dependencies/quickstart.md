# Quickstart: ArcGIS Web GIS Item Dependency Interrogation

## Prerequisites
- Active project environment with ArcGIS Python API available.
- Authenticated GIS profile and required config keys populated.
- Feature branch `001-execute-feature-hook` checked out.

## Setup
1. Activate environment.
2. Confirm dependencies import in Python.
3. Ensure config includes fallback `request_item_ids` for config-driven scenario testing.

## Validation Scenario 1: Single Item, Default Return
1. Call `interrogate_item_dependencies(item_ids="<valid_id>")`.
2. Verify returned object is a DataFrame.
3. Verify required columns from contract:
- `parent_item_id`
- `parent_item_name`
- `dependent_item_id`
- `dependent_item_name`

Expected outcome:
- DataFrame returned with required schema.
- Recursive dependencies included.

## Validation Scenario 2: Multiple Items, Mixed Validity
1. Call function with list containing valid and invalid/inaccessible IDs.
2. Verify successful dependency rows are present for valid IDs.
3. Verify failure rows are present for failed IDs.
4. Verify failure row markers:
- `dependent_item_id == "__ERROR__"`
- `dependent_item_name` contains readable failure reason.

Expected outcome:
- Best-effort completion without dropping valid rows.
- In-table failure encoding matches contract.

## Validation Scenario 3: Recursive Cycle Safety and Dedupe
1. Use test fixture or mocked graph containing cyclical relationships.
2. Execute dependency interrogation.
3. Verify processing terminates.
4. Verify dedupe by `(parent_item_id, dependent_item_id)`.

Expected outcome:
- No infinite traversal.
- No duplicate parent-dependent rows.

## Validation Scenario 4: Config-Driven IDs
1. Omit `item_ids` parameter.
2. Ensure config `request_item_ids` is populated.
3. Execute function.

Expected outcome:
- IDs are resolved from config and processed successfully.

## Validation Scenario 5: Workbook Export Mode
1. Call function with `output_excel=<writable_path>`.
2. Verify returned object is a `Path`.
3. Verify workbook exists and is readable.

Expected outcome:
- Workbook written with dependency rows.
- Return value is output workbook path.

## Suggested Test Commands
```powershell
pytest -q testing/test_dependency_interrogation.py
```

If broader regression confidence is needed:
```powershell
pytest -q
```