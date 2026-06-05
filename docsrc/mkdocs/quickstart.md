---
title: Quickstart
---

# Quickstart

This page explains what is included in this project and the three primary workflows it supports.

## What Is Included

| Component | Location | Purpose |
|---|---|---|
| Python package | `src/arcgis_dependency/` | Core dependency and impact analysis logic |
| Public API docs | `docsrc/mkdocs/api.md` | Reference for callable workflows |
| Example notebook | `docsrc/mkdocs/storymap_dependency_investigation.ipynb` | End-to-end StoryMap investigation example |
| Tests | `testing/` | Regression coverage for dependency and parent-impact behavior |
| Project docs site config | `docsrc/mkdocs.yml` | MkDocs navigation and plugin setup |

## Before You Start

1. Create or activate the project environment.
2. Authenticate to ArcGIS Online/Enterprise with either:
   - `GIS("home")` or `GIS()` in notebook contexts where supported, or
   - `GIS(profile="your_profile")` for explicit profile auth.
3. Import the package workflows:

```python
from arcgis_dependency import (
    interrogate_item_dependencies,
    interrogate_parent_dependency_impact,
)
```

## Workflow 1: Item Dependency Interrogation

Use this when you need to know what one or more items depend on.

```python
dependency_df = interrogate_item_dependencies(
    item_ids="2f9e9b3fec654af890d4b8c680167f8e",
    gis=gis,
)
```

Expected output:

- A pandas DataFrame containing parent/dependent relationship rows
- Best-effort error rows for unresolved items
- Optional Excel output when `output_excel` is provided

## Workflow 2: Parent Dependency Impact Analysis

Use this when you need to know what would be affected if target items were deleted.

```python
impact_result = interrogate_parent_dependency_impact(
    target_item_ids=["2f9e9b3fec654af890d4b8c680167f8e"],
    gis=gis,
)

impact_rows = impact_result["impact_rows"]
target_decisions = impact_result["target_decisions"]
```

Expected output:

- `impact_rows`: detailed affected-item relationship rows
- `target_decisions`: per-target tri-state decisions:
  - `safe_to_delete`
  - `not_safe_to_delete`
  - `unknown_requires_review`
- Optional two-sheet Excel output (`impact_rows`, `target_decisions`) when `output_excel` is provided

## Workflow 3: Notebook-First Investigation and Reporting

Use this when you want a guided, explainable analysis session that can be shared.

1. Open the example notebook:
   - `docsrc/mkdocs/storymap_dependency_investigation.ipynb`
2. Run cells top-to-bottom.
3. Review DataFrame outputs.
4. Export workbook results for stakeholders when needed.

This workflow is ideal for:

- StoryMap dependency reviews
- Change planning meetings
- Capturing reproducible investigation steps

## Which Workflow Should I Use?

| If your goal is... | Use this workflow | Why |
|---|---|---|
| Understand what an item references | Workflow 1: Item Dependency Interrogation | Returns direct and recursive dependency relationships for the item(s). |
| Assess delete risk before removing content | Workflow 2: Parent Dependency Impact Analysis | Returns affected-item rows plus per-target tri-state safety decisions. |
| Walk through analysis with explainable, shareable steps | Workflow 3: Notebook-First Investigation and Reporting | Gives a reproducible narrative workflow with optional export output. |
| Deliver a stakeholder-ready spreadsheet | Workflow 1 or 2 with `output_excel` | Writes workbook output for review and archival. |
| Investigate a StoryMap quickly | Workflow 3 first, then Workflow 2 if delete-risk is needed | The notebook provides guided setup and can branch into impact analysis. |

## Next Steps

- API details: see `API` in the docs navigation
- Example walkthrough: see `Example Dependency Investigation` in the docs navigation
- Tests: run `make test` from the project root
