# Crawlora YouTube API client for PHP (`crawlora/youtube`)

This PHP package calls Crawlora's hosted YouTube API at `https://api.crawlora.net/api/v1`. It exposes 14 endpoints covering search, channels, videos, playlists, comments, captions, and transcripts. It does not call or scrape YouTube directly. Requests require a Crawlora API key and use your Crawlora account's service plan.

## Install

```sh
composer require crawlora/youtube
```

Create an account at [crawlora.net](https://crawlora.net/signup?utm_source=packagist&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-php-signup), open the [Crawlora console](https://crawlora.net/app?utm_source=packagist&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-php-console) to get an API key, then set `CRAWLORA_API_KEY` in your environment.

```php
<?php
require __DIR__ . '/vendor/autoload.php';

$client = new Crawlora\Youtube\Client(apiKey: getenv('CRAWLORA_API_KEY'));
$result = $client->request("youtube-search", ['q' => 'science explainers']);
print_r($result);
$client->close();
```

The client uses PHP cURL and JSON. Constructor options are `apiKey`, `baseUrl`, and `timeout`. Call the operation-specific method for direct access to each supported operation, or `request($operationId, $params, $responseType)` to dispatch by operation ID. Set `$responseType` to `text` for raw text output such as transcript formats. The package includes 14 API operations.

## Supported YouTube API endpoints

Browse every route included in this Composer package. The [endpoint reference](https://github.com/Crawlora-org/crawlora-youtube/blob/main/docs/usage.md) includes parameter and response details.

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

See [Crawlora](https://crawlora.net/?utm_source=packagist&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-php-homepage), the [API documentation](https://crawlora.net/docs?utm_source=packagist&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-php-api-docs), and the [PHP client source](https://github.com/Crawlora-org/crawlora-youtube). The complete operation and parameter reference is in the [platform repository](https://github.com/Crawlora-org/crawlora-youtube/blob/main/docs/usage.md).
