import asyncio
import unittest

import crawlora_youtube as client_package
from crawlora_youtube.client import _Response


class TextTranscriptTests(unittest.TestCase):
    def test_sync_text_formats_return_plain_text(self):
        class Transport:
            def __init__(self):
                self.requests = []

            def __call__(self, request, _timeout):
                self.requests.append(request)
                return _Response(200, {"Content-Type": "text/plain"}, b"line one\nline two")

        transport = Transport()
        with client_package.Client(api_key="fixture-key", transport=transport) as client:
            self.assertEqual(client.transcript(id="video-id", format="text"), "line one\nline two")
            self.assertEqual(client.transcript(id="video-id", format="srt"), "line one\nline two")
            self.assertEqual(client.youtube.transcript(id="video-id", format="vtt"), "line one\nline two")

    def test_async_text_formats_return_plain_text(self):
        async_module = __import__("crawlora_youtube.async_client", fromlist=["httpx"])
        async_module.httpx = None

        class Transport:
            def __call__(self, _request, _timeout):
                return _Response(200, {"Content-Type": "text/plain"}, b"line one\nline two")

        async def run():
            async with client_package.AsyncClient(api_key="fixture-key", transport=Transport()) as client:
                self.assertEqual(await client.transcript(id="video-id", format="text"), "line one\nline two")
                self.assertEqual(await client.youtube.transcript(id="video-id", format="srt"), "line one\nline two")

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
