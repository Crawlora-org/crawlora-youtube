"""Synchronize one focused client from the current public Swagger contract."""

from __future__ import annotations

import argparse
import copy
from datetime import date as current_date
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "platformsdk"

from .generate import regenerate
from .spec import HTTP_METHODS, PLATFORMS, dumps, refs, select


DEFAULT_SOURCE = "https://api.crawlora.net/swagger/doc.json"
MAX_SOURCE_BYTES = 32 * 1024 * 1024
SOURCE_TIMEOUT_SECONDS = 45
USER_AGENT = "Crawlora-Platform-Sync/1.0"
_SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
_METHODS = HTTP_METHODS
_HIDDEN_SEGMENTS = {"admin", "internal", "private"}
_AUTH_DEFINITIONS = {
    "ApiKeyAuth": {"type": "apiKey", "name": "x-api-key", "in": "header"},
    "JWTAuth": {"type": "apiKey", "name": "Authorization", "in": "header"},
}
_WIRE_TOP_LEVEL = ("host", "basePath", "schemes", "consumes", "produces", "security")
_RUNTIME_URL_FIELDS = ("host", "basePath", "schemes")
_CLIENT_RESERVED_NAMES = {
    # JavaScript inherited client methods and instance state.
    "constructor", "request", "operation", "paginate", "paginateItems", "close",
    "apiKey", "jwtToken", "baseUrl", "timeout", "retries", "retryDelay", "maxRetryDelay",
    "retryStatuses", "isRetryable", "onRetry", "requestId", "idempotencyKeys", "logger",
    "beforeRequest", "afterResponse", "limiter", "headers", "userAgent", "fetch",
    # Python sync/async client methods and instance state.
    "__init__", "__enter__", "__exit__", "__aenter__", "__aexit__", "close", "aclose",
    "request", "operation", "paginate", "paginate_items", "sync_client", "uses_httpx",
    "api_key", "jwt_token", "base_url", "timeout", "retries", "retry_delay", "max_retry_delay",
    "retry_statuses", "retry_predicate", "on_retry", "request_id", "idempotency_keys", "rate_limit",
    "max_concurrency", "_rate_limiter", "logger", "before_request", "after_response", "headers",
    "user_agent", "_transport", "_client", "_owns_client",
}


def read_source(*, spec_path: Path | None = None, source_url: str = DEFAULT_SOURCE) -> tuple[bytes, dict]:
    """Read bounded JSON from a local file or the public source URL."""
    if spec_path is not None:
        try:
            with spec_path.open("rb") as stream:
                raw = stream.read(MAX_SOURCE_BYTES + 1)
        except OSError as exc:
            raise ValueError(f"cannot read spec file {spec_path}: {exc}") from exc
    else:
        request = Request(source_url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with urlopen(request, timeout=SOURCE_TIMEOUT_SECONDS) as response:
                length = response.headers.get("Content-Length")
                if length and int(length) > MAX_SOURCE_BYTES:
                    raise ValueError(f"source exceeds {MAX_SOURCE_BYTES} bytes")
                raw = response.read(MAX_SOURCE_BYTES + 1)
        except HTTPError as exc:
            raise ValueError(f"source returned HTTP {exc.code} {exc.reason}") from exc
        except URLError as exc:
            raise ValueError(f"source request failed: {exc.reason}") from exc
        except TimeoutError as exc:
            raise ValueError(f"source request timed out after {SOURCE_TIMEOUT_SECONDS}s") from exc
    if len(raw) > MAX_SOURCE_BYTES:
        raise ValueError(f"source exceeds {MAX_SOURCE_BYTES} bytes")
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"source is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("source JSON must be an object")
    return raw, value


def _deprecated(operation: dict) -> bool:
    if operation.get("deprecated") is True:
        return True
    return any("deprecated" in str(operation.get(key, "")).lower()
               for key in ("operationId", "summary", "description"))


def _hidden_path(path: str) -> bool:
    return any(segment.lower() in _HIDDEN_SEGMENTS for segment in path.split("/"))


def normalize_public_spec(source: dict, platform: str) -> dict:
    """Mirror public Swagger normalization and remove non-public platform ops."""
    if source.get("swagger") != "2.0":
        raise ValueError("expected a Swagger 2 public contract")
    raw_paths = source.get("paths")
    if not isinstance(raw_paths, dict):
        raise ValueError("swagger paths must be an object")

    public_paths: dict = {}
    for path, path_item in raw_paths.items():
        if not isinstance(path, str) or not isinstance(path_item, dict):
            raise ValueError(f"swagger path {path!r} must be an object")
        if _hidden_path(path):
            continue
        for method, original in path_item.items():
            if method not in _METHODS:
                continue
            if not isinstance(original, dict):
                raise ValueError(f"swagger operation {method.upper()} {path} must be an object")
            if _deprecated(original):
                continue
            operation = copy.deepcopy(original)
            inferred_security: str | None = None
            parameters = operation.get("parameters")
            if isinstance(parameters, list):
                filtered = []
                for parameter in parameters:
                    if not isinstance(parameter, dict):
                        filtered.append(parameter)
                        continue
                    if parameter.get("in") == "header":
                        header_name = str(parameter.get("name", "")).lower()
                        if header_name == "x-api-key":
                            inferred_security = "ApiKeyAuth"
                            continue
                        if header_name == "authorization":
                            inferred_security = "JWTAuth"
                            continue
                    filtered.append(parameter)
                if filtered:
                    operation["parameters"] = filtered
                else:
                    operation.pop("parameters", None)
            if "security" not in operation and inferred_security:
                operation["security"] = [{inferred_security: []}]
            if "JWTAuth" in _security_names(operation, source):
                continue
            if _hidden_path(path):
                continue
            public_paths.setdefault(path, {})[method] = operation

    result = {key: copy.deepcopy(value) for key, value in source.items() if key != "paths"}
    result["paths"] = public_paths
    # Match pkg/sdkopenapi/export.go, which publishes stable definitions for
    # both auth schemes regardless of which operations use them.
    result["securityDefinitions"] = copy.deepcopy(_AUTH_DEFINITIONS)
    return select(result, platform)


def _security_names(operation: dict, spec: dict) -> set[str]:
    security = operation.get("security", spec.get("security", []))
    if not isinstance(security, list):
        return set()
    return {str(name) for entry in security if isinstance(entry, dict) for name in entry}


def _comparison_value(selected: dict) -> dict:
    value = copy.deepcopy(selected)
    info = value.get("info")
    if isinstance(info, dict):
        info.pop("version", None)
    return value


def _contract_hash(selected: dict) -> str:
    digest = hashlib.sha256(dumps(selected).encode("utf-8")).hexdigest()
    return "sha256:" + digest


def _validate_client_aliases(selected: dict) -> None:
    """Fail closed when generator-derived facade aliases shadow client state."""
    from .documentation import _canonical_method_names

    aliases = _canonical_method_names(selected, Path(__file__).resolve().parent / "vendor")
    collisions = sorted(
        (language, operation_id, method_name)
        for language, by_operation in aliases.items()
        for operation_id, method_name in by_operation.items()
        if method_name in _CLIENT_RESERVED_NAMES
    )
    if collisions:
        language, operation_id, method_name = collisions[0]
        raise ValueError(
            f"unsupported collisionalias {method_name!r} for {operation_id} ({language} client facade)"
        )


def _operation_entries(selected: dict) -> dict[str, tuple[dict, dict]]:
    """Map each ID to its operation and the schema closure reachable from it."""
    entries: dict[str, tuple[dict, dict]] = {}
    sections = ("definitions", "parameters", "responses")
    for path, path_item in selected["paths"].items():
        for method, operation in path_item.items():
            if method not in _METHODS:
                continue
            identifier = operation["operationId"]
            queue = list(refs(operation))
            closure: dict[str, dict] = {}
            while queue:
                ref = queue.pop()
                tokens = ref.split("/")
                if len(tokens) != 3 or tokens[0] != "#" or tokens[1] not in sections:
                    continue  # select() has already rejected unsupported refs.
                section, encoded = tokens[1:]
                name = encoded.replace("~1", "/").replace("~0", "~")
                key = f"{section}/{name}"
                if key in closure:
                    continue
                node = selected[section][name]
                closure[key] = node
                queue.extend(refs(node))
            entries[identifier] = ({"path": path, "method": method, "operation": operation}, closure)
    return entries


def _semantic_version(value: object) -> tuple[int, int, int, str | None, str | None]:
    if not isinstance(value, str) or not (match := _SEMVER.fullmatch(value)):
        raise ValueError(f"invalid semantic version: {value!r}")
    major, minor, patch = (int(match.group(i)) for i in range(1, 4))
    return major, minor, patch, match.group(4), match.group(5)


def _bump_version(current: str, *, minor: bool) -> str:
    major, minor_value, patch, prerelease, _build = _semantic_version(current)
    if prerelease:
        raise ValueError("cannot sync from a prerelease version")
    if minor:
        return f"{major}.{minor_value + 1}.0"
    return f"{major}.{minor_value}.{patch + 1}"


def _operation_wire_value(entry: tuple[dict, dict]) -> dict:
    operation, closure = entry
    return {"operation": operation, "schemas": closure}


def _strip_schema_docs(value):
    if not isinstance(value, dict):
        return value
    result = {}
    for key, child in value.items():
        if key in {"description", "title", "example", "examples", "externalDocs"}:
            continue
        if key in {"properties", "patternProperties", "definitions"} and isinstance(child, dict):
            # These are schema maps. Keep every property name, even when it is
            # literally "title", "description", or "example".
            result[key] = {name: _strip_schema_docs(schema) for name, schema in child.items()}
        elif key in {"items", "additionalProperties", "not"} and isinstance(child, dict):
            result[key] = _strip_schema_docs(child)
        elif key in {"allOf", "anyOf", "oneOf"} and isinstance(child, list):
            result[key] = [_strip_schema_docs(schema) for schema in child]
        else:
            result[key] = child
    return result


def _strip_parameter_docs(value):
    if not isinstance(value, dict):
        return value
    return {
        key: _strip_schema_docs(child) if key in {"schema", "items"} else child
        for key, child in value.items()
        if key not in {"description", "example", "examples"}
    }


def _strip_response_docs(value):
    if not isinstance(value, dict):
        return value
    result = {}
    for key, child in value.items():
        if key in {"description", "examples", "externalDocs"}:
            continue
        if key == "schema":
            result[key] = _strip_schema_docs(child)
        elif key == "headers" and isinstance(child, dict):
            result[key] = {name: _strip_parameter_docs(header) for name, header in child.items()}
        else:
            result[key] = child
    return result


def _strip_documentation(value):
    """Remove Swagger documentation while preserving JSON Schema map keys."""
    entry = value.get("operation", {})
    operation = entry.get("operation", {})
    schemas = value.get("schemas", {})
    clean_operation = {}
    for key, child in operation.items():
        if key in {"summary", "description", "externalDocs"}:
            continue
        if key == "parameters" and isinstance(child, list):
            clean_operation[key] = [_strip_parameter_docs(param) for param in child]
        elif key == "responses" and isinstance(child, dict):
            clean_operation[key] = {status: _strip_response_docs(response) for status, response in child.items()}
        else:
            clean_operation[key] = child
    clean_schemas = {}
    for key, node in schemas.items():
        section = key.split("/", 1)[0]
        if section == "definitions":
            clean_schemas[key] = _strip_schema_docs(node)
        elif section == "parameters":
            clean_schemas[key] = _strip_parameter_docs(node)
        elif section == "responses":
            clean_schemas[key] = _strip_response_docs(node)
        else:
            clean_schemas[key] = node
    clean_entry = {key: child for key, child in entry.items() if key != "operation"}
    clean_entry["operation"] = clean_operation
    return {"operation": clean_entry, "schemas": clean_schemas}


def _operation_changes(previous: dict, current: dict) -> tuple[list[str], list[str], list[str], bool]:
    old_entries = _operation_entries(previous)
    new_entries = _operation_entries(current)
    old_ids, new_ids = set(old_entries), set(new_entries)
    added = sorted(new_ids - old_ids)
    removed = sorted(old_ids - new_ids)
    modified = sorted(
        identifier for identifier in old_ids & new_ids
        if dumps(_operation_wire_value(old_entries[identifier])) != dumps(_operation_wire_value(new_entries[identifier]))
    )
    old_wire = tuple(previous.get(key) for key in _WIRE_TOP_LEVEL)
    new_wire = tuple(current.get(key) for key in _WIRE_TOP_LEVEL)
    return added, removed, modified, old_wire != new_wire


def _history(config: dict, changelog: str, version: str, date: str, changes: list[str]) -> list[dict]:
    existing = config.get("releases")
    if existing is not None:
        if not isinstance(existing, list):
            raise ValueError("config['releases'] must be a list ordered newest first")
        history = copy.deepcopy(existing)
    else:
        history = []
        sections = re.split(r"(?m)^##\s+", changelog)
        for section in sections[1:]:
            lines = section.strip().splitlines()
            if not lines:
                continue
            header = lines[0]
            match = re.fullmatch(r"(.+?)\s+[—–-]\s+(\d{4}-\d{2}-\d{2})", header)
            if not match:
                continue
            old_version, old_date = match.groups()
            bullets = [line.strip()[2:].strip() for line in lines[1:] if line.strip().startswith("- ")]
            if bullets:
                history.append({"version": old_version, "date": old_date, "changes": bullets})
    if history and str(history[0].get("version", "")) == version:
        history.pop(0)
    return [{"version": version, "date": date, "changes": changes}, *history]


def _change_descriptions(added: list[str], modified: list[str], wire_changed: bool) -> list[str]:
    lines = []
    if added:
        lines.append("Added operations: " + ", ".join(added) + ".")
    if modified:
        lines.append("Updated operation contracts: " + ", ".join(modified) + ".")
    if wire_changed:
        lines.append("Updated the API host or base URL metadata.")
    if not lines:
        lines.append("Updated contract descriptions or metadata.")
    return lines


def _report_path(path: Path | None, report: dict) -> None:
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _github_output(path: Path | None, report: dict) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as output:
        for key in ("changed", "version", "contract_revision"):
            output.write(f"{key}={str(report[key]).lower() if isinstance(report[key], bool) else report[key]}\n")


def _stage_and_generate(root: Path, config: dict, selected: dict) -> None:
    """Generate into a sibling copy, then replace changed files with rollback."""
    root = root.resolve()
    with tempfile.TemporaryDirectory(prefix="platform-sync-") as temporary:
        stage = Path(temporary) / "root"
        shutil.copytree(root, stage, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".venv", "node_modules"))
        (stage / "platform.json").write_text(dumps(config), encoding="utf-8")
        (stage / "openapi/public.json").write_text(dumps(selected), encoding="utf-8")
        regenerate(stage)

        replacements: dict[Path, bytes] = {}
        for staged_file in stage.rglob("*"):
            if not staged_file.is_file():
                continue
            relative = staged_file.relative_to(stage)
            actual = root / relative
            payload = staged_file.read_bytes()
            if not actual.exists() or actual.read_bytes() != payload:
                replacements[actual] = payload
        previous = {
            path: (path.read_bytes(), stat.S_IMODE(path.stat().st_mode)) if path.exists() else None
            for path in replacements
        }
        missing_dirs = {
            parent
            for path in replacements
            for parent in path.parents
            if parent != root and not parent.exists()
        }
        written: list[Path] = []
        try:
            for path, payload in replacements.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                temp_path = None
                try:
                    with tempfile.NamedTemporaryFile(
                        mode="wb", prefix=f".{path.name}.sync-", dir=path.parent, delete=False
                    ) as temporary_file:
                        temp_path = Path(temporary_file.name)
                        temporary_file.write(payload)
                        temporary_file.flush()
                        os.fsync(temporary_file.fileno())
                    original = previous[path]
                    os.chmod(temp_path, original[1] if original else 0o644)
                    os.replace(temp_path, path)
                finally:
                    if temp_path is not None:
                        temp_path.unlink(missing_ok=True)
                written.append(path)
        except OSError as exc:
            for path in reversed(written):
                original_state = previous[path]
                if original_state is None:
                    path.unlink(missing_ok=True)
                else:
                    original, mode = original_state
                    path.write_bytes(original)
                    os.chmod(path, mode)
            for directory in sorted(missing_dirs, key=lambda item: len(item.parts), reverse=True):
                try:
                    directory.rmdir()
                except OSError:
                    pass
            raise ValueError(f"could not commit generated files; previous files restored: {exc}") from exc


def synchronize(
    root: Path,
    *,
    platform: str | None = None,
    spec_path: Path | None = None,
    source_url: str = DEFAULT_SOURCE,
    apply: bool = False,
    date: str | None = None,
) -> dict:
    """Compare a raw contract with a focused repo and optionally apply changes."""
    root = Path(root).resolve()
    try:
        config = json.loads((root / "platform.json").read_text(encoding="utf-8"))
        previous_selected_raw = json.loads((root / "openapi/public.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read existing platform contract: {exc}") from exc
    if not isinstance(config, dict) or not isinstance(previous_selected_raw, dict):
        raise ValueError("platform.json and openapi/public.json must contain JSON objects")
    platform = platform or config.get("platform")
    if platform not in PLATFORMS:
        raise ValueError(f"unsupported platform: {platform}")
    if config.get("platform") != platform:
        raise ValueError(f"root platform {config.get('platform')!r} does not match {platform!r}")
    previous_version = config.get("version")
    _semantic_version(previous_version)
    if date is not None and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise ValueError(f"date must be YYYY-MM-DD: {date!r}")
    if date is not None:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError(f"date must be a valid YYYY-MM-DD date: {date!r}") from exc

    raw, source = read_source(spec_path=spec_path, source_url=source_url)
    selected = normalize_public_spec(source, platform)
    _validate_client_aliases(selected)
    previous_selected = select(previous_selected_raw, platform)
    selected_info = selected.setdefault("info", {})
    previous_info = previous_selected.get("info", {})
    if not isinstance(selected_info, dict) or not isinstance(previous_info, dict):
        raise ValueError("swagger info must be an object")
    if "version" in previous_info:
        selected_info["version"] = previous_info["version"]
    else:
        selected_info.pop("version", None)
    previous_comparison = _comparison_value(previous_selected)
    current_comparison = _comparison_value(selected)
    changed = dumps(previous_comparison) != dumps(current_comparison)
    revision = _contract_hash(selected)
    source_hash = hashlib.sha256(raw).hexdigest()
    added, removed, modified, wire_changed = _operation_changes(previous_selected, selected)
    if any(previous_selected.get(key) != selected.get(key) for key in _RUNTIME_URL_FIELDS):
        raise ValueError(
            "runtime transport review required: source host/basePath/schemes changed; "
            "the pinned client's default base URL is not regenerated from Swagger metadata"
        )
    if removed:
        raise ValueError("platform operations were removed; refusing automatic sync: " + ", ".join(removed))
    version = previous_version
    report = {
        "changed": changed,
        "platform": platform,
        "previous_version": previous_version,
        "version": version,
        "added": added,
        "removed": removed,
        "modified": modified,
        "contract_revision": revision if changed else (config.get("contract_revision") or _contract_hash(previous_selected)),
        "source_contract_sha256": source_hash,
    }
    if not changed:
        return report

    # Existing operation/schema changes that affect generated calls or payload
    # types need a minor release. Description and display metadata changes are
    # patch releases even though they still change the selected contract hash.
    old_entries = _operation_entries(previous_selected)
    new_entries = _operation_entries(selected)
    operation_wire_changed = any(
        dumps(_strip_documentation(_operation_wire_value(old_entries[identifier])))
        != dumps(_strip_documentation(_operation_wire_value(new_entries[identifier])))
        for identifier in set(old_entries) & set(new_entries)
    )
    minor = bool(added or operation_wire_changed or wire_changed)
    version = _bump_version(previous_version, minor=minor)
    report["version"] = version
    if not apply:
        return report

    release_date = date or current_date.today().isoformat()
    changelog_path = root / "CHANGELOG.md"
    changelog = changelog_path.read_text(encoding="utf-8") if changelog_path.exists() else ""
    next_config = copy.deepcopy(config)
    next_config["version"] = version
    next_config["contract_revision"] = revision
    next_config["source_contract_sha256"] = source_hash
    next_config["releases"] = _history(
        config, changelog, version, release_date,
        _change_descriptions(added, modified, wire_changed),
    )
    _stage_and_generate(root, next_config, selected)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--platform", choices=sorted(PLATFORMS))
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--spec", type=Path)
    source.add_argument("--source", default=DEFAULT_SOURCE, help="raw Swagger URL (default: %(default)s)")
    parser.add_argument("--apply", action="store_true", help="write selected contract and regenerate clients")
    parser.add_argument("--date", help="release date in YYYY-MM-DD form")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = synchronize(args.root, platform=args.platform, spec_path=args.spec,
                             source_url=args.source, apply=args.apply, date=args.date)
        _report_path(args.report, report)
        _github_output(args.github_output, report)
    except (ValueError, OSError) as exc:
        print(f"sync_contract: {exc}", file=sys.stderr)
        return 1
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.report is None:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
