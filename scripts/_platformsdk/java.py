"""Emit focused Java/Maven clients for Crawlora's hosted platform APIs."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from .utm import crawlora_url


def _load_core(assets: Path):
    assets = Path(assets).resolve()
    if str(assets) not in sys.path:
        sys.path.insert(0, str(assets))
    from _sdkgen import core

    return core


def _quote(value: str) -> str:
    # JSON string literals are valid Java string literals for our operation ids
    # and parameter names; avoid ensure_ascii so generated files remain readable.
    return json.dumps(value, ensure_ascii=False)


def _java_type(param: dict[str, Any]) -> str:
    typ = param.get("type", "string")
    if typ == "integer":
        return "integer"
    if typ == "number":
        return "number"
    if typ == "boolean":
        return "boolean"
    if typ == "array":
        return "array"
    if typ == "object":
        return "object"
    return "string"


def _method_aliases(model: Any) -> list[tuple[str, str]]:
    methods = [(method, operation_id) for group in model.groups.values() for method, operation_id in group.items()]
    names = [name for name, _ in methods]
    if len(names) != len(set(names)):
        raise ValueError("Java platform method aliases collide")
    return methods


def _operation_source(operation_id: str, operation: dict[str, Any], source_params: list[dict[str, Any]]) -> str:
    params = []
    for param in source_params:
        location = param.get("in")
        if location not in {"path", "query"} or param.get("name", "").lower() == "x-api-key":
            continue
        enum = param.get("enum") or param.get("items", {}).get("enum") or []
        values = ", ".join(_quote(str(value)) for value in enum)
        params.append(
            "new Param(%s, %s, %s, %s, List.of(%s), %s)"
            % (
                _quote(param["name"]),
                _quote(location),
                "true" if param.get("required") else "false",
                _quote(_java_type(param)),
                values,
                _quote(param.get("collectionFormat", "csv")),
            )
        )
    included_params = [p for p in source_params if p.get("in") in {"path", "query"} and p.get("name", "").lower() != "x-api-key"]
    param_map = "Map.ofEntries(" + ", ".join(
        f"Map.entry({_quote(param['name'])}, {value})"
        for param, value in zip(
            included_params,
            params,
        )
    ) + ")" if params else "Map.of()"
    produces = ", ".join(_quote(str(value).lower()) for value in operation.get("produces", []))
    return (
        f"        operations.put({_quote(operation_id)}, new Operation({_quote(operation_id)}, "
        f"{_quote(operation['method'].upper())}, {_quote(operation['path'])}, "
        f"{param_map}, List.of({produces})));"
    )


def emit(root: Path, config: dict, spec: dict, assets: Path) -> None:
    """Generate a Maven project under ``root/java`` for one platform contract."""
    root = Path(root)
    template_dir = Path(__file__).resolve().parent / "templates" / "java"
    core = _load_core(Path(assets))
    policy = core.NamingPolicy(
        case_fn=lambda parts: "".join(part if index == 0 else part[:1].upper() + part[1:] for index, part in enumerate(parts)),
        keywords=frozenset({
            "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char", "class", "const",
            "continue", "default", "do", "double", "else", "enum", "extends", "final", "finally", "float",
            "for", "goto", "if", "implements", "import", "instanceof", "int", "interface", "long", "native",
            "new", "package", "private", "protected", "public", "return", "short", "static", "strictfp",
            "super", "switch", "synchronized", "this", "throw", "throws", "transient", "try", "void",
            "volatile", "while", "true", "false", "null", "var", "yield", "record", "sealed", "permits",
        }),
    )
    model = core.build_model(spec, policy)
    if not model.meta:
        raise ValueError("the sliced specification contains no operations")
    for op_id, operation in model.operations.items():
        if operation["method"] != "GET":
            raise ValueError(f"platform Java client supports GET only: {op_id}")

    platform = config["platform"]
    package_name = f"net.crawlora.{platform}"
    values = {
        "platform": platform,
        "display_name": config["display_name"],
        "java_description": config.get("java_description") or (
            f"Java client for Crawlora's hosted {config['display_name']} API, with direct methods for supported operations. "
            "Requires a Crawlora API key."
        ),
        "package_name": package_name,
        "version": config["version"],
        "repository": config["repository"],
        "operation_count": str(model.operation_count),
        "operation_ids": ",\n".join(f"            {_quote(op_id)}" for op_id in sorted(model.operations)),
        "operation_id_values": ", ".join(_quote(op_id) for op_id in sorted(model.operations)),
        "operation_rows": "\n".join(
            _operation_source(op_id, op, model.meta[op_id]["params"])
            for op_id, op in model.operations.items()
        ),
        "direct_methods": "\n".join(
            f"    public Object {name}(Map<String, ?> params) {{ return request({_quote(op_id)}, params); }}"
            for name, op_id in _method_aliases(model)
        ),
        "base_sdk_version": str(config.get("general_sdk_version", "1.46.0-sdk.1")),
    }
    values["class_name"] = "Client"
    values["default_base_url"] = "https://api.crawlora.net/api/v1"
    values["scm_url"] = config["repository"].removesuffix(".git")
    values["scm_browse_url"] = values["scm_url"].rstrip("/") + "/blob/main/java/README.md"
    values["homepage_url"] = escape(crawlora_url(source="maven-central", platform=platform, surface="java", destination="homepage"))
    values["organization_url"] = escape(crawlora_url(source="maven-central", platform=platform, surface="java", destination="organization-homepage"))
    values["repository_name"] = values["scm_url"].rstrip("/").rsplit("/", 1)[-1]
    values["test_operation_id"], test_params, test_method = _test_operation(model)
    values["test_params"] = test_params
    values["test_method_name"] = _quote(test_method)
    test_operation = model.meta[json.loads(values["test_operation_id"])]
    values["path_encoding_assertion"] = (
        '            assertTrue(seenUri.get().contains("path%20%2Fone"), "path values should be URL encoded");'
        if any(param.get("in") == "path" for param in test_operation["params"])
        else "            // This operation has no path parameters to encode."
    )
    usage_operation, usage_method = next(
        (
            (op_id, method)
            for group in model.groups.values()
            for method, op_id in group.items()
            if model.meta[op_id]["has_required_params"]
        ),
        next((op_id, method) for group in model.groups.values() for method, op_id in group.items()),
    )
    if config.get("platform") == "bbb" and "bbb-search" in model.meta:
        usage_operation = "bbb-search"
        usage_method = next(
            method
            for group in model.groups.values()
            for method, operation_id in group.items()
            if operation_id == usage_operation
        )
    values["usage_method"] = usage_method
    if config.get("platform") == "bbb" and usage_operation == "bbb-search":
        values["usage_params"] = (
            'Map.ofEntries(Map.entry("query", "coffee"), Map.entry("location", "New York, NY"))'
        )
    else:
        values["usage_params"] = _sample_param_map(model.meta[usage_operation]["params"])
    text_operation = next(
        (op_id for op_id, operation in model.operations.items() if "text/plain" in operation.get("produces", [])),
        next(iter(model.operations)),
    )
    values["text_operation_id"] = _quote(text_operation)
    values["text_params"] = _sample_param_map(model.meta[text_operation]["params"])
    values["enum_assertion"] = _enum_assertion(model)

    package_dir = root / "java"
    source_dir = package_dir / "src" / "main" / "java" / Path(*package_name.split("."))
    test_dir = package_dir / "src" / "test" / "java" / Path(*package_name.split("."))
    source_dir.mkdir(parents=True, exist_ok=True)
    test_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("pom.xml", "README.md"):
        _write(package_dir / filename, template_dir / f"{filename}.tmpl", values)
    for filename in ("Client.java", "Operation.java", "Param.java", "CrawloraException.java"):
        _write(source_dir / filename, template_dir / f"{filename}.tmpl", values)
    _write(test_dir / "ClientTest.java", template_dir / "ClientTest.java.tmpl", values)


def _write(target: Path, template: Path, values: dict[str, str]) -> None:
    text = template.read_text()
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    unresolved = re.findall(r"\{\{[a-z_]+\}\}", text)
    if unresolved:
        raise ValueError(f"unresolved Java template placeholders in {target}: {unresolved}")
    target.write_text(text)


def _sample_value(param: dict[str, Any]) -> Any:
    if param.get("enum"):
        return param["enum"][0]
    typ = param.get("type")
    if typ == "integer" or typ == "number":
        return 1
    if typ == "boolean":
        return True
    if typ == "array":
        return ["sample"]
    if typ == "object":
        return {}
    return "sample"


def _sample_param_map(params: list[dict[str, Any]], *, special_query: bool = False) -> str:
    values: dict[str, Any] = {}
    for param in params:
        if param.get("in") not in {"path", "query"} or param.get("name", "").lower() == "x-api-key":
            continue
        if param.get("required"):
            values[param["name"]] = "path /one" if special_query and param.get("in") == "path" else _sample_value(param)
    if special_query:
        query = next(
            (param for param in params if param.get("in") == "query" and not param.get("enum")
             and param.get("type", "string") == "string" and param.get("name", "").lower() != "x-api-key"),
            None,
        )
        if query:
            values[query["name"]] = "value &/one"
    if not values:
        return "Map.of()"
    return "Map.ofEntries(" + ", ".join(f"Map.entry({_quote(key)}, {_java_value(value)})" for key, value in values.items()) + ")"


def _java_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, list):
        return "List.of(" + ", ".join(_java_value(item) for item in value) + ")"
    if isinstance(value, dict):
        return "Map.of()"
    return _quote(str(value))


def _test_operation(model: Any) -> tuple[str, str, str]:
    candidates = []
    aliases = {operation_id: method for group in model.groups.values() for method, operation_id in group.items()}
    for operation_id, meta in model.meta.items():
        params = meta["params"]
        has_query = any(p.get("in") == "query" and p.get("name", "").lower() != "x-api-key" for p in params)
        has_string_query = any(
            p.get("in") == "query" and p.get("type", "string") == "string" and not p.get("enum")
            and p.get("name", "").lower() != "x-api-key" for p in params
        )
        candidates.append((has_string_query, has_query, any(p.get("in") == "path" for p in params), operation_id, params))
    _a, _b, _c, operation_id, params = max(candidates, key=lambda item: item[:3])
    return _quote(operation_id), _sample_param_map(params, special_query=True), aliases[operation_id]


def _enum_assertion(model: Any) -> str:
    for operation_id, meta in model.meta.items():
        params = meta["params"]
        enum = next((p for p in params if p.get("in") in {"path", "query"} and p.get("enum")
                     and p.get("name", "").lower() != "x-api-key"), None)
        if enum:
            values = {p["name"]: _sample_value(p) for p in params if p.get("required") and p.get("name", "").lower() != "x-api-key"}
            values[enum["name"]] = "__invalid_java_test_enum__"
            literal = "Map.ofEntries(" + ", ".join(
                f"Map.entry({_quote(key)}, {_java_value(value)})" for key, value in values.items()
            ) + ")"
            return (
                "        assertThrows(IllegalArgumentException.class, () -> new Client(\"key\", baseUrl, Duration.ofSeconds(1))"
                f".request({_quote(operation_id)}, {literal}));"
            )
    return "        assertTrue(true); // This contract currently defines no operation enum parameters."
