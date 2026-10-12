# Crawlora YouTube API client for Ruby (`crawlora-youtube`)

This Ruby gem calls Crawlora's hosted YouTube API at `https://api.crawlora.net/api/v1`. It exposes 14 endpoints covering search, channels, videos, playlists, comments, captions, and transcripts; it does not call or scrape YouTube directly. Requests require your Crawlora API key and use your account's service plan.

## Install

```ruby
gem "crawlora-youtube"
```

Create an account at [crawlora.net](https://crawlora.net/signup?utm_source=rubygems&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-ruby-signup), open the [Crawlora console](https://crawlora.net/app?utm_source=rubygems&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-ruby-console) to get an API key, and set `CRAWLORA_API_KEY` before running the client:

```ruby
require "json"
require "crawlora/youtube"

client = Crawlora::Youtube::Client.new
result = client.request("youtube-search", JSON.parse("{\"q\": \"science explainers\"}"))
puts result
client.close
```

Use an operation-specific method for normal calls. `request(operation_id, params = {}, response_type: :auto)` is available for every operation. `response_type: :text` returns raw response text. This gem includes 14 API operations.

```ruby
client = Crawlora::Youtube::Client.new(api_key: ENV.fetch("CRAWLORA_API_KEY"), timeout: 30)
# client.<operation_method>(<endpoint parameters>)
client.close
```

Client options include `api_key`, `base_url`, and `timeout`. Ruby stdlib provides the HTTP and JSON support.

## Supported YouTube API endpoints

Browse every route included in this gem. The [endpoint reference](https://github.com/Crawlora-org/crawlora-youtube/blob/main/docs/usage.md) includes parameter and response details.

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

See [Crawlora](https://crawlora.net/?utm_source=rubygems&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-ruby-homepage), the [API documentation](https://crawlora.net/docs?utm_source=rubygems&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-ruby-api-docs), and [the package repository](https://github.com/Crawlora-org/crawlora-youtube) for account setup, the API operation reference, and release history.
