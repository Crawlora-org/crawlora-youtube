"""Typed YouTube client for the Crawlora hosted API."""

from .platform import YouTubeClient, AsyncYouTubeClient
from .client import CrawloraClientError, CrawloraError, CrawloraNetworkError, CrawloraServerError
from .operations import OPERATION_COUNT, OPERATION_IDS, PLATFORM

Client = YouTubeClient
AsyncClient = AsyncYouTubeClient
__version__ = '0.1.4'
DISPLAY_NAME = 'YouTube'
PLATFORM = 'youtube'
CONTRACT_REVISION = 'sha256:677d4bc412f42cf0083135b32bf36b478ab37efbea5f35fc5e8b6e86caaf6a68'

__all__ = [
    "YouTubeClient", "AsyncYouTubeClient", "Client", "AsyncClient",
    "CrawloraError", "CrawloraClientError", "CrawloraServerError", "CrawloraNetworkError",
    "DISPLAY_NAME", "PLATFORM", "CONTRACT_REVISION", "OPERATION_COUNT", "OPERATION_IDS", "__version__",
]
