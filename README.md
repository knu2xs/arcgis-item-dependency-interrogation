# ArcGIS Item Dependency Interrogation

<!--start-->
This project is designed to help ArcGIS Online and ArcGIS Enterprise users answer dependency-risk questions before making content changes.

In plain terms, it helps you determine:

- What this item depends on
- What would be affected if I delete this item
- Which targets are safe to delete, not safe to delete, or require review

## What This Project Does

The package provides Python-first workflows built on the ArcGIS Python API:

- Recursive dependency interrogation for one or many items
- Parent-impact analysis (reverse dependency risk) for deletion planning
- Best-effort handling for mixed-validity item lists
- Optional workbook exports for sharing and review

The code is intentionally explicit and beginner-friendly, so analysts can follow logic in notebooks and promote reusable pieces into package modules.

## Core Use Cases

- StoryMap dependency investigation prior to edits or migration
- Cleanup planning for stale content in ArcGIS Online organizations
- Change impact review for web maps, apps, and related assets
- Shareable dependency evidence as DataFrames or Excel workbooks

## Current Project Status

- Development stage: pre-alpha
- Python package name: `arcgis-item-dependency-interrogation`
- Runtime requirement: Python 3.9+

## Quick Start

1. Clone the repository.

2. Create the project environment.

```bash
make env
```

3. Start exploring in notebooks.

```bash
jupyter lab
```

Start with the example notebook:

- [notebooks/storymap_dependency_investigation.ipynb](notebooks/storymap_dependency_investigation.ipynb)

## Package Entry Points

Main public functions are exposed from:

- [src/arcgis_dependency/__init__.py](src/arcgis_dependency/__init__.py)

Implemented workflows include:

- `interrogate_item_dependencies(...)`
- `interrogate_parent_dependency_impact(...)`

Implementation details live in:

- [src/arcgis_dependency/_main.py](src/arcgis_dependency/_main.py)

## Typical Outputs

- In-memory pandas DataFrame results
- Optional `.xlsx` exports via `openpyxl`
- In-table error rows for unresolved items/dependencies
- Per-target tri-state decisions for parent-impact analysis

## Repository Structure

- Package code: [src/arcgis_dependency](src/arcgis_dependency)
- Tests: [testing](testing)
- Notebooks: [notebooks](notebooks)
- Documentation sources: [docsrc](docsrc)
- ArcGIS Pro assets: [arcgis](arcgis)

## Notes on Authentication

You can pass an existing `GIS` object to public functions, or rely on configured profile/credential settings in project config.

For notebooks, avoid hardcoding secrets. Prefer profile-based auth or local secret/config files.
<!--end-->
