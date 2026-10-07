import asyncio
import copy
import unittest

import crawlora_youtube as client_package
from crawlora_youtube.client import _Response


TEST_OPERATION_ID = 'youtube-transcript'
TEST_METHOD_NAME = 'transcript'
TEST_GROUP_NAME = 'youtube'
TEST_PARAMS = {'id': 'test value', 'lang': 'test value'}
TEST_URL = 'https://api.example.test/youtube/transcript/test%20value?lang=test+value'
TEST_HAS_API_KEY = True


class MockTransport:
    def __init__(self, responses=None):
        self.responses = list(responses or [])
        self.requests = []

    def __call__(self, request, _timeout):
        self.requests.append(request)
        status, content_type, body = self.responses.pop(0) if self.responses else (200, "application/json", b"{}")
        return _Response(status, {"Content-Type": content_type}, body)


class PackageTests(unittest.TestCase):
    def test_platform_metadata_and_aliases(self):
        self.assertEqual(client_package.PLATFORM, "youtube")
        self.assertEqual(client_package.__version__, "0.1.3")
        self.assertIs(client_package.Client, client_package.YouTubeClient)
        self.assertIs(client_package.AsyncClient, client_package.AsyncYouTubeClient)
        self.assertEqual(client_package.OPERATION_COUNT, len(client_package.OPERATION_IDS))

    def test_sync_request_auth_serialization_group_and_error_mapping(self):
        transport = MockTransport()
        with client_package.Client(api_key="fixture-key", base_url="https://api.example.test", transport=transport) as client:
            result = getattr(client, TEST_METHOD_NAME)(**copy.deepcopy(TEST_PARAMS))
            self.assertEqual(result, {})
            self.assertEqual(transport.requests[-1].full_url, TEST_URL)
            self.assertEqual(transport.requests[-1].get_header("X-api-key"), "fixture-key" if TEST_HAS_API_KEY else None)

            group = getattr(client, TEST_GROUP_NAME)
            getattr(group, TEST_METHOD_NAME)(**copy.deepcopy(TEST_PARAMS))
            self.assertEqual(transport.requests[-1].full_url, TEST_URL)

            with self.assertRaises(ValueError):
                client.request("__another_platform_operation__", {})

        for status, error_type in ((404, client_package.CrawloraClientError), (503, client_package.CrawloraServerError)):
            transport = MockTransport([(status, "application/json", b'{"code":%d}' % status)])
            with client_package.Client(transport=transport) as client:
                with self.assertRaises(error_type) as raised:
                    getattr(client, TEST_METHOD_NAME)(**copy.deepcopy(TEST_PARAMS))
                self.assertEqual(raised.exception.status, status)

    def test_sync_retries_transient_server_failure(self):
        transport = MockTransport([
            (503, "application/json", b'{"code":503}'),
            (200, "application/json", b"{}"),
        ])
        retries = []
        with client_package.Client(transport=transport, retries=1, retry_delay=0, on_retry=lambda *args: retries.append(args)) as client:
            self.assertEqual(getattr(client, TEST_METHOD_NAME)(**copy.deepcopy(TEST_PARAMS)), {})
        self.assertEqual(len(transport.requests), 2)
        self.assertEqual(len(retries), 1)

    def test_async_request_and_context_manager(self):
        async_module = __import__("crawlora_youtube.async_client", fromlist=["httpx"])
        async_module.httpx = None  # exercise the dependency-free asyncio.to_thread fallback
        transport = MockTransport()

        async def run():
            async with client_package.AsyncClient(api_key="fixture-key", base_url="https://api.example.test", transport=transport) as client:
                result = await getattr(client, TEST_METHOD_NAME)(**copy.deepcopy(TEST_PARAMS))
                self.assertEqual(result, {})
                self.assertEqual(transport.requests[-1].full_url, TEST_URL)
                group = getattr(client, TEST_GROUP_NAME)
                self.assertEqual(await getattr(group, TEST_METHOD_NAME)(**copy.deepcopy(TEST_PARAMS)), {})
                self.assertEqual(transport.requests[-1].full_url, TEST_URL)

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
