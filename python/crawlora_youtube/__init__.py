"""Typed YouTube client for the Crawlora hosted API."""

from .platform import YouTubeClient, AsyncYouTubeClient
from .client import CrawloraClientError, CrawloraError, CrawloraNetworkError, CrawloraServerError
from .operations import OPERATION_COUNT, OPERATION_IDS, PLATFORM

Client = YouTubeClient
AsyncClient = AsyncYouTubeClient
__version__ = '0.3.0'
DISPLAY_NAME = 'YouTube'
PLATFORM = 'youtube'
CONTRACT_REVISION = 'sha256:8e809efec74ebe90dd87d86c6eb8b963305d7f27fce19aa82a5620934883bed2'

__all__ = [
    "YouTubeClient", "AsyncYouTubeClient", "Client", "AsyncClient",
    "CrawloraError", "CrawloraClientError", "CrawloraServerError", "CrawloraNetworkError",
    "DISPLAY_NAME", "PLATFORM", "CONTRACT_REVISION", "OPERATION_COUNT", "OPERATION_IDS", "__version__",
]
