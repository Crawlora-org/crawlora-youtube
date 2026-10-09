# Crawlora YouTube Ruby client

This gem calls the Crawlora hosted API at `https://api.crawlora.net/api/v1`. It does not call or scrape YouTube directly. Requests require your Crawlora API key and use your account's service plan.

## Install

```ruby
gem "crawlora-youtube"
```

Create an account at [crawlora.net](https://crawlora.net/signup?utm_source=rubygems&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-ruby-signup), open the [Crawlora console](https://crawlora.net/app?utm_source=rubygems&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-ruby-console) to get an API key, and set `CRAWLORA_API_KEY` before running the client:

```ruby
require "json"
require "crawlora/youtube"

client = Crawlora::Youtube::Client.new
result = client.request("youtube-channel-search", JSON.parse("{\"id\": \"sample-id\", \"q\": \"science explainers\"}"))
puts result
client.close
```

Use a operation-specific method for normal calls. `request(operation_id, params = {}, response_type: :auto)` is available for every operation. `response_type: :text` returns raw response text. This gem supports 14 operations.

```ruby
client = Crawlora::Youtube::Client.new(api_key: ENV.fetch("CRAWLORA_API_KEY"), timeout: 30)
# client.<operation_method>(...)
client.close
```

Client options include `api_key`, `base_url`, and `timeout`. Ruby stdlib provides the HTTP and JSON transport.

See [Crawlora](https://crawlora.net/?utm_source=rubygems&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-ruby-homepage), the [API documentation](https://crawlora.net/docs?utm_source=rubygems&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-ruby-api-docs), and [the package repository](https://github.com/Crawlora-org/crawlora-youtube) for account setup, the operation reference, and release history.
