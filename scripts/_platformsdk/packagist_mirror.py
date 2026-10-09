"""Prepare a PHP-only Composer repository snapshot for Packagist."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys

_PACKAGE_ROOT_FILES = {"composer.json", "README.md", "CHANGELOG.md", "LICENSE"}
_PACKAGE_ROOT_DIRS = {"src", "tests"}
_FOREIGN_INSTALLS = (
    "npm install",
    "python -m pip install",
    "go get ",
    "gem install",
    "mvn ",
    "javascript / typescript:",
    "python:",
    "ruby:",
    "java:",
)


class MirrorError(ValueError):
    """The candidate does not contain only a valid PHP Composer package."""


def validate_package(source: Path, *, allow_git: bool = False) -> None:
    source = Path(source).resolve()
    if not source.is_dir():
        raise MirrorError(f"PHP package source directory is missing: {source}")
    entries = {entry.name for entry in source.iterdir()}
    if allow_git:
        entries.discard(".git")
    expected = _PACKAGE_ROOT_FILES | _PACKAGE_ROOT_DIRS
    if entries != expected:
        unexpected = sorted(entries - expected)
        missing = sorted(expected - entries)
        raise MirrorError(f"unexpected PHP package contents; unexpected={unexpected}, missing={missing}")
    for path in source.rglob("*"):
        if path.is_symlink():
            raise MirrorError(f"symbolic links are not allowed in the PHP package: {path.relative_to(source)}")

    try:
        manifest = json.loads((source / "composer.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MirrorError(f"invalid Composer manifest: {exc}") from exc
    name = manifest.get("name", "")
    if not isinstance(name, str) or not name.startswith("crawlora/"):
        raise MirrorError("Composer manifest must declare a Crawlora package name")
    if manifest.get("type", "library") != "library":
        raise MirrorError("Composer package type must be library")
    requirements = manifest.get("require", {})
    if not isinstance(requirements, dict) or not isinstance(requirements.get("php"), str):
        raise MirrorError("Composer manifest must declare its PHP version requirement")
    autoload = manifest.get("autoload", {}).get("psr-4", {})
    if not isinstance(autoload, dict) or not autoload:
        raise MirrorError("Composer manifest must define a PSR-4 PHP namespace")
    for relative in autoload.values():
        paths = relative if isinstance(relative, list) else [relative]
        if any(not isinstance(path, str) or not (source / path).is_dir() for path in paths):
            raise MirrorError("Composer PSR-4 paths must resolve inside the PHP package")

    readme = (source / "README.md").read_text(encoding="utf-8")
    lowered = readme.lower()
    if "composer require " + name not in lowered or "```php" not in lowered:
        raise MirrorError("Packagist README must contain this package's install command and a PHP example")
    if any(install in lowered for install in _FOREIGN_INSTALLS):
        raise MirrorError("Packagist README contains another language's install instructions")


def prepare(source: Path, target: Path) -> None:
    """Replace target contents with the validated, language-only package tree."""
    source = Path(source).resolve()
    target = Path(target).resolve()
    if source == target or source in target.parents or target in source.parents:
        raise MirrorError("source and destination must be separate directories")
    validate_package(source)
    target.mkdir(parents=True, exist_ok=True)
    for entry in target.iterdir():
        if entry.name == ".git":
            continue
        if entry.is_dir() and not entry.is_symlink():
            shutil.rmtree(entry)
        else:
            entry.unlink()
    for name in sorted(_PACKAGE_ROOT_FILES | _PACKAGE_ROOT_DIRS):
        origin = source / name
        destination = target / name
        if origin.is_dir():
            shutil.copytree(origin, destination)
        else:
            shutil.copy2(origin, destination)
    validate_package(target, allow_git=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="generated PHP package directory")
    parser.add_argument("--target", type=Path, required=True, help="checked-out PHP-only Git repository")
    args = parser.parse_args()
    try:
        prepare(args.source, args.target)
    except (MirrorError, OSError) as exc:
        print(f"Packagist PHP mirror failed: {exc}", file=sys.stderr)
        return 1
    count = sum(1 for path in args.target.rglob("*") if path.is_file() and path.name != ".git")
    print(f"Prepared PHP-only Composer source with {count} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
