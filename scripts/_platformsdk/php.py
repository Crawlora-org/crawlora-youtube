"""Emit a small standalone PHP package for Crawlora's hosted platform API."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .utm import crawlora_url

from .ruby import _example_call, _operations, _replace


def _class_name(platform: str) -> str:
    return "".join(part.capitalize() for part in re.split(r"[^a-zA-Z0-9]+", platform))


def _php_value(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"
    if isinstance(value, list):
        return "[" + ", ".join(_php_value(item) for item in value) + "]"
    if isinstance(value, dict):
        return "[" + ", ".join(f"{_php_value(str(key))} => {_php_value(item)}" for key, item in value.items()) + "]"
    return str(value)


def emit(root: Path, config: dict[str, Any], spec: dict[str, Any], assets: Path) -> None:
    """Write/regenerate a dependency-light Composer package in ``root/php``."""
    from .python import _load_helpers

    core, generator = _load_helpers(Path(assets))
    model = core.build_model(spec, generator.POLICY)
    operations, aliases = _operations(spec, model)
    platform = config["platform"]
    example_operation, example_params = _example_call(platform, model)
    php = config.get("php", {})
    if not isinstance(php, dict):
        php = {}
    class_name = php.get("class_name", _class_name(platform))
    package_name = php.get("package_name", config.get("php_package_name", "crawlora/" + platform))
    version = php.get("version", config.get("php_version", config.get("version", "0.1.4")))
    repo = config.get("repository", "https://github.com/Crawlora-org/crawlora-" + platform)
    package = Path(root) / "php"
    src = package / "src" / "Crawlora" / class_name
    src.mkdir(parents=True, exist_ok=True)
    templates = Path(__file__).resolve().parent / "templates" / "php"
    values = {
        "PLATFORM": platform,
        "DISPLAY_NAME": config.get("display_name", platform.title()),
        "CLASS_NAME": class_name,
        "PACKAGE_NAME": package_name,
        "VERSION": version,
        "REPOSITORY": repo,
        "HOMEPAGE_URL": crawlora_url(source="packagist", platform=platform, surface="php", destination="homepage"),
        "DOCUMENTATION_URL": crawlora_url(source="packagist", platform=platform, surface="php", destination="api-docs", path="/docs"),
        "CONTRACT_REVISION": str(config.get("contract_revision", "")),
        "OPERATION_JSON": json.dumps(operations, ensure_ascii=False, sort_keys=True),
        "OPERATION_IDS_JSON": json.dumps(sorted(operations)),
        "OPERATION_COUNT": str(len(operations)),
        "OPERATION_IDS_PHP": "[" + ", ".join(json.dumps(item) for item in sorted(operations)) + "]",
        "DIRECT_METHODS": "\n".join(
            "    public function " + method + "(mixed ...$params): mixed\n    {\n"
            "        $responseType = $params['_response_type'] ?? $params['response_type'] ?? 'auto';\n"
            "        unset($params['_response_type'], $params['response_type']);\n"
            f"        return $this->request({json.dumps(operation_id)}, $params, $responseType);\n"
            "    }"
            for method, operation_id in aliases
        ),
        "DEPENDENCIES_JSON": json.dumps(php.get("dependencies", config.get("php_dependencies", {})), ensure_ascii=False),
        "EXAMPLE_OPERATION_JSON": json.dumps(example_operation),
        "EXAMPLE_PARAMS_PHP": _php_value(example_params),
    }
    (src / "Client.php").write_text(_replace((templates / "Client.php.tpl").read_text(encoding="utf-8"), values), encoding="utf-8")
    composer = _replace((templates / "composer.json.tpl").read_text(encoding="utf-8"), values)
    composer_data = json.loads(composer)
    deps = php.get("dependencies", config.get("php_dependencies", {}))
    if isinstance(deps, dict):
        composer_data["require"].update(deps)
    elif isinstance(deps, list):
        composer_data["require"].update({item: "*" for item in deps})
    (package / "composer.json").write_text(json.dumps(composer_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    root_composer = json.loads(json.dumps(composer_data))
    namespace = f"Crawlora\\{class_name}\\"
    root_composer["autoload"]["psr-4"][namespace] = f"php/src/Crawlora/{class_name}/"
    root_composer["autoload-dev"]["psr-4"][f"Crawlora\\{class_name}\\Tests\\"] = "php/tests/"
    root_composer["scripts"]["test"] = "php php/tests/client_test.php"
    root_composer["homepage"] = values["HOMEPAGE_URL"]
    (Path(root) / "composer.json").write_text(
        json.dumps(root_composer, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (package / "tests").mkdir(exist_ok=True)
    test_template = (templates / "client_test.php.tpl").read_text(encoding="utf-8")
    test_values = {
        **values,
        "EXAMPLE_OPERATION_JSON": json.dumps(example_operation),
        "EXAMPLE_PARAMS_PHP": _php_value(example_params),
    }
    (package / "tests" / "client_test.php").write_text(_replace(test_template, test_values), encoding="utf-8")
    readme = php.get("readme", config.get("php_readme"))
    readme_text = str(readme) if readme else _replace((templates / "README.md.tpl").read_text(encoding="utf-8"), values)
    (package / "README.md").write_text(readme_text.rstrip() + "\n", encoding="utf-8")
    (package / "LICENSE").write_text((templates / "LICENSE.tpl").read_text(encoding="utf-8"), encoding="utf-8")
    history = php.get("changelog", php.get("history", config.get("php_changelog", config.get("php_history"))))
    if history:
        history_text = "\n".join(history) if isinstance(history, list) else str(history)
    else:
        history_text = f"# Changelog\n\n## {version}\n\n- Initial focused {values['DISPLAY_NAME']} PHP client for Crawlora's hosted API.\n"
    (package / "CHANGELOG.md").write_text(history_text.rstrip() + "\n", encoding="utf-8")
    (package / "src" / "Crawlora" / class_name / "operations.json").write_text(
        json.dumps({"platform": platform, "operationCount": len(operations), "operationIds": sorted(operations), "methods": dict(aliases), "operations": operations}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
