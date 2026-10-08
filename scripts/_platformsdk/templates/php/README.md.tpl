# Crawlora {{DISPLAY_NAME}} PHP client

This package calls the Crawlora hosted API at `https://api.crawlora.net/api/v1`. It does not call or scrape {{DISPLAY_NAME}} directly. Requests require a Crawlora API key and use your Crawlora account's service plan.

## Install

```sh
composer require {{PACKAGE_NAME}}
```

Create an account at [crawlora.net](https://crawlora.net/signup), open the [Crawlora console](https://crawlora.net/app) to get an API key, then set `CRAWLORA_API_KEY` in your environment.

```php
<?php
require __DIR__ . '/vendor/autoload.php';

$client = new Crawlora\{{CLASS_NAME}}\Client(apiKey: getenv('CRAWLORA_API_KEY'));
$result = $client->request({{EXAMPLE_OPERATION_JSON}}, {{EXAMPLE_PARAMS_PHP}});
print_r($result);
$client->close();
```

The client uses PHP cURL and JSON. Constructor options are `apiKey`, `baseUrl`, and `timeout`. Call a generated method for direct access to each supported operation, or `request($operationId, $params, $responseType)` to dispatch by operation ID. Set `$responseType` to `text` for raw text output where supported. The package supports {{OPERATION_COUNT}} operations.

See [Crawlora](https://crawlora.net/), the [API documentation](https://crawlora.net/docs), and [the package repository]({{REPOSITORY}}) for account setup and the complete operation reference.
