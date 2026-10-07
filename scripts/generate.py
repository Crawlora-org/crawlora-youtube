"""Regenerate clients, types, docs, and examples from the pinned public contract."""
from pathlib import Path
from _platformsdk.generate import regenerate

regenerate(Path(__file__).resolve().parents[1])
