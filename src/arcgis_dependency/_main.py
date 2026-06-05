"""Main module for :mod:`arcgis_dependency`.

This module exposes the public item dependency interrogation function used by
the package root export.
"""

from __future__ import annotations

from collections.abc import Iterable
import datetime as _dt
import html
import zipfile
from xml.sax.saxutils import escape
from pathlib import Path
from typing import Any

import pandas as pd
from arcgis.gis import GIS

from .config import config
from .utils import get_logger

logger = get_logger(__name__, level="DEBUG", add_stream_handler=False)

DEPENDENCY_COLUMNS: tuple[str, ...] = (
	"parent_item_id",
	"parent_item_name",
	"dependent_item_id",
	"dependent_item_name",
)
ERROR_SENTINEL = "__ERROR__"


def interrogate_item_dependencies(
	item_ids: str | list[str] | None = None,
	output_excel: str | Path | None = None,
) -> pd.DataFrame | Path:
	"""Interrogate ArcGIS item dependencies for one or more item IDs.

	Args:
		item_ids: Single item ID, list of item IDs, or ``None`` to resolve from
			configuration.
		output_excel: Optional workbook path. When provided, results are written
			to Excel and the written path is returned.

	Returns:
		pandas.DataFrame | Path: Dependency table by default, or the written
		workbook path when ``output_excel`` is provided.

	Raises:
		ValueError: If no usable item IDs or GIS connection settings are found.
		RuntimeError: If item interrogation fails unexpectedly.
	"""
	resolved_item_ids = _resolve_requested_item_ids(item_ids)
	if not resolved_item_ids:
		msg = (
			"No item IDs were provided and no config item_ids value was available."
		)
		logger.error(msg)
		raise ValueError(msg)

	gis = _build_gis()
	rows: list[dict[str, str]] = []
	seen_edges: set[tuple[str, str]] = set()
	visited_items: set[str] = set()

	for requested_item_id in resolved_item_ids:
		try:
			item = gis.content.get(requested_item_id)
		except Exception as exc:
			msg = f"Failed to load item '{requested_item_id}' from GIS: {exc}"
			logger.warning(msg)
			rows.append(
				{
					"parent_item_id": requested_item_id,
					"parent_item_name": ERROR_SENTINEL,
					"dependent_item_id": ERROR_SENTINEL,
					"dependent_item_name": msg,
				}
			)
			continue

		if item is None:
			msg = f"Item '{requested_item_id}' was not found or is inaccessible."
			logger.warning(msg)
			rows.append(
				{
					"parent_item_id": requested_item_id,
					"parent_item_name": ERROR_SENTINEL,
					"dependent_item_id": ERROR_SENTINEL,
					"dependent_item_name": msg,
				}
			)
			continue

		visited_items.add(str(getattr(item, "id", requested_item_id)))
		_collect_dependency_rows(
			gis=gis,
			item=item,
			rows=rows,
			seen_edges=seen_edges,
			visited_items=visited_items,
		)

	dataframe = pd.DataFrame(rows, columns=DEPENDENCY_COLUMNS)
	if dataframe.empty:
		dataframe = pd.DataFrame(columns=DEPENDENCY_COLUMNS)

	if output_excel is None:
		return dataframe

	output_path = Path(output_excel)
	output_path.parent.mkdir(parents=True, exist_ok=True)
	_write_workbook(output_path, dataframe)
	logger.info("Wrote dependency workbook to %s", output_path)
	return output_path


def _build_gis() -> GIS:
	"""Build a GIS connection from project configuration."""
	gis_profile = _resolve_config_value("esri.gis_profile") or _resolve_config_value(
		"gis_profile"
	)
	gis_url = _resolve_config_value("esri.gis_url") or _resolve_config_value(
		"gis_url"
	)
	gis_username = _resolve_config_value("esri.gis_username") or _resolve_config_value(
		"gis_username"
	)
	gis_password = _resolve_config_value("esri.gis_password") or _resolve_config_value(
		"gis_password"
	)

	if gis_profile:
		logger.debug("Connecting to GIS using profile '%s'", gis_profile)
		return GIS(profile=str(gis_profile))

	if gis_url and gis_username and gis_password:
		logger.debug("Connecting to GIS using explicit URL and credentials.")
		return GIS(
			url=str(gis_url),
			username=str(gis_username),
			password=str(gis_password),
		)

	msg = (
		"GIS connection settings are missing. Provide esri.gis_profile or a "
		"complete URL/username/password configuration."
	)
	logger.error(msg)
	raise ValueError(msg)


def _resolve_requested_item_ids(item_ids: str | list[str] | None) -> list[str]:
	"""Resolve item IDs from a direct argument or configuration fallback."""
	if item_ids is None:
		getter = getattr(config, "get", None)
		item_ids = getter("item_ids", None) if callable(getter) else None

	return _unique_non_empty_strings(item_ids)


def _resolve_config_value(path: str) -> Any:
	"""Resolve a dotted config path from the project configuration."""
	current: Any = config
	for part in path.split("."):
		if current is None:
			return None
		if isinstance(current, dict):
			current = current.get(part)
			continue
		if hasattr(current, part):
			current = getattr(current, part)
			continue
		getter = getattr(current, "get", None)
		if callable(getter):
			current = getter(part)
			continue
		return None
	return current


def _unique_non_empty_strings(value: Any) -> list[str]:
	"""Normalize strings or iterables of strings into a unique ordered list."""
	if value is None:
		return []

	if isinstance(value, str):
		candidates = [value]
	elif isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
		candidates = list(value)
	else:
		candidates = [value]

	results: list[str] = []
	seen: set[str] = set()
	for candidate in candidates:
		item_id = str(candidate).strip()
		if not item_id or item_id in seen:
			continue
		seen.add(item_id)
		results.append(item_id)
	return results


def _collect_dependency_rows(
	gis: GIS,
	item: Any,
	rows: list[dict[str, str]],
	seen_edges: set[tuple[str, str]],
	visited_items: set[str],
) -> None:
	"""Recursively collect dependency rows for an item."""
	parent_item_id = str(getattr(item, "id", "") or "").strip()
	parent_item_name = _resolve_item_name(item)

	try:
		dependency_entries = item.get_dependencies(
			deep=False,
			outside_org=True,
			out_format="item",
		)
	except TypeError:
		dependency_entries = item.get_dependencies(deep=False, outside_org=True)
	except Exception as exc:
		msg = f"Failed to interrogate dependencies for item '{parent_item_id}': {exc}"
		logger.warning(msg)
		rows.append(
			{
				"parent_item_id": parent_item_id or ERROR_SENTINEL,
				"parent_item_name": parent_item_name or ERROR_SENTINEL,
				"dependent_item_id": ERROR_SENTINEL,
				"dependent_item_name": msg,
			}
		)
		return

	for dependency_entry in _normalize_dependency_entries(dependency_entries):
		dependent_item_id, dependent_item_name, dependent_item = _extract_dependency_entry(
			dependency_entry,
		)
		if not dependent_item_id:
			msg = (
				f"Could not resolve a dependency item for parent '{parent_item_id or ERROR_SENTINEL}'."
			)
			logger.warning(msg)
			rows.append(
				{
					"parent_item_id": parent_item_id or ERROR_SENTINEL,
					"parent_item_name": parent_item_name or ERROR_SENTINEL,
					"dependent_item_id": ERROR_SENTINEL,
					"dependent_item_name": msg,
				}
			)
			continue

		edge_key = (parent_item_id, dependent_item_id)
		if edge_key not in seen_edges:
			rows.append(
				{
					"parent_item_id": parent_item_id,
					"parent_item_name": parent_item_name,
					"dependent_item_id": dependent_item_id,
					"dependent_item_name": dependent_item_name,
				}
			)
			seen_edges.add(edge_key)

		if dependent_item_id in visited_items:
			continue

		visited_items.add(dependent_item_id)
		if dependent_item is None:
			try:
				dependent_item = gis.content.get(dependent_item_id)
			except Exception as exc:
				logger.warning(
					"Failed to resolve dependent item '%s' for recursion: %s",
					dependent_item_id,
					exc,
				)
				continue

		if dependent_item is None:
			continue

		_collect_dependency_rows(
			gis=gis,
			item=dependent_item,
			rows=rows,
			seen_edges=seen_edges,
			visited_items=visited_items,
		)


def _normalize_dependency_entries(dependency_entries: Any) -> list[Any]:
	"""Normalize the raw dependency response into a list of entries."""
	if dependency_entries is None:
		return []

	if isinstance(dependency_entries, dict):
		for key in ("items", "dependencies", "results", "data"):
			if key in dependency_entries:
				dependency_entries = dependency_entries[key]
				break
		else:
			return [dependency_entries]

	if isinstance(dependency_entries, (str, bytes)):
		return [dependency_entries]

	try:
		return list(dependency_entries)
	except TypeError:
		return [dependency_entries]


def _extract_dependency_entry(entry: Any) -> tuple[str, str, Any]:
	"""Extract item ID, display name, and item object from a dependency entry."""
	if entry is None:
		return "", "", None

	if isinstance(entry, str):
		item_id = entry.strip()
		return item_id, item_id, None

	if isinstance(entry, dict):
		item_id = _first_present(entry, ("id", "item_id", "dependent_item_id", "value"))
		item_name = _first_present(
			entry,
			("title", "name", "item_name", "dependent_item_name", "displayName"),
		)
		nested_item = entry.get("item") or entry.get("dependent_item") or entry.get("value")
		if item_id is None and isinstance(nested_item, str):
			item_id = nested_item
		item_id = str(item_id).strip() if item_id is not None else ""
		item_name = str(item_name).strip() if item_name is not None else item_id
		return item_id, item_name, nested_item if hasattr(nested_item, "get_dependencies") else None

	item_id = getattr(entry, "id", None) or getattr(entry, "item_id", None)
	item_name = (
		getattr(entry, "title", None)
		or getattr(entry, "name", None)
		or getattr(entry, "item_name", None)
		or getattr(entry, "dependent_item_name", None)
	)
	item_id = str(item_id).strip() if item_id is not None else ""
	item_name = str(item_name).strip() if item_name is not None else item_id
	nested_item = entry if hasattr(entry, "get_dependencies") else None
	return item_id, item_name, nested_item


def _resolve_item_name(item: Any) -> str:
	"""Resolve a display name for an item-like object."""
	for attr in ("title", "name", "item_name"):
		value = getattr(item, attr, None)
		if value:
			return str(value)
	item_id = getattr(item, "id", None)
	return str(item_id) if item_id is not None else ERROR_SENTINEL


def _first_present(mapping: dict[str, Any], keys: tuple[str, ...]) -> Any:
	"""Return the first present non-empty mapping value from a key sequence."""
	for key in keys:
		value = mapping.get(key)
		if value not in (None, ""):
			return value
	return None


def _write_workbook(output_path: Path, dataframe: pd.DataFrame) -> None:
	"""Write a minimal XLSX workbook using the standard library only."""
	rows = [list(dataframe.columns)] + dataframe.fillna("").astype(str).values.tolist()
	with zipfile.ZipFile(output_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
		archive.writestr("[Content_Types].xml", _content_types_xml())
		archive.writestr("_rels/.rels", _rels_xml())
		archive.writestr("docProps/app.xml", _app_xml(dataframe.shape[1]))
		archive.writestr("docProps/core.xml", _core_xml())
		archive.writestr("xl/workbook.xml", _workbook_xml())
		archive.writestr("xl/_rels/workbook.xml.rels", _workbook_rels_xml())
		archive.writestr("xl/styles.xml", _styles_xml())
		archive.writestr("xl/worksheets/sheet1.xml", _sheet_xml(rows))


def _content_types_xml() -> str:
	"""Return the workbook content-types document."""
	return (
		'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
		'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
		'<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
		'<Default Extension="xml" ContentType="application/xml"/>'
		'<Override PartName="/xl/workbook.xml" '
		'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
		'<Override PartName="/xl/worksheets/sheet1.xml" '
		'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
		'<Override PartName="/xl/styles.xml" '
		'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
		'<Override PartName="/docProps/core.xml" '
		'ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
		'<Override PartName="/docProps/app.xml" '
		'ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
		"</Types>"
	)


def _rels_xml() -> str:
	"""Return the package relationships document."""
	return (
		'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
		'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
		'<Relationship Id="rId1" '
		'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
		'Target="xl/workbook.xml"/>'
		'<Relationship Id="rId2" '
		'Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" '
		'Target="docProps/core.xml"/>'
		'<Relationship Id="rId3" '
		'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" '
		'Target="docProps/app.xml"/>'
		"</Relationships>"
	)


def _app_xml(sheet_count: int) -> str:
	"""Return the extended properties document."""
	return (
		'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
		'<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
		'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
		f"<Application>arcgis-item-dependency-interrogation</Application><Sheets>{sheet_count}</Sheets>"
		"</Properties>"
	)


def _core_xml() -> str:
	"""Return the core properties document."""
	created = _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
	return (
		'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
		'<cp:coreProperties '
		'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
		'xmlns:dc="http://purl.org/dc/elements/1.1/" '
		'xmlns:dcterms="http://purl.org/dc/terms/" '
		'xmlns:dcmitype="http://purl.org/dc/dcmitype/" '
		'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
		"<dc:creator>arcgis_dependency</dc:creator>"
		"<cp:lastModifiedBy>arcgis_dependency</cp:lastModifiedBy>"
		f"<dcterms:created xsi:type=\"dcterms:W3CDTF\">{created}</dcterms:created>"
		f"<dcterms:modified xsi:type=\"dcterms:W3CDTF\">{created}</dcterms:modified>"
		"</cp:coreProperties>"
	)


def _workbook_xml() -> str:
	"""Return the workbook document."""
	return (
		'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
		'<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
		'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
		'<sheets><sheet name="Dependencies" sheetId="1" r:id="rId1"/></sheets>'
		"</workbook>"
	)


def _workbook_rels_xml() -> str:
	"""Return the workbook relationships document."""
	return (
		'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
		'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
		'<Relationship Id="rId1" '
		'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
		'Target="worksheets/sheet1.xml"/>'
		"</Relationships>"
	)


def _styles_xml() -> str:
	"""Return a minimal styles document."""
	return (
		'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
		'<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
		"<fonts count='1'><font><sz val='11'/><name val='Calibri'/></font></fonts>"
		"<fills count='1'><fill><patternFill patternType='none'/></fill></fills>"
		"<borders count='1'><border/></borders>"
		"<cellStyleXfs count='1'><xf numFmtId='0' fontId='0' fillId='0' borderId='0'/></cellStyleXfs>"
		"<cellXfs count='1'><xf numFmtId='0' fontId='0' fillId='0' borderId='0' xfId='0'/></cellXfs>"
		"</styleSheet>"
	)


def _sheet_xml(rows: list[list[str]]) -> str:
	"""Build the worksheet XML using inline string cells."""
	def cell_ref(row_index: int, column_index: int) -> str:
		column_name = ""
		index = column_index + 1
		while index:
			index, remainder = divmod(index - 1, 26)
			column_name = chr(65 + remainder) + column_name
		return f"{column_name}{row_index}"

	def xml_cell(value: str, row_index: int, column_index: int) -> str:
		ref = cell_ref(row_index, column_index)
		return (
			f'<c r="{ref}" t="inlineStr"><is><t>{escape(value)}</t></is></c>'
		)

	row_xml = []
	for row_index, row in enumerate(rows, start=1):
		cells = "".join(xml_cell(value, row_index, col_index) for col_index, value in enumerate(row))
		row_xml.append(f'<row r="{row_index}">{cells}</row>')

	return (
		'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
		'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
		'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
		'<sheetData>'
		+ "".join(row_xml)
		+ "</sheetData></worksheet>"
	)
