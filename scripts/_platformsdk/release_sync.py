"""Recover a partially published same-version Crawlora platform release."""

from __future__ import annotations

import argparse
import http.client
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
try:
    import tomllib
except ImportError:  # pragma: no cover - Python 3.10 compatibility for public repositories.
    tomllib = None
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen


GITHUB_API = "https://api.github.com"
NPM_REGISTRY = "https://registry.npmjs.org"
PYPI_JSON = "https://pypi.org/pypi"
RUBYGEMS_API = "https://rubygems.org/api/v2/rubygems"
MAVEN_SEARCH = "https://search.maven.org/solrsearch/select"
PACKAGIST_P2 = "https://repo.packagist.org/p2"
GO_PROXY = "https://proxy.golang.org"
GITHUB_PACKAGES_API = f"{GITHUB_API}/orgs/Crawlora-org/packages"
TIMEOUT_SECONDS = 20
SUPPORTED = {
    "sofascore": {
        "repository": "Crawlora-org/crawlora-sofascore",
        "npm": "@crawlora-org/sofascore",
        "pypi": "crawlora-sofascore",
        "go": "github.com/Crawlora-org/crawlora-sofascore",
        "ruby": "crawlora-sofascore",
        "maven_group": "net.crawlora",
        "maven_artifact": "crawlora-sofascore",
        "packagist": "crawlora/sofascore",
    },
    "flashscore": {
        "repository": "Crawlora-org/crawlora-flashscore",
        "npm": "@crawlora-org/flashscore",
        "pypi": "crawlora-flashscore",
        "go": "github.com/Crawlora-org/crawlora-flashscore",
        "ruby": "crawlora-flashscore",
        "maven_group": "net.crawlora",
        "maven_artifact": "crawlora-flashscore",
        "packagist": "crawlora/flashscore",
    },
    "fotmob": {
        "repository": "Crawlora-org/crawlora-fotmob",
        "npm": "@crawlora-org/fotmob",
        "pypi": "crawlora-fotmob",
        "go": "github.com/Crawlora-org/crawlora-fotmob",
        "ruby": "crawlora-fotmob",
        "maven_group": "net.crawlora",
        "maven_artifact": "crawlora-fotmob",
        "packagist": "crawlora/fotmob",
    },
    "youtube": {
        "repository": "Crawlora-org/crawlora-youtube",
        "npm": "@crawlora-org/youtube",
        "pypi": "crawlora-youtube",
        "go": "github.com/Crawlora-org/crawlora-youtube",
        "ruby": "crawlora-youtube",
        "maven_group": "net.crawlora",
        "maven_artifact": "crawlora-youtube",
        "packagist": "crawlora/youtube",
    },
}
_VERSION = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
_ARTIFACT_PATHS = ("javascript", "python", "go.mod", "client.go", "operations.go", "ruby", "java", "php", "composer.json", "README.md", "openapi/public.json")


class ReleaseSyncError(RuntimeError):
    """Raised when publication state cannot be verified safely."""


def _http_json(
    url: str,
    *,
    token: str | None,
    opener: Callable[..., Any],
    missing_ok: bool = False,
) -> dict[str, Any] | None:
    headers = {"Accept": "application/json", "User-Agent": "Crawlora-Platform-Release-Sync/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    try:
        with opener(request, timeout=TIMEOUT_SECONDS) as response:
            status = getattr(response, "status", response.getcode())
            body = response.read()
    except HTTPError as exc:
        code, reason = exc.code, exc.reason
        exc.close()
        if missing_ok and code == 404:
            return None
        raise ReleaseSyncError(f"GET {url} returned HTTP {code}: {reason}") from exc
    except (URLError, TimeoutError, OSError, http.client.HTTPException) as exc:
        raise ReleaseSyncError(f"GET {url} failed: {exc}") from exc
    if status != 200:
        if missing_ok and status == 404:
            return None
        raise ReleaseSyncError(f"GET {url} returned HTTP {status}")
    try:
        value = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseSyncError(f"GET {url} returned malformed JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ReleaseSyncError(f"GET {url} returned JSON that is not an object")
    return value


def _http_json_array(
    url: str,
    *,
    token: str,
    opener: Callable[..., Any],
    missing_ok: bool = False,
) -> list[Any] | None:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Crawlora-Platform-Release-Sync/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {token}",
    }
    request = Request(url, headers=headers)
    try:
        with opener(request, timeout=TIMEOUT_SECONDS) as response:
            status = getattr(response, "status", response.getcode())
            body = response.read()
    except HTTPError as exc:
        code, reason = exc.code, exc.reason
        exc.close()
        if missing_ok and code == 404:
            return None
        raise ReleaseSyncError(f"GET {url} returned HTTP {code}: {reason}") from exc
    except (URLError, TimeoutError, OSError, http.client.HTTPException) as exc:
        raise ReleaseSyncError(f"GET {url} failed: {exc}") from exc
    if status != 200:
        if missing_ok and status == 404:
            return None
        raise ReleaseSyncError(f"GET {url} returned HTTP {status}")
    try:
        value = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseSyncError(f"GET {url} returned malformed JSON: {exc}") from exc
    if not isinstance(value, list):
        raise ReleaseSyncError(f"GET {url} returned JSON that is not an array")
    return value


def _registry_url(registry: str, name: str, version: str) -> str:
    if registry == "npm":
        encoded_name = quote(name, safe="@")
        return f"{NPM_REGISTRY}/{encoded_name}/{quote(version, safe='.-+')}"
    if registry == "pypi":
        return f"{PYPI_JSON}/{quote(name, safe='')}/{quote(version, safe='')}/json"
    if registry == "ruby":
        return f"{RUBYGEMS_API}/{quote(name, safe='')}/versions/{quote(version, safe='')}.json"
    if registry == "maven":
        query = f'g:"net.crawlora" AND a:"{name}" AND v:"{version}"'
        return f"{MAVEN_SEARCH}?{urlencode({'q': query, 'rows': 1, 'wt': 'json'})}"
    if registry == "packagist":
        return f"{PACKAGIST_P2}/{quote(name, safe='/')}.json"
    if registry == "go":
        escaped = "".join("!" + char.lower() if char.isupper() else char for char in name)
        return f"{GO_PROXY}/{quote(escaped, safe='/')}/@v/v{quote(version, safe='.-+')}.info"
    raise ReleaseSyncError(f"unsupported package registry: {registry}")


def _published(registry: str, name: str, version: str, *, opener: Callable[..., Any]) -> bool:
    url = _registry_url(registry, name, version)
    payload = _http_json(url, token=None, opener=opener, missing_ok=True)
    if payload is None:
        return False
    found = payload.get("version")
    if registry == "pypi":
        info = payload.get("info")
        found = info.get("version") if isinstance(info, dict) else None
    elif registry == "ruby":
        found = payload.get("number")
    elif registry == "maven":
        response = payload.get("response")
        docs = response.get("docs") if isinstance(response, dict) else None
        if not isinstance(docs, list):
            raise ReleaseSyncError("Maven Central returned malformed exact-version search results")
        if not docs:
            return False
        if not any(
            isinstance(doc, dict)
            and doc.get("g") == "net.crawlora"
            and doc.get("a") == name
            and doc.get("v") == version
            for doc in docs
        ):
            raise ReleaseSyncError(f"Maven Central returned mismatched coordinates for {name}:{version}")
        found = version
    elif registry == "packagist":
        packages = payload.get("packages")
        versions = packages.get(name) if isinstance(packages, dict) else None
        if not isinstance(versions, list):
            raise ReleaseSyncError(f"Packagist returned malformed package metadata for {name}")
        matches = [
            item for item in versions
            if isinstance(item, dict) and str(item.get("version", "")).removeprefix("v") == version
        ]
        if not matches:
            return False
        found = version
    elif registry == "go":
        found = payload.get("Version")
        if found == "v" + version:
            return True
    if found != version:
        raise ReleaseSyncError(
            f"{registry} returned version {found!r} for exact version lookup {name}@{version}"
        )
    return True


def _github_package_published(
    manifest: dict[str, str],
    version: str,
    *,
    token: str,
    opener: Callable[..., Any],
) -> bool:
    packages_url = f"{GITHUB_PACKAGES_API}?package_type=maven&per_page=100"
    packages = _http_json_array(packages_url, token=token, opener=opener)
    expected_repository = manifest["repository"].lower()
    expected_names = {
        manifest["maven_artifact"],
        f"{manifest['maven_group']}:{manifest['maven_artifact']}",
        f"{manifest['maven_group']}.{manifest['maven_artifact']}",
    }
    candidates = []
    for package in packages or []:
        if not isinstance(package, dict):
            raise ReleaseSyncError("GitHub Packages returned malformed package metadata")
        repository = package.get("repository")
        repository_name = repository.get("full_name") if isinstance(repository, dict) else None
        if str(repository_name or "").lower() == expected_repository or package.get("name") in expected_names:
            candidates.append(package)
    for package in candidates:
        name = package.get("name")
        if not isinstance(name, str) or not name:
            raise ReleaseSyncError("GitHub Packages returned a package without a name")
        package_url = package.get("url")
        parsed_url = urlparse(str(package_url or ""))
        if parsed_url.hostname != "api.github.com" or not parsed_url.path.startswith(
            "/orgs/Crawlora-org/packages/maven/"
        ):
            raise ReleaseSyncError("GitHub Packages returned an invalid Maven package URL")
        versions_url = str(package_url).rstrip("/") + "/versions?per_page=100"
        versions = _http_json_array(versions_url, token=token, opener=opener, missing_ok=True)
        if versions is None:
            continue
        if any(isinstance(item, dict) and item.get("name") == version for item in versions):
            return True
    return False


def _repository_url(repository: str) -> str:
    return "https://github.com/" + repository


def _project_metadata(text: str) -> dict[str, str]:
    if tomllib is not None:
        try:
            parsed = tomllib.loads(text)
        except tomllib.TOMLDecodeError as exc:
            raise ReleaseSyncError(f"pyproject.toml is malformed: {exc}") from exc
        project = parsed.get("project")
        if isinstance(project, dict):
            return {key: project.get(key) for key in ("name", "version")}
        return {}
    values: dict[str, str] = {}
    in_project = False
    for line in text.splitlines():
        section = re.match(r"^\s*\[([^]]+)\]\s*(?:#.*)?$", line)
        if section:
            in_project = section.group(1) == "project"
            continue
        if not in_project:
            continue
        item = re.match(r"^\s*(name|version)\s*=\s*(['\"])([^'\"]+)\2\s*(?:#.*)?$", line)
        if item:
            values[item.group(1)] = item.group(3)
    return values


def _normalize_remote(remote: str) -> str:
    value = remote.strip()
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.split(":", 1)[1]
    elif value.startswith("ssh://git@github.com/"):
        value = "https://github.com/" + value.split("/", 3)[-1]
    parsed = urlparse(value)
    if parsed.hostname != "github.com":
        return ""
    return parsed.path.strip("/").removesuffix(".git").lower()


def _run(
    command: list[str],
    *,
    root: Path,
    runner: Callable[..., Any],
    env: dict[str, str],
    allowed: tuple[int, ...] = (0,),
) -> Any:
    result = runner(command, cwd=root, env=env, capture_output=True, text=True, check=False)
    if result.returncode not in allowed:
        detail = (result.stderr or result.stdout or "").strip()
        raise ReleaseSyncError(f"command failed ({result.returncode}): {' '.join(command)}: {detail}")
    return result


def _read_manifest(root: Path) -> tuple[dict[str, Any], dict[str, str]]:
    try:
        config = json.loads((root / "platform.json").read_text(encoding="utf-8"))
        npm_package = json.loads((root / "javascript" / "package.json").read_text(encoding="utf-8"))
        pyproject_text = (root / "python" / "pyproject.toml").read_text(encoding="utf-8")
        go_mod = (root / "go.mod").read_text(encoding="utf-8")
        go_client = (root / "client.go").read_text(encoding="utf-8")
        ruby_gemspecs = list((root / "ruby").glob("*.gemspec"))
        ruby_version = (root / "ruby" / "lib" / "crawlora" / str(config.get("platform")) / "version.rb").read_text(encoding="utf-8")
        java_pom = ET.parse(root / "java" / "pom.xml").getroot()
        composer = json.loads((root / "composer.json").read_text(encoding="utf-8"))
        php_composer = json.loads((root / "php" / "composer.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ET.ParseError) as exc:
        raise ReleaseSyncError(f"cannot read the platform release manifest: {exc}") from exc
    if not isinstance(config, dict) or not isinstance(npm_package, dict):
        raise ReleaseSyncError("platform.json and javascript/package.json must contain JSON objects")
    platform = config.get("platform")
    if not isinstance(platform, str):
        raise ReleaseSyncError(f"unsupported platform in platform.json: {platform!r}")
    expected = SUPPORTED.get(platform)
    if expected is None:
        raise ReleaseSyncError(f"unsupported platform in platform.json: {platform!r}")
    version = config.get("version")
    revision = config.get("contract_revision")
    if not isinstance(version, str) or not _VERSION.fullmatch(version):
        raise ReleaseSyncError(f"invalid platform version: {version!r}")
    if not isinstance(revision, str) or not revision.strip():
        raise ReleaseSyncError("platform.json contract_revision must be a non-empty string")
    if config.get("npm_name") != expected["npm"]:
        raise ReleaseSyncError(f"platform.json npm_name must be {expected['npm']!r}")
    if config.get("python_name") != expected["pypi"]:
        raise ReleaseSyncError(f"platform.json python_name must be {expected['pypi']!r}")
    for field, key in (
        ("golang_module_name", "go"),
        ("ruby_gem_name", "ruby"),
        ("php_package_name", "packagist"),
        ("maven_group_id", "maven_group"),
        ("maven_artifact_id", "maven_artifact"),
    ):
        if config.get(field) != expected[key]:
            raise ReleaseSyncError(f"platform.json {field} must be {expected[key]!r}")
    wanted_repo = _repository_url(expected["repository"])
    if str(config.get("repository", "")).rstrip("/").removesuffix(".git").lower() != wanted_repo.lower():
        raise ReleaseSyncError(f"platform.json repository must identify {expected['repository']}")
    package_repo = npm_package.get("repository")
    package_repo = package_repo.get("url") if isinstance(package_repo, dict) else package_repo
    if npm_package.get("name") != expected["npm"] or npm_package.get("version") != version:
        raise ReleaseSyncError("javascript/package.json name/version do not match the release manifest")
    if _normalize_remote(str(package_repo or "")) != expected["repository"].lower():
        raise ReleaseSyncError("javascript/package.json repository does not match the platform manifest")
    project = _project_metadata(pyproject_text)
    if project.get("name") != expected["pypi"] or project.get("version") != version:
        raise ReleaseSyncError("python/pyproject.toml project name/version do not match the release manifest")
    module_match = re.search(r"(?m)^module\s+(\S+)\s*$", go_mod)
    go_version_match = re.search(r'(?m)^\s*Version\s*=\s*"([^"]+)"', go_client)
    if not module_match or module_match.group(1) != expected["go"]:
        raise ReleaseSyncError("go.mod module path does not match the platform manifest")
    if not go_version_match or go_version_match.group(1) != version:
        raise ReleaseSyncError("Go client version does not match the release manifest")
    if len(ruby_gemspecs) != 1:
        raise ReleaseSyncError("ruby/ must contain exactly one gemspec")
    gemspec = ruby_gemspecs[0].read_text(encoding="utf-8")
    gem_name = re.search(r'(?m)^\s*spec\.name\s*=\s*["\']([^"\']+)', gemspec)
    ruby_version_match = re.search(r'(?m)^\s*VERSION\s*=\s*["\']([^"\']+)', ruby_version)
    if not gem_name or gem_name.group(1) != expected["ruby"] or ruby_gemspecs[0].stem != expected["ruby"]:
        raise ReleaseSyncError("Ruby gemspec name does not match the platform manifest")
    if not ruby_version_match or ruby_version_match.group(1) != version:
        raise ReleaseSyncError("Ruby gem version does not match the release manifest")
    namespace = {"m": "http://maven.apache.org/POM/4.0.0"}
    java_group = java_pom.findtext("m:groupId", namespaces=namespace)
    java_artifact = java_pom.findtext("m:artifactId", namespaces=namespace)
    java_version = java_pom.findtext("m:version", namespaces=namespace)
    if (java_group, java_artifact, java_version) != (expected["maven_group"], expected["maven_artifact"], version):
        raise ReleaseSyncError("java/pom.xml coordinates/version do not match the platform manifest")
    if composer.get("name") != expected["packagist"] or php_composer.get("name") != expected["packagist"]:
        raise ReleaseSyncError("root and php/composer.json package names do not match the platform manifest")
    manifest = {**expected, "platform": platform, "version": version, "contract_revision": revision}
    return config, manifest


def _validate_git_root(
    root: Path,
    manifest: dict[str, str],
    *,
    runner: Callable[..., Any],
    env: dict[str, str],
) -> str:
    expected_repo = manifest["repository"].lower()
    remote = _run(["git", "remote", "get-url", "origin"], root=root, runner=runner, env=env).stdout.strip()
    if _normalize_remote(remote) != expected_repo.lower():
        raise ReleaseSyncError(f"origin remote does not match expected repository {manifest['repository']}")
    head = _run(["git", "rev-parse", "HEAD"], root=root, runner=runner, env=env).stdout.strip()
    if not re.fullmatch(r"[0-9a-fA-F]{40,64}", head):
        raise ReleaseSyncError(f"git returned an invalid HEAD SHA: {head!r}")
    status = _run(
        ["git", "status", "--porcelain", "--untracked-files=all", "--", "platform.json", "README.md", "composer.json", "javascript", "python", "go.mod", "client.go", "operations.go", "ruby", "java", "php", "openapi/public.json"],
        root=root,
        runner=runner,
        env=env,
    ).stdout
    if status.strip():
        raise ReleaseSyncError("release files are dirty; refusing to tag uncommitted package content")
    return head.lower()


def _remote_tag(
    root: Path,
    tag: str,
    *,
    runner: Callable[..., Any],
    env: dict[str, str],
) -> str | None:
    result = _run(
        ["git", "ls-remote", "--tags", "origin", f"refs/tags/{tag}", f"refs/tags/{tag}^{{}}"],
        root=root,
        runner=runner,
        env=env,
    )
    direct = None
    peeled = None
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) != 2:
            raise ReleaseSyncError(f"malformed git ls-remote output for {tag}: {line!r}")
        if parts[1] == f"refs/tags/{tag}":
            direct = parts[0]
        elif parts[1] == f"refs/tags/{tag}^{{}}":
            peeled = parts[0]
        else:
            raise ReleaseSyncError(f"unexpected ref returned while looking up {tag}: {parts[1]}")
    commit = peeled or direct
    if commit is not None and not re.fullmatch(r"[0-9a-fA-F]{40,64}", commit):
        raise ReleaseSyncError(f"remote tag {tag} has invalid target {commit!r}")
    return commit.lower() if commit else None


def _release_url(repository: str, tag: str) -> str:
    return f"{GITHUB_API}/repos/{repository}/releases/tags/{quote(tag, safe='')}"


def _active_run(
    root: Path,
    manifest: dict[str, str],
    tag: str,
    commit: str,
    *,
    runner: Callable[..., Any],
    env: dict[str, str],
) -> dict[str, Any] | None:
    result = _run(
        [
            "gh", "run", "list", "--workflow", "release.yml", "--branch", tag,
            "--json", "status,headSha,headBranch,databaseId,url", "--limit", "20",
            "--repo", manifest["repository"],
        ],
        root=root,
        runner=runner,
        env=env,
    )
    try:
        runs = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ReleaseSyncError(f"gh run list returned malformed JSON: {exc}") from exc
    if not isinstance(runs, list):
        raise ReleaseSyncError("gh run list output must be a JSON array")
    for run in runs:
        if not isinstance(run, dict):
            raise ReleaseSyncError("gh run list returned a malformed run entry")
        if (
            not isinstance(run.get("status"), str)
            or not isinstance(run.get("headBranch"), str)
            or not isinstance(run.get("headSha"), str)
        ):
            raise ReleaseSyncError("gh run list returned a run without status, headBranch, or headSha")
        if (
            run.get("status") in {"queued", "in_progress"}
            and run.get("headBranch") == tag
            and str(run.get("headSha", "")).lower() == commit.lower()
        ):
            return run
    return None


def _read_tag_config(
    root: Path,
    tag: str,
    manifest: dict[str, str],
    *,
    runner: Callable[..., Any],
    env: dict[str, str],
) -> None:
    raw = _run(["git", "show", f"{tag}:platform.json"], root=root, runner=runner, env=env).stdout
    try:
        tagged = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ReleaseSyncError(f"tagged platform.json is malformed: {exc}") from exc
    if (
        not isinstance(tagged, dict)
        or tagged.get("version") != manifest["version"]
        or tagged.get("contract_revision") != manifest["contract_revision"]
    ):
        raise ReleaseSyncError(f"tag {tag} does not contain the requested version and contract_revision")


def _verify_tagged_content(
    root: Path,
    tag: str,
    *,
    runner: Callable[..., Any],
    env: dict[str, str],
) -> None:
    result = _run(
        ["git", "diff", "--quiet", tag, "HEAD", "--", *_ARTIFACT_PATHS],
        root=root,
        runner=runner,
        env=env,
        allowed=(0, 1),
    )
    if result.returncode == 1:
        raise ReleaseSyncError(f"tag {tag} package artifacts differ from local HEAD")


def _local_tag_commit(
    root: Path,
    tag: str,
    *,
    runner: Callable[..., Any],
    env: dict[str, str],
) -> str | None:
    result = _run(
        ["git", "rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}"],
        root=root,
        runner=runner,
        env=env,
        allowed=(0, 128, 1),
    )
    if result.returncode:
        return None
    value = result.stdout.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{40,64}", value):
        raise ReleaseSyncError(f"local tag {tag} resolves to an invalid commit: {value!r}")
    return value


def _fetch_and_validate_tag(
    root: Path,
    tag: str,
    remote_commit: str,
    manifest: dict[str, str],
    *,
    runner: Callable[..., Any],
    env: dict[str, str],
) -> str:
    local_commit = _local_tag_commit(root, tag, runner=runner, env=env)
    if local_commit and local_commit != remote_commit:
        raise ReleaseSyncError(f"local tag {tag} differs from immutable remote tag target")
    _run(
        ["git", "fetch", "--no-tags", "origin", f"refs/tags/{tag}:refs/tags/{tag}"],
        root=root,
        runner=runner,
        env=env,
    )
    fetched = _run(["git", "rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}"], root=root, runner=runner, env=env).stdout.strip().lower()
    if fetched != remote_commit:
        raise ReleaseSyncError(f"fetched tag {tag} resolved to {fetched}, expected {remote_commit}")
    _read_tag_config(root, tag, manifest, runner=runner, env=env)
    _verify_tagged_content(root, tag, runner=runner, env=env)
    return fetched


def _create_release(
    root: Path,
    manifest: dict[str, str],
    tag: str,
    *,
    target: str | None,
    runner: Callable[..., Any],
    env: dict[str, str],
) -> None:
    notes = (
        f"Publication recovery for all Crawlora {manifest['platform']} platform packages "
        f"version {manifest['version']} (contract {manifest['contract_revision']}).\n"
    )
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", prefix="release-sync-", suffix=".md", delete=False) as stream:
        stream.write(notes)
        notes_path = stream.name
    try:
        command = ["gh", "release", "create", tag, "--repo", manifest["repository"], "--notes-file", notes_path]
        if target:
            command.extend(["--target", target])
        _run(command, root=root, runner=runner, env=env)
    finally:
        Path(notes_path).unlink(missing_ok=True)


def sync_release(
    root: Path,
    *,
    check_only: bool = False,
    github_output: Path | None = None,
    report_path: Path | None = None,
    opener: Callable[..., Any] = urlopen,
    runner: Callable[..., Any] = subprocess.run,
    environ: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Ensure every package registry contains the manifest version, safely retrying it if needed."""
    root = Path(root).resolve()
    env = dict(os.environ if environ is None else environ)
    config, manifest = _read_manifest(root)
    token = env.get("GH_TOKEN") or env.get("GITHUB_TOKEN")
    if not token:
        raise ReleaseSyncError("GH_TOKEN or GITHUB_TOKEN is required to verify GitHub Packages")
    published = {
        "npm": _published("npm", manifest["npm"], manifest["version"], opener=opener),
        "pypi": _published("pypi", manifest["pypi"], manifest["version"], opener=opener),
        "go": _published("go", manifest["go"], manifest["version"], opener=opener),
        "ruby": _published("ruby", manifest["ruby"], manifest["version"], opener=opener),
        "maven": _published("maven", manifest["maven_artifact"], manifest["version"], opener=opener),
        "packagist": _published("packagist", manifest["packagist"], manifest["version"], opener=opener),
        "github_packages": _github_package_published(
            manifest, manifest["version"], token=token, opener=opener
        ),
    }
    tag = "v" + manifest["version"]
    report: dict[str, Any] = {
        "version": manifest["version"],
        "published": published,
        "needs_release": not all(published.values()),
        "tag": tag,
        "tag_commit": None,
        "dispatched": False,
    }

    if report["needs_release"] and not check_only:
        head = _validate_git_root(root, manifest, runner=runner, env=env)
        env["GH_TOKEN"] = token
        release = _http_json(
            _release_url(manifest["repository"], tag),
            token=token,
            opener=opener,
            missing_ok=True,
        )
        if release is not None:
            if release.get("tag_name") != tag or release.get("draft") is True:
                raise ReleaseSyncError(f"GitHub release lookup returned an invalid release for {tag}")
        remote_commit = _remote_tag(root, tag, runner=runner, env=env)
        if release is not None and remote_commit is None:
            raise ReleaseSyncError(f"GitHub release {tag} exists but its immutable tag is missing")
        if remote_commit is None:
            local_commit = _local_tag_commit(root, tag, runner=runner, env=env)
            if local_commit and local_commit != head:
                raise ReleaseSyncError(f"local tag {tag} exists at another commit; refusing to move it")
            candidate_commit = head
        else:
            candidate_commit = _fetch_and_validate_tag(
                root, tag, remote_commit, manifest, runner=runner, env=env
            )
            report["tag_commit"] = candidate_commit

        active = _active_run(root, manifest, tag, candidate_commit, runner=runner, env=env)
        if active:
            report["tag_commit"] = candidate_commit
            report["active_run"] = active
        else:
            release_created = False
            if remote_commit is None:
                _create_release(root, manifest, tag, target=head, runner=runner, env=env)
                release_created = True
                remote_commit = _remote_tag(root, tag, runner=runner, env=env)
                if remote_commit is None:
                    raise ReleaseSyncError(f"release creation did not create tag {tag}")

            validated_commit = candidate_commit
            if report["tag_commit"] is None:
                validated_commit = _fetch_and_validate_tag(
                    root, tag, remote_commit, manifest, runner=runner, env=env
                )
            report["tag_commit"] = validated_commit
            if release is None and not release_created:
                # Attach a release to an existing immutable tag; omit --target so
                # GitHub cannot create or retarget a ref in this path.
                _create_release(root, manifest, tag, target=None, runner=runner, env=env)
            _run(
                ["gh", "workflow", "run", "release.yml", "--ref", tag, "--repo", manifest["repository"]],
                root=root,
                runner=runner,
                env=env,
            )
            report["dispatched"] = True
    elif check_only and report["needs_release"]:
        # A check-only run intentionally avoids fetching refs, querying release
        # automation, writing outputs, or changing GitHub/registry state.
        pass

    if report_path is not None:
        report_path = Path(report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if github_output is not None:
        github_output = Path(github_output)
        github_output.parent.mkdir(parents=True, exist_ok=True)
        with github_output.open("a", encoding="utf-8") as output:
            for key in ("needs_release", "dispatched", "version"):
                value = report[key]
                output.write(f"{key}={str(value).lower() if isinstance(value, bool) else value}\n")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    try:
        report = sync_release(
            args.root,
            check_only=args.check_only,
            github_output=args.github_output,
            report_path=args.report,
        )
    except (ReleaseSyncError, OSError) as exc:
        print(f"release_sync: {exc}", file=sys.stderr)
        return 1
    if args.report is None:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
