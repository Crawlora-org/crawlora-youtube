# @crawlora-org/youtube — YouTube API client for JavaScript and TypeScript

JavaScript and TypeScript client for Crawlora's hosted YouTube API.
It exposes 14 API endpoints for search, channels, videos, playlists, comments, captions, and transcripts through [Crawlora](https://crawlora.net/?utm_source=npm&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-javascript-homepage). It does not run a browser or scrape YouTube locally. A Crawlora account and `CRAWLORA_API_KEY` are required, and API use is billed under your Crawlora account. Crawlora is independent from and not endorsed by YouTube or its owners.

## Install

```sh
npm install @crawlora-org/youtube
```

## Get an API key

Create an account at [crawlora.net](https://crawlora.net/signup?utm_source=npm&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-javascript-signup), then open the [Crawlora console](https://crawlora.net/app?utm_source=npm&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-javascript-console) for API-key setup. Set your key in the shell before running the client:

```sh
export CRAWLORA_API_KEY="your-crawlora-api-key"
```

## Use

Save this example as `example.mjs`, then run `node example.mjs` after installing the package and setting your API key.

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

Methods return promises and can be awaited. See the [runnable example](https://github.com/Crawlora-org/crawlora-youtube/blob/main/examples/javascript.mjs) for a complete usage example.

## Supported YouTube API endpoints

This package exposes each route below as a direct method and through the `youtube` group. See the [endpoint and parameter reference](https://github.com/Crawlora-org/crawlora-youtube/blob/main/docs/usage.md) for complete input details.

| Method | Endpoint | API operation | Description |
| --- | --- | --- | --- |
| `GET` | `/youtube/captions/{id}` | `youtube-captions` | Retrieve auto-generated or human captions |
| `GET` | `/youtube/channel/{id}/playlists` | `youtube-channel-playlists` | Retrieve the playlists tab for a YouTube channel |
| `GET` | `/youtube/channel/{id}/search` | `youtube-channel-search` | Search within a YouTube channel |
| `GET` | `/youtube/channel/{id}/shorts` | `youtube-channel-shorts` | Retrieve the shorts tab for a YouTube channel |
| `GET` | `/youtube/channel/{id}/videos` | `youtube-channel-videos` | Retrieve the videos tab for a YouTube channel |
| `GET` | `/youtube/comments/{id}` | `youtube-comments` | Retrieve video comments (top-level & replies) |
| `GET` | `/youtube/playlist/{id}` | `youtube-playlist` | Retrieve playlist metadata and items |
| `GET` | `/youtube/profile/{id}` | `youtube-profile` | Retrieve channel profile |
| `GET` | `/youtube/search` | `youtube-search` | Search YouTube |
| `GET` | `/youtube/suggest` | `youtube-suggest` | Suggest YouTube search queries |
| `GET` | `/youtube/tag/{tag}` | `youtube-tag` | Retrieve YouTube videos by tag |
| `GET` | `/youtube/transcript/{id}` | `youtube-transcript` | Retrieve transcript for a YouTube video |
| `GET` | `/youtube/transcript/{id}/languages` | `youtube-transcript-languages` | List transcript languages for a YouTube video |
| `GET` | `/youtube/video/{id}` | `youtube-video` | Retrieve video metadata & captions |

## Configuration

Pass your key through `apiKey` or set `CRAWLORA_API_KEY` and read it from the
environment. Keep credentials out of source control and logs. Requests are
made to Crawlora's hosted API. Response data and availability depend on
Crawlora's current API behavior.
