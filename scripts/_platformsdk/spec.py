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
    "bbb": ("Better Business Bureau", "BBBClient"),
    "reddit": ("Reddit", "RedditClient"),
    "tiktok": ("TikTok", "TikTokClient"),
    "amazon": ("Amazon", "AmazonClient"),
    "imdb": ("IMDb", "IMDbClient"),
}
# TikTok's public API uses product-area tags for several operation groups. Keep
# those in the TikTok package while excluding neighboring products that share
# an operation-ID prefix (for example Amazon Jobs).
PLATFORM_TAG_ALIASES = {
    "tiktok": frozenset({"tiktok", "tiktok creative center", "tiktok popular trend", "tiktok top ads"}),
}
PLATFORM_EXCLUDED_TAGS = {
    "amazon": frozenset({"amazon jobs"}),
}
JAVA_DESCRIPTIONS = {
    "sofascore": (
        "Java client for Crawlora's hosted SofaScore API, with direct methods for live events, match details, "
        "lineups, statistics, tournaments, and player/team data. Requires a Crawlora API key."
    ),
    "flashscore": (
        "Java client for Crawlora's hosted Flashscore API, with methods for scores, match details, competitions, "
        "teams, players, odds, and news. Requires a Crawlora API key."
    ),
    "fotmob": (
        "Java client for Crawlora's hosted FotMob API, with methods for leagues, matches, fixtures, teams, "
        "players, search, standings, news, and rankings. Requires a Crawlora API key."
    ),
    "youtube": (
        "Java client for Crawlora's hosted YouTube API, with methods for search, channels, videos, playlists, "
        "comments, captions, and transcripts. Requires a Crawlora API key."
    ),
    "bbb": (
        "Java client for Crawlora's hosted Better Business Bureau API, with methods for business search, profiles, "
        "complaints, reviews, categories, and ScamTracker reports. Requires a Crawlora API key."
    ),
    "reddit": (
        "Java client for Crawlora's hosted Reddit API, with search, post and comment details, subreddit feeds, "
        "user history, domain listings, trends, and leads. Requires a Crawlora API key."
    ),
    "tiktok": (
        "Java client for Crawlora's hosted TikTok API, with video, user, and hashtag search; profiles and posts; "
        "comments; trends; Creative Center; and Top Ads data. Requires a Crawlora API key."
    ),
    "amazon": (
        "Java client for Crawlora's hosted Amazon Marketplace API, with product search, suggestions, product details, "
        "and chart/category discovery. Requires a Crawlora API key."
    ),
    "imdb": (
        "Java client for Crawlora's hosted IMDb API, with title and name search, charts, ratings, credits, awards, "
        "episodes, reviews, images, and title metadata. Requires a Crawlora API key."
    ),
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
        "golang_module_name": "github.com/Crawlora-org/crawlora-" + platform,
        "golang_version": version,
        "ruby_gem_name": "crawlora-" + platform,
        "php_package_name": "crawlora/" + platform,
        "maven_group_id": "net.crawlora",
        "maven_artifact_id": "crawlora-" + platform,
        "java_description": JAVA_DESCRIPTIONS.get(
            platform,
            f"Java client for Crawlora's hosted {display} API, with direct methods for supported operations. "
            "Requires a Crawlora API key.",
        ),
        "general_sdk_version": "1.46.0-sdk.1",
        "repository": "https://github.com/Crawlora-org/crawlora-" + platform,
        "php_repository": "https://github.com/Crawlora-org/crawlora-" + platform + "-php",
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
            if original.get("deprecated"):
                continue
            tags = {str(tag).strip().lower() for tag in original.get("tags", []) if str(tag).strip()}
            allowed_tags = PLATFORM_TAG_ALIASES.get(platform, frozenset({platform}))
            if tags.intersection(PLATFORM_EXCLUDED_TAGS.get(platform, frozenset())):
                continue
            path_matches = path.startswith("/" + platform + "/")
            tag_matches = bool(tags.intersection(allowed_tags))
            if not isinstance(identifier, str) or not identifier.startswith(platform + "-"):
                if path_matches or tag_matches:
                    raise ValueError(
                        f"unexpected operation ID for {platform} operation at {path}: {identifier!r}"
                    )
                continue
            if not path.startswith("/" + platform + "/"):
                raise ValueError(f"unexpected path for {identifier}: {path}")
            if tags and tags.isdisjoint(allowed_tags):
                raise ValueError(f"unexpected tag for {identifier}: {sorted(tags)}")
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
