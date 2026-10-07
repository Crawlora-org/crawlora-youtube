import test from "node:test";
import assert from "node:assert/strict";
import {
  {{class_name}}, CrawloraClientError, CrawloraNetworkError,
  CrawloraServerError, groups, operations, operationCount
} from "../src/index.js";

const json = (data, status = 200, headers = {}) => new Response(JSON.stringify(data), {
  status, headers: { "content-type": "application/json", ...headers }
});

test("exports only this platform and exposes direct and grouped methods", async () => {
  const client = new {{class_name}}({ apiKey: "test-key", fetch: async () => json({ ok: true }) });
  assert.equal(operationCount, Object.keys(operations).length);
  assert.deepEqual(Object.keys(groups), [{{group_name_json}}]);
  assert.equal(typeof client[{{first_method_json}}], "function");
  assert.equal(typeof client[{{group_name_json}}][{{first_method_json}}], "function");
});

test("serializes required query/path values, adds API key and platform User-Agent", async () => {
  let seen;
  const client = new {{class_name}}({ apiKey: "secret", fetch: async (url, init) => {
    seen = { url: String(url), headers: init.headers };
    return json({ ok: true });
  } });
  await client.request({{first_operation_json}}, {{first_params_json}});
  assert.match(seen.url, /{{first_path_match}}/);
  assert.equal(seen.headers["x-api-key"], "secret");
  assert.equal(seen.headers["user-agent"], {{user_agent_json}});
});

test("allows caller User-Agent override and response text mode", async () => {
  let seen;
  const client = new {{class_name}}({ apiKey: "key", userAgent: "custom-agent", fetch: async (_url, init) => {
    seen = init.headers;
    return new Response("caption text", { headers: { "content-type": "text/plain" } });
  } });
  const result = await client.request({{text_operation_json}}, {{text_params_json}}, { responseType: "text" });
  assert.equal(seen["user-agent"], "custom-agent");
  assert.equal(result, "caption text");

  const rawFeed = "1~home|2~away\n";
  const autoClient = new {{class_name}}({ fetch: async () => new Response(rawFeed, {
    headers: { "content-type": "text/plain" }
  }) });
  assert.equal(await autoClient.request({{text_operation_json}}, {{text_params_json}}), rawFeed);
});

test("maps API errors and retries server failures", async () => {
  let calls = 0;
  const client = new {{class_name}}({ apiKey: "key", retries: 1, retryDelay: 0, fetch: async () => {
    calls++;
    return calls === 1 ? json({ msg: "try again" }, 503) : json({ ok: true });
  } });
  assert.deepEqual(await client.request({{first_operation_json}}, {{first_params_json}}), { ok: true });
  assert.equal(calls, 2);

  const bad = new {{class_name}}({ fetch: async () => json({ msg: "bad input" }, 400) });
  await assert.rejects(bad.request({{first_operation_json}}, {{first_params_json}}), CrawloraClientError);
  const down = new {{class_name}}({ fetch: async () => json({ msg: "down" }, 503) });
  await assert.rejects(down.request({{first_operation_json}}, {{first_params_json}}), CrawloraServerError);
});

test("reports timeout and caller cancellation as network errors", async () => {
  const hanging = (_url, { signal }) => new Promise((_resolve, reject) => {
    signal.addEventListener("abort", () => reject(new Error("aborted")), { once: true });
  });
  const timed = new {{class_name}}({ timeout: 5, fetch: hanging });
  await assert.rejects(timed.request({{first_operation_json}}, {{first_params_json}}), CrawloraNetworkError);

  const controller = new AbortController();
  const aborted = new {{class_name}}({ fetch: hanging });
  const pending = aborted.request({{first_operation_json}}, {{first_params_json}}, { signal: controller.signal });
  controller.abort();
  await assert.rejects(pending, CrawloraNetworkError);
});
