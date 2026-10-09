# Crawlora {{DISPLAY_NAME}} Ruby client

This gem calls the Crawlora hosted API at `https://api.crawlora.net/api/v1`. It does not call or scrape {{DISPLAY_NAME}} directly. Requests require your Crawlora API key and use your account's service plan.

## Install

```ruby
gem "{{GEM_NAME}}"
```

Create an account at [crawlora.net](https://crawlora.net/signup?utm_source=rubygems&utm_medium=referral&utm_campaign=platform-clients&utm_content={{PLATFORM}}-ruby-signup), open the [Crawlora console](https://crawlora.net/app?utm_source=rubygems&utm_medium=referral&utm_campaign=platform-clients&utm_content={{PLATFORM}}-ruby-console) to get an API key, and set `CRAWLORA_API_KEY` before running the client:

```ruby
require "json"
require "crawlora/{{PLATFORM}}"

client = Crawlora::{{CLASS_NAME}}::Client.new
result = client.request({{EXAMPLE_OPERATION_JSON}}, JSON.parse({{EXAMPLE_PARAMS_JSON}}))
puts result
client.close
```

Use a operation-specific method for normal calls. `request(operation_id, params = {}, response_type: :auto)` is available for every operation. `response_type: :text` returns raw response text. This gem supports {{OPERATION_COUNT}} operations.

```ruby
client = Crawlora::{{CLASS_NAME}}::Client.new(api_key: ENV.fetch("CRAWLORA_API_KEY"), timeout: 30)
# client.<operation_method>(...)
client.close
```

Client options include `api_key`, `base_url`, and `timeout`. Ruby stdlib provides the HTTP and JSON transport.

See [Crawlora](https://crawlora.net/?utm_source=rubygems&utm_medium=referral&utm_campaign=platform-clients&utm_content={{PLATFORM}}-ruby-homepage), the [API documentation](https://crawlora.net/docs?utm_source=rubygems&utm_medium=referral&utm_campaign=platform-clients&utm_content={{PLATFORM}}-ruby-api-docs), and [the package repository]({{REPOSITORY}}) for account setup, the operation reference, and release history.
