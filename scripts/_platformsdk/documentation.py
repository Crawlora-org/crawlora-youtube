"""Emit public documentation, examples, and registry workflows for platform clients."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


def _vendor_directory(assets: Path) -> Path:
    candidates = (
        assets / "vendor",
        assets,
        Path(__file__).parent / "vendor",
    )
    return next(
        (candidate for candidate in candidates if (candidate / "typescript_generator.py").is_file()),
        candidates[-1],
    )


def _canonical_method_names(spec: dict[str, Any], assets: Path) -> dict[str, dict[str, str]]:
    """Read method aliases from the pinned TypeScript and Python generators."""
    vendor = _vendor_directory(assets)
    original_path = str(vendor)
    sys.path.insert(0, original_path)
    try:
        loaded: dict[str, Any] = {}
        for label, filename in (
            ("javascript", "typescript_generator.py"),
            ("python", "python_generator.py"),
        ):
            module_name = f"_platformsdk_docs_{label}_generator"
            module_spec = importlib.util.spec_from_file_location(module_name, vendor / filename)
            if module_spec is None or module_spec.loader is None:
                raise RuntimeError(f"unable to load pinned {label} generator from {vendor}")
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module)
            loaded[label] = module
    finally:
        if sys.path and sys.path[0] == original_path:
            sys.path.pop(0)

    result: dict[str, dict[str, str]] = {}
    for language, generator in loaded.items():
        model = generator.core.build_model(spec, generator.POLICY)
        result[language] = {
            operation_id: method_name
            for methods in model.groups.values()
            for method_name, operation_id in methods.items()
        }
    return result


def _operations(spec: dict[str, Any], platform: str, method_names: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    operations: list[dict[str, Any]] = []
    for path, path_item in (spec.get("paths") or {}).items():
        if not isinstance(path_item, dict):
            continue
        for verb, operation in path_item.items():
            if verb.lower() not in _METHODS or not isinstance(operation, dict):
                continue
            operation_id = str(operation.get("operationId") or "")
            tags = [str(tag).strip().lower() for tag in operation.get("tags", [])]
            if tags and platform.lower() not in tags and not operation_id.lower().startswith(platform.lower() + "-"):
                continue
            try:
                js_name = method_names["javascript"][operation_id]
                py_name = method_names["python"][operation_id]
            except KeyError as error:
                raise ValueError(f"operation {operation_id!r} is missing from the pinned client models") from error
            params = [
                p
                for p in operation.get("parameters", [])
                if isinstance(p, dict) and p.get("in") in {"path", "query", "body", "formData"}
            ]
            operations.append(
                {
                    "id": operation_id,
                    "js": js_name,
                    "py": py_name,
                    "verb": verb.upper(),
                    "path": str(path),
                    "summary": str(operation.get("summary") or operation.get("description") or operation_id).split("\n", 1)[0],
                    "params": params,
                    "produces": [str(x).lower() for x in operation.get("produces", [])],
                }
            )
    operations.sort(key=lambda op: (op["js"].casefold(), op["path"]))
    return operations


def _param_label(param: dict[str, Any]) -> str:
    name = str(param.get("name", "value"))
    required = "required" if param.get("required") else "optional"
    location = str(param.get("in", "parameter"))
    allowed = param.get("enum") or (param.get("items") or {}).get("enum") or []
    encoded_values = ["`" + str(value).replace("|", "\\|") + "`" for value in allowed]
    suffix = f"; values: {', '.join(encoded_values)}" if encoded_values else ""
    return f"`{name}` ({location}, {required}{suffix})"


def _operation_catalog(operations: list[dict[str, Any]]) -> str:
    rows = ["| Method | Endpoint | Parameters | Description |", "| --- | --- | --- | --- |"]
    for op in operations:
        params = ", ".join(_param_label(param) for param in op["params"]) or "—"
        summary = op["summary"].replace("|", "\\|").replace("\n", " ")
        rows.append(f"| `{op['js']}` / `{op['py']}` | `{op['verb']} {op['path']}` | {params} | {summary} |")
    return "\n".join(rows)


def _example_values(platform: str, operations: list[dict[str, Any]]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Choose useful calls using only methods and parameter names in this spec."""
    by_id = {op["id"].lower(): op for op in operations}
    selected: list[tuple[dict[str, Any], dict[str, Any]]] = []

    def add(operation_id: str, values: dict[str, Any]) -> None:
        op = by_id.get(operation_id.lower())
        if op is None:
            return
        known = {str(p.get("name")) for p in op["params"]}
        selected.append((op, {k: v for k, v in values.items() if k in known}))

    if platform == "sofascore":
        add("sofascore-search", {"q": "Liverpool"})
        add("sofascore-live-events", {"sport": "football"})
    elif platform == "flashscore":
        add("flashscore-sports", {})
        add("flashscore-scores", {"sport": "football", "day_offset": 0})
    elif platform == "fotmob":
        add("fotmob-leagues", {})
        add("fotmob-search", {"term": "Premier League"})
    elif platform == "youtube":
        add("youtube-search", {"q": "science explainers", "type": "video"})
        add("youtube-video", {"id": "dQw4w9WgXcQ"})
        add("youtube-transcript", {"id": "dQw4w9WgXcQ", "format": "text"})
    return selected


def _render_examples(platform: str, config: dict[str, Any], operations: list[dict[str, Any]]) -> tuple[str, str]:
    calls = _example_values(platform, operations)
    cls = str(config["class_name"])
    module = str(config["module_name"])
    js_lines = [
        f"import {{ {cls} }} from \"../javascript/src/index.js\";",
        "",
        "const apiKey = process.env.CRAWLORA_API_KEY;",
        "if (!apiKey) throw new Error(\"Set CRAWLORA_API_KEY before running this example.\");",
        f"const client = new {cls}({{ apiKey }});",
        "",
    ]
    py_lines = [
        "import os",
        "",
        f"from {module} import {cls}",
        "",
        "api_key = os.environ.get(\"CRAWLORA_API_KEY\")",
        "if not api_key:",
        '    raise RuntimeError("Set CRAWLORA_API_KEY before running this example.")',
        "",
        f"with {cls}(api_key=api_key) as client:",
    ]
    if not calls:
        raise ValueError(f"no contract-backed example calls are configured for {platform}")
    for op, values in calls:
        js_args = ", ".join(f"{key}: {json.dumps(value)}" for key, value in values.items())
        py_args = ", ".join(f"{key}={value!r}" for key, value in values.items())
        js_lines.extend([f"  const {op['js']} = await client.{op['js']}({{ {js_args} }});", f"  console.log({json.dumps(op['js'])}, {op['js']});"])
        py_lines.extend([f"    {op['py']} = client.{op['py']}({py_args})", f"    print({op['py']!r}, {op['py']})"])
    js_lines.append("")
    py_lines.append("")
    return "\n".join(js_lines), "\n".join(py_lines)


def _render_readme_calls(
    calls: list[tuple[dict[str, Any], dict[str, Any]]],
    language: str,
    *,
    indent: str,
    asynchronous: bool = False,
) -> str:
    """Render concise package-install examples from contract-selected calls."""
    lines: list[str] = []
    for index, (operation, values) in enumerate(calls, start=1):
        method = operation["js"] if language == "javascript" else operation["py"]
        if language == "javascript":
            args = ", ".join(f"{key}: {json.dumps(value)}" for key, value in values.items())
            argument_object = "{ " + args + " }" if args else "{}"
            await_prefix = "await " if asynchronous else ""
            lines.extend(
                [
                    f"{indent}const result{index} = {await_prefix}client.{method}({argument_object});",
                    f"{indent}console.log(result{index});",
                ]
            )
        else:
            args = ", ".join(f"{key}={value!r}" for key, value in values.items())
            await_prefix = "await " if asynchronous else ""
            lines.extend(
                [
                    f"{indent}result_{index} = {await_prefix}client.{method}({args})",
                    f"{indent}print(result_{index})",
                ]
            )
    return "\n".join(lines)


def _values(config: dict[str, Any], operations: list[dict[str, Any]]) -> dict[str, str]:
    platform = str(config["platform"])
    display = str(config["display_name"])
    cls = str(config["class_name"])
    async_cls = str(config["async_class_name"])
    npm = str(config["npm_name"])
    py_name = str(config["python_name"])
    module = str(config["module_name"])
    go_module = str(config.get("golang_module_name", f"github.com/Crawlora-org/crawlora-{platform}"))
    gem_name = str(config.get("ruby_gem_name", f"crawlora-{platform}"))
    composer_name = str(config.get("php_package_name", f"crawlora/{platform}"))
    maven_group = str(config.get("maven_group_id", "net.crawlora"))
    maven_artifact = str(config.get("maven_artifact_id", f"crawlora-{platform}"))
    repo = str(config["repository"])
    version = str(config["version"])
    js_example, py_example = _render_examples(platform, config, operations)
    calls = _example_values(platform, operations)
    async_calls = calls[:1]
    if platform == "youtube":
        async_calls = [next((call for call in calls if call[0]["id"].lower() == "youtube-transcript"), calls[0])]
    transcript_formats = []
    transcript_op = next((op for op in operations if op["id"].lower() == "youtube-transcript"), None)
    if transcript_op:
        fmt_param = next((p for p in transcript_op["params"] if p.get("name") == "format"), {})
        transcript_formats = fmt_param.get("enum") or (fmt_param.get("items") or {}).get("enum") or []
    if platform == "flashscore":
        special_notes = "The Flashscore scores feed preserves its upstream delimited text response."
    elif platform == "youtube":
        formats = ", ".join(f"`{item}`" for item in transcript_formats)
        special_notes = (
            f"YouTube clients include all {len(operations)} contract operations; transcript calls can request "
            f"plain text with `format=\"text\"` (Python) or `format: \"text\"` (JavaScript). "
            f"The contract lists these transcript formats: {formats}."
        )
    else:
        special_notes = ""
    sync_schedules = {
        "sofascore": "17 3 * * *",
        "flashscore": "27 3 * * *",
        "fotmob": "37 3 * * *",
        "youtube": "47 3 * * *",
    }
    try:
        sync_cron = sync_schedules[platform]
    except KeyError as error:
        raise ValueError(f"no daily contract sync schedule is configured for {platform}") from error
    catalog = _operation_catalog(operations)
    return {
        "PLATFORM": platform,
        "DISPLAY_NAME": display,
        "CLASS_NAME": cls,
        "ASYNC_CLASS_NAME": async_cls,
        "NPM_NAME": npm,
        "PYTHON_NAME": py_name,
        "MODULE_NAME": module,
        "GO_MODULE": go_module,
        "GEM_NAME": gem_name,
        "COMPOSER_NAME": composer_name,
        "MAVEN_COORDINATE": f"{maven_group}:{maven_artifact}:{version}",
        "MAVEN_ARTIFACT": maven_artifact,
        "REPOSITORY": repo,
        "DOCS_URL": f"{repo}/blob/main/docs/usage.md",
        "JS_EXAMPLE_URL": f"{repo}/blob/main/examples/javascript.mjs",
        "PYTHON_EXAMPLE_URL": f"{repo}/blob/main/examples/python.py",
        "VERSION": version,
        "CONTRACT_REVISION": str(config.get("contract_revision") or version),
        "OPERATION_COUNT": str(len(operations)),
        "OPERATION_CATALOG": catalog,
        "JS_EXAMPLE": js_example.rstrip(),
        "PYTHON_EXAMPLE": py_example.rstrip(),
        "JS_README_CALLS": _render_readme_calls(calls, "javascript", indent="", asynchronous=True),
        "PYTHON_README_CALLS": _render_readme_calls(calls, "python", indent="    "),
        "PYTHON_ASYNC_README_CALLS": _render_readme_calls(
            async_calls,
            "python",
            indent="        ",
            asynchronous=True,
        ),
        "PLATFORM_SPECIAL_NOTES": special_notes,
        "SYNC_CRON": sync_cron,
        "SYNC_UTC_TIME": sync_cron.split()[1].zfill(2) + ":" + sync_cron.split()[0].zfill(2),
    }


def _template(template: Path, values: dict[str, str]) -> str:
    content = template.read_text(encoding="utf-8")
    for key, value in values.items():
        content = content.replace("{{" + key + "}}", value)
    return content


def _changelog(config: dict[str, Any], template: Path, values: dict[str, str]) -> str:
    """Render optional changelog history in caller-supplied newest-first order."""
    releases = config.get("releases")
    if not releases:
        return _template(template, values)
    if not isinstance(releases, list):
        raise ValueError("config['releases'] must be a list ordered newest first")

    sections: list[str] = []
    seen_versions: set[str] = set()
    for release in releases:
        if not isinstance(release, dict):
            raise ValueError("each config['releases'] entry must be an object")
        version = str(release.get("version") or "").strip()
        date = str(release.get("date") or "").strip()
        changes = release.get("changes")
        if not version or not date or not changes:
            raise ValueError("each release requires version, date, and at least one change")
        if version in seen_versions:
            raise ValueError(f"duplicate changelog release version: {version}")
        seen_versions.add(version)
        if isinstance(changes, str):
            changes = [changes]
        if not isinstance(changes, list) or any(not isinstance(change, str) or not change.strip() for change in changes):
            raise ValueError(f"changes for release {version} must be nonempty strings")
        bullets = "\n".join(f"- {change.strip()}" for change in changes)
        sections.append(f"## {version} — {date}\n\n{bullets}")
    return "# Changelog\n\n" + "\n\n".join(sections)


def emit(root: Path, config: dict[str, Any], spec: dict[str, Any], assets: Path) -> None:
    """Write public-facing docs, runnable examples, and release workflows."""
    root = Path(root)
    assets = Path(assets)
    platform = str(config["platform"])
    canonical_names = _canonical_method_names(spec, assets)
    operations = _operations(spec, platform, canonical_names)
    values = _values(config, operations)
    candidates = (
        assets / "templates" / "documentation",
        assets / "documentation",
        assets,
        Path(__file__).parent / "templates" / "documentation",
    )
    template_root = next(
        (candidate for candidate in candidates if (candidate / "README.md.tmpl").is_file()),
        candidates[-1],
    )

    template_map = {
        "README.md": "README.md.tmpl",
        "javascript/README.md": "javascript-README.md.tmpl",
        "python/README.md": "python-README.md.tmpl",
        "CHANGELOG.md": "CHANGELOG.md.tmpl",
        "LICENSE": "LICENSE.tmpl",
        "javascript/LICENSE": "LICENSE.tmpl",
        "python/LICENSE": "LICENSE.tmpl",
        ".gitignore": "gitignore.tmpl",
        "docs/usage.md": "usage.md.tmpl",
        ".github/workflows/ci.yml": "ci.yml.tmpl",
        ".github/workflows/release.yml": "release.yml.tmpl",
        ".github/workflows/sync-contract.yml": "sync-contract.yml.tmpl",
        "examples/javascript.mjs": "javascript-example.mjs.tmpl",
        "examples/python.py": "python-example.py.tmpl",
    }
    for output, template_name in template_map.items():
        target = root / output
        target.parent.mkdir(parents=True, exist_ok=True)
        if template_name == "javascript-example.mjs.tmpl":
            content = values["JS_EXAMPLE"] + "\n"
        elif template_name == "python-example.py.tmpl":
            content = values["PYTHON_EXAMPLE"] + "\n"
        elif output == "CHANGELOG.md":
            content = _changelog(config, template_root / template_name, values)
        else:
            content = _template(template_root / template_name, values)
        if re.search(r"\{\{[A-Z][A-Z_]*\}\}", content):
            raise ValueError(f"unresolved documentation template value in {template_name}")
        target.write_text(content.rstrip() + "\n", encoding="utf-8")
