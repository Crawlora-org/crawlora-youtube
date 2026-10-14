# Crawlora YouTube API client for Java

The official Java client for Crawlora's hosted YouTube API. It exposes 14 endpoints covering search, channels, videos, playlists, comments, captions, and transcripts. Requests use your `x-api-key`; the client does not connect to the upstream site directly.

## Install

```xml
<dependency>
  <groupId>net.crawlora</groupId>
  <artifactId>crawlora-youtube</artifactId>
  <version>0.2.0</version>
</dependency>
```

## Use

Create an account at [crawlora.net](https://crawlora.net/signup?utm_source=maven-central&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-java-signup), then open the [Crawlora console](https://crawlora.net/app?utm_source=maven-central&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-java-console) to get an API key.

```java
import net.crawlora.youtube.Client;
import java.time.Duration;
import java.util.Map;

try (Client client = new Client(System.getenv("CRAWLORA_API_KEY"))) {
    Object result = client.captions(Map.ofEntries(Map.entry("id", "sample")));
    System.out.println(result);
}
```

Each operation has a direct method that accepts the parameters documented for that endpoint. Use `client.request(operationId, params)` for generic dispatch. `Client.OPERATION_IDS`, `Client.OPERATION_COUNT`, `client.getOperationIds()`, and `client.getOperationCount()` describe this platform's operations only.

For custom hosted API routing and timeouts, use `new Client(apiKey, baseUrl, Duration.ofSeconds(20))`. Text responses are returned as `String`; JSON responses are parsed into Java maps, lists, and scalar values.

## Supported YouTube API endpoints

Browse every route included in this Java package. The [endpoint reference](https://github.com/Crawlora-org/crawlora-youtube/blob/main/docs/usage.md) also lists parameters and response details.

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

## Links

- [Crawlora](https://crawlora.net/?utm_source=maven-central&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-java-homepage)
- [Crawlora platform clients](https://github.com/Crawlora-org/crawlora-youtube)
- [API documentation](https://crawlora.net/docs?utm_source=maven-central&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-java-api-docs)
