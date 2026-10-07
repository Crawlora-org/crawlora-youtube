"""Platform-specific convenience clients."""
from __future__ import annotations
from typing import Any
from .client import CrawloraClient
from .async_client import AsyncCrawloraClient

class YouTubeClient(CrawloraClient):
    """Synchronous YouTube API client."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault('user_agent', 'crawlora-youtube-python/0.1.4')
        super().__init__(*args, **kwargs)

    def captions(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return self.request('youtube-captions', params, response_type=response_type, timeout=timeout, headers=headers)

    def channel_playlists(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return self.request('youtube-channel-playlists', params, response_type=response_type, timeout=timeout, headers=headers)

    def channel_search(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return self.request('youtube-channel-search', params, response_type=response_type, timeout=timeout, headers=headers)

    def channel_shorts(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return self.request('youtube-channel-shorts', params, response_type=response_type, timeout=timeout, headers=headers)

    def channel_videos(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return self.request('youtube-channel-videos', params, response_type=response_type, timeout=timeout, headers=headers)

    def comments(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return self.request('youtube-comments', params, response_type=response_type, timeout=timeout, headers=headers)

    def playlist(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return self.request('youtube-playlist', params, response_type=response_type, timeout=timeout, headers=headers)

    def profile(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return self.request('youtube-profile', params, response_type=response_type, timeout=timeout, headers=headers)

    def search(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return self.request('youtube-search', params, response_type=response_type, timeout=timeout, headers=headers)

    def suggest(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return self.request('youtube-suggest', params, response_type=response_type, timeout=timeout, headers=headers)

    def tag(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return self.request('youtube-tag', params, response_type=response_type, timeout=timeout, headers=headers)

    def transcript(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return self.request('youtube-transcript', params, response_type=response_type, timeout=timeout, headers=headers)

    def transcript_languages(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return self.request('youtube-transcript-languages', params, response_type=response_type, timeout=timeout, headers=headers)

    def video(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return self.request('youtube-video', params, response_type=response_type, timeout=timeout, headers=headers)

class AsyncYouTubeClient(AsyncCrawloraClient):
    """Asynchronous YouTube API client."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault('user_agent', 'crawlora-youtube-python/0.1.4')
        super().__init__(*args, **kwargs)

    async def captions(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return await self.request('youtube-captions', params, response_type=response_type, timeout=timeout, headers=headers)

    async def channel_playlists(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return await self.request('youtube-channel-playlists', params, response_type=response_type, timeout=timeout, headers=headers)

    async def channel_search(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return await self.request('youtube-channel-search', params, response_type=response_type, timeout=timeout, headers=headers)

    async def channel_shorts(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return await self.request('youtube-channel-shorts', params, response_type=response_type, timeout=timeout, headers=headers)

    async def channel_videos(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return await self.request('youtube-channel-videos', params, response_type=response_type, timeout=timeout, headers=headers)

    async def comments(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return await self.request('youtube-comments', params, response_type=response_type, timeout=timeout, headers=headers)

    async def playlist(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return await self.request('youtube-playlist', params, response_type=response_type, timeout=timeout, headers=headers)

    async def profile(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return await self.request('youtube-profile', params, response_type=response_type, timeout=timeout, headers=headers)

    async def search(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return await self.request('youtube-search', params, response_type=response_type, timeout=timeout, headers=headers)

    async def suggest(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return await self.request('youtube-suggest', params, response_type=response_type, timeout=timeout, headers=headers)

    async def tag(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return await self.request('youtube-tag', params, response_type=response_type, timeout=timeout, headers=headers)

    async def transcript(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return await self.request('youtube-transcript', params, response_type=response_type, timeout=timeout, headers=headers)

    async def transcript_languages(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return await self.request('youtube-transcript-languages', params, response_type=response_type, timeout=timeout, headers=headers)

    async def video(self, **params: Any) -> Any:
        response_type = params.pop('_response_type', 'auto')
        timeout = params.pop('_timeout', None)
        headers = params.pop('_headers', None)
        return await self.request('youtube-video', params, response_type=response_type, timeout=timeout, headers=headers)
