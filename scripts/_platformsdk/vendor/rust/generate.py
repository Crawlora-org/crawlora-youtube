#!/usr/bin/env python3
"""Generate the Rust SDK surface and operation metadata from OpenAPI v2."""

from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPEC = ROOT / "openapi" / "public.json"
SPEC_PATH = Path(os.environ.get("CRAWLORA_OPENAPI_SPEC", str(DEFAULT_SPEC)))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _sdkgen import core  # noqa: E402

RUST_KEYWORDS = frozenset(
    "as async await break const continue crate dyn else enum extern false fn for if impl in let loop match mod move mut pub ref return self Self static struct super trait true type unsafe use where while abstract become box do final macro override priv typeof unsized virtual yield try gen".split()
)
TAG_OVERRIDES = {
    "1stDibs": "first_dibs",
    "7NOW": "seven_now",
    "7NEWS Australia": "seven_news_australia",
    "9to5Mac": "nine_to_five_mac",
    "9to5Google": "nine_to_five_google",
    "AppStore": "app_store",
    "CoinGecko": "coin_gecko",
    "GooglePlay": "google_play",
    "ProductHunt": "product_hunt",
    "SimilarWeb": "similar_web",
    "SpotifyPodcasts": "spotify_podcasts",
    "TikTok": "tiktok",
    "YouTube": "youtube",
}


def rust_snake(parts: list[str]) -> str:
    name = "_".join(parts) or "call"
    if name[0].isdigit():
        name = "n_" + name
    if name in RUST_KEYWORDS:
        name += "_"
    return name


def snake(value: str) -> str:
    return rust_snake(core.words(value))


def pascal(value: str) -> str:
    parts = core.words(value)
    name = "".join(part[:1].upper() + part[1:] for part in parts) or "Value"
    if name[0].isdigit():
        name = "N" + name
    if name in RUST_KEYWORDS:
        name += "Value"
    return name


def rust_string(value: Any) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def unique_name(base: str, used: set[str]) -> str:
    name = base
    number = 2
    while name in used:
        name = f"{base}_{number}"
        number += 1
    used.add(name)
    return name


POLICY = core.NamingPolicy(
    case_fn=rust_snake,
    dedup_sep="_",
    tag_group_overrides=TAG_OVERRIDES,
    keywords=RUST_KEYWORDS,
    type_base_fn=lambda group, method: pascal(f"{group}-{method}"),
)


def schema_ref_name(ref: str) -> str:
    return ref.rsplit("/", 1)[-1]


def refs_and_properties(definitions: dict[str, dict]) -> tuple[dict[str, dict], dict[str, str]]:
    """Flatten allOf properties and preserve required/additionalProperties metadata."""
    cache: dict[str, dict] = {}

    def collect_schema(schema: dict, stack: tuple[str, ...]) -> dict:
        properties: dict[str, dict] = {}
        required: set[str] = set()
        additional: dict | bool | None = None
        ref = schema.get("$ref")
        if ref:
            target = schema_ref_name(ref)
            if target not in stack and target in definitions:
                inherited = collect_name(target, stack)
                properties.update(inherited["properties"])
                required.update(inherited["required"])
                additional = inherited["additional"]
        for part in schema.get("allOf", []) or []:
            if isinstance(part, dict):
                part_result = collect_schema(part, stack)
                for name, prop in part_result["properties"].items():
                    properties.setdefault(name, prop)
                required.update(part_result["required"])
                if additional is None and part_result["additional"] is not None:
                    additional = part_result["additional"]
        for name, prop in (schema.get("properties") or {}).items():
            properties[name] = prop if isinstance(prop, dict) else {}
        required.update(schema.get("required", []) or [])
        if "additionalProperties" in schema:
            additional = schema["additionalProperties"]
        return {"properties": properties, "required": required, "additional": additional}

    def collect_name(name: str, stack: tuple[str, ...] = ()) -> dict:
        if name in cache:
            return cache[name]
        if name in stack:
            return {"properties": {}, "required": set(), "additional": None}
        schema = definitions.get(name) or {}
        result = collect_schema(schema, stack + (name,))
        cache[name] = result
        return result

    for definition_name in definitions:
        collect_name(definition_name)
    return cache, {}


def direct_reference(schema: dict) -> str | None:
    if not isinstance(schema, dict):
        return None
    if schema.get("$ref"):
        return schema_ref_name(schema["$ref"])
    return None


def model_type_names(definitions: dict[str, dict]) -> dict[str, str]:
    used: set[str] = set()
    result = {}
    for raw_name in sorted(definitions):
        result[raw_name] = unique_name("Model" + pascal(raw_name), used)
    return result


def strongly_connected_components(graph: dict[str, set[str]]) -> dict[str, int]:
    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    component: dict[str, int] = {}
    next_component = 0

    def visit(node: str) -> None:
        nonlocal index, next_component
        indices[node] = index
        lowlink[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in graph.get(node, set()):
            if target not in graph:
                continue
            if target not in indices:
                visit(target)
                lowlink[node] = min(lowlink[node], lowlink[target])
            elif target in on_stack:
                lowlink[node] = min(lowlink[node], indices[target])
        if lowlink[node] == indices[node]:
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component[member] = next_component
                if member == node:
                    break
            next_component += 1

    for node in graph:
        if node not in indices:
            visit(node)
    return component


def model_fields(definitions: dict[str, dict], flattened: dict[str, dict]) -> dict[str, list[tuple[str, dict]]]:
    return {
        name: list((flattened.get(name) or {}).get("properties", {}).items())
        for name in definitions
    }


def recursive_field_edges(definitions: dict[str, dict], flattened: dict[str, dict]) -> set[tuple[str, str]]:
    graph: dict[str, set[str]] = {name: set() for name in definitions}
    edges: list[tuple[str, str, str]] = []
    fields = model_fields(definitions, flattened)
    for source, props in fields.items():
        for property_name, schema in props:
            target = direct_reference(schema)
            if target in definitions:
                graph[source].add(target)
                edges.append((source, property_name, target))
    components = strongly_connected_components(graph)
    sizes: dict[int, int] = defaultdict(int)
    for value in components.values():
        sizes[value] += 1
    return {
        (source, prop)
        for source, prop, target in edges
        if components.get(source) == components.get(target)
        and (source == target or sizes.get(components.get(source, -1), 0) > 1)
    }


def schema_type(schema: dict | None, names: dict[str, str], *, box_ref: bool = False) -> str:
    if not isinstance(schema, dict):
        return "serde_json::Value"
    if schema.get("$ref"):
        name = names.get(schema_ref_name(schema["$ref"]), "serde_json::Value")
        return f"Box<{name}>" if box_ref else name
    if schema.get("enum"):
        return "String"
    if schema.get("allOf"):
        refs = [part for part in schema["allOf"] if isinstance(part, dict) and part.get("$ref")]
        if len(refs) == 1 and len(schema["allOf"]) == 1:
            return schema_type(refs[0], names, box_ref=box_ref)
        return "serde_json::Value"
    kind = schema.get("type")
    if kind == "array":
        return f"Vec<{schema_type(schema.get('items') or {}, names)}>"
    if kind == "integer":
        return "i32" if schema.get("format") == "int32" else "i64"
    if kind == "number":
        return "f32" if schema.get("format") == "float" else "f64"
    if kind == "boolean":
        return "bool"
    if kind == "string":
        return "Vec<u8>" if schema.get("format") == "binary" else "String"
    if kind == "file":
        return "Vec<u8>"
    if kind == "object":
        additional = schema.get("additionalProperties")
        if isinstance(additional, dict):
            return f"std::collections::BTreeMap<String, {schema_type(additional, names)}>"
        return "serde_json::Value"
    return "serde_json::Value"


def parameter_schema(param: dict) -> dict:
    if param.get("in") == "body":
        return param.get("schema") or {}
    result = {"type": param.get("type", "string")}
    if param.get("format"):
        result["format"] = param["format"]
    if param.get("items"):
        result["items"] = param["items"]
    if param.get("enum"):
        result["enum"] = param["enum"]
    return result


def enum_values(param: dict) -> list[str]:
    values = param.get("enum") or param.get("items", {}).get("enum") or []
    return [str(value) for value in values]


def render_parameter_definition(param: dict) -> str:
    collection_format = param.get("collectionFormat")
    kind = param.get("type")
    enum = enum_values(param)
    return (
        "ParameterDefinition { "
        f"name: {rust_string(param.get('name', ''))}, "
        f"collection_format: {f'Some({rust_string(collection_format)})' if collection_format else 'None'}, "
        f"kind: {f'Some({rust_string(kind)})' if kind else 'None'}, "
        f"required: {'true' if param.get('required') else 'false'}, "
        f"enum_values: &[{', '.join(rust_string(value) for value in enum)}] "
        "}"
    )


def render_str_slice(values: list[str]) -> str:
    return "&[" + ", ".join(rust_string(value) for value in values) + "]"


def render_operations(model: core.Model) -> str:
    entries = []
    for operation_id, operation in model.operations.items():
        meta = model.meta[operation_id]
        path_params = [param for param in meta["params"] if param.get("in") == "path"]
        query_params = operation.get("queryParams", [])
        form_params = operation.get("formParams", [])
        body_param = operation.get("bodyParam")
        consumes = operation.get("consumes", [])
        produces = operation.get("produces", [])
        security = operation.get("security", [])
        body_required = operation.get("bodyRequired", False)
        entries.append(
            "    OperationDefinition {\n"
            f"        id: {rust_string(operation_id)}, method: {rust_string(operation['method'])}, path: {rust_string(operation['path'])},\n"
            f"        path_params: &[{', '.join(render_parameter_definition(param) for param in path_params)}],\n"
            f"        query_params: &[{', '.join(render_parameter_definition(param) for param in query_params)}],\n"
            f"        form_params: &[{', '.join(render_parameter_definition(param) for param in form_params)}],\n"
            f"        body_param: {f'Some({rust_string(body_param)})' if body_param else 'None'}, body_required: {'true' if body_required else 'false'},\n"
            f"        consumes: {render_str_slice(consumes)}, produces: {render_str_slice(produces)}, security: {render_str_slice(security)},\n"
            "    }"
        )
    entry_text = ",\n".join(entries)
    return (
        "// @generated by scripts/generate.py; do not edit by hand.\n"
        "use crate::operation::{OperationDefinition, ParameterDefinition};\n\n"
        f"static OPERATIONS: &[OperationDefinition] = &[\n{entry_text}\n];\n\n"
        "pub(crate) fn get(id: &str) -> Option<&'static OperationDefinition> {\n"
        "    OPERATIONS.iter().find(|operation| operation.id == id)\n"
        "}\n"
    )


def render_models(definitions: dict[str, dict], names: dict[str, str], flattened: dict[str, dict]) -> str:
    boxed = recursive_field_edges(definitions, flattened)
    output = [
        "// @generated by scripts/generate.py; do not edit by hand.",
        "use serde::{Deserialize, Serialize};",
        "use serde_json::Value;",
        "use std::collections::BTreeMap;",
        "",
    ]
    for raw_name in sorted(definitions):
        schema = definitions.get(raw_name) or {}
        name = names[raw_name]
        props = (flattened.get(raw_name) or {}).get("properties", {})
        additional = (flattened.get(raw_name) or {}).get("additional")
        kind = schema.get("type")
        if props or schema.get("allOf"):
            output.extend(["#[derive(Debug, Clone, Default, Serialize, Deserialize)]", f"pub struct {name} {{"])
            used_fields: set[str] = set()
            for property_name, property_schema in props.items():
                field = unique_name(snake(property_name), used_fields)
                boxed_ref = (raw_name, property_name) in boxed
                field_type = schema_type(property_schema, names, box_ref=boxed_ref)
                output.append(
                    f"    #[serde(rename = {rust_string(property_name)}, default, skip_serializing_if = \"Option::is_none\")]"
                )
                output.append(f"    pub {field}: Option<{field_type}>,")
            if additional is not False:
                value_type = schema_type(additional, names) if isinstance(additional, dict) else "Value"
                extra_field = unique_name("additional", used_fields)
                output.append("    #[serde(flatten)]")
                output.append(f"    pub {extra_field}: BTreeMap<String, {value_type}>,")
            output.extend(["}", ""])
        else:
            alias = schema_type(schema, names)
            if kind == "object" and isinstance(additional, dict):
                alias = f"std::collections::BTreeMap<String, {schema_type(additional, names)}>"
            elif kind == "object" and additional is not False:
                alias = "std::collections::BTreeMap<String, Value>"
            output.extend([f"pub type {name} = {alias};", ""])
    return "\n".join(output)


def render_params_struct(operation_id: str, params: list[dict], type_name: str, names: dict[str, str]) -> str:
    output = ["#[derive(Debug, Clone, Default, serde::Serialize)]", f"pub struct {type_name} {{"]
    used_fields: set[str] = set()
    if not params:
        output.append("    #[serde(skip)]")
        output.append("    _empty: Option<()>,")
    for param in params:
        raw_name = param.get("name", "param")
        field = unique_name(snake(raw_name), used_fields)
        field_type = schema_type(parameter_schema(param), names)
        output.append(
            f"    #[serde(rename = {rust_string(raw_name)}, skip_serializing_if = \"Option::is_none\")]"
        )
        output.append(f"    pub {field}: Option<{field_type}>,")
    output.extend(["}", ""])
    return "\n".join(output)


def render_services(model: core.Model, names: dict[str, str]) -> str:
    type_names: dict[str, str] = {}
    used_types: set[str] = set()
    for operation_id, meta in model.meta.items():
        type_names[operation_id] = unique_name(pascal(meta["type_base"]) + "Params", used_types)

    group_type_names: dict[str, str] = {}
    used_group_types: set[str] = set()
    for group in model.groups:
        group_type_names[group] = unique_name(pascal(group) + "Api", used_group_types)

    output = [
        "// @generated by scripts/generate.py; do not edit by hand.",
        "use crate::client::ClientInner;",
        "#[allow(unused_imports)]",
        "use crate::models::*;",
        "use crate::{ApiResponse, Error, RequestOptions};",
        "use std::sync::Arc;",
        "",
        "#[derive(Clone)]",
        "pub struct Services {",
    ]
    used_fields: set[str] = set()
    group_fields: dict[str, str] = {}
    for group in model.groups:
        field = unique_name(snake(group), used_fields)
        group_fields[group] = field
        output.append(f"    pub {field}: {group_type_names[group]},")
    output.extend(["}", "", "impl Services {", "    pub(crate) fn new(inner: Arc<ClientInner>) -> Self {", "        Self {"])
    for group in model.groups:
        output.append(
            f"            {group_fields[group]}: {group_type_names[group]} {{ inner: Arc::clone(&inner) }},"
        )
    output.extend(["        }", "    }", "}", ""])

    for operation_id, meta in model.meta.items():
        output.append(render_params_struct(operation_id, meta["params"], type_names[operation_id], names))

    for group, methods in model.groups.items():
        group_type = group_type_names[group]
        output.extend(["#[derive(Clone)]", f"pub struct {group_type} {{", "    pub(crate) inner: Arc<ClientInner>,", "}", ""])
        output.extend([f"impl {group_type} {{"])
        for method_name, operation_id in methods.items():
            meta = model.meta[operation_id]
            params_type = type_names[operation_id]
            output.extend(
                [
                    f"    pub async fn {method_name}(&self, params: {params_type}) -> Result<ApiResponse, Error> {{",
                    f"        self.inner.call({rust_string(operation_id)}, &params, RequestOptions::default()).await",
                    "    }",
                    "",
                ]
            )
        output.extend(["}", ""])
    return "\n".join(output)


def render_param_doc(param: dict, names: dict[str, str]) -> str:
    typ = schema_type(parameter_schema(param), names)
    enums = enum_values(param)
    if enums:
        return f"{typ} enum{{{', '.join(enums)}}}"
    return typ


def main() -> None:
    if not SPEC_PATH.exists():
        raise SystemExit(f"OpenAPI contract not found: {SPEC_PATH}")
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    model = core.build_model(spec, POLICY)
    definitions = model.definitions
    names = model_type_names(definitions)
    flattened, _ = refs_and_properties(definitions)

    (ROOT / "src" / "models.rs").write_text(render_models(definitions, names, flattened), encoding="utf-8")
    (ROOT / "src" / "operations_generated.rs").write_text(render_operations(model), encoding="utf-8")
    (ROOT / "src" / "services_generated.rs").write_text(render_services(model, names), encoding="utf-8")
    docs = core.operation_docs(
        model,
        title="Crawlora Rust SDK Operations",
        type_render=lambda param: render_param_doc(param, names),
    )
    (ROOT / "docs" / "operations.md").write_text(docs, encoding="utf-8")
    print(f"generated {model.operation_count} operations and {len(definitions)} models from {SPEC_PATH}")


if __name__ == "__main__":
    main()
