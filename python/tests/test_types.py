import os
import tempfile
import unittest
from pathlib import Path

from mypy import api

import crawlora_youtube as client_package


class PublicTypingTests(unittest.TestCase):
    def test_installed_client_and_transcript_mode_types(self):
        source = '''
from typing_extensions import assert_type
from crawlora_youtube import AsyncClient, AsyncYouTubeClient, Client, YouTubeClient
from crawlora_youtube.platform import YoutubeTranscriptResponse

def check_sync() -> None:
    named: YouTubeClient = Client(api_key="key")
    with Client(api_key="key") as client:
        assert_type(client.transcript(id="video", format="text"), str)
        assert_type(client.transcript(id="video", format="srt"), str)
        assert_type(client.transcript(id="video", format="json"), YoutubeTranscriptResponse)
        assert_type(client.transcript(id="video", format="json", _response_type="text"), str)
        assert_type(client.transcript(id="video", format="json", _response_type="stream").read(), bytes)
        assert_type(client.transcript(id="video", format="text", _response_type="stream").read(), bytes)
        assert_type(client.request("youtube-transcript", {"id": "video"}), YoutubeTranscriptResponse)

async def check_async() -> None:
    named: AsyncYouTubeClient = AsyncClient(api_key="key")
    async with AsyncClient(api_key="key") as client:
        assert_type(await client.transcript(id="video", format="text"), str)
        assert_type(await client.transcript(id="video", format="vtt"), str)
        assert_type(await client.transcript(id="video", format="json"), YoutubeTranscriptResponse)
        assert_type(await client.transcript(id="video", format="json", _response_type="text"), str)
        assert_type((await client.transcript(id="video", format="json", _response_type="stream")).read(), bytes)
        assert_type((await client.transcript(id="video", format="text", _response_type="stream")).read(), bytes)
'''
        with tempfile.TemporaryDirectory(prefix="crawlora-python-mypy-") as temp:
            source_path = Path(temp) / "typecheck.py"
            source_path.write_text(source, encoding="utf-8")
            old_mypy_path = os.environ.get("MYPYPATH")
            package_root = str(Path(client_package.__file__).resolve().parent.parent)
            os.environ["MYPYPATH"] = package_root if old_mypy_path is None else package_root + os.pathsep + old_mypy_path
            try:
                stdout, stderr, status = api.run(["--strict", "--python-version=3.10", "--no-incremental", str(source_path)])
            finally:
                if old_mypy_path is None:
                    os.environ.pop("MYPYPATH", None)
                else:
                    os.environ["MYPYPATH"] = old_mypy_path
        self.assertEqual(status, 0, stdout + stderr)

        negative = '''
from crawlora_youtube import Client
Client().transcript(format="json")
Client().search(q=123)
'''
        with tempfile.TemporaryDirectory(prefix="crawlora-python-mypy-negative-") as temp:
            source_path = Path(temp) / "invalid.py"
            source_path.write_text(negative, encoding="utf-8")
            old_mypy_path = os.environ.get("MYPYPATH")
            package_root = str(Path(client_package.__file__).resolve().parent.parent)
            os.environ["MYPYPATH"] = package_root if old_mypy_path is None else package_root + os.pathsep + old_mypy_path
            try:
                stdout, stderr, status = api.run(["--strict", "--python-version=3.10", "--no-incremental", str(source_path)])
            finally:
                if old_mypy_path is None:
                    os.environ.pop("MYPYPATH", None)
                else:
                    os.environ["MYPYPATH"] = old_mypy_path
        self.assertNotEqual(status, 0, stdout + stderr)
        self.assertIn("error:", stdout + stderr)


if __name__ == "__main__":
    unittest.main()
