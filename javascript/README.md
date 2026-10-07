# @crawlora-org/youtube

JavaScript and TypeScript client for Crawlora's hosted YouTube API.
It calls [Crawlora](https://crawlora.net); it does not run a browser or scrape YouTube locally. A Crawlora account and `CRAWLORA_API_KEY` are required, and API use is billed under your Crawlora account. Crawlora is independent from and not endorsed by YouTube or its owners.

## Install

```sh
npm install @crawlora-org/youtube
```

## Get an API key

Create an account at [crawlora.net](https://crawlora.net/signup), then open the [Crawlora console](https://crawlora.net/app) for API-key setup. Set your key in the shell before running the client:

```sh
export CRAWLORA_API_KEY="your-crawlora-api-key"
```

## Use

```js
import process from "node:process";
import { YouTubeClient } from "@crawlora-org/youtube";

const apiKey = process.env.CRAWLORA_API_KEY;
if (!apiKey) throw new Error("Set CRAWLORA_API_KEY before running this example.");
const client = new YouTubeClient({ apiKey });
const result1 = await client.search({ q: "science explainers", type: "video" });
console.log(result1);
const result2 = await client.video({ id: "dQw4w9WgXcQ" });
console.log(result2);
const result3 = await client.transcript({ id: "dQw4w9WgXcQ", format: "text" });
console.log(result3);
```

The client also exports `Client` as an alias for `YouTubeClient`. Operation
methods are available directly in camelCase and through the `youtube`
group. See the full method and parameter list in the [online reference](https://github.com/Crawlora-org/crawlora-youtube/blob/main/docs/usage.md).

Methods return promises and can be awaited. See the [runnable example](https://github.com/Crawlora-org/crawlora-youtube/blob/main/examples/javascript.mjs) for contract-backed examples and text transcript output where supported.

The import snippet above is for a project where this npm package is installed. The checked-in repository example instead imports `../javascript/src/index.js` so it runs directly from the repository root; see the [source-checkout instructions](https://github.com/Crawlora-org/crawlora-youtube#run-examples-from-a-source-checkout).

## Configuration

Pass your key through `apiKey` or set `CRAWLORA_API_KEY` and read it from the
environment. Keep credentials out of source control and logs. Requests are
made to Crawlora's hosted API; response data and availability follow that
service's current contract.
