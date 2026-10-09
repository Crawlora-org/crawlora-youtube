"""Canonical UTM URLs for registry-facing platform client metadata."""

from __future__ import annotations

import re
from urllib.parse import urlencode


def crawlora_url(*, source: str, platform: str, surface: str, destination: str, path: str = "/") -> str:
    """Build a consistent, validated marketing URL for a client surface."""
    for label, value in (("source", source), ("platform", platform), ("surface", surface), ("destination", destination)):
        if not re.fullmatch(r"[a-z0-9][a-z0-9.-]*", value):
            raise ValueError(f"invalid UTM {label}: {value!r}")
    if not path.startswith("/") or path.startswith("//") or "?" in path or "#" in path:
        raise ValueError(f"invalid Crawlora marketing path: {path!r}")
    query = urlencode(
        (
            ("utm_source", source),
            ("utm_medium", "referral"),
            ("utm_campaign", "platform-clients"),
            ("utm_content", f"{platform}-{surface}-{destination}"),
        )
    )
    return f"https://crawlora.net{path}?{query}"
