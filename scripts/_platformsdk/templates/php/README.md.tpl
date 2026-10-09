# Crawlora {{DISPLAY_NAME}} PHP client

This package calls the Crawlora hosted API at `https://api.crawlora.net/api/v1`. It does not call or scrape {{DISPLAY_NAME}} directly. Requests require a Crawlora API key and use your Crawlora account's service plan.

## Install

```sh
composer require {{PACKAGE_NAME}}
```

Create an account at [crawlora.net](https://crawlora.net/signup?utm_source=packagist&utm_medium=referral&utm_campaign=platform-clients&utm_content={{PLATFORM}}-php-signup), open the [Crawlora console](https://crawlora.net/app?utm_source=packagist&utm_medium=referral&utm_campaign=platform-clients&utm_content={{PLATFORM}}-php-console) to get an API key, then set `CRAWLORA_API_KEY` in your environment.

```php
<?php
require __DIR__ . '/vendor/autoload.php';

$client = new Crawlora\{{CLASS_NAME}}\Client(apiKey: getenv('CRAWLORA_API_KEY'));
$result = $client->request({{EXAMPLE_OPERATION_JSON}}, {{EXAMPLE_PARAMS_PHP}});
print_r($result);
$client->close();
```

The client uses PHP cURL and JSON. Constructor options are `apiKey`, `baseUrl`, and `timeout`. Call the operation-specific method for direct access to each supported operation, or `request($operationId, $params, $responseType)` to dispatch by operation ID. Set `$responseType` to `text` for raw text output such as transcript formats. The package includes {{OPERATION_COUNT}} API operations.

See [Crawlora](https://crawlora.net/?utm_source=packagist&utm_medium=referral&utm_campaign=platform-clients&utm_content={{PLATFORM}}-php-homepage), the [API documentation](https://crawlora.net/docs?utm_source=packagist&utm_medium=referral&utm_campaign=platform-clients&utm_content={{PLATFORM}}-php-api-docs), and [the PHP package source]({{PHP_REPOSITORY}}). The complete operation and parameter reference is in the [platform repository]({{REPOSITORY}}/blob/main/docs/usage.md).
