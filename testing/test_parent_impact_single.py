"""Single-target parent-impact tests."""

from dataclasses import dataclass, field
from types import SimpleNamespace

import pandas as pd

from arcgis_dependency import interrogate_parent_dependency_impact
import arcgis_dependency._main as dependency_main


@dataclass
class FakeItem:
    """Minimal item stand-in for dependency traversal tests."""

    item_id: str
    title: str
    dependencies: list[object] = field(default_factory=list)

    @property
    def id(self) -> str:
        return self.item_id

    def get_dependencies(
        self,
        deep: bool = False,
        outside_org: bool = False,
        out_format: str = "item",
    ) -> list[object]:
        return list(self.dependencies)


class FakeGISContent:
    """Minimal GIS content manager with deterministic item retrieval."""

    def __init__(self, items: dict[str, FakeItem | None]) -> None:
        self._items = items

    def get(self, item_id: str) -> FakeItem | None:
        return self._items.get(item_id)


class FakeGIS:
    """Minimal GIS wrapper for tests."""

    def __init__(self, items: dict[str, FakeItem | None]) -> None:
        self.content = FakeGISContent(items)


def test_parent_impact_single_target_returns_detailed_and_summary() -> None:
    """Single target should return resolved rows and one decision summary row."""
    target = FakeItem("target", "Target")
    viewer = FakeItem("viewer", "Viewer", dependencies=["target"])
    gis = FakeGIS({"target": target, "viewer": viewer})

    result = interrogate_parent_dependency_impact(target_item_ids="target", gis=gis)

    assert isinstance(result, dict)
    assert set(result.keys()) == {"impact_rows", "target_decisions"}

    impact_rows = result["impact_rows"]
    decisions = result["target_decisions"]

    assert isinstance(impact_rows, pd.DataFrame)
    assert isinstance(decisions, pd.DataFrame)

    assert "target_item_id" in impact_rows.columns
    assert "affected_item_id" in impact_rows.columns
    assert "relationship_status" in impact_rows.columns

    resolved = impact_rows[impact_rows["relationship_status"] == "resolved"]
    assert resolved.shape[0] == 1
    assert resolved.iloc[0]["target_item_id"] == "target"
    assert resolved.iloc[0]["affected_item_id"] == "viewer"

    assert decisions.shape[0] == 1
    assert decisions.iloc[0]["decision"] == "not_safe_to_delete"


def test_parent_impact_single_target_unknown_when_target_missing() -> None:
    """Missing targets should produce unknown_requires_review with error detail rows."""
    gis = FakeGIS({"viewer": FakeItem("viewer", "Viewer")})

    result = interrogate_parent_dependency_impact(target_item_ids="missing", gis=gis)

    impact_rows = result["impact_rows"]
    decisions = result["target_decisions"]

    error_rows = impact_rows[impact_rows["relationship_status"] == "error"]
    assert error_rows.shape[0] >= 1
    assert decisions.iloc[0]["decision"] == "unknown_requires_review"
    assert decisions.iloc[0]["unknown_count"] >= 1


def test_parent_impact_uses_caller_supplied_gis(monkeypatch) -> None:
    """A supplied GIS instance should bypass config-based GIS construction."""
    target = FakeItem("target", "Target")
    consumer = FakeItem("consumer", "Consumer", dependencies=["target"])
    provided_gis = FakeGIS({"target": target, "consumer": consumer})

    monkeypatch.setattr(
        dependency_main,
        "_build_gis",
        lambda: (_ for _ in ()).throw(AssertionError("_build_gis should not be called")),
    )
    monkeypatch.setattr(dependency_main, "config", SimpleNamespace(get=lambda key, default=None: default))

    result = interrogate_parent_dependency_impact(target_item_ids="target", gis=provided_gis)
    assert result["target_decisions"].iloc[0]["decision"] == "not_safe_to_delete"
