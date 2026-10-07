"""Portable tests for the bounded platform-contract synchronization core."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError

from . import sync
from .generate import regenerate
from .spec import config_for, dumps, select


PLATFORMS = ("sofascore", "flashscore", "fotmob", "youtube")


def _operation(platform: str, suffix: str, *, description: str = "A fixture operation") -> dict:
    return {
        "operationId": f"{platform}-{suffix}",
        "summary": description,
        "tags": [platform.title()],
        "parameters": [{"name": "q", "in": "query", "type": "string", "required": True}],
        "responses": {"200": {"description": "OK", "schema": {"$ref": "#/definitions/Envelope"}}},
    }


def _raw_spec(platform: str, *, extra: bool = False) -> dict:
    operation_ids = {
        "sofascore": [("search", "search")],
        "flashscore": [("search", "search"), ("sports", "sports"), ("scores", "scores")],
        "fotmob": [("leagues", "leagues"), ("search", "search")],
        "youtube": [("search", "search"), ("video", "video"), ("transcript", "transcript")],
    }[platform]
    paths = {}
    for suffix, path_suffix in operation_ids:
        operation = _operation(platform, suffix)
        if suffix == "search":
            operation["parameters"].append({"name": "X-API-Key", "in": "header", "type": "string"})
        paths[f"/{platform}/{path_suffix}"] = {"get": operation}
    search = paths[f"/{platform}/{operation_ids[0][1]}"]["get"]
    if extra:
        extra_op = _operation(platform, "new-feed", description="A useful new feed")
        extra_op["parameters"] = [
            {"name": "id", "in": "path", "type": "string", "required": True},
            {"name": "X-API-Key", "in": "header", "type": "string"},
        ]
        paths[f"/{platform}/feeds/{{id}}"] = {"get": extra_op}
    return {
        "swagger": "2.0",
        "info": {"title": "Crawlora API", "version": "2026.10", "description": "fixture"},
        "host": "api.crawlora.net",
        "basePath": "/api/v1",
        "schemes": ["https"],
        "paths": paths,
        "definitions": {
            "Envelope": {"type": "object", "properties": {"data": {"$ref": "#/definitions/Item"}}},
            "Item": {"type": "object", "properties": {"name": {"type": "string"}}},
            "Unused": {"type": "string"},
        },
    }


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(value), encoding="utf-8")


def _make_root(root: Path, platform: str, raw: dict | None = None) -> dict:
    raw = raw or _raw_spec(platform)
    selected = sync.normalize_public_spec(raw, platform)
    config = config_for(platform, version="1.2.3", revision=sync._contract_hash(selected))
    config["source_contract_sha256"] = hashlib.sha256(dumps(raw).encode()).hexdigest()
    (root / "openapi").mkdir(parents=True)
    _write_json(root / "platform.json", config)
    _write_json(root / "openapi/public.json", selected)
    regenerate(root)
    return config


def _snapshot(root: Path) -> dict[str, bytes]:
    return {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}


class ContractSyncTests(unittest.TestCase):
    def test_raw_header_normalization_matches_selected_public_contract(self) -> None:
        for platform in PLATFORMS:
            with self.subTest(platform=platform):
                source = _raw_spec(platform)
                normalized = sync.normalize_public_spec(source, platform)
                prepared = copy.deepcopy(source)
                prepared["securityDefinitions"] = copy.deepcopy(sync._AUTH_DEFINITIONS)
                search = next(op["get"] for path, op in prepared["paths"].items() if op["get"]["operationId"] == f"{platform}-search")
                search["parameters"] = [p for p in search["parameters"] if p.get("in") != "header"]
                search["security"] = [{"ApiKeyAuth": []}]
                expected = select(prepared, platform)
                self.assertEqual(normalized, expected)
                self.assertEqual(set(normalized["definitions"]), {"Envelope", "Item"})

    def test_discovers_and_generates_new_operation_for_all_four_clients(self) -> None:
        for platform in PLATFORMS:
            with self.subTest(platform=platform), tempfile.TemporaryDirectory(prefix="platform-sync-") as temp:
                root = Path(temp)
                _make_root(root, platform)
                source = _raw_spec(platform, extra=True)
                dry_run_before = _snapshot(root)
                report = sync.synchronize(root, spec_path=self._source_file(root, source))
                self.assertEqual(report["added"], [f"{platform}-new-feed"])
                self.assertEqual(report["version"], "1.3.0")
                self.assertEqual(_snapshot(root), dry_run_before, "dry run must leave the repository untouched")

                report = sync.synchronize(root, spec_path=self._source_file(root, source), apply=True, date="2026-10-07")
                self.assertTrue(report["changed"])
                self.assertEqual(report["contract_revision"], sync._contract_hash(sync.normalize_public_spec(source, platform)))
                config = json.loads((root / "platform.json").read_text())
                self.assertEqual(config["version"], "1.3.0")
                self.assertEqual([release["version"] for release in config["releases"]], ["1.3.0", "1.2.3"])
                selected = json.loads((root / "openapi/public.json").read_text())
                operation = selected["paths"][f"/{platform}/feeds/{{id}}"]["get"]
                self.assertEqual(operation["security"], [{"ApiKeyAuth": []}])
                self.assertFalse(any(p.get("in") == "header" for p in operation.get("parameters", [])))

                class_name = config_for(platform)["class_name"]
                js = (root / "javascript/src/operations.js").read_text()
                js_types = (root / "javascript/src/index.d.ts").read_text()
                py_ops = (root / "python" / config["module_name"] / "operations.py").read_text()
                py_types = (root / "python" / config["module_name"] / "platform.pyi").read_text()
                docs = (root / "javascript/docs/javascript-operations.md").read_text()
                operation_count = sum(len(methods) for methods in selected["paths"].values())
                self.assertIn(f"operationCount = {operation_count};", js)
                self.assertIn(f"OPERATION_COUNT = {operation_count}", py_ops)
                self.assertIn("newFeed", js)
                self.assertIn("newFeed", js_types)
                self.assertIn("new_feed", py_ops)
                self.assertIn("new_feed", py_types)
                self.assertIn("newFeed", docs)
                self.assertIn(class_name, js_types)
                self.assertTrue((root / "javascript/package.json").exists())

    @staticmethod
    def _source_file(root: Path, value: dict) -> Path:
        path = root.parent / (root.name + "-source.json")
        _write_json(path, value)
        return path

    def test_cycles_are_retained_and_unrelated_changes_are_noop(self) -> None:
        with tempfile.TemporaryDirectory(prefix="platform-sync-") as temp:
            root = Path(temp) / "client"
            root.mkdir()
            raw = _raw_spec("sofascore")
            raw["definitions"]["Envelope"]["properties"]["parent"] = {"$ref": "#/definitions/Item"}
            raw["definitions"]["Item"]["properties"]["envelope"] = {"$ref": "#/definitions/Envelope"}
            config = _make_root(root, "sofascore", raw)
            self.assertEqual(set(json.loads((root / "openapi/public.json").read_text())["definitions"]), {"Envelope", "Item"})
            before = _snapshot(root)
            unrelated = copy.deepcopy(raw)
            unrelated["info"]["version"] = "2027.01"
            unrelated["paths"]["/other/endpoint"] = {"get": _operation("other", "endpoint")}
            report = sync.synchronize(root, spec_path=self._source_file(root, unrelated))
            self.assertFalse(report["changed"])
            self.assertEqual(report["contract_revision"], config["contract_revision"])
            self.assertEqual(_snapshot(root), before)
            self.assertEqual(json.loads((root / "platform.json").read_text())["source_contract_sha256"], config["source_contract_sha256"])

    def test_description_only_change_is_patch_and_applies_with_history(self) -> None:
        with tempfile.TemporaryDirectory(prefix="platform-sync-") as temp:
            root = Path(temp)
            _make_root(root, "sofascore")
            source = _raw_spec("sofascore")
            source["paths"]["/sofascore/search"]["get"]["description"] = "Updated documentation only"
            report = sync.synchronize(root, spec_path=self._source_file(root, source))
            self.assertEqual(report["version"], "1.2.4")
            self.assertEqual(report["modified"], ["sofascore-search"])
            sync.synchronize(root, spec_path=self._source_file(root, source), apply=True, date="2026-10-07")
            changelog = (root / "CHANGELOG.md").read_text()
            self.assertIn("## 1.2.4 — 2026-10-07", changelog)
            self.assertIn("## 1.2.3 — 2026-10-07", changelog)

    def test_schema_property_named_title_is_wire_data_and_keeps_info_version(self) -> None:
        with tempfile.TemporaryDirectory(prefix="platform-sync-") as temp:
            root = Path(temp)
            raw = _raw_spec("sofascore")
            raw["definitions"]["Item"]["properties"]["title"] = {"type": "string"}
            _make_root(root, "sofascore", raw)
            source = copy.deepcopy(raw)
            source["info"]["version"] = "2027.01"
            source["definitions"]["Item"]["properties"]["title"] = {"type": "integer"}
            report = sync.synchronize(root, spec_path=self._source_file(root, source))
            self.assertEqual(report["version"], "1.3.0")
            self.assertEqual(report["modified"], ["sofascore-search"])
            self.assertTrue(report["contract_revision"].startswith("sha256:"))
            sync.synchronize(root, spec_path=self._source_file(root, source), apply=True, date="2026-10-07")
            selected = json.loads((root / "openapi/public.json").read_text())
            config = json.loads((root / "platform.json").read_text())
            self.assertEqual(selected["info"]["version"], raw["info"]["version"])
            self.assertEqual(selected["definitions"]["Item"]["properties"]["title"]["type"], "integer")
            self.assertEqual(config["contract_revision"], "sha256:" + hashlib.sha256(dumps(selected).encode()).hexdigest())

    def test_transport_metadata_change_requires_runtime_review_before_mutation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="platform-sync-") as temp:
            root = Path(temp)
            _make_root(root, "sofascore")
            before = _snapshot(root)
            for field, value in (("host", "api-next.crawlora.net"), ("basePath", "/api/v2"), ("schemes", ["http"])):
                source = _raw_spec("sofascore", extra=True)
                source[field] = value
                with self.subTest(field=field), self.assertRaisesRegex(ValueError, "runtime transport review required"):
                    sync.synchronize(root, spec_path=self._source_file(root, source), apply=True)
                self.assertEqual(_snapshot(root), before)

    def test_replacement_failure_after_first_write_restores_tree_and_removes_temps(self) -> None:
        with tempfile.TemporaryDirectory(prefix="platform-sync-") as temp:
            root = Path(temp)
            _make_root(root, "sofascore")
            before = _snapshot(root)
            source = self._source_file(root, _raw_spec("sofascore", extra=True))
            original_replace = sync.os.replace
            replacements = 0

            def fail_second_replace(source_path, target_path):
                nonlocal replacements
                replacements += 1
                if replacements == 2:
                    raise OSError("injected replacement failure")
                return original_replace(source_path, target_path)

            with patch.object(sync.os, "replace", side_effect=fail_second_replace):
                with self.assertRaisesRegex(ValueError, "previous files restored"):
                    sync.synchronize(root, spec_path=source, apply=True)
            self.assertGreaterEqual(replacements, 2)
            self.assertEqual(_snapshot(root), before)
            self.assertFalse(any(".sync-" in path.name for path in root.rglob("*")))

    def test_failed_inputs_removals_and_generation_leave_files_untouched(self) -> None:
        with tempfile.TemporaryDirectory(prefix="platform-sync-") as temp:
            root = Path(temp) / "client"
            root.mkdir()
            _make_root(root, "sofascore")
            source_file = self._source_file(root, _raw_spec("sofascore", extra=True))
            before = _snapshot(root)
            broken = root.parent / "broken.json"
            broken.write_text("{")
            for candidate in (broken, self._source_file(root, {"swagger": "2.0", "paths": {}})):
                with self.subTest(candidate=candidate.name), self.assertRaises(ValueError):
                    sync.synchronize(root, spec_path=candidate, apply=True)
                self.assertEqual(_snapshot(root), before)

            removed = _raw_spec("sofascore")
            removed["paths"].pop("/sofascore/search")
            removed["paths"]["/sofascore/status"] = {"get": _operation("sofascore", "status")}
            with self.assertRaisesRegex(ValueError, "removed"):
                sync.synchronize(root, spec_path=self._source_file(root, removed), apply=True)
            self.assertEqual(_snapshot(root), before)

            with patch.object(sync, "regenerate", side_effect=RuntimeError("fixture generation failure")):
                with self.assertRaisesRegex(RuntimeError, "fixture generation"):
                    sync.synchronize(root, spec_path=self._source_file(root, _raw_spec("sofascore", extra=True)), apply=True)
            self.assertEqual(_snapshot(root), before)

    def test_dangling_refs_retrieval_and_invalid_semver_fail_without_writes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="platform-sync-") as temp:
            root = Path(temp)
            config = _make_root(root, "sofascore")
            before = _snapshot(root)
            invalid = _raw_spec("sofascore", extra=True)
            invalid["paths"]["/sofascore/search"]["get"]["responses"]["200"]["schema"] = {"$ref": "#/definitions/Missing"}
            with self.assertRaisesRegex(ValueError, "dangling"):
                sync.synchronize(root, spec_path=self._source_file(root, invalid), apply=True)
            invalid_auth = _raw_spec("sofascore", extra=True)
            invalid_auth["paths"]["/sofascore/search"]["get"]["security"] = [{"UnconfiguredAuth": []}]
            with self.assertRaisesRegex(ValueError, "security definition"):
                sync.synchronize(root, spec_path=self._source_file(root, invalid_auth), apply=True)
            with patch.object(sync, "urlopen", side_effect=URLError("offline")):
                with self.assertRaisesRegex(ValueError, "source request failed"):
                    sync.synchronize(root)
            invalid_config = copy.deepcopy(config)
            invalid_config["version"] = "1.2"
            _write_json(root / "platform.json", invalid_config)
            with self.assertRaisesRegex(ValueError, "semantic version"):
                sync.synchronize(root, spec_path=self._source_file(root, _raw_spec("sofascore", extra=True)), apply=True)
            _write_json(root / "platform.json", config)
            self.assertEqual(_snapshot(root), before)

    def test_private_routes_jwt_operations_and_alias_collisions_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="platform-sync-") as temp:
            root = Path(temp)
            _make_root(root, "sofascore")
            before = _snapshot(root)
            raw = _raw_spec("sofascore", extra=True)
            for section in ("admin", "internal", "private"):
                raw["paths"][f"/sofascore/{section}/probe"] = {
                    "get": _operation("sofascore", f"{section}-probe")
                }
            jwt = _operation("sofascore", "jwt-probe")
            jwt["parameters"].append({"name": "Authorization", "in": "header", "type": "string"})
            raw["paths"]["/sofascore/jwt-probe"] = {"get": jwt}
            selected = sync.normalize_public_spec(raw, "sofascore")
            ids = {operation["operationId"] for methods in selected["paths"].values() for operation in methods.values()}
            self.assertEqual(ids, {"sofascore-search", "sofascore-new-feed"})

            for suffix in ("request", "close", "constructor"):
                collision = copy.deepcopy(raw)
                collision["paths"][f"/sofascore/{suffix}"] = {"get": _operation("sofascore", suffix)}
                with self.subTest(alias=suffix), self.assertRaisesRegex(ValueError, "collisionalias"):
                    sync.synchronize(root, spec_path=self._source_file(root, collision), apply=True)
                self.assertEqual(_snapshot(root), before)

    def test_apply_is_deterministic_and_repeat_sync_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory(prefix="platform-sync-") as temp:
            root = Path(temp)
            _make_root(root, "youtube")
            source = self._source_file(root, _raw_spec("youtube", extra=True))
            first = sync.synchronize(root, spec_path=source, apply=True, date="2026-10-07")
            after_first = _snapshot(root)
            second = sync.synchronize(root, spec_path=source, apply=True, date="2026-10-07")
            self.assertTrue(first["changed"])
            self.assertFalse(second["changed"])
            self.assertEqual(first["contract_revision"], second["contract_revision"])
            self.assertEqual(after_first, _snapshot(root))


if __name__ == "__main__":
    unittest.main()
