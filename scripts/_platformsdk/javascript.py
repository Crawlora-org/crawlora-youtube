"""Emit a focused JavaScript client package from a sliced Swagger 2 spec."""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any


def _load_generator(assets: Path):
    assets = assets.resolve()
    if str(assets) not in sys.path:
        sys.path.insert(0, str(assets))
    spec = importlib.util.spec_from_file_location(
        "platformclients_typescript_generator", assets / "typescript_generator.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load TypeScript generator from {assets}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _replace(template: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def _direct_methods(model: Any) -> list[tuple[str, str]]:
    """Return unambiguous grouped aliases exposed as convenience methods."""
    methods = [(method, operation_id) for group in model.groups.values() for method, operation_id in group.items()]
    names = [name for name, _ in methods]
    if len(names) != len(set(names)):
        duplicates = sorted({name for name in names if names.count(name) > 1})
        raise ValueError(f"platform operation aliases collide: {', '.join(duplicates)}")
    return methods


def _sample_value(param: dict[str, Any]) -> Any:
    if param.get("enum"):
        return param["enum"][0]
    if param.get("items", {}).get("enum"):
        return [param["items"]["enum"][0]]
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


def _sample_params(meta: dict[str, Any], *, include_optional: bool = False) -> dict[str, Any]:
    return {
        param["name"]: ({} if param.get("in") == "body" else _sample_value(param))
        for param in meta["params"]
        if param.get("required") or include_optional and param.get("in") in {"path", "query", "formData", "body"}
    }


def _path_pattern(path: str) -> str:
    pattern = re.sub(r"\{[^}]+\}", "PLACEHOLDER", path)
    return re.escape(pattern).replace("/", r"\/").replace("PLACEHOLDER", "[^/]+")


def emit(root: Path, config: dict, spec: dict, assets: Path) -> None:
    """Write a self-contained npm client package into ``root``.

    ``assets`` points at the pinned generator and maintained JavaScript
    transport. Runtime transport code is copied unchanged from that source.
    """
    root = Path(root)
    assets = Path(assets)
    templates = Path(__file__).resolve().parent / "templates" / "javascript"
    module = _load_generator(assets)
    model = module.core.build_model(spec, module.POLICY)
    if not model.meta:
        raise ValueError("the sliced specification contains no operations")

    package_dir = root / "javascript"
    src_dir = package_dir / "src"
    test_dir = package_dir / "test"
    docs_dir = package_dir / "docs"
    for directory in (src_dir, test_dir, docs_dir):
        directory.mkdir(parents=True, exist_ok=True)

    platform = config["platform"]
    values = {
        "platform": platform,
        "display_name": config["display_name"],
        "class_name": config["class_name"],
        "npm_name": config["npm_name"],
        "version": config["version"],
        "user_agent": f"crawlora-{platform}-js/{config['version']}",
        "repository": config["repository"],
        "homepage": config["repository"].rstrip("/") + "#readme",
        "bugs_url": config["repository"].rstrip("/") + "/issues",
        "group_name": config["group_name"],
        "contract_revision": config["contract_revision"],
    }
    values["user_agent_json"] = json.dumps(values["user_agent"])
    values["version_json"] = json.dumps(values["version"])
    values["group_name_json"] = json.dumps(values["group_name"])
    shutil.copyfile(assets / "javascript" / "client.js", src_dir / "client.js")
    for name in ("package.json", "package-lock.json", "tsconfig.json", "index.js", "runtime.test.js", "types.test.ts"):
        source = templates / name
        target = package_dir / name if name in {"package.json", "package-lock.json", "tsconfig.json"} else (
            test_dir / ("client.test.js" if name == "runtime.test.js" else "types.test.ts")
            if name in {"runtime.test.js", "types.test.ts"} else src_dir / name
        )
        target.write_text(_replace(source.read_text(), values))

    operation_aliases = _direct_methods(model)
    first_operation_id = next(
        (op_id for op_id, meta in model.meta.items() if meta["has_required_params"]),
        next(iter(model.meta)),
    )
    first_meta = model.meta[first_operation_id]
    first_method = next(method for method, op_id in operation_aliases if op_id == first_operation_id)
    text_operation_id = "youtube-transcript" if "youtube-transcript" in model.meta else first_operation_id
    text_meta = model.meta[text_operation_id]
    test_values = {
        "first_method_json": json.dumps(first_method),
        "first_method": first_method,
        "first_operation_json": json.dumps(first_operation_id),
        "first_params_json": json.dumps(_sample_params(first_meta)),
        "first_params_ts": json.dumps(_sample_params(first_meta)),
        "first_path_match": _path_pattern(first_meta["path"]),
        "text_operation_json": json.dumps(text_operation_id),
        "text_params_json": json.dumps(_sample_params(text_meta)),
        "text_params_ts": json.dumps(_sample_params(text_meta, include_optional=True)),
    }
    for test_file in (test_dir / "client.test.js", test_dir / "types.test.ts"):
        test_file.write_text(_replace(test_file.read_text(), test_values))
    runtime = (src_dir / "index.js").read_text()
    direct_bindings = "\n".join(
        f"    this[{json.dumps(method)}] = (...args) => this.request({json.dumps(operation_id)}, ...args);"
        for method, operation_id in operation_aliases
    )
    runtime = runtime.replace("{{direct_bindings}}", direct_bindings)
    (src_dir / "index.js").write_text(runtime)

    operation_ids = {
        meta["type_base"]: operation_id
        for operation_id, meta in sorted(model.meta.items(), key=lambda item: item[1]["type_base"])
    }
    (src_dir / "operations.js").write_text(
        "// Generated by the Crawlora platform client generator. Do not edit.\n"
        f"export const operations = {json.dumps(model.operations, indent=2, sort_keys=True)};\n\n"
        f"export const groups = {json.dumps(model.groups, indent=2, sort_keys=True)};\n\n"
        f"export const operationCount = {model.operation_count};\n\n"
        f"export const OperationIds = Object.freeze({json.dumps(operation_ids, indent=2, sort_keys=True)});\n"
    )

    type_text = module.type_declarations(model)
    (src_dir / "types.d.ts").write_text(type_text)
    declarations = (templates / "index.d.ts").read_text()
    text_mode_declarations = [
        "  request<I extends OperationId>(operationId: I, params: OperationParamsMap[I], "
        "options: CrawloraRequestOptions & { responseType: \"text\" }): Promise<string>;",
        "  operation<I extends OperationId>(operationId: I, params: OperationParamsMap[I], "
        "options: CrawloraRequestOptions & { responseType: \"text\" }): Promise<string>;",
    ]
    stream_mode_declarations = [
        "  request<I extends OperationId>(operationId: I, params: OperationParamsMap[I], "
        "options: CrawloraRequestOptions & { responseType: \"stream\" }): Promise<Response>;",
        "  operation<I extends OperationId>(operationId: I, params: OperationParamsMap[I], "
        "options: CrawloraRequestOptions & { responseType: \"stream\" }): Promise<Response>;",
    ]
    for method, operation_id in operation_aliases:
        params_type = f"OperationParamsMap[{json.dumps(operation_id)}]"
        if model.meta[operation_id]["has_required_params"]:
            stream_mode_declarations.append(
                f"  {method}(params: {params_type}, options: CrawloraRequestOptions & "
                "{ responseType: \"stream\" }): Promise<Response>;"
            )
        else:
            stream_mode_declarations.append(
                f"  {method}(params?: {params_type}, options?: CrawloraRequestOptions & "
                "{ responseType: \"stream\" }): Promise<Response>;"
            )
        if model.meta[operation_id]["has_required_params"]:
            text_mode_declarations.append(
                f"  {method}(params: {params_type}, options: CrawloraRequestOptions & "
                "{ responseType: \"text\" }): Promise<string>;"
            )
        else:
            text_mode_declarations.append(
                f"  {method}(params?: {params_type}, options?: CrawloraRequestOptions & "
                "{ responseType: \"text\" }): Promise<string>;"
            )
    text_mode_declarations = "\n".join(text_mode_declarations)
    stream_mode_declarations = "\n".join(stream_mode_declarations)
    direct_declarations = "\n".join(
        f"  {method}(...args: OperationRequestArgs<{json.dumps(operation_id)}>): "
        f"Promise<OperationResponseMap[{json.dumps(operation_id)}]>;"
        for method, operation_id in operation_aliases
    )
    transcript_declarations = ""
    transcript_test = ""
    optional_method_test = ""
    optional_operation = next(
        (op_id for op_id, meta in model.meta.items() if not meta["has_required_params"]), None
    )
    if optional_operation:
        optional_method = next(method for method, op_id in operation_aliases if op_id == optional_operation)
        optional_method_test = (
            f"void client.{optional_method}();\nvoid client.request({json.dumps(optional_operation)});"
        )
    transcript = model.meta.get("youtube-transcript")
    if transcript:
        format_param = next(
            (param for param in transcript["params"] if param.get("name") == "format"), None
        )
        text_formats = [
            value
            for value in (format_param or {}).get("enum", [])
            if value in {"text", "srt", "vtt"}
        ]
        if text_formats:
            alias = next(method for method, op_id in operation_aliases if op_id == "youtube-transcript")
            format_union = " | ".join(json.dumps(value) for value in text_formats)
            params_type = f"OperationParamsMap[\"youtube-transcript\"]"
            transcript_declarations = (
                f"  {alias}(params: {params_type} & {{ format: {format_union} }}, "
                'options?: Omit<CrawloraRequestOptions, "responseType"> & '
                '{ responseType?: "auto" | "text" }): Promise<string>;\n'
                f"  request(operationId: \"youtube-transcript\", params: {params_type} & "
                f"{{ format: {format_union} }}, options?: Omit<CrawloraRequestOptions, \"responseType\"> & "
                '{ responseType?: "auto" | "text" }): Promise<string>;\n'
                f"  operation(operationId: \"youtube-transcript\", params: {params_type} & "
                f"{{ format: {format_union} }}, options?: Omit<CrawloraRequestOptions, \"responseType\"> & "
                '{ responseType?: "auto" | "text" }): Promise<string>;'
            )
            sample_params = _sample_params(transcript, include_optional=True)
            sample_params["format"] = text_formats[0]
            transcript_test = (
                f"const transcriptText: Promise<string> = client.{alias}({json.dumps(sample_params)});\n"
                f"const transcriptTextViaRequest: Promise<string> = client.request(\"youtube-transcript\", "
                f"{json.dumps(sample_params)});\nvoid transcriptText; void transcriptTextViaRequest;"
            )
            transcript_stream_test = (
                f"const transcriptStream: Promise<Response> = client.{alias}({json.dumps(sample_params)}, "
                '{ responseType: "stream" });\nvoid transcriptStream;'
            )
            if text_operation_id == "youtube-transcript":
                typed_text_params = _sample_params(text_meta, include_optional=True)
                typed_text_params["format"] = text_formats[0]
                type_test = (test_dir / "types.test.ts").read_text()
                type_test = type_test.replace(
                    json.dumps(_sample_params(text_meta, include_optional=True)),
                    json.dumps(typed_text_params),
                )
                (test_dir / "types.test.ts").write_text(type_test)
        else:
            transcript_stream_test = ""
    else:
        transcript_stream_test = ""
    declarations = _replace(
        declarations,
        values
        | {
            "direct_declarations": direct_declarations,
            "stream_mode_declarations": stream_mode_declarations,
            "text_mode_declarations": text_mode_declarations,
            "transcript_declarations": transcript_declarations,
        },
    )
    (src_dir / "index.d.ts").write_text(declarations)
    type_test = (test_dir / "types.test.ts").read_text()
    (test_dir / "types.test.ts").write_text(
        _replace(
            type_test,
            {
                "transcript_type_test": transcript_test,
                "transcript_stream_type_test": transcript_stream_test,
                "optional_method_test": optional_method_test,
            },
        )
    )

    (docs_dir / "javascript-operations.md").write_text(
        module.core.operation_docs(
            model,
            title=f"Crawlora {config['display_name']} JavaScript Client Operations",
            type_render=module.ts_type,
        )
    )
