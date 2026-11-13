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
    "google": ("Google", "GoogleClient"),
    "bing": ("Bing", "BingClient"),
    "brave": ("Brave Search", "BraveClient"),
    "duckduckgo": ("DuckDuckGo", "DuckDuckGoClient"),
    "ebay": ("eBay", "EbayClient"),
    "googleplay": ("Google Play", "GooglePlayClient"),
    "appstore": ("App Store", "AppStoreClient"),
    "airbnb": ("Airbnb", "AirbnbClient"),
    "spotify": ("Spotify", "SpotifyClient"),
    "tiktok-mobile": ("TikTok Mobile", "TikTokMobileClient"),
    "xiaohongshu": ("Xiaohongshu", "XiaohongshuClient"),
    "rednote": ("RedNote", "RednoteClient"),
    "kick": ("Kick", "KickClient"),
    "wattpad": ("Wattpad", "WattpadClient"),
    "reelshort": ("ReelShort", "ReelShortClient"),
    "dramabox": ("DramaBox", "DramaBoxClient"),
    "wallapop": ("Wallapop", "WallapopClient"),
    "jumia": ("Jumia", "JumiaClient"),
    "cardmarket": ("Cardmarket", "CardmarketClient"),
    "fanduel": ("FanDuel", "FanDuelClient"),
    "fussballde": ("Fussball.de", "FussballdeClient"),
    "opendota": ("OpenDota", "OpenDotaClient"),
    "cricbuzz": ("Cricbuzz", "CricbuzzClient"),
    "gosugamers": ("GosuGamers", "GosuGamersClient"),
    "lolesports": ("LoL Esports", "LoLEsportsClient"),
    "vlr": ("VLR.gg", "VLRClient"),
    "bo3": ("BO3.gg", "BO3Client"),
}
# TikTok's public API uses product-area tags for several operation groups. Keep
# those in the TikTok package while excluding neighboring products that share
# an operation-ID prefix (for example Amazon Jobs).
PLATFORM_TAG_ALIASES = {
    "tiktok": frozenset({"tiktok", "tiktok creative center", "tiktok popular trend", "tiktok top ads"}),
    "tiktok-mobile": frozenset({"tiktok", "tiktok-mobile"}),
    "fussballde": frozenset({"fussball.de", "fussballde"}),
    "lolesports": frozenset({"lol esports", "lolesports"}),
    "duckduckgo": frozenset({"duckduckgo", "duckduckgo search"}),
    "spotify": frozenset({"spotify", "spotifypodcasts"}),
}
PLATFORM_EXCLUDED_TAGS = {
    "amazon": frozenset({"amazon jobs"}),
    "google": frozenset({"google jobs"}),
}
# Spotify Podcasts is served from a sibling path family and belongs in the
# Spotify package. TikTok Mobile uses the nested "/tiktok/mobile/" family.
# Other platforms own exactly "/<platform>/".
PLATFORM_PATH_PREFIXES = {
    "spotify": ("/spotify/", "/spotify-podcasts/"),
    "tiktok-mobile": ("/tiktok/mobile/",),
}
# Operations kept out of a package even if the public contract lists them
# again later. Google web search has no dependable upstream path, so the
# Google package must never pick it up through the daily contract sync.
PLATFORM_EXCLUDED_OPERATIONS = {
    "google": frozenset({"google-search"}),
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
    "google": (
        "Java client for Crawlora's hosted Google API, with Maps search, places, reviews and photos; News; Trends; "
        "Finance quotes and markets; suggestions; videos; and jobs. Requires a Crawlora API key."
    ),
    "bing": (
        "Java client for Crawlora's hosted Bing API, with web, news, image, and video search plus query suggestions. "
        "Requires a Crawlora API key."
    ),
    "brave": (
        "Java client for Crawlora's hosted Brave Search API, with web, news, image, and video search plus query "
        "suggestions. Requires a Crawlora API key."
    ),
    "duckduckgo": (
        "Java client for Crawlora's hosted DuckDuckGo API, with web, news, image, video, and shopping search plus "
        "query suggestions. Requires a Crawlora API key."
    ),
    "ebay": (
        "Java client for Crawlora's hosted eBay API, with listing search, item details, seller profiles, feedback and "
        "shops, and eBay Live streams. Requires a Crawlora API key."
    ),
    "googleplay": (
        "Java client for Crawlora's hosted Google Play API, with app search, details, reviews, ratings, permissions, "
        "data safety, charts, similar apps, and developers. Requires a Crawlora API key."
    ),
    "appstore": (
        "Java client for Crawlora's hosted App Store API, with app search, details, reviews, ratings, privacy labels, "
        "version history, charts, editorial collections, and developers. Requires a Crawlora API key."
    ),
    "airbnb": (
        "Java client for Crawlora's hosted Airbnb API, with listing search, room details, calendars and reviews, and "
        "host profiles, listings and reviews. Requires a Crawlora API key."
    ),
    "spotify": (
        "Java client for Crawlora's hosted Spotify API, with search, tracks, albums, artists, playlists, profiles, "
        "audiobooks, charts, and podcast shows and episodes. Requires a Crawlora API key."
    ),
    "tiktok-mobile": (
        "Java client for Crawlora's hosted TikTok Mobile API, with mobile feed, search, video, creator, music, "
        "LIVE, and place endpoints. Requires a Crawlora API key."
    ),
    "xiaohongshu": (
        "Java client for Crawlora's hosted Xiaohongshu API, with public explore feeds, note details, comments, "
        "and search suggestions. Requires a Crawlora API key."
    ),
    "rednote": (
        "Java client for Crawlora's hosted RedNote API, with public explore feeds, note details, comments, "
        "and search suggestions. Requires a Crawlora API key."
    ),
    "kick": (
        "Java client for Crawlora's hosted Kick API, with channels, livestreams, clips, categories, search, "
        "and public mobile-app catalogues. Requires a Crawlora API key."
    ),
    "wattpad": (
        "Java client for Crawlora's hosted Wattpad API, with story, author, search, category, language, "
        "and public comment data. Requires a Crawlora API key."
    ),
    "reelshort": (
        "Java client for Crawlora's hosted ReelShort API, with title discovery, search, movie details, "
        "new releases, and public Fandom articles. Requires a Crawlora API key."
    ),
    "dramabox": (
        "Java client for Crawlora's hosted DramaBox API, with title discovery, categories, search, rankings, "
        "recommendations, and public title details. Requires a Crawlora API key."
    ),
    "wallapop": (
        "Java client for Crawlora's hosted Wallapop API, with public listing search, categories, filters, "
        "and item details. Requires a Crawlora API key."
    ),
    "jumia": (
        "Java client for Crawlora's hosted Jumia API, with country and category discovery, product search, "
        "and product details. Requires a Crawlora API key."
    ),
    "cardmarket": (
        "Java client for Crawlora's hosted Cardmarket API, with game and catalogue discovery, product lookup, "
        "and price guides. Requires a Crawlora API key."
    ),
    "fanduel": (
        "Java client for Crawlora's hosted FanDuel API, with public racing, casino catalogue, and research data. "
        "Requires a Crawlora API key."
    ),
    "fussballde": (
        "Java client for Crawlora's hosted Fussball.de API, with amateur football clubs, players, matches, "
        "statistics, news, and federation data. Requires a Crawlora API key."
    ),
    "opendota": (
        "Java client for Crawlora's hosted OpenDota API, with Dota 2 matches, heroes, players, teams, leagues, "
        "statistics, and game constants. Requires a Crawlora API key."
    ),
    "cricbuzz": (
        "Java client for Crawlora's hosted Cricbuzz API, with cricket matches, schedules, news, rankings, "
        "series, and records. Requires a Crawlora API key."
    ),
    "gosugamers": (
        "Java client for Crawlora's hosted GosuGamers API, with esports matches, results, tournaments, games, "
        "news, and articles. Requires a Crawlora API key."
    ),
    "lolesports": (
        "Java client for Crawlora's hosted LoL Esports API, with leagues, schedules, live and completed events, "
        "teams, players, and game details. Requires a Crawlora API key."
    ),
    "vlr": (
        "Java client for Crawlora's hosted VLR.gg API, with Valorant matches, events, results, rankings, "
        "statistics, news, and forum data. Requires a Crawlora API key."
    ),
    "bo3": (
        "Java client for Crawlora's hosted BO3.gg API, with Counter-Strike and Valorant matches, teams, players, "
        "tournaments, rankings, news, and statistics. Requires a Crawlora API key."
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
        "group_name": {"tiktok-mobile": "tiktokMobile"}.get(platform, platform),
        "api_path_prefix": PLATFORM_PATH_PREFIXES.get(platform, ("/" + platform + "/",))[0],
        "class_name": cls,
        "async_class_name": "Async" + cls,
        "npm_name": "@crawlora-org/" + platform,
        "python_name": "crawlora-" + platform,
        "module_name": "crawlora_" + platform.replace("-", "_"),
        "golang_module_name": "github.com/Crawlora-org/crawlora-" + platform,
        "golang_version": version,
        "ruby_gem_name": "crawlora-" + platform,
        "php_package_name": "crawlora/" + platform,
        "rust_crate_name": "crawlora-" + platform,
        "rust_module_name": "crawlora_" + platform.replace("-", "_"),
        "maven_group_id": "net.crawlora",
        "maven_artifact_id": "crawlora-" + platform,
        "java_description": JAVA_DESCRIPTIONS.get(
            platform,
            f"Java client for Crawlora's hosted {display} API, with direct methods for supported operations. "
            "Requires a Crawlora API key.",
        ),
        "general_sdk_version": "1.50.0-sdk.1",
        "repository": "https://github.com/Crawlora-org/crawlora-" + platform,
        # Composer publishes from the multi-language platform repository.
        "php_repository": "https://github.com/Crawlora-org/crawlora-" + platform,
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
            if identifier in PLATFORM_EXCLUDED_OPERATIONS.get(platform, frozenset()):
                continue
            prefixes = PLATFORM_PATH_PREFIXES.get(platform, ("/" + platform + "/",))
            path_matches = path.startswith(prefixes)
            tag_matches = bool(tags.intersection(allowed_tags))
            if not isinstance(identifier, str) or not identifier.startswith(platform + "-"):
                # A nested client may share its upstream tag with a parent
                # platform. Its explicit path prefix scopes the package; the
                # shared tag alone must not claim the parent operations.
                if path_matches or (tag_matches and platform not in PLATFORM_PATH_PREFIXES):
                    raise ValueError(
                        f"unexpected operation ID for {platform} operation at {path}: {identifier!r}"
                    )
                continue
            if not path_matches:
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
