# Crawlora YouTube PHP client

This package calls the Crawlora hosted API at `https://api.crawlora.net/api/v1`. It does not call or scrape YouTube directly. Requests require a Crawlora API key and use your Crawlora account's service plan.

## Install

```sh
composer require crawlora/youtube
```

Create an account at [crawlora.net](https://crawlora.net/signup), open the [Crawlora console](https://crawlora.net/app) to get an API key, then set `CRAWLORA_API_KEY` in your environment.

```php
<?php
require __DIR__ . '/vendor/autoload.php';

$client = new Crawlora\Youtube\Client(apiKey: getenv('CRAWLORA_API_KEY'));
$result = $client->request("youtube-channel-search", ['id' => 'sample-id', 'q' => 'science explainers']);
print_r($result);
$client->close();
```

The client uses PHP cURL and JSON. Constructor options are `apiKey`, `baseUrl`, `timeout`, and an optional callable `transport` for tests. Call a generated method for direct access to each supported operation, or `request($operationId, $params, $responseType)` to dispatch by operation ID. Set `$responseType` to `text` for raw text output such as transcript formats. The package contains 14 operations and follows contract revision `sha256:677d4bc412f42cf0083135b32bf36b478ab37efbea5f35fc5e8b6e86caaf6a68`.

See [Crawlora](https://crawlora.net/), the [API documentation](https://crawlora.net/docs), and [the package repository](https://github.com/Crawlora-org/crawlora-youtube) for account setup and the complete operation reference.
