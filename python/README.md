# crawlora-youtube

Python client for Crawlora's hosted YouTube API. It calls Crawlora's
service; it does not run a browser or scrape YouTube locally. A Crawlora
account and `CRAWLORA_API_KEY` are required, and API use is billed under your
Crawlora account. Crawlora is independent from and not endorsed by
YouTube or its owners.

## Install

```sh
python -m pip install crawlora-youtube
```

## Use

```python
import os

from crawlora_youtube import YouTubeClient

with YouTubeClient(api_key=os.environ["CRAWLORA_API_KEY"]) as client:
    result = client.search(q='science explainers', type='video')
    print(result)
```

The package also exports `Client` as an alias for `YouTubeClient`. Operation
methods are available directly in snake_case and through the `youtube`
group. The async package client is `AsyncYouTubeClient`; see the [online
endpoint and parameter reference](https://github.com/Crawlora-org/crawlora-youtube/blob/main/docs/usage.md) and [runnable example](https://github.com/Crawlora-org/crawlora-youtube/blob/main/examples/python.py).

The import snippet above is for a project where this PyPI package is installed. To run the checked-in example from a source checkout, install `./python` from the repository root and run `python examples/python.py`; see the [source-checkout instructions](https://github.com/Crawlora-org/crawlora-youtube#run-examples-from-a-source-checkout).

## Configuration

Pass your key through `api_key` or read `CRAWLORA_API_KEY` from the environment.
Keep credentials out of source control and logs. Requests go to Crawlora's
hosted API, and response data and availability follow its current contract.
