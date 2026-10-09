"""Emit a small stdlib Ruby gem for Crawlora's hosted platform API."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .utm import crawlora_url


def _class_name(platform: str) -> str:
    return "".join(part.capitalize() for part in re.split(r"[^a-zA-Z0-9]+", platform))


def _replace(template: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def _example_call(platform: str, model: Any) -> tuple[str, dict[str, Any]]:
    """Choose a contract-backed searchable operation and representative params."""
    operation_ids = list(model.meta)
    operation_id = next((item for item in operation_ids if item.endswith("-search")), operation_ids[0])
    preferred = {
        "sofascore": "Liverpool",
        "flashscore": "football",
        "fotmob": "Premier League",
        "youtube": "science explainers",
    }.get(platform, "sample")
    params: dict[str, Any] = {}
    for param in model.meta[operation_id]["params"]:
        location = param.get("in")
        name = str(param.get("name", ""))
        if location not in {"path", "query"} or name.lower() == "x-api-key":
            continue
        common_search = name.lower() in {"q", "query", "term", "search"}
        if not param.get("required") and not common_search:
            continue
        enum = param.get("enum") or param.get("items", {}).get("enum") or []
        if enum:
            value: Any = enum[0]
        elif param.get("type") == "integer":
            value = 1
        elif param.get("type") == "number":
            value = 1.0
        elif param.get("type") == "boolean":
            value = True
        elif param.get("type") == "array":
            value = [preferred]
        elif location == "path":
            value = "sample-id"
        else:
            value = preferred if common_search else "sample"
        params[name] = value
    return operation_id, params


def _operations(spec: dict[str, Any], model: Any) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    source = {
        operation.get("operationId"): operation
        for methods in spec.get("paths", {}).values()
        for operation in methods.values()
        if isinstance(operation, dict) and operation.get("operationId")
    }
    operations: dict[str, Any] = {}
    aliases: list[tuple[str, str]] = []
    for _group, entries in model.groups.items():
        aliases.extend((method, operation_id) for method, operation_id in entries.items())
    names = [method for method, _ in aliases]
    if len(names) != len(set(names)):
        raise ValueError("platform operation aliases must be unique")
    for operation_id, parsed in model.operations.items():
        if parsed["method"] != "GET":
            raise ValueError(f"focused client supports GET operations only: {operation_id}")
        raw = source[operation_id]
        params = model.meta[operation_id]["params"]
        operations[operation_id] = {
            "id": operation_id,
            "method": parsed["method"],
            "path": parsed["path"],
            "pathParams": parsed.get("pathParams", []),
            "queryParams": parsed.get("queryParams", []),
            "params": params,
            "produces": raw.get("produces", []),
            "security": parsed.get("security", []),
        }
    return operations, aliases


def emit(root: Path, config: dict[str, Any], spec: dict[str, Any], assets: Path) -> None:
    """Write/regenerate the focused gem in ``root/ruby``."""
    from .python import _load_helpers

    core, generator = _load_helpers(Path(assets))
    model = core.build_model(spec, generator.POLICY)
    operations, aliases = _operations(spec, model)
    platform = config["platform"]
    example_operation, example_params = _example_call(platform, model)
    ruby = config.get("ruby", {})
    if not isinstance(ruby, dict):
        ruby = {}
    class_name = ruby.get("class_name", _class_name(platform))
    gem_name = ruby.get("gem_name", ruby.get("package_name", config.get("ruby_gem_name", "crawlora-" + platform)))
    version = ruby.get("version", config.get("ruby_version", config.get("version", "0.1.4")))
    repo = config.get("repository", "https://github.com/Crawlora-org/crawlora-" + platform)
    dependencies = ruby.get("dependencies", config.get("ruby_dependencies", {}))
    if isinstance(dependencies, dict):
        dependency_lines = "\n".join(
            f"  spec.add_runtime_dependency({name!r}, {str(version)!r})" for name, version in dependencies.items()
        )
    elif isinstance(dependencies, list):
        dependency_lines = "\n".join(
            f"  spec.add_runtime_dependency({str(item)!r})" for item in dependencies
        )
    else:
        raise ValueError("Ruby dependencies must be a map or list")
    package = Path(root) / "ruby"
    lib = package / "lib" / "crawlora" / platform
    lib.mkdir(parents=True, exist_ok=True)
    template_root = Path(__file__).resolve().parent / "templates" / "ruby"
    values = {
        "PLATFORM": platform,
        "DISPLAY_NAME": config.get("display_name", platform.title()),
        "CLASS_NAME": class_name,
        "GEM_NAME": gem_name,
        "VERSION": version,
        "REPOSITORY": repo,
        "HOMEPAGE_URL": crawlora_url(source="rubygems", platform=platform, surface="ruby", destination="homepage"),
        "DOCUMENTATION_URL": crawlora_url(source="rubygems", platform=platform, surface="ruby", destination="api-docs", path="/docs"),
        "CONTRACT_REVISION": str(config.get("contract_revision", "")),
        "OPERATION_JSON": json.dumps(operations, ensure_ascii=False, sort_keys=True),
        "OPERATION_IDS_JSON": json.dumps(sorted(operations)),
        "OPERATION_COUNT": str(len(operations)),
        "DEPENDENCIES": dependency_lines,
        "DIRECT_METHODS": "\n".join(
            f"      define_method({method!r}) do |**params|\n"
            "        response_type = params.delete(:response_type) || params.delete(:_response_type) || :auto\n"
            f"        request({operation_id!r}, params, response_type: response_type)\n"
            "      end"
            for method, operation_id in aliases
        ),
        "EXAMPLE_OPERATION_JSON": json.dumps(example_operation),
        "EXAMPLE_PARAMS_JSON": json.dumps(json.dumps(example_params, ensure_ascii=False)),
    }
    for source, target in (("client.rb.tpl", lib / "client.rb"), ("version.rb.tpl", lib / "version.rb")):
        target.write_text(_replace((template_root / source).read_text(encoding="utf-8"), values), encoding="utf-8")
    (package / "lib" / "crawlora" / f"{platform}.rb").write_text(
        _replace((template_root / "entry.rb.tpl").read_text(encoding="utf-8"), values), encoding="utf-8"
    )
    gemspec = _replace((template_root / "gem.gemspec.tpl").read_text(encoding="utf-8"), values)
    (package / f"{gem_name}.gemspec").write_text(gemspec, encoding="utf-8")
    (package / "README.md").write_text(
        _replace((template_root / "README.md.tpl").read_text(encoding="utf-8"), values), encoding="utf-8"
    )
    changelog = ruby.get("changelog", ruby.get("history", config.get("ruby_changelog", config.get("ruby_history"))))
    if changelog:
        history_text = "\n".join(changelog) if isinstance(changelog, list) else str(changelog)
        (package / "CHANGELOG.md").write_text(history_text.rstrip() + "\n", encoding="utf-8")
    else:
        (package / "CHANGELOG.md").write_text(
            f"# Changelog\n\n## {version}\n\n- Initial focused {values['DISPLAY_NAME']} Ruby client for Crawlora's hosted API.\n",
            encoding="utf-8",
        )
    readme = ruby.get("readme", config.get("ruby_readme"))
    if readme:
        (package / "README.md").write_text(str(readme).rstrip() + "\n", encoding="utf-8")
    (package / "lib" / "crawlora" / platform / "operations.json").write_text(
        json.dumps({"platform": platform, "operationCount": len(operations), "operationIds": sorted(operations), "methods": dict(aliases), "operations": operations}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (package / "Gemfile").write_text("source 'https://rubygems.org'\n\ngemspec\n", encoding="utf-8")
    (package / ".ruby-version").write_text("3.2.0\n", encoding="utf-8")
    (package / "LICENSE").write_text((template_root / "LICENSE.tpl").read_text(encoding="utf-8"), encoding="utf-8")
    test_values = {
        **values,
        "EXAMPLE_OPERATION_JSON": json.dumps(example_operation),
        "EXAMPLE_PARAMS_JSON": json.dumps(json.dumps(example_params, ensure_ascii=False)),
    }
    test_dir = package / "test"
    test_dir.mkdir(exist_ok=True)
    (test_dir / "test_client.rb").write_text(
        _replace((template_root / "test_client.rb.tpl").read_text(encoding="utf-8"), test_values),
        encoding="utf-8",
    )
