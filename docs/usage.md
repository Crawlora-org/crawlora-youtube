# YouTube client usage

The `@crawlora-org/youtube` and `crawlora-youtube` packages call Crawlora's hosted API. Set `CRAWLORA_API_KEY` to a key for your Crawlora account before making requests. Service usage is billed under that account. These clients do not run a browser or scrape YouTube locally; Crawlora is independent from and not endorsed by YouTube or its owners.

The package tracks the public API contract revision `sha256:677d4bc412f42cf0083135b32bf36b478ab37efbea5f35fc5e8b6e86caaf6a68` bundled with release `0.1.5`. Maintainers can preview daily contract updates with the repository's `Sync live API contract` workflow; unchanged contracts do not produce package releases.

Both packages expose all 14 operations in the bundled API contract. JavaScript uses camelCase methods and Python uses snake_case methods. Methods also remain available through the `youtube` group and the generated `Client` alias.

## Examples

The checked-in examples discover current entities or feeds before making the related requests, using parameter names and values supported by the API contract:

- [JavaScript](../examples/javascript.mjs)
- [Python](../examples/python.py)

YouTube clients include all 14 contract operations; transcript calls can request plain text with `format="text"` (Python) or `format: "text"` (JavaScript). The contract lists these transcript formats: `json`, `text`, `srt`, `vtt`.

## Complete operation reference

Required and optional parameter names below come from this package's generated OpenAPI contract. Path parameters are passed alongside query and body values in the same method argument object/keywords.

| Method | Endpoint | Parameters | Description |
| --- | --- | --- | --- |
| `captions` / `captions` | `GET /youtube/captions/{id}` | `id` (path, required), `lang` (query, optional) | Retrieve auto-generated or human captions |
| `channelPlaylists` / `channel_playlists` | `GET /youtube/channel/{id}/playlists` | `id` (path, required), `continuation_token` (query, optional) | Retrieve the playlists tab for a YouTube channel |
| `channelSearch` / `channel_search` | `GET /youtube/channel/{id}/search` | `id` (path, required), `q` (query, required), `continuation_token` (query, optional) | Search within a YouTube channel |
| `channelShorts` / `channel_shorts` | `GET /youtube/channel/{id}/shorts` | `id` (path, required) | Retrieve the shorts tab for a YouTube channel |
| `channelVideos` / `channel_videos` | `GET /youtube/channel/{id}/videos` | `id` (path, required), `continuation_token` (query, optional) | Retrieve the videos tab for a YouTube channel |
| `comments` / `comments` | `GET /youtube/comments/{id}` | `id` (path, required), `continuation_token` (query, optional) | Retrieve video comments (top-level & replies) |
| `playlist` / `playlist` | `GET /youtube/playlist/{id}` | `id` (path, required), `continuation_token` (query, optional) | Retrieve playlist metadata and items |
| `profile` / `profile` | `GET /youtube/profile/{id}` | `id` (path, required) | Retrieve channel profile |
| `search` / `search` | `GET /youtube/search` | `q` (query, optional), `search_query` (query, optional), `continuation_token` (query, optional), `type` (query, optional; values: `video`, `shorts`, `channel`, `playlist`, `movie`), `sort_by` (query, optional; values: `relevance`, `upload_date`, `view_count`, `popularity`, `rating`), `upload_date` (query, optional; values: `last_hour`, `today`, `this_week`, `this_month`, `this_year`), `duration` (query, optional; values: `under_3_minutes`, `three_to_20_minutes`, `over_20_minutes`, `under_3`, `three_to_20`, `over_20`, `short`, `medium`, `long`), `features` (query, optional), `hl` (query, optional), `gl` (query, optional), `params` (query, optional) | Search YouTube |
| `suggest` / `suggest` | `GET /youtube/suggest` | `q` (query, required), `count` (query, optional), `hl` (query, optional), `gl` (query, optional) | Suggest YouTube search queries |
| `tag` / `tag` | `GET /youtube/tag/{tag}` | `tag` (path, required), `type` (query, optional; values: `all`, `shorts`), `continuation_token` (query, optional) | Retrieve YouTube videos by tag |
| `transcript` / `transcript` | `GET /youtube/transcript/{id}` | `id` (path, required), `lang` (query, optional), `translate_to` (query, optional), `format` (query, optional; values: `json`, `text`, `srt`, `vtt`), `timestamps` (query, optional) | Retrieve transcript for a YouTube video |
| `transcriptLanguages` / `transcript_languages` | `GET /youtube/transcript/{id}/languages` | `id` (path, required) | List transcript languages for a YouTube video |
| `video` / `video` | `GET /youtube/video/{id}` | `id` (path, required) | Retrieve video metadata & captions |

## Client forms

- JavaScript: import `YouTubeClient` (also exported as `Client`) from `@crawlora-org/youtube`; use `new YouTubeClient({ apiKey })` and `await client.method({ ... })`.
- Python: import `YouTubeClient` (also exported as `Client`) from `crawlora_youtube`; use `with YouTubeClient(api_key=...) as client` and `client.method(...)`.
- Python async class: `AsyncYouTubeClient`, used with `async with` and `await`.

See the package READMEs for installation details. Keep API keys in environment variables or a secret store; do not commit them.
