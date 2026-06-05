"""Package-level smoke tests for :mod:`arcgis_dependency`."""

from arcgis_dependency import (
    interrogate_item_dependencies,
    interrogate_parent_dependency_impact,
)


def test_package_exports_dependency_interrogation_function() -> None:
    """Package root should export the dependency interrogation function."""
    assert callable(interrogate_item_dependencies)


def test_package_exports_parent_impact_interrogation_function() -> None:
    """Package root should export the parent-impact interrogation function."""
    assert callable(interrogate_parent_dependency_impact)