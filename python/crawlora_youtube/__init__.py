"""Typed YouTube client for the Crawlora hosted API."""

from .platform import YouTubeClient, AsyncYouTubeClient
from .client import CrawloraClientError, CrawloraError, CrawloraNetworkError, CrawloraServerError
from .operations import OPERATION_COUNT, OPERATION_IDS, PLATFORM

Client = YouTubeClient
AsyncClient = AsyncYouTubeClient
__version__ = '0.2.0'
DISPLAY_NAME = 'YouTube'
PLATFORM = 'youtube'
CONTRACT_REVISION = 'sha256:894a214e317ae02c6f1135c7b5834d15a22799212b199e8de55b1acf3b315f71'

__all__ = [
    "YouTubeClient", "AsyncYouTubeClient", "Client", "AsyncClient",
    "CrawloraError", "CrawloraClientError", "CrawloraServerError", "CrawloraNetworkError",
    "DISPLAY_NAME", "PLATFORM", "CONTRACT_REVISION", "OPERATION_COUNT", "OPERATION_IDS", "__version__",
]
