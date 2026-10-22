"""Emit a standalone, focused Rust client crate for one platform."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from .documentation import _canonical_method_names, _example_values, _operations
from .utm import crawlora_url


def _load_generator(assets: Path):
    vendor = Path(assets).resolve() / "rust"
    if str(vendor) not in sys.path:
        sys.path.insert(0, str(vendor))
    spec = importlib.util.spec_from_file_location("platformsdk_rust_generator", vendor / "generate.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load the pinned Rust generator from {vendor}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _rust_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _rust_value(value: Any, schema: dict[str, Any]) -> str:
    kind = schema.get("type")
    if schema.get("enum"):
        kind = "string"
    if kind == "array":
        item_schema = schema.get("items") or {}
        return "vec![" + ", ".join(_rust_value(item, item_schema) for item in value) + "]"
    if kind == "integer":
        return str(int(value))
    if kind == "number":
        return repr(float(value))
    if kind == "boolean":
        return "true" if value else "false"
    if kind == "string":
        return _rust_string(str(value)) + ".to_owned()"
    if isinstance(value, (dict, list)):
        return "serde_json::json!(" + json.dumps(value, ensure_ascii=False) + ")"
    if value is None:
        return "serde_json::Value::Null"
    return "serde_json::json!(" + json.dumps(value, ensure_ascii=False) + ")"


def _quickstart(model: Any, generator: Any, config: dict[str, Any], spec: dict[str, Any], assets: Path) -> str:
    platform = str(config["platform"])
    operations = _operations(spec, platform, _canonical_method_names(spec, assets))
    examples = _example_values(platform, operations)
    methods = {
        operation_id: method
        for group_methods in model.groups.values()
        for method, operation_id in group_methods.items()
    }
    parameter_types: dict[str, str] = {}
    used_types: set[str] = set()
    for operation_id, meta in model.meta.items():
        parameter_types[operation_id] = generator.unique_name(
            generator.pascal(meta["type_base"]) + "Params", used_types
        )

    selected_id: str | None = None
    selected_values: dict[str, Any] = {}
    for operation, values in examples:
        operation_id = operation["id"]
        meta = model.meta.get(operation_id)
        if meta and meta["method"] == "GET" and operation_id in methods:
            selected_id, selected_values = operation_id, values
            break
    if selected_id is None:
        for operation_id, meta in model.meta.items():
            if meta["method"] == "GET" and operation_id in methods:
                selected_id = operation_id
                break
    if selected_id is None:
        raise ValueError(f"{platform} has no GET operation for the Rust quick start")

    meta = model.meta[selected_id]
    model_names = generator.model_type_names(model.definitions)
    response_type = generator.schema_type(meta.get("response_schema"), model_names)
    fields: list[str] = []
    used_fields: set[str] = set()
    for param in meta["params"]:
        raw_name = str(param.get("name", ""))
        if raw_name not in selected_values:
            continue
        schema = generator.parameter_schema(param)
        field = generator.unique_name(generator.snake(raw_name), used_fields)
        fields.append(f"            {field}: Some({_rust_value(selected_values[raw_name], schema)}),")
    params_literal = "\n".join(fields)
    if meta["params"]:
        if params_literal:
            params_literal += "\n"
        params_expression = f"{parameter_types[selected_id]} {{\n{params_literal}            ..Default::default()\n        }}"
    else:
        params_expression = "Default::default()"
    service = generator.snake(next(iter(model.groups)))
    method = methods[selected_id]
    params_type = parameter_types[selected_id]
    module_name = str(config.get("rust_module_name") or "crawlora_" + platform.replace("-", "_"))
    imports = ["Client", params_type]
    if response_type == "serde_json::Value":
        imports.append("serde_json")
    else:
        imports.append(response_type)
    example = (
        "use " + module_name + "::{" + ", ".join(imports) + "};\n\n"
        "#[tokio::main]\n"
        "async fn main() -> Result<(), Box<dyn std::error::Error>> {\n"
        "    let api_key = std::env::var(\"CRAWLORA_API_KEY\")?;\n"
        "    let client = Client::new(api_key)?;\n"
        f"    let response = client\n"
        f"        .{service}\n"
        f"        .{method}({params_expression})\n"
        "        .await?;\n"
        f"    let data: {response_type} = response.into_json()?;\n"
        "    println!(\"{data:#?}\");\n"
        "    Ok(())\n"
        "}\n"
    )
    return example


def emit(root: Path, config: dict[str, Any], spec: dict[str, Any], assets: Path) -> None:
    root = Path(root)
    assets = Path(assets)
    rust_root = root / "rust"
    source = Path(__file__).resolve().parent
    templates = source / "templates" / "rust"
    generator = _load_generator(assets)
    model = generator.core.build_model(spec, generator.POLICY)
    if not model.meta or len(model.groups) != 1:
        raise ValueError("a focused Rust platform crate requires one non-empty service group")

    platform = str(config["platform"])
    version = str(config["version"])
    module_name = str(config.get("rust_module_name") or "crawlora_" + platform.replace("-", "_"))
    crate_name = str(config.get("rust_crate_name") or "crawlora-" + platform)
    example = _quickstart(model, generator, config, spec, assets)

    values = {
        "PLATFORM": platform,
        "DISPLAY_NAME": str(config["display_name"]),
        "CLASS_NAME": str(config["class_name"]),
        "RUST_MODULE_NAME": module_name,
        "RUST_CRATE_NAME": crate_name,
        "RUST_EXAMPLE": example.rstrip(),
        "VERSION": version,
        "OPERATION_COUNT": str(model.operation_count),
        "REPOSITORY": str(config["repository"]),
        "DOCS_URL": crawlora_url(source="crates.io", platform=platform, surface="rust", destination="api-docs", path="/docs"),
        "HOME_URL": crawlora_url(source="crates.io", platform=platform, surface="rust", destination="homepage"),
        "SIGNUP_URL": crawlora_url(source="crates.io", platform=platform, surface="rust", destination="signup", path="/signup"),
        "API_KEYS_URL": crawlora_url(source="crates.io", platform=platform, surface="rust", destination="api-keys", path="/app/api-keys"),
        "PRICING_URL": crawlora_url(source="crates.io", platform=platform, surface="rust", destination="pricing", path="/pricing"),
        "KEYWORDS_JSON": json.dumps(["crawlora", platform, "api-client", "web-scraping"], ensure_ascii=False),
        "DESCRIPTION": f"Typed Rust client for Crawlora's hosted {config['display_name']} API. Requires a Crawlora API key.",
    }

    rust_root.mkdir(parents=True, exist_ok=True)
    for relative, template in (
        ("Cargo.toml", "Cargo.toml.tmpl"),
        ("README.md", "README.md.tmpl"),
    ):
        text = (templates / template).read_text(encoding="utf-8")
        for key, value in values.items():
            text = text.replace("{{" + key + "}}", value)
        if "{{" in text:
            raise ValueError(f"unresolved Rust template value in {template}")
        target = rust_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text.rstrip() + "\n", encoding="utf-8")

    runtime = assets / "rust" / "runtime"
    (rust_root / "src").mkdir(exist_ok=True)
    for filename in ("client.rs", "error.rs", "operation.rs", "LICENSE"):
        target = rust_root / ("LICENSE" if filename == "LICENSE" else f"src/{filename}")
        content = (runtime / filename).read_text(encoding="utf-8")
        if filename == "client.rs":
            content = content.replace(
                'format!("crawlora-rust-sdk/{}", env!("CARGO_PKG_VERSION"))',
                'format!("{}/{}", env!("CARGO_PKG_NAME"), env!("CARGO_PKG_VERSION"))',
            )
        target.write_text(content, encoding="utf-8")

    lock_text = (runtime / "Cargo.lock").read_text(encoding="utf-8")
    package_match = 'name = "crawlora"\nversion = "1.49.0-sdk.3"'
    package_lock = f'name = "{crate_name}"\nversion = "{version}"'
    if lock_text.count(package_match) != 1:
        raise ValueError("pinned Rust Cargo.lock must contain exactly one general SDK package entry")
    (rust_root / "Cargo.lock").write_text(lock_text.replace(package_match, package_lock, 1), encoding="utf-8")

    models = model.definitions
    names = generator.model_type_names(models)
    flattened, _ = generator.refs_and_properties(models)
    (rust_root / "src/models.rs").write_text(
        generator.render_models(models, names, flattened), encoding="utf-8"
    )
    (rust_root / "src/operations_generated.rs").write_text(
        generator.render_operations(model), encoding="utf-8"
    )
    (rust_root / "src/services_generated.rs").write_text(
        generator.render_services(model, names), encoding="utf-8"
    )
    (rust_root / "src/lib.rs").write_text(
        "mod client;\nmod error;\nmod operation;\n"
        "pub mod models;\nmod operations_generated;\n"
        "pub mod services_generated;\n\n"
        "pub use client::{\n"
        "    CrawloraClient, CrawloraClientBuilder, CursorPaginator, OffsetPaginator, DEFAULT_BASE_URL,\n"
        "};\n"
        "pub use error::Error;\n"
        "pub use models::*;\n"
        "pub use operation::{ApiResponse, RequestOptions, ResponseBody, ResponseMode};\n"
        "pub use serde_json;\n"
        "pub use services_generated::*;\n\n"
        "pub const VERSION: &str = env!(\"CARGO_PKG_VERSION\");\n"
        "pub type Client = CrawloraClient;\n"
        f"pub type {config['class_name']} = CrawloraClient;\n",
        encoding="utf-8",
    )
    docs = generator.core.operation_docs(
        model,
        title=f"Crawlora {config['display_name']} Rust SDK Operations",
        type_render=lambda param: generator.render_param_doc(param, names),
    )
    docs_dir = rust_root / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "operations.md").write_text(docs, encoding="utf-8")
    examples_dir = rust_root / "examples"
    examples_dir.mkdir(exist_ok=True)
    (examples_dir / "quick_start.rs").write_text(example, encoding="utf-8")
    changelog = root / "CHANGELOG.md"
    if changelog.is_file():
        shutil.copyfile(changelog, rust_root / "CHANGELOG.md")
