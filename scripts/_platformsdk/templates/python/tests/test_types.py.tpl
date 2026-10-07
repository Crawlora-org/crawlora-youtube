import os
import tempfile
import unittest
from pathlib import Path

from mypy import api

import {{MODULE_NAME}} as client_package


TYPECHECK_SOURCE = '''
from typing_extensions import assert_type
from {{MODULE_NAME}} import AsyncClient, {{ASYNC_CLASS_NAME}}, Client, {{CLASS_NAME}}
from {{MODULE_NAME}}.platform import {{TEST_RESPONSE_TYPE}}

def check_sync() -> None:
    named: {{CLASS_NAME}} = Client(api_key="key")
    with Client(api_key="key") as client:
        assert_type(client.{{TEST_METHOD_IDENT}}({{TEST_DEFAULT_ARGS}}), {{TEST_RESPONSE_TYPE}})
        assert_type(client.{{TEST_METHOD_IDENT}}({{TEST_TEXT_ARGS}}), str)
        assert_type(client.{{TEST_METHOD_IDENT}}({{TEST_STREAM_ARGS}}).read(), bytes)
        assert_type(client.request({{TEST_OPERATION_ID}}, {{TEST_PARAMS}}), {{TEST_RESPONSE_TYPE}})
        assert_type(client.{{TEST_GROUP_IDENT}}.{{TEST_METHOD_IDENT}}({{TEST_DEFAULT_ARGS}}), {{TEST_RESPONSE_TYPE}})
        assert_type(client.{{TEST_GROUP_IDENT}}.{{TEST_METHOD_IDENT}}({{TEST_TEXT_ARGS}}), str)
        assert_type(client.{{TEST_GROUP_IDENT}}.{{TEST_METHOD_IDENT}}({{TEST_STREAM_ARGS}}).read(), bytes)
{{TEST_FORMAT_TEXT_ASSERTION}}
{{TEST_FORMAT_TEXT_GROUP_ASSERTION}}

async def check_async() -> None:
    named: {{ASYNC_CLASS_NAME}} = AsyncClient(api_key="key")
    async with AsyncClient(api_key="key") as client:
        assert_type(await client.{{TEST_METHOD_IDENT}}({{TEST_DEFAULT_ARGS}}), {{TEST_RESPONSE_TYPE}})
        assert_type(await client.{{TEST_METHOD_IDENT}}({{TEST_TEXT_ARGS}}), str)
        assert_type((await client.{{TEST_METHOD_IDENT}}({{TEST_STREAM_ARGS}})).read(), bytes)
        assert_type(await client.{{TEST_GROUP_IDENT}}.{{TEST_METHOD_IDENT}}({{TEST_DEFAULT_ARGS}}), {{TEST_RESPONSE_TYPE}})
        assert_type(await client.{{TEST_GROUP_IDENT}}.{{TEST_METHOD_IDENT}}({{TEST_TEXT_ARGS}}), str)
        assert_type((await client.{{TEST_GROUP_IDENT}}.{{TEST_METHOD_IDENT}}({{TEST_STREAM_ARGS}})).read(), bytes)
{{TEST_FORMAT_TEXT_ASYNC_ASSERTION}}
{{TEST_FORMAT_TEXT_GROUP_ASYNC_ASSERTION}}
'''

NEGATIVE_SOURCE = '''
from {{MODULE_NAME}} import Client
Client().{{TEST_METHOD_IDENT}}({{TEST_BAD_ARGS}})
Client().{{TEST_METHOD_IDENT}}()
'''


class PublicTypingTests(unittest.TestCase):
    def setUp(self):
        self.package_root = Path(client_package.__file__).resolve().parent
        self.old_mypy_path = os.environ.get("MYPYPATH")
        parent = str(self.package_root.parent)
        os.environ["MYPYPATH"] = parent if self.old_mypy_path is None else parent + os.pathsep + self.old_mypy_path

    def tearDown(self):
        if self.old_mypy_path is None:
            os.environ.pop("MYPYPATH", None)
        else:
            os.environ["MYPYPATH"] = self.old_mypy_path

    def test_installed_platform_stub_is_well_formed(self):
        stdout, stderr, status = api.run([
            "--strict", "--python-version=3.10", "--no-incremental", "--follow-imports=silent",
            str(self.package_root / "platform.pyi"),
        ])
        self.assertEqual(status, 0, stdout + stderr)

    def test_installed_client_signatures_accept_valid_calls_and_reject_invalid_calls(self):
        with tempfile.TemporaryDirectory(prefix="crawlora-python-mypy-") as temp:
            source_path = Path(temp) / "typecheck.py"
            source_path.write_text(TYPECHECK_SOURCE, encoding="utf-8")
            stdout, stderr, status = api.run([
                "--strict", "--python-version=3.10", "--no-incremental", "--follow-imports=silent", str(source_path),
            ])
        self.assertEqual(status, 0, stdout + stderr)

        with tempfile.TemporaryDirectory(prefix="crawlora-python-mypy-negative-") as temp:
            source_path = Path(temp) / "invalid.py"
            source_path.write_text(NEGATIVE_SOURCE, encoding="utf-8")
            stdout, stderr, status = api.run([
                "--strict", "--python-version=3.10", "--no-incremental", "--follow-imports=silent", str(source_path),
            ])
        self.assertNotEqual(status, 0, stdout + stderr)
        self.assertIn("{{TEST_BAD_FIELD}}", stdout + stderr)


if __name__ == "__main__":
    unittest.main()
