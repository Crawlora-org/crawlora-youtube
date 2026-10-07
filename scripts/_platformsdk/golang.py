"""Emit a focused Go module for one selected platform contract."""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Any


def _load_generator(assets: Path):
    assets = Path(assets).resolve()
    if str(assets) not in sys.path:
        sys.path.insert(0, str(assets))
    spec = importlib.util.spec_from_file_location("platformclients_go_core", assets / "_sdkgen" / "core.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Go generator from {assets}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.core = module
    module.POLICY = module.NamingPolicy(
        case_fn=lambda parts: "".join(part[:1].upper() + part[1:] for part in parts) or "Call",
        dedup_sep="",
        type_base_fn=lambda group, method: group + method,
        tag_group_overrides={
            "1stDibs": "FirstDibs", "7NOW": "SevenNow", "7NEWS Australia": "SevenNewsAustralia",
            "9to5Mac": "NineToFiveMac", "9to5Google": "NineToFiveGoogle", "AppStore": "AppStore",
            "CoinGecko": "CoinGecko", "GooglePlay": "GooglePlay", "ProductHunt": "ProductHunt",
            "SimilarWeb": "SimilarWeb", "SpotifyPodcasts": "SpotifyPodcasts", "TikTok": "TikTok",
            "YouTube": "YouTube",
        },
    )
    return module


def _replace(template: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def _go_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _go_value(value: Any) -> str:
    if isinstance(value, str):
        return _go_string(value)
    if isinstance(value, list):
        return "[]string{" + ", ".join(_go_value(item) for item in value) + "}"
    return json.dumps(value)


def _go_string_slice(values: list[str]) -> str:
    if not values:
        return "nil"
    return "[]string{" + ", ".join(_go_string(value) for value in values) + "}"


def _sample_params(params: list[dict[str, Any]], *, stress_path: bool = False) -> str:
    values = []
    for param in params:
        if not param.get("required"):
            continue
        kind = param.get("in")
        if kind == "path":
            value: Any = "folder/item" if stress_path else "sample-id"
        elif param.get("enum"):
            value = param["enum"][0]
        elif param.get("type") == "integer":
            value = 1
        elif param.get("type") == "number":
            value = 1.0
        elif param.get("type") == "boolean":
            value = True
        else:
            value = "sample"
        values.append(f"{_go_string(str(param['name']))}: {_go_value(value)}")
    return "Params{" + ", ".join(values) + "}"


def _param_literal(param: dict[str, Any]) -> str:
    fields = [f"Name: {_go_string(str(param['name']))}"]
    for key, field in (("in", "In"), ("type", "Type"), ("collectionFormat", "CollectionFormat")):
        if param.get(key):
            fields.append(f"{field}: {_go_string(str(param[key]))}")
    if param.get("required"):
        fields.append("Required: true")
    values = param.get("enum") or param.get("items", {}).get("enum") or []
    if values:
        fields.append("Enum: " + _go_string_slice([str(value) for value in values]))
    return "parameterDefinition{" + ", ".join(fields) + "}"


def _operation_literal(operation: dict[str, Any]) -> str:
    path_params = operation.get("pathParams", [])
    query_params = operation.get("queryParams", [])
    literals = [
        f"Method: {_go_string(str(operation.get('method', 'GET')).upper())}",
        f"Path: {_go_string(str(operation['path']))}",
        f"PathParams: {_go_string_slice(path_params)}",
        "QueryParams: []parameterDefinition{" + ", ".join(_param_literal(param) for param in query_params) + "}" if query_params else "QueryParams: nil",
        f"Produces: {_go_string_slice([str(value) for value in operation.get('produces', [])])}",
        f"Security: {_go_string_slice([str(value) for value in operation.get('security', [])])}",
    ]
    return "operationDefinition{" + ", ".join(literals) + "}"


def _module_name(config: dict[str, Any]) -> str:
    platform = str(config["platform"])
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", platform):
        raise ValueError(f"invalid platform slug for Go module: {platform!r}")
    return f"github.com/Crawlora-org/crawlora-{platform}"


def emit(root: Path, config: dict, spec: dict, assets: Path) -> None:
    """Write a standalone focused Go module into the platform repository root."""
    root = Path(root)
    templates = Path(__file__).resolve().parent / "templates" / "golang"
    module = _load_generator(assets)
    model = module.core.build_model(spec, module.POLICY)
    if not model.meta:
        raise ValueError("the sliced specification contains no operations")

    platform = str(config["platform"])
    package_name = {"sofascore": "sofascore"}.get(platform, platform.replace("-", ""))
    if not re.fullmatch(r"[a-z][a-z0-9]*", package_name):
        raise ValueError(f"invalid Go package name for platform: {package_name!r}")
    module_path = _module_name(config)
    version = str(config.get("golang_version", config.get("version", "0.1.4")))
    values = {
        "platform": platform,
        "package_name": package_name,
        "display_name": str(config.get("display_name", platform.title())),
        "module_path": module_path,
        "version": version,
        "repository": str(config.get("repository", f"https://github.com/Crawlora-org/crawlora-{platform}")),
        "operation_count": str(model.operation_count),
        "user_agent": f"crawlora-{platform}-go/{version}",
        "version_json": _go_string(version),
        "user_agent_json": _go_string(f"crawlora-{platform}-go/{version}"),
        "sample_operation": next(iter(model.meta)),
        "sample_params": _sample_params(model.meta[next(iter(model.meta))]["params"]),
    }

    operations = []
    methods = []
    reserved = {"Call", "Close", "OperationIDs", "OperationCount", "NewClient"}
    for operation_id, definition in model.operations.items():
        if definition["method"] != "GET":
            raise ValueError(f"Go platform clients currently support GET only: {operation_id}")
        operations.append(f"\t{_go_string(operation_id)}: {_operation_literal(definition)},")
        method = next((name for group in model.groups.values() for name, op_id in group.items() if op_id == operation_id), None)
        if method and method not in reserved:
            reserved.add(method)
            methods.append(
                f"// {method} calls the {operation_id} operation.\n"
                f"func (c *Client) {method}(ctx context.Context, params Params) (any, error) {{\n"
                f"\treturn c.Call(ctx, {_go_string(operation_id)}, params)\n"
                "}"
            )

    values["operation_entries"] = "\n".join(operations)
    values["method_declarations"] = "\n\n".join(methods)
    test_operation_id = next(
        (operation_id for operation_id in model.meta if operation_id.endswith("-search")),
        next(iter(model.meta)),
    )
    if not any(param.get("in") == "path" for param in model.meta[test_operation_id]["params"]) or not any(
        param.get("in") == "query" for param in model.meta[test_operation_id]["params"]
    ):
        test_operation_id = next(
            (operation_id for operation_id, meta in model.meta.items()
             if any(param.get("in") == "path" for param in meta["params"])
             and any(param.get("in") == "query" for param in meta["params"])),
            test_operation_id,
        )
    test_meta = model.meta[test_operation_id]
    test_params = []
    invalid_enum_params = []
    path_values = {}
    query_name = ""
    query_value = ""
    query_check_name = ""
    query_check_value = ""
    query_array = False
    invalid_enum_name = ""
    for param in test_meta["params"]:
        location = param.get("in")
        if location not in {"path", "query"}:
            continue
        if location == "path":
            value: Any = "folder/item"
            path_values[param["name"]] = value
        elif param.get("enum"):
            value = param["enum"][0]
        elif param.get("type") == "array":
            value = ["one", "two"]
            if not query_array:
                query_name, query_value, query_array = param["name"], "one", True
        elif param.get("type") == "integer":
            value = 1
        elif param.get("type") == "number":
            value = 1.0
        elif param.get("type") == "boolean":
            value = True
        else:
            value = "space & value"
        if location == "query" and not query_check_name and isinstance(value, str):
            query_check_name, query_check_value = param["name"], value
        if location == "query" and not query_name:
            query_name, query_value = param["name"], str(value if not isinstance(value, list) else value[0])
        test_params.append(f"{_go_string(str(param['name']))}: {_go_value(value)}")
        invalid_value = "__invalid_enum__" if location == "query" and param.get("enum") else value
        invalid_enum_params.append(f"{_go_string(str(param['name']))}: {_go_value(invalid_value)}")
        if location == "query" and param.get("enum") and not invalid_enum_name:
            invalid_enum_name = _go_string(str(param["name"]))
    expected_path = test_meta["path"]
    for name, value in path_values.items():
        expected_path = expected_path.replace("{" + name + "}", urllib.parse.quote(value, safe=""))
    values["request_operation"] = _go_string(test_operation_id)
    values["request_params"] = "Params{" + ", ".join(test_params) + "}"
    values["invalid_enum_operation"] = _go_string(test_operation_id)
    values["invalid_enum_params"] = "Params{" + ", ".join(invalid_enum_params) + "}"
    values["invalid_enum_name"] = invalid_enum_name or '""'
    values["fixture_path"] = expected_path.lstrip("/")
    values["query_name"] = _go_string(query_name)
    values["query_value"] = _go_string(query_value)
    values["query_array"] = "true" if query_array else "false"
    values["query_check_name"] = _go_string(query_check_name)
    values["query_check_encoded"] = _go_string(
        urllib.parse.quote(query_check_name, safe="") + "=" + urllib.parse.quote_plus(query_check_value, safe="")
        if query_check_name else ""
    )
    values["text_operation"] = _go_string(test_operation_id)
    values["text_params"] = values["request_params"][:-1] + ', "responseType": "text"}'
    values["search_operation"] = _go_string(test_operation_id)
    for source, target in (("go.mod.tmpl", "go.mod"), ("client.go.tmpl", "client.go"), ("operations.go.tmpl", "operations.go"), ("README.md.tmpl", "README.md"), ("client_test.go.tmpl", "client_test.go")):
        (root / target).write_text(_replace((templates / source).read_text(), values), encoding="utf-8")
    gofmt = shutil.which("gofmt")
    if gofmt is None:
        raise RuntimeError("gofmt is required to emit formatted Go source files")
    subprocess.run(
        [gofmt, "-w", str(root / "client.go"), str(root / "operations.go"), str(root / "client_test.go")],
        check=True,
        capture_output=True,
        text=True,
    )
