"""Create or regenerate focused npm and Python client repositories."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "platformsdk"

from .spec import PLATFORMS, config_for, dumps, select


def regenerate(root: Path) -> None:
    config = json.loads((root / "platform.json").read_text())
    spec = json.loads((root / "openapi/public.json").read_text())
    # Re-selection validates the complete scope and schema closure even when
    # running generation from an already-selected public repository.
    spec = select(spec, config["platform"])
    assets = Path(__file__).resolve().parent / "vendor"
    for name in ["javascript", "python", "documentation"]:
        emitter = importlib.import_module("." + name, __package__)
        emitter.emit(root, config, spec, assets)


def create(spec: dict, platform: str, root: Path, *, revision: str, version: str) -> None:
    config = config_for(platform, revision=revision, version=version)
    selected = select(spec, platform)
    config["source_contract_sha256"] = hashlib.sha256(dumps(spec).encode()).hexdigest()
    root.mkdir(parents=True, exist_ok=True)
    (root / "openapi").mkdir(exist_ok=True)
    (root / "platform.json").write_text(dumps(config))
    (root / "openapi/public.json").write_text(dumps(selected))
    code = root / "scripts/_platformsdk"
    code.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).resolve().parent
    for child in source.iterdir():
        # The synchronization checks also run in each public repository. Keep
        # their fixtures self-contained and their imports relative to this
        # package; the emitter tests remain private maintenance tooling.
        if (child.name.startswith("test_") and child.name not in {"test_sync.py", "test_release_sync.py"}) or child.name == "__pycache__":
            continue
        target = code / child.name
        if child.is_dir():
            shutil.copytree(child, target, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        elif child.suffix in {".py", ".json"}:
            shutil.copyfile(child, target)
    (root / "scripts/generate.py").write_text(
        '"""Regenerate clients, types, docs, and examples from the pinned public contract."""\n'
        'from pathlib import Path\nfrom _platformsdk.generate import regenerate\n\n'
        'regenerate(Path(__file__).resolve().parents[1])\n'
    )
    for script, module in [("sync_contract.py", "sync"), ("release_sync.py", "release_sync")]:
        (root / "scripts" / script).write_text(
            f'"""Run the platform {module} helper from this source checkout."""\n'
            f'from _platformsdk.{module} import main\n\n'
            'if __name__ == "__main__":\n    raise SystemExit(main())\n'
        )
    regenerate(root)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--platform", choices=PLATFORMS, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--contract-revision", required=True)
    parser.add_argument("--version", default="0.1.0")
    args = parser.parse_args()
    create(json.loads(args.spec.read_text()), args.platform, args.out,
           revision=args.contract_revision, version=args.version)


if __name__ == "__main__":
    main()
