"""Failure-oriented tests for same-version platform publication recovery."""

from __future__ import annotations

import json
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from urllib.error import HTTPError, URLError
from urllib.parse import quote

from .release_sync import (
    GITHUB_API,
    NPM_REGISTRY,
    PYPI_JSON,
    RUBYGEMS_API,
    MAVEN_CENTRAL,
    PACKAGIST_P2,
    GO_PROXY,
    GITHUB_PACKAGES_API,
    SUPPORTED,
    ReleaseSyncError,
    _registry_url,
    sync_release,
)


HEAD = "a" * 40
TAG_COMMIT = "b" * 40
VERSION = "0.1.0"
REVISION = "contract-abc123"


class Response:
    def __init__(self, status: int, body: bytes):
        self.status = status
        self._body = body

    def read(self) -> bytes:
        return self._body

    def getcode(self) -> int:
        return self.status

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None


class FakeHTTP:
    def __init__(self, answers: dict[str, tuple[int, bytes]]):
        self.answers = answers
        self.requests = []

    def __call__(self, request, timeout):
        self.requests.append((request.full_url, request, timeout))
        status, body = self.answers.get(request.full_url, (404, b"{}"))
        if status >= 400:
            raise HTTPError(request.full_url, status, "mocked status", {}, None)
        return Response(status, body)


class FakeRunner:
    def __init__(self, config: dict, *, remote_tag: str | None = None, local_tag: str | None = None,
                 tagged_config: dict | None = None, diff_status: int = 0, runs: list | None = None,
                 origin: str | None = None):
        self.config = config
        self.remote_tag = remote_tag
        self.local_tag = local_tag
        self.tagged_config = tagged_config or config
        self.diff_status = diff_status
        self.runs = runs or []
        self.origin = origin
        self.commands: list[list[str]] = []
        self.envs: list[dict] = []

    def __call__(self, command, *, cwd, env, capture_output, text, check):
        self.commands.append(list(command))
        self.envs.append(dict(env))
        stdout = ""
        stderr = ""
        status = 0
        if command[:4] == ["git", "remote", "get-url", "origin"]:
            platform = self.config["platform"]
            stdout = (self.origin or f"git@github.com:{SUPPORTED[platform]['repository']}.git") + "\n"
        elif command == ["git", "rev-parse", "HEAD"]:
            stdout = HEAD + "\n"
        elif command[:3] == ["git", "status", "--porcelain"]:
            stdout = ""
        elif command[:4] == ["git", "ls-remote", "--tags", "origin"]:
            if self.remote_tag:
                tag = "v" + VERSION
                stdout = f"{self.remote_tag}\trefs/tags/{tag}\n"
        elif command[:4] == ["git", "rev-parse", "--verify", "refs/tags/v" + VERSION + "^{commit}"]:
            if self.local_tag:
                stdout = self.local_tag + "\n"
            else:
                status = 128
                stderr = "unknown revision"
        elif command[:3] == ["git", "fetch", "--no-tags"]:
            self.local_tag = self.remote_tag
        elif command[:3] == ["git", "show", "v" + VERSION + ":platform.json"]:
            stdout = json.dumps(self.tagged_config)
        elif command[:3] == ["git", "diff", "--quiet"]:
            status = self.diff_status
        elif command[:3] == ["gh", "run", "list"]:
            stdout = json.dumps(self.runs)
        elif command[:3] == ["gh", "release", "create"]:
            self.created_release = True
            if "--target" in command:
                self.remote_tag = command[command.index("--target") + 1]
        elif command[:3] == ["gh", "workflow", "run"]:
            pass
        else:
            raise AssertionError(f"unexpected command: {command}")
        return SimpleNamespace(returncode=status, stdout=stdout, stderr=stderr)


def write_repo(root: Path, platform: str = "sofascore") -> dict:
    expected = SUPPORTED[platform]
    config = {
        "platform": platform,
        "repository": "https://github.com/" + expected["repository"],
        "npm_name": expected["npm"],
        "python_name": expected["pypi"],
        "golang_module_name": expected["go"],
        "ruby_gem_name": expected["ruby"],
        "php_package_name": expected["packagist"],
        "php_repository": "https://github.com/" + expected["repository"],
        "maven_group_id": expected["maven_group"],
        "maven_artifact_id": expected["maven_artifact"],
        "version": VERSION,
        "contract_revision": REVISION,
    }
    (root / "platform.json").write_text(json.dumps(config), encoding="utf-8")
    (root / "javascript").mkdir()
    (root / "javascript" / "package.json").write_text(
        json.dumps({
            "name": expected["npm"],
            "version": VERSION,
            "repository": {"type": "git", "url": config["repository"], "directory": "javascript"},
        }),
        encoding="utf-8",
    )
    python_root = root / "python"
    python_root.mkdir()
    (python_root / "pyproject.toml").write_text(
        f'[project]\nname = "{expected["pypi"]}"\nversion = "{VERSION}"\n', encoding="utf-8"
    )
    (root / "go.mod").write_text(f"module {expected['go']}\n\ngo 1.22\n", encoding="utf-8")
    (root / "client.go").write_text(f'package client\n\nconst (\n\tVersion = "{VERSION}"\n)\n', encoding="utf-8")
    (root / "operations.go").write_text("package client\n", encoding="utf-8")
    ruby_dir = root / "ruby" / "lib" / "crawlora" / platform
    ruby_dir.mkdir(parents=True)
    (root / "ruby" / f"{expected['ruby']}.gemspec").write_text(
        f'spec.name = "{expected["ruby"]}"\n', encoding="utf-8"
    )
    (ruby_dir / "version.rb").write_text(f'module Crawlora\n  VERSION = "{VERSION}"\nend\n', encoding="utf-8")
    java_dir = root / "java"
    java_dir.mkdir()
    (java_dir / "pom.xml").write_text(
        f'<project xmlns="http://maven.apache.org/POM/4.0.0"><groupId>{expected["maven_group"]}</groupId>'
        f'<artifactId>{expected["maven_artifact"]}</artifactId><version>{VERSION}</version></project>',
        encoding="utf-8",
    )
    php_dir = root / "php"
    php_dir.mkdir()
    composer = {
        "name": expected["packagist"],
        "support": {"source": config["repository"]},
    }
    (root / "composer.json").write_text(json.dumps(composer), encoding="utf-8")
    (php_dir / "composer.json").write_text(json.dumps(composer), encoding="utf-8")
    (root / "openapi").mkdir()
    (root / "openapi" / "public.json").write_text("{}\n", encoding="utf-8")
    return config


def http_fixture(platform: str = "sofascore", *, npm: int = 404, pypi: int = 404,
                 go: int = 404, ruby: int = 404, maven: int = 404, packagist: int = 404,
                 github_packages: bool = False,
                 release_status: int = 200, release_payload: dict | None = None) -> FakeHTTP:
    names = SUPPORTED[platform]
    statuses = {"npm": npm, "pypi": pypi, "go": go, "ruby": ruby, "maven": maven, "packagist": packagist}
    payloads = {
        "npm": {"version": VERSION},
        "pypi": {"info": {"version": VERSION}},
        "go": {"Version": "v" + VERSION},
        "ruby": {"number": VERSION},
        "maven": (
            f'<project xmlns="http://maven.apache.org/POM/4.0.0"><groupId>{names["maven_group"]}</groupId>'
            f'<artifactId>{names["maven_artifact"]}</artifactId><version>{VERSION}</version></project>'
        ),
        "packagist": {"packages": {names["packagist"]: [{"version": "v" + VERSION}]}},
    }
    answers = {
        _registry_url(registry, names[name_key] if name_key in names else names["maven_artifact"], VERSION): (
            statuses[registry], (payloads[registry].encode() if registry == "maven" else json.dumps(payloads[registry]).encode()) if statuses[registry] == 200 else b"{}"
        )
        for registry, name_key in (("npm", "npm"), ("pypi", "pypi"), ("go", "go"), ("ruby", "ruby"),
                                   ("maven", "maven_artifact"), ("packagist", "packagist"))
    }
    answers.update({
        f"{GITHUB_PACKAGES_API}?package_type=maven&per_page=100": (
            200,
            json.dumps([
                {
                    "name": f"{names['maven_group']}:{names['maven_artifact']}",
                    "url": f"{GITHUB_PACKAGES_API}/maven/{quote(names['maven_group'] + ':' + names['maven_artifact'], safe='')}",
                    "repository": {"full_name": names["repository"]},
                }
            ] if github_packages else []).encode(),
        ),
        f"{GITHUB_API}/repos/{names['repository']}/releases/tags/v{VERSION}": (
            release_status,
            json.dumps(release_payload or {"tag_name": "v" + VERSION, "draft": False}).encode()
            if release_status == 200 else b"{}",
        ),
    })
    if github_packages:
        package_name = f"{names['maven_group']}:{names['maven_artifact']}"
        versions_url = f"{GITHUB_PACKAGES_API}/maven/{quote(package_name, safe='')}/versions?per_page=100"
        answers[versions_url] = (200, json.dumps([{"name": VERSION}]).encode())
    return FakeHTTP(answers)


class ReleaseSyncTests(unittest.TestCase):
    @unittest.skipIf(os.environ.get("PLATFORMSDK_RELEASE_SYNC_EXPORTED_TEST") == "1", "nested export check")
    def test_copied_package_discovers_tests_with_only_public_toolkit_files(self):
        with tempfile.TemporaryDirectory(prefix="platform-release-export-") as tmp:
            root = Path(tmp)
            scripts = root / "scripts"
            package = scripts / "_platformsdk"
            package.mkdir(parents=True)
            source = Path(__file__).resolve().parent
            for name in ("__init__.py", "release_sync.py", "test_release_sync.py"):
                shutil.copyfile(source / name, package / name)
            self.assertEqual(
                {path.name for path in package.iterdir()},
                {"__init__.py", "release_sync.py", "test_release_sync.py"},
            )
            env = dict(os.environ, PLATFORMSDK_RELEASE_SYNC_EXPORTED_TEST="1")
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", str(package), "-t", str(scripts),
                 "-p", "test_release_sync.py"],
                cwd=root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("Ran ", result.stderr)

    def with_repo(self, callback, *, platform: str = "sofascore"):
        with tempfile.TemporaryDirectory(prefix="platform-release-sync-") as tmp:
            root = Path(tmp)
            config = write_repo(root, platform)
            callback(root, config)

    def sync(self, root, config, http, runner, **kwargs):
        return sync_release(
            root,
            opener=http,
            runner=runner,
            environ={"GH_TOKEN": "mock-token"},
            **kwargs,
        )

    def test_all_registries_published_is_a_noop(self):
        def run(root, config):
            http = http_fixture(npm=200, pypi=200, go=200, ruby=200, maven=200, packagist=200, github_packages=True)
            runner = FakeRunner(config)
            report = self.sync(root, config, http, runner)
            self.assertEqual(report["published"], {
                "npm": True, "pypi": True, "go": True, "ruby": True, "maven": True, "packagist": True,
                "github_packages": True,
            })
            self.assertFalse(report["needs_release"])
            self.assertEqual(runner.commands, [])
            self.assertEqual(len(http.requests), 8)
        self.with_repo(run)

    def test_npm_git_plus_https_repository_url_is_accepted(self):
        def run(root, config):
            package_path = root / "javascript" / "package.json"
            package = json.loads(package_path.read_text())
            package["repository"]["url"] = "git+https://github.com/" + SUPPORTED[config["platform"]]["repository"] + ".git"
            package_path.write_text(json.dumps(package))
            report = self.sync(root, config, http_fixture(npm=200, pypi=200, go=200, ruby=200, maven=200, packagist=200, github_packages=True), FakeRunner(config))
            self.assertFalse(report["needs_release"])
        self.with_repo(run)

    def test_repository_mismatch_error_does_not_disclose_remote_credentials(self):
        def run(root, config):
            runner = FakeRunner(config, origin="https://user:secret-token@github.com/attacker/other.git")
            with self.assertRaises(ReleaseSyncError) as caught:
                self.sync(root, config, http_fixture(), runner)
            self.assertNotIn("secret-token", str(caught.exception))
            self.assertNotIn("attacker/other", str(caught.exception))
        self.with_repo(run)

    def test_partial_publication_retries_the_same_tag_and_version(self):
        def run(root, config):
            http = http_fixture(npm=200, pypi=404)
            runner = FakeRunner(config, remote_tag=TAG_COMMIT, tagged_config=config)
            report = self.sync(root, config, http, runner)
            self.assertTrue(report["needs_release"])
            self.assertEqual(report["version"], VERSION)
            self.assertEqual(report["tag_commit"], TAG_COMMIT)
            self.assertTrue(report["dispatched"])
            self.assertFalse(any(command[:3] == ["gh", "release", "create"] for command in runner.commands))
            dispatch = next(command for command in runner.commands if command[:3] == ["gh", "workflow", "run"])
            self.assertEqual(dispatch[dispatch.index("--ref") + 1], "v" + VERSION)
        self.with_repo(run)

    def test_npm_uses_json_accept_and_404_is_the_only_absent_result(self):
        def run(root, config):
            http = http_fixture(release_status=404)
            runner = FakeRunner(config)
            report = self.sync(root, config, http, runner, check_only=True)
            self.assertEqual(report["published"], {
                "npm": False, "pypi": False, "go": False, "ruby": False, "maven": False, "packagist": False,
                "github_packages": False,
            })
            npm_request = next(request for url, request, _ in http.requests if url.startswith(NPM_REGISTRY))
            self.assertEqual(npm_request.get_header("Accept"), "application/json")
            self.assertIsNone(npm_request.get_header("Authorization"))
            self.assertIn("%2F", npm_request.full_url)
            pypi_request = next(request for url, request, _ in http.requests if url.startswith(PYPI_JSON))
            self.assertEqual(pypi_request.get_header("Accept"), "application/json")
            self.assertIsNone(pypi_request.get_header("Authorization"))
            for prefix in (RUBYGEMS_API, PACKAGIST_P2, GO_PROXY):
                request = next(request for url, request, _ in http.requests if url.startswith(prefix))
                self.assertEqual(request.get_header("Accept"), "application/json")
                self.assertIsNone(request.get_header("Authorization"))
            maven_request = next(request for url, request, _ in http.requests if url.startswith(MAVEN_CENTRAL))
            self.assertEqual(maven_request.get_header("Accept"), "application/xml")
            packages_request = next(request for url, request, _ in http.requests if url.startswith(GITHUB_PACKAGES_API))
            self.assertEqual(packages_request.get_header("Authorization"), "Bearer mock-token")
            self.assertEqual(runner.commands, [])
        self.with_repo(run)

    def test_go_module_proxy_path_uses_the_case_escape_marker(self):
        url = _registry_url("go", "github.com/Crawlora-org/crawlora-sofascore", VERSION)
        self.assertIn("github.com/!crawlora-org/crawlora-sofascore/@v/v0.1.0.info", url)
        self.assertNotIn("%21", url)

    def test_wrong_version_malformed_json_and_forbidden_registry_fail_before_git_or_release_writes(self):
        def run(root, config):
            cases = [
                (_registry_url("npm", config["npm_name"], VERSION), 200, json.dumps({"version": "0.2.0"}).encode()),
                (_registry_url("npm", config["npm_name"], VERSION), 200, b"not-json"),
                (_registry_url("npm", config["npm_name"], VERSION), 403, b"{}"),
                (_registry_url("pypi", config["python_name"], VERSION), 200,
                 json.dumps({"info": {"version": "0.2.0"}}).encode()),
                (_registry_url("ruby", config["ruby_gem_name"], VERSION), 200,
                 json.dumps({"number": "0.2.0"}).encode()),
                (_registry_url("maven", config["maven_artifact_id"], VERSION), 200,
                 f'<project xmlns="http://maven.apache.org/POM/4.0.0"><groupId>net.crawlora</groupId><artifactId>{config["maven_artifact_id"]}</artifactId><version>0.2.0</version></project>'.encode()),
                (_registry_url("go", config["golang_module_name"], VERSION), 200,
                 json.dumps({"Version": "v0.2.0"}).encode()),
            ]
            for url, status, body in cases:
                with self.subTest(url=url, status=status, body=body):
                    http = http_fixture()
                    http.answers[url] = (status, body)
                    runner = FakeRunner(config)
                    with self.assertRaises(ReleaseSyncError):
                        self.sync(root, config, http, runner)
                    self.assertEqual(runner.commands, [])
        self.with_repo(run)

    def test_check_only_writes_requested_outputs_but_performs_no_github_actions(self):
        def run(root, config):
            http = http_fixture()
            runner = FakeRunner(config)
            report_path = root / "result.json"
            output_path = root / "github-output.txt"
            report = self.sync(
                root, config, http, runner, check_only=True,
                report_path=report_path, github_output=output_path,
            )
            self.assertTrue(report["needs_release"])
            self.assertFalse(report["dispatched"])
            self.assertEqual(runner.commands, [])
            self.assertEqual(json.loads(report_path.read_text()), report)
            self.assertIn("needs_release=true", output_path.read_text())
            self.assertIn("dispatched=false", output_path.read_text())
            self.assertIn(f"version={VERSION}", output_path.read_text())
        self.with_repo(run)

    def test_existing_tag_requires_matching_manifest_and_packaged_content(self):
        def run(root, config):
            for tagged, diff in (
                ({**config, "version": "0.2.0"}, 0),
                ({**config, "contract_revision": "other-contract"}, 0),
                (config, 1),
            ):
                with self.subTest(tagged=tagged["contract_revision"], diff=diff):
                    http = http_fixture(pypi=404)
                    active = {"status": "in_progress", "headBranch": "v" + VERSION, "headSha": TAG_COMMIT}
                    runner = FakeRunner(
                        config, remote_tag=TAG_COMMIT, tagged_config=tagged, diff_status=diff, runs=[active]
                    )
                    with self.assertRaises(ReleaseSyncError):
                        self.sync(root, config, http, runner)
                    self.assertFalse(any(c[:3] == ["gh", "run", "list"] for c in runner.commands))
                    self.assertFalse(any(c[:3] == ["gh", "workflow", "run"] for c in runner.commands))
                    self.assertFalse(any(c[:3] == ["gh", "release", "create"] for c in runner.commands))
        self.with_repo(run)

    def test_missing_tag_creates_release_at_exact_head_then_verifies_and_dispatches(self):
        def run(root, config):
            http = http_fixture(release_status=404)
            runner = FakeRunner(config, tagged_config=config)
            report = self.sync(root, config, http, runner)
            create = next(c for c in runner.commands if c[:3] == ["gh", "release", "create"])
            self.assertEqual(create[create.index("--target") + 1], HEAD)
            self.assertTrue(Path(create[create.index("--notes-file") + 1]).exists() is False)
            self.assertEqual(report["tag_commit"], HEAD)
            self.assertTrue(report["dispatched"])
            self.assertLess(runner.commands.index(create), next(i for i,c in enumerate(runner.commands) if c[:3] == ["gh", "workflow", "run"]))
        self.with_repo(run)

    def test_active_same_tag_and_commit_skips_duplicate_dispatch(self):
        def run(root, config):
            active = {"status": "in_progress", "headBranch": "v" + VERSION, "headSha": TAG_COMMIT,
                      "databaseId": 88, "url": "https://github.com/example/run/88"}
            runner = FakeRunner(config, remote_tag=TAG_COMMIT, runs=[active])
            report = self.sync(root, config, http_fixture(pypi=404), runner)
            self.assertEqual(report["active_run"], active)
            self.assertFalse(report["dispatched"])
            self.assertFalse(any(c[:3] == ["gh", "workflow", "run"] for c in runner.commands))
            self.assertFalse(any(c[:3] == ["gh", "release", "create"] for c in runner.commands))
        self.with_repo(run)

    def test_completed_failed_run_retries(self):
        def run(root, config):
            completed = {"status": "completed", "headBranch": "v" + VERSION, "headSha": TAG_COMMIT,
                         "databaseId": 90, "url": "https://github.com/example/run/90", "conclusion": "failure"}
            runner = FakeRunner(config, remote_tag=TAG_COMMIT, runs=[completed])
            report = self.sync(root, config, http_fixture(pypi=404), runner)
            self.assertTrue(report["dispatched"])
        self.with_repo(run)

    def test_network_error_and_local_moved_tag_fail_before_github_writes(self):
        def run(root, config):
            class OfflineHTTP:
                def __call__(self, request, timeout):
                    raise URLError("offline")

            runner = FakeRunner(config)
            with self.assertRaisesRegex(ReleaseSyncError, "failed"):
                self.sync(root, config, OfflineHTTP(), runner)
            self.assertEqual(runner.commands, [])

            runner = FakeRunner(config, local_tag=TAG_COMMIT)
            with self.assertRaisesRegex(ReleaseSyncError, "another commit"):
                self.sync(root, config, http_fixture(release_status=404), runner)
            self.assertFalse(any(c[:3] == ["gh", "release", "create"] for c in runner.commands))
            self.assertFalse(any(c[:3] == ["gh", "workflow", "run"] for c in runner.commands))
        self.with_repo(run)

    def test_release_api_forbidden_is_not_classified_as_absent(self):
        def run(root, config):
            http = http_fixture(pypi=404, release_status=403)
            runner = FakeRunner(config)
            with self.assertRaisesRegex(ReleaseSyncError, "HTTP 403"):
                self.sync(root, config, http, runner)
            self.assertFalse(any(c[:3] == ["gh", "release", "create"] for c in runner.commands))
            self.assertFalse(any(c[:3] == ["gh", "workflow", "run"] for c in runner.commands))
        self.with_repo(run)


if __name__ == "__main__":
    unittest.main()
