# Crawlora YouTube Java Client

The official Java client for Crawlora's hosted YouTube API. It calls Crawlora's hosted API with your `x-api-key`; it does not connect to the upstream site directly.

## Install

```xml
<dependency>
  <groupId>net.crawlora</groupId>
  <artifactId>crawlora-youtube</artifactId>
  <version>0.1.4</version>
</dependency>
```

## Use

Create an account at [crawlora.net](https://crawlora.net/signup), then open the [Crawlora console](https://crawlora.net/app) to get an API key.

```java
import net.crawlora.youtube.Client;
import java.time.Duration;
import java.util.List;
import java.util.Map;

try (Client client = new Client(System.getenv("CRAWLORA_API_KEY"))) {
    Object result = client.captions(Map.ofEntries(Map.entry("id", "sample")));
    System.out.println(result);
}
```

Every selected operation has a direct method that accepts the parameter names from its endpoint contract. Use `client.request(operationId, params)` for generic dispatch. `Client.OPERATION_IDS`, `Client.OPERATION_COUNT`, `client.getOperationIds()`, and `client.getOperationCount()` describe this platform's operations only.

For custom hosted API routing and timeouts, use `new Client(apiKey, baseUrl, Duration.ofSeconds(20))`. YouTube transcript formats that return text are returned as `String`; JSON responses are parsed into Java maps, lists, and scalar values.

## Links

- [Crawlora](https://crawlora.net/)
- [Crawlora platform clients](https://github.com/Crawlora-org/crawlora-youtube)
- [API documentation](https://crawlora.net/docs)
