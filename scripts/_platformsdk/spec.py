"""Select one platform and its complete schema dependency graph."""

from __future__ import annotations

import copy
import json
from collections.abc import Iterator

PLATFORMS = {
    "sofascore": ("SofaScore", "SofascoreClient"),
    "flashscore": ("Flashscore", "FlashscoreClient"),
    "fotmob": ("FotMob", "FotMobClient"),
    "youtube": ("YouTube", "YouTubeClient"),
}
HTTP_METHODS = frozenset({"get", "put", "post", "delete", "options", "head", "patch"})


def config_for(platform: str, *, version: str = "0.1.0", revision: str = "") -> dict:
    if platform not in PLATFORMS:
        raise ValueError(f"unsupported platform: {platform}")
    display, cls = PLATFORMS[platform]
    return {
        "platform": platform,
        "display_name": display,
        "group_name": platform,
        "class_name": cls,
        "async_class_name": "Async" + cls,
        "npm_name": "@crawlora-org/" + platform,
        "python_name": "crawlora-" + platform,
        "module_name": "crawlora_" + platform,
        "repository": "https://github.com/Crawlora-org/crawlora-" + platform,
        "version": version,
        "contract_revision": revision,
    }


def refs(value: object) -> Iterator[str]:
    if isinstance(value, dict):
        if "$ref" in value:
            yield value["$ref"]
        for child in value.values():
            yield from refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from refs(child)


def operation_ids(spec: dict) -> set[str]:
    return {
        op["operationId"]
        for methods in spec["paths"].values()
        for method, op in methods.items()
        if method in HTTP_METHODS
    }


def select(spec: dict, platform: str) -> dict:
    """Preserve wire contracts; normalize tags for concise client method names."""
    config_for(platform)
    if spec.get("swagger") != "2.0":
        raise ValueError("expected a Swagger 2 public contract")
    paths: dict = {}
    seen: set[str] = set()
    for path, methods in sorted(spec["paths"].items()):
        for method, original in sorted(methods.items()):
            if method not in HTTP_METHODS or not isinstance(original, dict):
                continue
            identifier = original.get("operationId", "")
            if not identifier.startswith(platform + "-") or original.get("deprecated"):
                continue
            if not path.startswith("/" + platform + "/"):
                raise ValueError(f"unexpected path for {identifier}: {path}")
            if identifier in seen:
                raise ValueError(f"duplicate operation: {identifier}")
            seen.add(identifier)
            op = copy.deepcopy(original)
            op["tags"] = [platform]
            paths.setdefault(path, {})[method] = op
    if not paths:
        raise ValueError(f"no public operations found for {platform}")

    result = {k: copy.deepcopy(v) for k, v in spec.items()
              if k not in {"paths", "definitions", "parameters", "responses", "securityDefinitions", "tags"}}
    result["paths"] = paths
    result["tags"] = [{"name": platform}]
    # Include references transitively, retaining cycles and failing on dangling
    # or external refs instead of silently weakening generated client types.
    queue = list(refs(paths))
    included: set[str] = set()
    while queue:
        ref = queue.pop()
        if ref in included:
            continue
        tokens = ref.split("/")
        if len(tokens) != 3 or tokens[0] != "#" or tokens[1] not in {"definitions", "parameters", "responses"}:
            raise ValueError(f"unsupported schema reference: {ref}")
        section, encoded = tokens[1:]
        name = encoded.replace("~1", "/").replace("~0", "~")
        try:
            node = spec[section][name]
        except KeyError as exc:
            raise ValueError(f"dangling schema reference: {ref}") from exc
        included.add(ref)
        result.setdefault(section, {})[name] = copy.deepcopy(node)
        queue.extend(refs(node))
    result.setdefault("definitions", {})
    security = set()
    for methods in paths.values():
        for op in methods.values():
            for entry in op.get("security", spec.get("security", [])):
                security.update(entry)
    result["securityDefinitions"] = {}
    for name in sorted(security):
        if name not in spec.get("securityDefinitions", {}):
            raise ValueError(f"missing security definition: {name}")
        result["securityDefinitions"][name] = copy.deepcopy(spec["securityDefinitions"][name])
    return result


def dumps(value: dict) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
