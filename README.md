# YouTube clients for Crawlora

Official Crawlora client packages for the hosted YouTube API. These packages send requests to Crawlora's API and require a Crawlora account and `CRAWLORA_API_KEY`; service usage follows your Crawlora account billing plan.

The packages do not run a browser or scrape YouTube locally. Crawlora is an independent service and is not affiliated with or endorsed by YouTube or its owners.

- JavaScript / TypeScript: [`@crawlora-org/youtube`](javascript/README.md)
- Python: [`crawlora-youtube`](python/README.md)
- Full endpoint and parameter reference: [docs/usage.md](docs/usage.md)
- Runnable samples: [examples/](examples/)
- Source repository: [https://github.com/Crawlora-org/crawlora-youtube](https://github.com/Crawlora-org/crawlora-youtube)

## Install

```sh
npm install @crawlora-org/youtube
python -m pip install crawlora-youtube
```

Set your Crawlora key in the environment before running a client:

```sh
export CRAWLORA_API_KEY="your-crawlora-api-key"
```

Do not commit API keys. See the language-specific READMEs for sync and async use.

## Run examples from a source checkout

From the repository root, set `CRAWLORA_API_KEY` as shown above and run:

```sh
node examples/javascript.mjs
python -m pip install ./python
python examples/python.py
```

The checked-in JavaScript example imports the generated local source at `javascript/src/index.js`. The Python command installs this checkout's package before running its example. The import snippets in the language-specific READMEs are for separate projects using installed npm and PyPI packages; copy those snippets into your own project after installing the package.

## Contract

This package release is `0.1.2`. The generated client methods follow the bundled `openapi/public.json` contract at revision `sha256:677d4bc412f42cf0083135b32bf36b478ab37efbea5f35fc5e8b6e86caaf6a68`. `scripts/generate.py` regenerates both language clients and the documentation from the shared source.

## Contract updates and releases

The `Sync live API contract` workflow checks the deployed public OpenAPI contract every day at **03:47 UTC**. It always reads `https://api.crawlora.net/swagger/doc.json`; its only manual option is `dry_run`, which applies the candidate in the workflow and reports the result without validating, committing, tagging, or publishing it.

An unchanged contract is a no-op and does not run the client test matrix or create a release. Additions and updates are applied to a candidate, checked on Node.js 18 and 22 and Python 3.10 and 3.12, then committed to `main` only after all checks pass. Removing or deprecating an existing operation stops the run for maintainer review; packages already published remain available. The release workflow publishes an accepted version to npm and PyPI. A failed fetch, invalid contract, or failed check also stops before the commit. A later scheduled run can resume an incomplete registry publication at the same package version and immutable tag; recovery does not bypass the removed-operation review.

The workflow does not accept an alternate source URL or a caller-supplied version. To preview a change, open **Actions → Sync live API contract → Run workflow** and select `dry_run`.

## License

MIT. See [LICENSE](LICENSE).
