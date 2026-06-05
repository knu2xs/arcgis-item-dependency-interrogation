"""Batch parent-impact tests."""

from dataclasses import dataclass, field

from arcgis_dependency import interrogate_parent_dependency_impact


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
    """Minimal GIS content manager with deterministic retrieval and search."""

    def __init__(self, items: dict[str, FakeItem | None]) -> None:
        self._items = items

    def get(self, item_id: str) -> FakeItem | None:
        return self._items.get(item_id)

    def search(self, query: str = "*", max_items: int = 10000) -> list[FakeItem]:
        return [item for item in self._items.values() if item is not None]


class FakeGIS:
    """Minimal GIS wrapper for tests."""

    def __init__(self, items: dict[str, FakeItem | None]) -> None:
        self.content = FakeGISContent(items)


def test_parent_impact_batch_mixed_validity_and_deduplication() -> None:
    """Batch runs should preserve valid rows, represent failures, and dedupe relationships."""
    target_a = FakeItem("target-a", "Target A")
    target_b = FakeItem("target-b", "Target B")
    app = FakeItem("app", "App", dependencies=["target-a", "target-a", "target-b"])
    gis = FakeGIS(
        {
            "target-a": target_a,
            "target-b": target_b,
            "app": app,
        }
    )

    result = interrogate_parent_dependency_impact(
        target_item_ids=["target-a", "missing-target", "target-b"],
        gis=gis,
    )

    impact_rows = result["impact_rows"]
    decisions = result["target_decisions"]

    resolved = impact_rows[impact_rows["relationship_status"] == "resolved"]
    assert resolved[(resolved["target_item_id"] == "target-a") & (resolved["affected_item_id"] == "app")].shape[0] == 1
    assert resolved[(resolved["target_item_id"] == "target-b") & (resolved["affected_item_id"] == "app")].shape[0] == 1

    missing_row = decisions[decisions["target_item_id"] == "missing-target"].iloc[0]
    assert missing_row["decision"] == "unknown_requires_review"


def test_parent_impact_discovers_dependents_beyond_target_list() -> None:
    """All-accessible scan should find affected items outside the provided target list."""
    target = FakeItem("target", "Target")
    unrelated = FakeItem("other", "Other")
    dashboard = FakeItem("dashboard", "Dashboard", dependencies=["target"])
    gis = FakeGIS({"target": target, "other": unrelated, "dashboard": dashboard})

    result = interrogate_parent_dependency_impact(target_item_ids=["target"], gis=gis)

    resolved = result["impact_rows"]
    resolved = resolved[resolved["relationship_status"] == "resolved"]
    assert "dashboard" in set(resolved["affected_item_id"].tolist())


def test_parent_impact_logs_partial_failures_and_continues(monkeypatch) -> None:
    """Traversal failures should produce error rows while valid impacts continue."""
    target = FakeItem("target", "Target")
    stable = FakeItem("stable", "Stable", dependencies=["target"])
    broken = FakeItem("broken", "Broken", dependencies=[{"id": "missing-leaf"}])
    gis = FakeGIS({"target": target, "stable": stable, "broken": broken})

    result = interrogate_parent_dependency_impact(target_item_ids=["target"], gis=gis)

    impact_rows = result["impact_rows"]
    assert impact_rows[impact_rows["relationship_status"] == "resolved"].shape[0] >= 1
    assert impact_rows[impact_rows["relationship_status"] == "error"].shape[0] >= 1

    decisions = result["target_decisions"]
    assert decisions.iloc[0]["decision"] in {"not_safe_to_delete", "unknown_requires_review"}


def test_parent_impact_handles_cycle_without_infinite_recursion() -> None:
    """Cycle-safe traversal should terminate and still detect affected items."""
    target = FakeItem("target", "Target")
    node_a = FakeItem("node-a", "Node A")
    node_b = FakeItem("node-b", "Node B")

    node_a.dependencies = ["node-b"]
    node_b.dependencies = ["node-a", "target"]

    gis = FakeGIS({"target": target, "node-a": node_a, "node-b": node_b})
    result = interrogate_parent_dependency_impact(target_item_ids=["target"], gis=gis)

    resolved = result["impact_rows"]
    resolved = resolved[resolved["relationship_status"] == "resolved"]
    assert "node-a" in set(resolved["affected_item_id"].tolist())
