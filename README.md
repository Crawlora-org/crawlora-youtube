# YouTube clients for Crawlora

Official Crawlora client packages for the hosted YouTube API. These packages send requests to Crawlora's API and require a Crawlora account and `CRAWLORA_API_KEY`; service usage follows your Crawlora account billing plan.

The packages do not run a browser or scrape YouTube locally. Crawlora is an independent service and is not affiliated with or endorsed by YouTube or its owners.

- JavaScript / TypeScript: [`@crawlora-org/youtube`](javascript/README.md)
- Python: [`crawlora-youtube`](python/README.md)
- Go: [`github.com/Crawlora-org/crawlora-youtube`](go.mod)
- Ruby: [`crawlora-youtube`](ruby/README.md)
- Java: [`net.crawlora:crawlora-youtube:0.1.4`](java/README.md)
- PHP: [`crawlora/youtube`](php/README.md)
- Full endpoint and parameter reference: [docs/usage.md](docs/usage.md)
- Runnable samples: [examples/](examples/)
- Source repository: [https://github.com/Crawlora-org/crawlora-youtube](https://github.com/Crawlora-org/crawlora-youtube)

Create an account at [crawlora.net](https://crawlora.net/signup), open the [Crawlora console](https://crawlora.net/app) to get an API key, or read the [API documentation](https://crawlora.net/docs).

## Install

```sh
npm install @crawlora-org/youtube
python -m pip install crawlora-youtube
go get github.com/Crawlora-org/crawlora-youtube@latest
gem install crawlora-youtube
composer require crawlora/youtube
```

For Java, add `net.crawlora:crawlora-youtube:0.1.4` to your Maven dependencies; see [java/README.md](java/README.md).

Set your Crawlora key in the environment before running a client:

```sh
export CRAWLORA_API_KEY="your-crawlora-api-key"
```

Do not commit API keys. See the language-specific READMEs for sync and async use.

## PHP example

The Packagist package is available as `crawlora/youtube`:

```sh
composer require crawlora/youtube
```

```php
<?php
require __DIR__ . '/vendor/autoload.php';

$apiKey = getenv('CRAWLORA_API_KEY');
if (!$apiKey) throw new RuntimeException('Set CRAWLORA_API_KEY before running this example.');
$client = new \Crawlora\YouTube\Client(apiKey: $apiKey);
$result = $client->request("youtube-search", ['q' => 'science explainers', 'type' => 'video']);
print_r($result);
$client->close();
```

The same example and install details are in [php/README.md](php/README.md).

## License

MIT. See [LICENSE](LICENSE).
