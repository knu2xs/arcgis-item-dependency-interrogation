"""Feature tests for ArcGIS Web GIS item dependency interrogation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
import zipfile
from xml.etree import ElementTree as ET

import pandas as pd

from arcgis_dependency import interrogate_item_dependencies
import arcgis_dependency._main as dependency_main


@dataclass
class FakeItem:
    """Minimal ArcGIS Item stand-in for dependency interrogation tests."""

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
    """Minimal content manager for resolving items by ID."""

    def __init__(self, items: dict[str, FakeItem | None]) -> None:
        self._items = items

    def get(self, item_id: str) -> FakeItem | None:
        return self._items.get(item_id)


class FakeGIS:
    """Minimal GIS stand-in with a content manager."""

    def __init__(self, items: dict[str, FakeItem | None]) -> None:
        self.content = FakeGISContent(items)


def _patch_gis(monkeypatch, items: dict[str, FakeItem | None]) -> None:
    monkeypatch.setattr(dependency_main, "_build_gis", lambda: FakeGIS(items))


def test_interrogate_item_dependencies_returns_recursive_dataframe(monkeypatch) -> None:
    """Single-item interrogation returns recursive dependency rows and schema."""
    grandchild = FakeItem("grandchild", "Grandchild Item")
    child = FakeItem("child", "Child Item", dependencies=[grandchild])
    root = FakeItem("root", "Root Item", dependencies=[child])
    _patch_gis(monkeypatch, {"root": root, "child": child, "grandchild": grandchild})
    monkeypatch.setattr(dependency_main.config, "get", lambda key, default=None: default)

    result = interrogate_item_dependencies(item_ids="root")

    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == [
        "parent_item_id",
        "parent_item_name",
        "dependent_item_id",
        "dependent_item_name",
    ]
    assert set(result["dependent_item_id"].tolist()) == {"child", "grandchild"}


def test_interrogate_item_dependencies_uses_config_request_item_ids(monkeypatch) -> None:
    """When no item IDs are supplied, config request_item_ids should be used."""
    child = FakeItem("child", "Child Item")
    root = FakeItem("root", "Root Item", dependencies=[child])
    _patch_gis(monkeypatch, {"root": root, "child": child})
    monkeypatch.setattr(
        dependency_main,
        "config",
        SimpleNamespace(
            get=lambda key, default=None: ["root"]
            if key == "request_item_ids"
            else default
        ),
    )

    result = interrogate_item_dependencies()

    assert isinstance(result, pd.DataFrame)
    assert result["parent_item_id"].tolist() == ["root"]
    assert result["dependent_item_id"].tolist() == ["child"]


def test_interrogate_item_dependencies_best_effort_and_dedupes(monkeypatch) -> None:
    """Mixed-validity batches should preserve valid rows, emit failure rows, and dedupe."""
    shared = FakeItem("shared", "Shared Item")
    root = FakeItem("root", "Root Item", dependencies=[shared, shared])
    _patch_gis(monkeypatch, {"root": root, "shared": shared, "missing": None})
    monkeypatch.setattr(dependency_main.config, "get", lambda key, default=None: default)

    result = interrogate_item_dependencies(item_ids=["root", "missing"])

    assert isinstance(result, pd.DataFrame)
    assert result[result["dependent_item_id"] == "shared"].shape[0] == 1
    failure_rows = result[result["dependent_item_id"] == "__ERROR__"]
    assert failure_rows.shape[0] == 1
    assert failure_rows.iloc[0]["parent_item_id"] == "missing"
    assert failure_rows.iloc[0]["parent_item_name"] == "__ERROR__"
    assert "missing" in str(failure_rows.iloc[0]["dependent_item_name"]).lower()


def test_interrogate_item_dependencies_handles_twenty_five_item_batch(monkeypatch) -> None:
    """A 25-item batch should complete without losing valid rows."""
    items: dict[str, FakeItem | None] = {}
    roots: list[str] = []
    for index in range(25):
        child = FakeItem(f"child-{index}", f"Child {index}")
        root = FakeItem(f"root-{index}", f"Root {index}", dependencies=[child])
        items[root.id] = root
        items[child.id] = child
        roots.append(root.id)
    _patch_gis(monkeypatch, items)
    monkeypatch.setattr(dependency_main.config, "get", lambda key, default=None: default)

    result = interrogate_item_dependencies(item_ids=roots)

    assert isinstance(result, pd.DataFrame)
    assert result.shape[0] == 25
    assert set(result["dependent_item_id"].tolist()) == {f"child-{index}" for index in range(25)}


def test_interrogate_item_dependencies_writes_workbook_and_returns_path(monkeypatch, temp_dir) -> None:
    """Workbook export should write a file and return the output path."""
    child = FakeItem("child", "Child Item")
    root = FakeItem("root", "Root Item", dependencies=[child])
    _patch_gis(monkeypatch, {"root": root, "child": child})
    monkeypatch.setattr(dependency_main, "config", SimpleNamespace(get=lambda key, default=None: default))

    output_path = temp_dir / "dependencies.xlsx"
    result = interrogate_item_dependencies(item_ids="root", output_excel=output_path)

    assert isinstance(result, Path)
    assert result == output_path
    assert result.exists()
    assert zipfile.is_zipfile(result)
    with zipfile.ZipFile(result) as archive:
        sheet_xml = archive.read("xl/worksheets/sheet1.xml")
    sheet = ET.fromstring(sheet_xml)
    namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    values = [node.text for node in sheet.findall(".//main:t", namespace)]
    assert "child" in values