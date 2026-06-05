---
title: Python API
---

# Python API

This package is built around two core analysis workflows in
`arcgis_dependency._main`:

- `interrogate_item_dependencies(...)`: Given one or more item IDs, returns
	recursive dependency relationships (or writes an Excel workbook).
- `interrogate_parent_dependency_impact(...)`: Given one or more target item
	IDs, returns delete-impact analysis with detailed rows and per-target
	tri-state decisions (or writes an Excel workbook).

## Core Analysis Workflows

::: arcgis_dependency
		options:
			members:
				- interrogate_item_dependencies
				- interrogate_parent_dependency_impact
			show_root_heading: true
			show_source: false

## Supporting Configuration

::: arcgis_dependency.config
		options:
			show_root_heading: true
			show_source: false

## Supporting Utilities

::: arcgis_dependency.utils
		options:
			show_root_heading: true
			show_source: false
