from __future__ import annotations

import sys
from typing import Any, Callable, Iterable, Iterator, Literal, Mapping, overload

if sys.version_info >= (3, 11):
    from typing import NotRequired, Required, TypedDict, Unpack
else:
    from typing_extensions import NotRequired, Required, TypedDict, Unpack

ResponseType = Literal["auto", "json", "text", "stream"]

class CrawloraError(Exception):
    status: int
    code: int | None
    body: Any
    raw_body: str
    headers: Mapping[str, str]
    request_id: str | None
    def __init__(self, message: str, *, status: int = ..., code: int | None = ..., body: Any = ..., raw_body: str = ..., headers: Mapping[str, str] | None = ..., request_id: str | None = ..., cause: BaseException | None = ...) -> None: ...

class CrawloraClientError(CrawloraError): ...
class CrawloraServerError(CrawloraError): ...
class CrawloraNetworkError(CrawloraError): ...

class _RequestOptions(TypedDict, total=False):
    _response_type: ResponseType
    _timeout: float
    _headers: Mapping[str, str]

ModelAppResponse = TypedDict('ModelAppResponse', {
    'code': NotRequired[int],
    'data': NotRequired[Any],
    'msg': NotRequired[Any],
}, total=False)

ModelYoutubeVideoResponseDoc = TypedDict('ModelYoutubeVideoResponseDoc', {
    'code': NotRequired[int],
    'data': NotRequired[ModelYoutubeVideoDetail],
    'msg': NotRequired[str],
}, total=False)

ModelYoutubeVideoDetail = TypedDict('ModelYoutubeVideoDetail', {
    'channel_id': NotRequired[str],
    'channel_title': NotRequired[str],
    'comments_count': NotRequired[int],
    'description': NotRequired[str],
    'dislikes_count': NotRequired[int],
    'duration_seconds': NotRequired[float],
    'id': NotRequired[str],
    'likes_count': NotRequired[int],
    'published_at': NotRequired[str],
    'title': NotRequired[str],
    'views_count': NotRequired[int],
}, total=False)

ModelYoutubeTranscriptLanguagesResponseDoc = TypedDict('ModelYoutubeTranscriptLanguagesResponseDoc', {
    'code': NotRequired[int],
    'data': NotRequired[list[ModelYoutubeTranscriptLanguage]],
    'msg': NotRequired[str],
}, total=False)

ModelYoutubeTranscriptLanguage = TypedDict('ModelYoutubeTranscriptLanguage', {
    'is_generated': NotRequired[bool],
    'is_translatable': NotRequired[bool],
    'language': NotRequired[str],
    'language_code': NotRequired[str],
}, total=False)

ModelYoutubeTranscriptResponseDoc = TypedDict('ModelYoutubeTranscriptResponseDoc', {
    'code': NotRequired[int],
    'data': NotRequired[ModelYoutubeTranscriptResponse],
    'msg': NotRequired[str],
}, total=False)

ModelYoutubeTranscriptResponse = TypedDict('ModelYoutubeTranscriptResponse', {
    'is_generated': NotRequired[bool],
    'language': NotRequired[str],
    'language_code': NotRequired[str],
    'segments': NotRequired[list[ModelYoutubeTranscriptSegment]],
    'text': NotRequired[str],
    'translation_language': NotRequired[str],
    'video_id': NotRequired[str],
}, total=False)

ModelYoutubeTranscriptSegment = TypedDict('ModelYoutubeTranscriptSegment', {
    'duration': NotRequired[float],
    'start': NotRequired[float],
    'text': NotRequired[str],
}, total=False)

ModelYoutubeTagResponseDoc = TypedDict('ModelYoutubeTagResponseDoc', {
    'code': NotRequired[int],
    'data': NotRequired[ModelYoutubeTagResp],
    'msg': NotRequired[str],
}, total=False)

ModelYoutubeTagResp = TypedDict('ModelYoutubeTagResp', {
    'continuation_token': NotRequired[str],
    'meta': NotRequired[ModelYoutubeTagMeta],
    'videos': NotRequired[list[ModelYoutubeVideoDetail]],
}, total=False)

ModelYoutubeTagMeta = TypedDict('ModelYoutubeTagMeta', {
    'channelsCount': NotRequired[int],
    'videosCount': NotRequired[int],
}, total=False)

ModelYoutubeSuggestResponseDoc = TypedDict('ModelYoutubeSuggestResponseDoc', {
    'code': NotRequired[int],
    'data': NotRequired[ModelSuggestResponse],
    'msg': NotRequired[str],
}, total=False)

ModelSuggestResponse = TypedDict('ModelSuggestResponse', {
    'query': NotRequired[str],
    'suggestions': NotRequired[list[ModelSuggestSuggestion]],
}, total=False)

ModelSuggestSuggestion = TypedDict('ModelSuggestSuggestion', {
    'position': NotRequired[int],
    'query': NotRequired[str],
}, total=False)

ModelYoutubeSearchResponseDoc = TypedDict('ModelYoutubeSearchResponseDoc', {
    'code': NotRequired[int],
    'data': NotRequired[ModelYoutubeSearchResponse],
    'msg': NotRequired[str],
}, total=False)

ModelYoutubeSearchResponse = TypedDict('ModelYoutubeSearchResponse', {
    'continuation_token': NotRequired[str],
    'estimated_results': NotRequired[int],
    'items': NotRequired[list[ModelYoutubeSearchItem]],
    'query': NotRequired[str],
}, total=False)

ModelYoutubeSearchItem = TypedDict('ModelYoutubeSearchItem', {
    'badges': NotRequired[list[str]],
    'channel_id': NotRequired[str],
    'channel_thumbnail': NotRequired[str],
    'channel_title': NotRequired[str],
    'description_snippet': NotRequired[str],
    'duration': NotRequired[str],
    'duration_seconds': NotRequired[int],
    'handle': NotRequired[str],
    'is_live': NotRequired[bool],
    'is_short': NotRequired[bool],
    'is_verified': NotRequired[bool],
    'playlist_id': NotRequired[str],
    'position': NotRequired[int],
    'published_text': NotRequired[str],
    'short_view_count': NotRequired[str],
    'subscriber_count': NotRequired[str],
    'thumbnail': NotRequired[str],
    'title': NotRequired[str],
    'type': NotRequired[str],
    'url': NotRequired[str],
    'video_count': NotRequired[str],
    'video_id': NotRequired[str],
    'view_count': NotRequired[str],
}, total=False)

ModelYoutubeProfileResponseDoc = TypedDict('ModelYoutubeProfileResponseDoc', {
    'code': NotRequired[int],
    'data': NotRequired[ModelYoutubeProfile],
    'msg': NotRequired[str],
}, total=False)

ModelYoutubeProfile = TypedDict('ModelYoutubeProfile', {
    'bio': NotRequired[str],
    'channel_id': NotRequired[str],
    'channel_name': NotRequired[str],
    'channel_url': NotRequired[str],
    'created_at': NotRequired[str],
    'id': NotRequired[str],
    'joined_date': NotRequired[str],
    'links': NotRequired[list[str]],
    'profile_pic': NotRequired[str],
    'region': NotRequired[str],
    'stats': NotRequired[ModelYoutubeProfileStats],
    'updated_at': NotRequired[str],
}, total=False)

ModelYoutubeProfileStats = TypedDict('ModelYoutubeProfileStats', {
    'followers_count': NotRequired[int],
    'videos_count': NotRequired[int],
    'views_count': NotRequired[int],
}, total=False)

ModelYoutubePlaylistResponseDoc = TypedDict('ModelYoutubePlaylistResponseDoc', {
    'code': NotRequired[int],
    'data': NotRequired[ModelYoutubePlaylistResponse],
    'msg': NotRequired[str],
}, total=False)

ModelYoutubePlaylistResponse = TypedDict('ModelYoutubePlaylistResponse', {
    'channel_id': NotRequired[str],
    'channel_title': NotRequired[str],
    'continuation_token': NotRequired[str],
    'items': NotRequired[list[ModelYoutubeSearchItem]],
    'playlist_id': NotRequired[str],
    'thumbnail': NotRequired[str],
    'title': NotRequired[str],
    'url': NotRequired[str],
    'video_count': NotRequired[str],
}, total=False)

ModelYoutubeCommentsResponseDoc = TypedDict('ModelYoutubeCommentsResponseDoc', {
    'code': NotRequired[int],
    'data': NotRequired[ModelYoutubeCommentResponse],
    'msg': NotRequired[str],
}, total=False)

ModelYoutubeCommentResponse = TypedDict('ModelYoutubeCommentResponse', {
    'comments': NotRequired[list[ModelYoutubeComment]],
    'continuation_token': NotRequired[str],
}, total=False)

ModelYoutubeComment = TypedDict('ModelYoutubeComment', {
    'channel_id': NotRequired[str],
    'comment_id': NotRequired[str],
    'content': NotRequired[str],
    'continuation_token': NotRequired[str],
    'likes_count': NotRequired[int],
    'published_time': NotRequired[str],
    'reply_count': NotRequired[int],
    'user_name': NotRequired[str],
}, total=False)

ModelYoutubeChannelFeedResponseDoc = TypedDict('ModelYoutubeChannelFeedResponseDoc', {
    'code': NotRequired[int],
    'data': NotRequired[ModelYoutubeChannelFeedResponse],
    'msg': NotRequired[str],
}, total=False)

ModelYoutubeChannelFeedResponse = TypedDict('ModelYoutubeChannelFeedResponse', {
    'channel_id': NotRequired[str],
    'channel_title': NotRequired[str],
    'channel_url': NotRequired[str],
    'continuation_token': NotRequired[str],
    'handle': NotRequired[str],
    'items': NotRequired[list[ModelYoutubeSearchItem]],
    'query': NotRequired[str],
    'thumbnail': NotRequired[str],
}, total=False)

ModelYoutubeChannelShortsResponseDoc = TypedDict('ModelYoutubeChannelShortsResponseDoc', {
    'code': NotRequired[int],
    'data': NotRequired[ModelYoutubeChannelShortsResponse],
    'msg': NotRequired[str],
}, total=False)

ModelYoutubeChannelShortsResponse = TypedDict('ModelYoutubeChannelShortsResponse', {
    'channel_id': NotRequired[str],
    'channel_title': NotRequired[str],
    'channel_url': NotRequired[str],
    'handle': NotRequired[str],
    'shorts': NotRequired[list[ModelYoutubeChannelShort]],
    'thumbnail': NotRequired[str],
}, total=False)

ModelYoutubeChannelShort = TypedDict('ModelYoutubeChannelShort', {
    'position': NotRequired[int],
    'thumbnail': NotRequired[str],
    'title': NotRequired[str],
    'url': NotRequired[str],
    'video_id': NotRequired[str],
    'view_count': NotRequired[str],
}, total=False)

ModelYoutubeChannelSearchResponseDoc = TypedDict('ModelYoutubeChannelSearchResponseDoc', {
    'code': NotRequired[int],
    'data': NotRequired[ModelYoutubeChannelSearchResponseDataDoc],
    'msg': NotRequired[str],
}, total=False)

ModelYoutubeChannelSearchResponseDataDoc = TypedDict('ModelYoutubeChannelSearchResponseDataDoc', {
    'channel_id': NotRequired[str],
    'channel_title': NotRequired[str],
    'channel_url': NotRequired[str],
    'continuation_token': NotRequired[str],
    'handle': NotRequired[str],
    'items': NotRequired[list[ModelYoutubeSearchItem]],
    'query': NotRequired[str],
    'thumbnail': NotRequired[str],
}, total=False)

ModelYoutubeCaptionsResponseDoc = TypedDict('ModelYoutubeCaptionsResponseDoc', {
    'code': NotRequired[int],
    'data': NotRequired[list[ModelYoutubeCaption]],
    'msg': NotRequired[str],
}, total=False)

ModelYoutubeCaption = TypedDict('ModelYoutubeCaption', {
    'duration': NotRequired[float],
    'start': NotRequired[float],
    'text': NotRequired[str],
}, total=False)

YoutubeCaptionsResponse = ModelYoutubeCaptionsResponseDoc
YoutubeCaptionsParams = TypedDict('YoutubeCaptionsParams', {
    '_response_type': NotRequired[ResponseType],
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    'id': Required[str],
    'lang': NotRequired[str],
}, total=False)

YoutubeChannelPlaylistsResponse = ModelYoutubeChannelFeedResponseDoc
YoutubeChannelPlaylistsParams = TypedDict('YoutubeChannelPlaylistsParams', {
    '_response_type': NotRequired[ResponseType],
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    'id': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeChannelSearchResponse = ModelYoutubeChannelSearchResponseDoc
YoutubeChannelSearchParams = TypedDict('YoutubeChannelSearchParams', {
    '_response_type': NotRequired[ResponseType],
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    'id': Required[str],
    'q': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeChannelShortsResponse = ModelYoutubeChannelShortsResponseDoc
YoutubeChannelShortsParams = TypedDict('YoutubeChannelShortsParams', {
    '_response_type': NotRequired[ResponseType],
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    'id': Required[str],
}, total=False)

YoutubeChannelVideosResponse = ModelYoutubeChannelFeedResponseDoc
YoutubeChannelVideosParams = TypedDict('YoutubeChannelVideosParams', {
    '_response_type': NotRequired[ResponseType],
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    'id': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeCommentsResponse = ModelYoutubeCommentsResponseDoc
YoutubeCommentsParams = TypedDict('YoutubeCommentsParams', {
    '_response_type': NotRequired[ResponseType],
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    'id': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubePlaylistResponse = ModelYoutubePlaylistResponseDoc
YoutubePlaylistParams = TypedDict('YoutubePlaylistParams', {
    '_response_type': NotRequired[ResponseType],
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    'id': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeProfileResponse = ModelYoutubeProfileResponseDoc
YoutubeProfileParams = TypedDict('YoutubeProfileParams', {
    '_response_type': NotRequired[ResponseType],
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    'id': Required[str],
}, total=False)

YoutubeSearchResponse = ModelYoutubeSearchResponseDoc
YoutubeSearchParams = TypedDict('YoutubeSearchParams', {
    '_response_type': NotRequired[ResponseType],
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    'q': NotRequired[str],
    'search_query': NotRequired[str],
    'continuation_token': NotRequired[str],
    'type': NotRequired[Literal['video', 'shorts', 'channel', 'playlist', 'movie']],
    'sort_by': NotRequired[Literal['relevance', 'upload_date', 'view_count', 'popularity', 'rating']],
    'upload_date': NotRequired[Literal['last_hour', 'today', 'this_week', 'this_month', 'this_year']],
    'duration': NotRequired[Literal['under_3_minutes', 'three_to_20_minutes', 'over_20_minutes', 'under_3', 'three_to_20', 'over_20', 'short', 'medium', 'long']],
    'features': NotRequired[str],
    'hl': NotRequired[str],
    'gl': NotRequired[str],
    'params': NotRequired[str],
}, total=False)

YoutubeSuggestResponse = ModelYoutubeSuggestResponseDoc
YoutubeSuggestParams = TypedDict('YoutubeSuggestParams', {
    '_response_type': NotRequired[ResponseType],
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    'q': Required[str],
    'count': NotRequired[int],
    'hl': NotRequired[str],
    'gl': NotRequired[str],
}, total=False)

YoutubeTagResponse = ModelYoutubeTagResponseDoc
YoutubeTagParams = TypedDict('YoutubeTagParams', {
    '_response_type': NotRequired[ResponseType],
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    'tag': Required[str],
    'type': NotRequired[Literal['all', 'shorts']],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeTranscriptResponse = ModelYoutubeTranscriptResponseDoc
YoutubeTranscriptParams = TypedDict('YoutubeTranscriptParams', {
    '_response_type': NotRequired[ResponseType],
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    'id': Required[str],
    'lang': NotRequired[str],
    'translate_to': NotRequired[str],
    'format': NotRequired[Literal['json', 'text', 'srt', 'vtt']],
    'timestamps': NotRequired[bool],
}, total=False)

YoutubeTranscriptLanguagesResponse = ModelYoutubeTranscriptLanguagesResponseDoc
YoutubeTranscriptLanguagesParams = TypedDict('YoutubeTranscriptLanguagesParams', {
    '_response_type': NotRequired[ResponseType],
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    'id': Required[str],
}, total=False)

YoutubeVideoResponse = ModelYoutubeVideoResponseDoc
YoutubeVideoParams = TypedDict('YoutubeVideoParams', {
    '_response_type': NotRequired[ResponseType],
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    'id': Required[str],
}, total=False)

class YoutubeGroup:
    @overload
    def captions(self, **params: Unpack[YoutubeCaptionsStreamParams]) -> BinaryIO: ...
    @overload
    def captions(self, **params: Unpack[YoutubeCaptionsTextResponseParams]) -> str: ...
    @overload
    def captions(self, **params: Unpack[YoutubeCaptionsDefaultParams]) -> YoutubeCaptionsResponse: ...
    @overload
    def channel_playlists(self, **params: Unpack[YoutubeChannelPlaylistsStreamParams]) -> BinaryIO: ...
    @overload
    def channel_playlists(self, **params: Unpack[YoutubeChannelPlaylistsTextResponseParams]) -> str: ...
    @overload
    def channel_playlists(self, **params: Unpack[YoutubeChannelPlaylistsDefaultParams]) -> YoutubeChannelPlaylistsResponse: ...
    @overload
    def channel_search(self, **params: Unpack[YoutubeChannelSearchStreamParams]) -> BinaryIO: ...
    @overload
    def channel_search(self, **params: Unpack[YoutubeChannelSearchTextResponseParams]) -> str: ...
    @overload
    def channel_search(self, **params: Unpack[YoutubeChannelSearchDefaultParams]) -> YoutubeChannelSearchResponse: ...
    @overload
    def channel_shorts(self, **params: Unpack[YoutubeChannelShortsStreamParams]) -> BinaryIO: ...
    @overload
    def channel_shorts(self, **params: Unpack[YoutubeChannelShortsTextResponseParams]) -> str: ...
    @overload
    def channel_shorts(self, **params: Unpack[YoutubeChannelShortsDefaultParams]) -> YoutubeChannelShortsResponse: ...
    @overload
    def channel_videos(self, **params: Unpack[YoutubeChannelVideosStreamParams]) -> BinaryIO: ...
    @overload
    def channel_videos(self, **params: Unpack[YoutubeChannelVideosTextResponseParams]) -> str: ...
    @overload
    def channel_videos(self, **params: Unpack[YoutubeChannelVideosDefaultParams]) -> YoutubeChannelVideosResponse: ...
    @overload
    def comments(self, **params: Unpack[YoutubeCommentsStreamParams]) -> BinaryIO: ...
    @overload
    def comments(self, **params: Unpack[YoutubeCommentsTextResponseParams]) -> str: ...
    @overload
    def comments(self, **params: Unpack[YoutubeCommentsDefaultParams]) -> YoutubeCommentsResponse: ...
    @overload
    def playlist(self, **params: Unpack[YoutubePlaylistStreamParams]) -> BinaryIO: ...
    @overload
    def playlist(self, **params: Unpack[YoutubePlaylistTextResponseParams]) -> str: ...
    @overload
    def playlist(self, **params: Unpack[YoutubePlaylistDefaultParams]) -> YoutubePlaylistResponse: ...
    @overload
    def profile(self, **params: Unpack[YoutubeProfileStreamParams]) -> BinaryIO: ...
    @overload
    def profile(self, **params: Unpack[YoutubeProfileTextResponseParams]) -> str: ...
    @overload
    def profile(self, **params: Unpack[YoutubeProfileDefaultParams]) -> YoutubeProfileResponse: ...
    @overload
    def search(self, **params: Unpack[YoutubeSearchStreamParams]) -> BinaryIO: ...
    @overload
    def search(self, **params: Unpack[YoutubeSearchTextResponseParams]) -> str: ...
    @overload
    def search(self, **params: Unpack[YoutubeSearchDefaultParams]) -> YoutubeSearchResponse: ...
    @overload
    def suggest(self, **params: Unpack[YoutubeSuggestStreamParams]) -> BinaryIO: ...
    @overload
    def suggest(self, **params: Unpack[YoutubeSuggestTextResponseParams]) -> str: ...
    @overload
    def suggest(self, **params: Unpack[YoutubeSuggestDefaultParams]) -> YoutubeSuggestResponse: ...
    @overload
    def tag(self, **params: Unpack[YoutubeTagStreamParams]) -> BinaryIO: ...
    @overload
    def tag(self, **params: Unpack[YoutubeTagTextResponseParams]) -> str: ...
    @overload
    def tag(self, **params: Unpack[YoutubeTagDefaultParams]) -> YoutubeTagResponse: ...
    @overload
    def transcript(self, **params: Unpack[YoutubeTranscriptStreamParams]) -> BinaryIO: ...
    @overload
    def transcript(self, **params: Unpack[YoutubeTranscriptTextResponseParams]) -> str: ...
    @overload
    def transcript(self, **params: Unpack[YoutubeTranscriptTextParams]) -> str: ...
    @overload
    def transcript(self, **params: Unpack[YoutubeTranscriptDefaultParams]) -> YoutubeTranscriptResponse: ...
    @overload
    def transcript_languages(self, **params: Unpack[YoutubeTranscriptLanguagesStreamParams]) -> BinaryIO: ...
    @overload
    def transcript_languages(self, **params: Unpack[YoutubeTranscriptLanguagesTextResponseParams]) -> str: ...
    @overload
    def transcript_languages(self, **params: Unpack[YoutubeTranscriptLanguagesDefaultParams]) -> YoutubeTranscriptLanguagesResponse: ...
    @overload
    def video(self, **params: Unpack[YoutubeVideoStreamParams]) -> BinaryIO: ...
    @overload
    def video(self, **params: Unpack[YoutubeVideoTextResponseParams]) -> str: ...
    @overload
    def video(self, **params: Unpack[YoutubeVideoDefaultParams]) -> YoutubeVideoResponse: ...

OperationId = Literal[
    'youtube-captions',
    'youtube-channel-playlists',
    'youtube-channel-search',
    'youtube-channel-shorts',
    'youtube-channel-videos',
    'youtube-comments',
    'youtube-playlist',
    'youtube-profile',
    'youtube-search',
    'youtube-suggest',
    'youtube-tag',
    'youtube-transcript',
    'youtube-transcript-languages',
    'youtube-video',
]

class CrawloraClient:
    youtube: YoutubeGroup
    api_key: str
    jwt_token: str
    base_url: str
    timeout: float
    retries: int
    retry_delay: float
    max_retry_delay: float
    retry_statuses: frozenset[int] | None
    retry_predicate: Callable[[int, BaseException | None], bool] | None
    on_retry: Callable[[int, BaseException, float], None] | None
    request_id: bool
    idempotency_keys: bool
    rate_limit: float | None
    max_concurrency: int | None
    logger: Callable[[Mapping[str, Any]], None] | None
    before_request: list[Callable[[dict[str, Any]], None]]
    after_response: list[Callable[[str, int, Mapping[str, str], Any], Any]]
    headers: dict[str, str]
    user_agent: str
    def _is_retryable(self, status: int, exc: BaseException | None) -> bool: ...
    def _compute_retry_delay(self, attempt: int, headers: Mapping[str, str]) -> float: ...
    def _log(self, event: Mapping[str, Any]) -> None: ...
    def __init__(
        self,
        *,
        api_key: str | None = ...,
        jwt_token: str | None = ...,
        base_url: str | None = ...,
        timeout: float = ...,
        retries: int = ...,
        retry_delay: float = ...,
        max_retry_delay: float = ...,
        retry_statuses: Iterable[int] | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
        on_retry: Callable[[int, BaseException, float], None] | None = ...,
        request_id: bool = ...,
        idempotency_keys: bool = ...,
        rate_limit: float | None = ...,
        max_concurrency: int | None = ...,
        logger: Callable[[Mapping[str, Any]], None] | None = ...,
        before_request: Callable[[dict[str, Any]], None] | Iterable[Callable[[dict[str, Any]], None]] | None = ...,
        after_response: Callable[[str, int, Mapping[str, str], Any], Any] | Iterable[Callable[[str, int, Mapping[str, str], Any], Any]] | None = ...,
        headers: Mapping[str, str] | None = ...,
        user_agent: str | None = ...,
        transport: Callable[..., Any] | None = ...,
    ) -> None: ...
    def close(self) -> None: ...
    def __enter__(self) -> CrawloraClient: ...
    def __exit__(self, *exc: Any) -> None: ...
    def paginate(
        self,
        operation_id: str,
        params: Mapping[str, Any] | None = ...,
        *,
        page_param: str | None = ...,
        cursor_param: str | None = ...,
        next_cursor: Callable[[Any], Any] | None = ...,
        start: Any = ...,
        step: int = ...,
        max_pages: int | None = ...,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
    ) -> Iterator[Any]: ...
    def paginate_items(
        self,
        operation_id: str,
        params: Mapping[str, Any] | None = ...,
        *,
        items: Callable[[Any], Any] | None = ...,
        page_param: str | None = ...,
        cursor_param: str | None = ...,
        next_cursor: Callable[[Any], Any] | None = ...,
        start: Any = ...,
        step: int = ...,
        max_pages: int | None = ...,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
    ) -> Iterator[Any]: ...
    @overload
    def operation(
        self,
        operation_id: Literal['youtube-captions'],
        params: YoutubeCaptionsParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeCaptionsResponse: ...
    @overload
    def operation(
        self,
        operation_id: Literal['youtube-channel-playlists'],
        params: YoutubeChannelPlaylistsParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeChannelPlaylistsResponse: ...
    @overload
    def operation(
        self,
        operation_id: Literal['youtube-channel-search'],
        params: YoutubeChannelSearchParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeChannelSearchResponse: ...
    @overload
    def operation(
        self,
        operation_id: Literal['youtube-channel-shorts'],
        params: YoutubeChannelShortsParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeChannelShortsResponse: ...
    @overload
    def operation(
        self,
        operation_id: Literal['youtube-channel-videos'],
        params: YoutubeChannelVideosParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeChannelVideosResponse: ...
    @overload
    def operation(
        self,
        operation_id: Literal['youtube-comments'],
        params: YoutubeCommentsParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeCommentsResponse: ...
    @overload
    def operation(
        self,
        operation_id: Literal['youtube-playlist'],
        params: YoutubePlaylistParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubePlaylistResponse: ...
    @overload
    def operation(
        self,
        operation_id: Literal['youtube-profile'],
        params: YoutubeProfileParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeProfileResponse: ...
    @overload
    def operation(
        self,
        operation_id: Literal['youtube-search'],
        params: YoutubeSearchParams = ...,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeSearchResponse: ...
    @overload
    def operation(
        self,
        operation_id: Literal['youtube-suggest'],
        params: YoutubeSuggestParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeSuggestResponse: ...
    @overload
    def operation(
        self,
        operation_id: Literal['youtube-tag'],
        params: YoutubeTagParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeTagResponse: ...
    @overload
    def operation(
        self,
        operation_id: Literal['youtube-transcript'],
        params: YoutubeTranscriptParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeTranscriptResponse: ...
    @overload
    def operation(
        self,
        operation_id: Literal['youtube-transcript-languages'],
        params: YoutubeTranscriptLanguagesParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeTranscriptLanguagesResponse: ...
    @overload
    def operation(
        self,
        operation_id: Literal['youtube-video'],
        params: YoutubeVideoParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeVideoResponse: ...
    @overload
    def operation(
        self,
        operation_id: str,
        params: Mapping[str, Any] | None = ...,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> Any: ...
    @overload
    def request(
        self,
        operation_id: Literal['youtube-captions'],
        params: YoutubeCaptionsParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeCaptionsResponse: ...
    @overload
    def request(
        self,
        operation_id: Literal['youtube-channel-playlists'],
        params: YoutubeChannelPlaylistsParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeChannelPlaylistsResponse: ...
    @overload
    def request(
        self,
        operation_id: Literal['youtube-channel-search'],
        params: YoutubeChannelSearchParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeChannelSearchResponse: ...
    @overload
    def request(
        self,
        operation_id: Literal['youtube-channel-shorts'],
        params: YoutubeChannelShortsParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeChannelShortsResponse: ...
    @overload
    def request(
        self,
        operation_id: Literal['youtube-channel-videos'],
        params: YoutubeChannelVideosParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeChannelVideosResponse: ...
    @overload
    def request(
        self,
        operation_id: Literal['youtube-comments'],
        params: YoutubeCommentsParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeCommentsResponse: ...
    @overload
    def request(
        self,
        operation_id: Literal['youtube-playlist'],
        params: YoutubePlaylistParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubePlaylistResponse: ...
    @overload
    def request(
        self,
        operation_id: Literal['youtube-profile'],
        params: YoutubeProfileParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeProfileResponse: ...
    @overload
    def request(
        self,
        operation_id: Literal['youtube-search'],
        params: YoutubeSearchParams = ...,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeSearchResponse: ...
    @overload
    def request(
        self,
        operation_id: Literal['youtube-suggest'],
        params: YoutubeSuggestParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeSuggestResponse: ...
    @overload
    def request(
        self,
        operation_id: Literal['youtube-tag'],
        params: YoutubeTagParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeTagResponse: ...
    @overload
    def request(
        self,
        operation_id: Literal['youtube-transcript'],
        params: YoutubeTranscriptParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeTranscriptResponse: ...
    @overload
    def request(
        self,
        operation_id: Literal['youtube-transcript-languages'],
        params: YoutubeTranscriptLanguagesParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeTranscriptLanguagesResponse: ...
    @overload
    def request(
        self,
        operation_id: Literal['youtube-video'],
        params: YoutubeVideoParams,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> YoutubeVideoResponse: ...
    @overload
    def request(
        self,
        operation_id: str,
        params: Mapping[str, Any] | None = ...,
        *,
        response_type: ResponseType = ...,
        timeout: float | None = ...,
        headers: Mapping[str, str] | None = ...,
        retries: int | None = ...,
        retry_predicate: Callable[[int, BaseException | None], bool] | None = ...,
    ) -> Any: ...

VERSION: str

# Internal helpers reused by the async client; not part of the public API.
def _build_request(base_url: str, operation: Mapping[str, Any], params: dict[str, Any]) -> tuple[Any, Any, dict[str, str]]: ...
def _merge_headers(*sources: Mapping[str, str]) -> dict[str, str]: ...
def _auth_headers(security: list[str], api_key: str, jwt_token: str) -> dict[str, str]: ...
def _ensure_request_id(headers: dict[str, str]) -> str: ...
def _header_value(headers: Mapping[str, str], name: str) -> str: ...
def _parse_response(body: bytes, content_type: str, response_type: str) -> Any: ...
def _validate_response_type(response_type: str) -> ResponseType: ...
def _api_error_class(status: int) -> type[CrawloraError]: ...
def _run_before_request(hooks: list[Any], ctx: dict[str, Any]) -> None: ...
def _run_after_response(hooks: list[Any], operation_id: Any, status: int, headers: Mapping[str, str], body: Any) -> Any: ...
def _allowed_params(operation_id: str) -> set[str]: ...

from typing import BinaryIO

class AsyncCrawloraClient:
    def __init__(self, **kwargs: Any) -> None: ...
    async def aclose(self) -> None: ...
    async def __aenter__(self) -> AsyncCrawloraClient: ...
    async def __aexit__(self, *exc: Any) -> None: ...
    async def request(self, operation_id: str, params: Mapping[str, Any] | None = ..., *, response_type: ResponseType = ..., timeout: float | None = ..., headers: Mapping[str, str] | None = ..., retries: int | None = ..., retry_predicate: Callable[[int, BaseException | None], bool] | None = ...) -> Any: ...

class YouTubeClient(CrawloraClient):
    def __enter__(self) -> YouTubeClient: ...
    @overload
    def captions(self, **params: Unpack[YoutubeCaptionsStreamParams]) -> BinaryIO: ...
    @overload
    def captions(self, **params: Unpack[YoutubeCaptionsTextResponseParams]) -> str: ...
    @overload
    def captions(self, **params: Unpack[YoutubeCaptionsDefaultParams]) -> YoutubeCaptionsResponse: ...
    @overload
    def channel_playlists(self, **params: Unpack[YoutubeChannelPlaylistsStreamParams]) -> BinaryIO: ...
    @overload
    def channel_playlists(self, **params: Unpack[YoutubeChannelPlaylistsTextResponseParams]) -> str: ...
    @overload
    def channel_playlists(self, **params: Unpack[YoutubeChannelPlaylistsDefaultParams]) -> YoutubeChannelPlaylistsResponse: ...
    @overload
    def channel_search(self, **params: Unpack[YoutubeChannelSearchStreamParams]) -> BinaryIO: ...
    @overload
    def channel_search(self, **params: Unpack[YoutubeChannelSearchTextResponseParams]) -> str: ...
    @overload
    def channel_search(self, **params: Unpack[YoutubeChannelSearchDefaultParams]) -> YoutubeChannelSearchResponse: ...
    @overload
    def channel_shorts(self, **params: Unpack[YoutubeChannelShortsStreamParams]) -> BinaryIO: ...
    @overload
    def channel_shorts(self, **params: Unpack[YoutubeChannelShortsTextResponseParams]) -> str: ...
    @overload
    def channel_shorts(self, **params: Unpack[YoutubeChannelShortsDefaultParams]) -> YoutubeChannelShortsResponse: ...
    @overload
    def channel_videos(self, **params: Unpack[YoutubeChannelVideosStreamParams]) -> BinaryIO: ...
    @overload
    def channel_videos(self, **params: Unpack[YoutubeChannelVideosTextResponseParams]) -> str: ...
    @overload
    def channel_videos(self, **params: Unpack[YoutubeChannelVideosDefaultParams]) -> YoutubeChannelVideosResponse: ...
    @overload
    def comments(self, **params: Unpack[YoutubeCommentsStreamParams]) -> BinaryIO: ...
    @overload
    def comments(self, **params: Unpack[YoutubeCommentsTextResponseParams]) -> str: ...
    @overload
    def comments(self, **params: Unpack[YoutubeCommentsDefaultParams]) -> YoutubeCommentsResponse: ...
    @overload
    def playlist(self, **params: Unpack[YoutubePlaylistStreamParams]) -> BinaryIO: ...
    @overload
    def playlist(self, **params: Unpack[YoutubePlaylistTextResponseParams]) -> str: ...
    @overload
    def playlist(self, **params: Unpack[YoutubePlaylistDefaultParams]) -> YoutubePlaylistResponse: ...
    @overload
    def profile(self, **params: Unpack[YoutubeProfileStreamParams]) -> BinaryIO: ...
    @overload
    def profile(self, **params: Unpack[YoutubeProfileTextResponseParams]) -> str: ...
    @overload
    def profile(self, **params: Unpack[YoutubeProfileDefaultParams]) -> YoutubeProfileResponse: ...
    @overload
    def search(self, **params: Unpack[YoutubeSearchStreamParams]) -> BinaryIO: ...
    @overload
    def search(self, **params: Unpack[YoutubeSearchTextResponseParams]) -> str: ...
    @overload
    def search(self, **params: Unpack[YoutubeSearchDefaultParams]) -> YoutubeSearchResponse: ...
    @overload
    def suggest(self, **params: Unpack[YoutubeSuggestStreamParams]) -> BinaryIO: ...
    @overload
    def suggest(self, **params: Unpack[YoutubeSuggestTextResponseParams]) -> str: ...
    @overload
    def suggest(self, **params: Unpack[YoutubeSuggestDefaultParams]) -> YoutubeSuggestResponse: ...
    @overload
    def tag(self, **params: Unpack[YoutubeTagStreamParams]) -> BinaryIO: ...
    @overload
    def tag(self, **params: Unpack[YoutubeTagTextResponseParams]) -> str: ...
    @overload
    def tag(self, **params: Unpack[YoutubeTagDefaultParams]) -> YoutubeTagResponse: ...
    @overload
    def transcript(self, **params: Unpack[YoutubeTranscriptStreamParams]) -> BinaryIO: ...
    @overload
    def transcript(self, **params: Unpack[YoutubeTranscriptTextResponseParams]) -> str: ...
    @overload
    def transcript(self, **params: Unpack[YoutubeTranscriptTextParams]) -> str: ...
    @overload
    def transcript(self, **params: Unpack[YoutubeTranscriptDefaultParams]) -> YoutubeTranscriptResponse: ...
    @overload
    def transcript_languages(self, **params: Unpack[YoutubeTranscriptLanguagesStreamParams]) -> BinaryIO: ...
    @overload
    def transcript_languages(self, **params: Unpack[YoutubeTranscriptLanguagesTextResponseParams]) -> str: ...
    @overload
    def transcript_languages(self, **params: Unpack[YoutubeTranscriptLanguagesDefaultParams]) -> YoutubeTranscriptLanguagesResponse: ...
    @overload
    def video(self, **params: Unpack[YoutubeVideoStreamParams]) -> BinaryIO: ...
    @overload
    def video(self, **params: Unpack[YoutubeVideoTextResponseParams]) -> str: ...
    @overload
    def video(self, **params: Unpack[YoutubeVideoDefaultParams]) -> YoutubeVideoResponse: ...

class AsyncYouTubeClient(AsyncCrawloraClient):
    async def __aenter__(self) -> AsyncYouTubeClient: ...
    youtube: _AsyncYoutubeGroup
    @overload
    async def captions(self, **params: Unpack[YoutubeCaptionsStreamParams]) -> BinaryIO: ...
    @overload
    async def captions(self, **params: Unpack[YoutubeCaptionsTextResponseParams]) -> str: ...
    @overload
    async def captions(self, **params: Unpack[YoutubeCaptionsDefaultParams]) -> YoutubeCaptionsResponse: ...
    @overload
    async def channel_playlists(self, **params: Unpack[YoutubeChannelPlaylistsStreamParams]) -> BinaryIO: ...
    @overload
    async def channel_playlists(self, **params: Unpack[YoutubeChannelPlaylistsTextResponseParams]) -> str: ...
    @overload
    async def channel_playlists(self, **params: Unpack[YoutubeChannelPlaylistsDefaultParams]) -> YoutubeChannelPlaylistsResponse: ...
    @overload
    async def channel_search(self, **params: Unpack[YoutubeChannelSearchStreamParams]) -> BinaryIO: ...
    @overload
    async def channel_search(self, **params: Unpack[YoutubeChannelSearchTextResponseParams]) -> str: ...
    @overload
    async def channel_search(self, **params: Unpack[YoutubeChannelSearchDefaultParams]) -> YoutubeChannelSearchResponse: ...
    @overload
    async def channel_shorts(self, **params: Unpack[YoutubeChannelShortsStreamParams]) -> BinaryIO: ...
    @overload
    async def channel_shorts(self, **params: Unpack[YoutubeChannelShortsTextResponseParams]) -> str: ...
    @overload
    async def channel_shorts(self, **params: Unpack[YoutubeChannelShortsDefaultParams]) -> YoutubeChannelShortsResponse: ...
    @overload
    async def channel_videos(self, **params: Unpack[YoutubeChannelVideosStreamParams]) -> BinaryIO: ...
    @overload
    async def channel_videos(self, **params: Unpack[YoutubeChannelVideosTextResponseParams]) -> str: ...
    @overload
    async def channel_videos(self, **params: Unpack[YoutubeChannelVideosDefaultParams]) -> YoutubeChannelVideosResponse: ...
    @overload
    async def comments(self, **params: Unpack[YoutubeCommentsStreamParams]) -> BinaryIO: ...
    @overload
    async def comments(self, **params: Unpack[YoutubeCommentsTextResponseParams]) -> str: ...
    @overload
    async def comments(self, **params: Unpack[YoutubeCommentsDefaultParams]) -> YoutubeCommentsResponse: ...
    @overload
    async def playlist(self, **params: Unpack[YoutubePlaylistStreamParams]) -> BinaryIO: ...
    @overload
    async def playlist(self, **params: Unpack[YoutubePlaylistTextResponseParams]) -> str: ...
    @overload
    async def playlist(self, **params: Unpack[YoutubePlaylistDefaultParams]) -> YoutubePlaylistResponse: ...
    @overload
    async def profile(self, **params: Unpack[YoutubeProfileStreamParams]) -> BinaryIO: ...
    @overload
    async def profile(self, **params: Unpack[YoutubeProfileTextResponseParams]) -> str: ...
    @overload
    async def profile(self, **params: Unpack[YoutubeProfileDefaultParams]) -> YoutubeProfileResponse: ...
    @overload
    async def search(self, **params: Unpack[YoutubeSearchStreamParams]) -> BinaryIO: ...
    @overload
    async def search(self, **params: Unpack[YoutubeSearchTextResponseParams]) -> str: ...
    @overload
    async def search(self, **params: Unpack[YoutubeSearchDefaultParams]) -> YoutubeSearchResponse: ...
    @overload
    async def suggest(self, **params: Unpack[YoutubeSuggestStreamParams]) -> BinaryIO: ...
    @overload
    async def suggest(self, **params: Unpack[YoutubeSuggestTextResponseParams]) -> str: ...
    @overload
    async def suggest(self, **params: Unpack[YoutubeSuggestDefaultParams]) -> YoutubeSuggestResponse: ...
    @overload
    async def tag(self, **params: Unpack[YoutubeTagStreamParams]) -> BinaryIO: ...
    @overload
    async def tag(self, **params: Unpack[YoutubeTagTextResponseParams]) -> str: ...
    @overload
    async def tag(self, **params: Unpack[YoutubeTagDefaultParams]) -> YoutubeTagResponse: ...
    @overload
    async def transcript(self, **params: Unpack[YoutubeTranscriptStreamParams]) -> BinaryIO: ...
    @overload
    async def transcript(self, **params: Unpack[YoutubeTranscriptTextResponseParams]) -> str: ...
    @overload
    async def transcript(self, **params: Unpack[YoutubeTranscriptTextParams]) -> str: ...
    @overload
    async def transcript(self, **params: Unpack[YoutubeTranscriptDefaultParams]) -> YoutubeTranscriptResponse: ...
    @overload
    async def transcript_languages(self, **params: Unpack[YoutubeTranscriptLanguagesStreamParams]) -> BinaryIO: ...
    @overload
    async def transcript_languages(self, **params: Unpack[YoutubeTranscriptLanguagesTextResponseParams]) -> str: ...
    @overload
    async def transcript_languages(self, **params: Unpack[YoutubeTranscriptLanguagesDefaultParams]) -> YoutubeTranscriptLanguagesResponse: ...
    @overload
    async def video(self, **params: Unpack[YoutubeVideoStreamParams]) -> BinaryIO: ...
    @overload
    async def video(self, **params: Unpack[YoutubeVideoTextResponseParams]) -> str: ...
    @overload
    async def video(self, **params: Unpack[YoutubeVideoDefaultParams]) -> YoutubeVideoResponse: ...

class _AsyncYoutubeGroup:
    @overload
    async def captions(self, **params: Unpack[YoutubeCaptionsStreamParams]) -> BinaryIO: ...
    @overload
    async def captions(self, **params: Unpack[YoutubeCaptionsTextResponseParams]) -> str: ...
    @overload
    async def captions(self, **params: Unpack[YoutubeCaptionsDefaultParams]) -> YoutubeCaptionsResponse: ...
    @overload
    async def channel_playlists(self, **params: Unpack[YoutubeChannelPlaylistsStreamParams]) -> BinaryIO: ...
    @overload
    async def channel_playlists(self, **params: Unpack[YoutubeChannelPlaylistsTextResponseParams]) -> str: ...
    @overload
    async def channel_playlists(self, **params: Unpack[YoutubeChannelPlaylistsDefaultParams]) -> YoutubeChannelPlaylistsResponse: ...
    @overload
    async def channel_search(self, **params: Unpack[YoutubeChannelSearchStreamParams]) -> BinaryIO: ...
    @overload
    async def channel_search(self, **params: Unpack[YoutubeChannelSearchTextResponseParams]) -> str: ...
    @overload
    async def channel_search(self, **params: Unpack[YoutubeChannelSearchDefaultParams]) -> YoutubeChannelSearchResponse: ...
    @overload
    async def channel_shorts(self, **params: Unpack[YoutubeChannelShortsStreamParams]) -> BinaryIO: ...
    @overload
    async def channel_shorts(self, **params: Unpack[YoutubeChannelShortsTextResponseParams]) -> str: ...
    @overload
    async def channel_shorts(self, **params: Unpack[YoutubeChannelShortsDefaultParams]) -> YoutubeChannelShortsResponse: ...
    @overload
    async def channel_videos(self, **params: Unpack[YoutubeChannelVideosStreamParams]) -> BinaryIO: ...
    @overload
    async def channel_videos(self, **params: Unpack[YoutubeChannelVideosTextResponseParams]) -> str: ...
    @overload
    async def channel_videos(self, **params: Unpack[YoutubeChannelVideosDefaultParams]) -> YoutubeChannelVideosResponse: ...
    @overload
    async def comments(self, **params: Unpack[YoutubeCommentsStreamParams]) -> BinaryIO: ...
    @overload
    async def comments(self, **params: Unpack[YoutubeCommentsTextResponseParams]) -> str: ...
    @overload
    async def comments(self, **params: Unpack[YoutubeCommentsDefaultParams]) -> YoutubeCommentsResponse: ...
    @overload
    async def playlist(self, **params: Unpack[YoutubePlaylistStreamParams]) -> BinaryIO: ...
    @overload
    async def playlist(self, **params: Unpack[YoutubePlaylistTextResponseParams]) -> str: ...
    @overload
    async def playlist(self, **params: Unpack[YoutubePlaylistDefaultParams]) -> YoutubePlaylistResponse: ...
    @overload
    async def profile(self, **params: Unpack[YoutubeProfileStreamParams]) -> BinaryIO: ...
    @overload
    async def profile(self, **params: Unpack[YoutubeProfileTextResponseParams]) -> str: ...
    @overload
    async def profile(self, **params: Unpack[YoutubeProfileDefaultParams]) -> YoutubeProfileResponse: ...
    @overload
    async def search(self, **params: Unpack[YoutubeSearchStreamParams]) -> BinaryIO: ...
    @overload
    async def search(self, **params: Unpack[YoutubeSearchTextResponseParams]) -> str: ...
    @overload
    async def search(self, **params: Unpack[YoutubeSearchDefaultParams]) -> YoutubeSearchResponse: ...
    @overload
    async def suggest(self, **params: Unpack[YoutubeSuggestStreamParams]) -> BinaryIO: ...
    @overload
    async def suggest(self, **params: Unpack[YoutubeSuggestTextResponseParams]) -> str: ...
    @overload
    async def suggest(self, **params: Unpack[YoutubeSuggestDefaultParams]) -> YoutubeSuggestResponse: ...
    @overload
    async def tag(self, **params: Unpack[YoutubeTagStreamParams]) -> BinaryIO: ...
    @overload
    async def tag(self, **params: Unpack[YoutubeTagTextResponseParams]) -> str: ...
    @overload
    async def tag(self, **params: Unpack[YoutubeTagDefaultParams]) -> YoutubeTagResponse: ...
    @overload
    async def transcript(self, **params: Unpack[YoutubeTranscriptStreamParams]) -> BinaryIO: ...
    @overload
    async def transcript(self, **params: Unpack[YoutubeTranscriptTextResponseParams]) -> str: ...
    @overload
    async def transcript(self, **params: Unpack[YoutubeTranscriptTextParams]) -> str: ...
    @overload
    async def transcript(self, **params: Unpack[YoutubeTranscriptDefaultParams]) -> YoutubeTranscriptResponse: ...
    @overload
    async def transcript_languages(self, **params: Unpack[YoutubeTranscriptLanguagesStreamParams]) -> BinaryIO: ...
    @overload
    async def transcript_languages(self, **params: Unpack[YoutubeTranscriptLanguagesTextResponseParams]) -> str: ...
    @overload
    async def transcript_languages(self, **params: Unpack[YoutubeTranscriptLanguagesDefaultParams]) -> YoutubeTranscriptLanguagesResponse: ...
    @overload
    async def video(self, **params: Unpack[YoutubeVideoStreamParams]) -> BinaryIO: ...
    @overload
    async def video(self, **params: Unpack[YoutubeVideoTextResponseParams]) -> str: ...
    @overload
    async def video(self, **params: Unpack[YoutubeVideoDefaultParams]) -> YoutubeVideoResponse: ...

YoutubeCaptionsDefaultParams = TypedDict('YoutubeCaptionsDefaultParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': NotRequired[Literal["auto", "json"]],
    'id': Required[str],
    'lang': NotRequired[str],
}, total=False)

YoutubeCaptionsTextResponseParams = TypedDict('YoutubeCaptionsTextResponseParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["text"]],
    'id': Required[str],
    'lang': NotRequired[str],
}, total=False)

YoutubeCaptionsStreamParams = TypedDict('YoutubeCaptionsStreamParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["stream"]],
    'id': Required[str],
    'lang': NotRequired[str],
}, total=False)

YoutubeChannelPlaylistsDefaultParams = TypedDict('YoutubeChannelPlaylistsDefaultParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': NotRequired[Literal["auto", "json"]],
    'id': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeChannelPlaylistsTextResponseParams = TypedDict('YoutubeChannelPlaylistsTextResponseParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["text"]],
    'id': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeChannelPlaylistsStreamParams = TypedDict('YoutubeChannelPlaylistsStreamParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["stream"]],
    'id': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeChannelSearchDefaultParams = TypedDict('YoutubeChannelSearchDefaultParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': NotRequired[Literal["auto", "json"]],
    'id': Required[str],
    'q': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeChannelSearchTextResponseParams = TypedDict('YoutubeChannelSearchTextResponseParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["text"]],
    'id': Required[str],
    'q': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeChannelSearchStreamParams = TypedDict('YoutubeChannelSearchStreamParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["stream"]],
    'id': Required[str],
    'q': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeChannelShortsDefaultParams = TypedDict('YoutubeChannelShortsDefaultParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': NotRequired[Literal["auto", "json"]],
    'id': Required[str],
}, total=False)

YoutubeChannelShortsTextResponseParams = TypedDict('YoutubeChannelShortsTextResponseParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["text"]],
    'id': Required[str],
}, total=False)

YoutubeChannelShortsStreamParams = TypedDict('YoutubeChannelShortsStreamParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["stream"]],
    'id': Required[str],
}, total=False)

YoutubeChannelVideosDefaultParams = TypedDict('YoutubeChannelVideosDefaultParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': NotRequired[Literal["auto", "json"]],
    'id': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeChannelVideosTextResponseParams = TypedDict('YoutubeChannelVideosTextResponseParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["text"]],
    'id': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeChannelVideosStreamParams = TypedDict('YoutubeChannelVideosStreamParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["stream"]],
    'id': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeCommentsDefaultParams = TypedDict('YoutubeCommentsDefaultParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': NotRequired[Literal["auto", "json"]],
    'id': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeCommentsTextResponseParams = TypedDict('YoutubeCommentsTextResponseParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["text"]],
    'id': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeCommentsStreamParams = TypedDict('YoutubeCommentsStreamParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["stream"]],
    'id': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubePlaylistDefaultParams = TypedDict('YoutubePlaylistDefaultParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': NotRequired[Literal["auto", "json"]],
    'id': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubePlaylistTextResponseParams = TypedDict('YoutubePlaylistTextResponseParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["text"]],
    'id': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubePlaylistStreamParams = TypedDict('YoutubePlaylistStreamParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["stream"]],
    'id': Required[str],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeProfileDefaultParams = TypedDict('YoutubeProfileDefaultParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': NotRequired[Literal["auto", "json"]],
    'id': Required[str],
}, total=False)

YoutubeProfileTextResponseParams = TypedDict('YoutubeProfileTextResponseParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["text"]],
    'id': Required[str],
}, total=False)

YoutubeProfileStreamParams = TypedDict('YoutubeProfileStreamParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["stream"]],
    'id': Required[str],
}, total=False)

YoutubeSearchDefaultParams = TypedDict('YoutubeSearchDefaultParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': NotRequired[Literal["auto", "json"]],
    'q': NotRequired[str],
    'search_query': NotRequired[str],
    'continuation_token': NotRequired[str],
    'type': NotRequired[Literal['video', 'shorts', 'channel', 'playlist', 'movie']],
    'sort_by': NotRequired[Literal['relevance', 'upload_date', 'view_count', 'popularity', 'rating']],
    'upload_date': NotRequired[Literal['last_hour', 'today', 'this_week', 'this_month', 'this_year']],
    'duration': NotRequired[Literal['under_3_minutes', 'three_to_20_minutes', 'over_20_minutes', 'under_3', 'three_to_20', 'over_20', 'short', 'medium', 'long']],
    'features': NotRequired[str],
    'hl': NotRequired[str],
    'gl': NotRequired[str],
    'params': NotRequired[str],
}, total=False)

YoutubeSearchTextResponseParams = TypedDict('YoutubeSearchTextResponseParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["text"]],
    'q': NotRequired[str],
    'search_query': NotRequired[str],
    'continuation_token': NotRequired[str],
    'type': NotRequired[Literal['video', 'shorts', 'channel', 'playlist', 'movie']],
    'sort_by': NotRequired[Literal['relevance', 'upload_date', 'view_count', 'popularity', 'rating']],
    'upload_date': NotRequired[Literal['last_hour', 'today', 'this_week', 'this_month', 'this_year']],
    'duration': NotRequired[Literal['under_3_minutes', 'three_to_20_minutes', 'over_20_minutes', 'under_3', 'three_to_20', 'over_20', 'short', 'medium', 'long']],
    'features': NotRequired[str],
    'hl': NotRequired[str],
    'gl': NotRequired[str],
    'params': NotRequired[str],
}, total=False)

YoutubeSearchStreamParams = TypedDict('YoutubeSearchStreamParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["stream"]],
    'q': NotRequired[str],
    'search_query': NotRequired[str],
    'continuation_token': NotRequired[str],
    'type': NotRequired[Literal['video', 'shorts', 'channel', 'playlist', 'movie']],
    'sort_by': NotRequired[Literal['relevance', 'upload_date', 'view_count', 'popularity', 'rating']],
    'upload_date': NotRequired[Literal['last_hour', 'today', 'this_week', 'this_month', 'this_year']],
    'duration': NotRequired[Literal['under_3_minutes', 'three_to_20_minutes', 'over_20_minutes', 'under_3', 'three_to_20', 'over_20', 'short', 'medium', 'long']],
    'features': NotRequired[str],
    'hl': NotRequired[str],
    'gl': NotRequired[str],
    'params': NotRequired[str],
}, total=False)

YoutubeSuggestDefaultParams = TypedDict('YoutubeSuggestDefaultParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': NotRequired[Literal["auto", "json"]],
    'q': Required[str],
    'count': NotRequired[int],
    'hl': NotRequired[str],
    'gl': NotRequired[str],
}, total=False)

YoutubeSuggestTextResponseParams = TypedDict('YoutubeSuggestTextResponseParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["text"]],
    'q': Required[str],
    'count': NotRequired[int],
    'hl': NotRequired[str],
    'gl': NotRequired[str],
}, total=False)

YoutubeSuggestStreamParams = TypedDict('YoutubeSuggestStreamParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["stream"]],
    'q': Required[str],
    'count': NotRequired[int],
    'hl': NotRequired[str],
    'gl': NotRequired[str],
}, total=False)

YoutubeTagDefaultParams = TypedDict('YoutubeTagDefaultParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': NotRequired[Literal["auto", "json"]],
    'tag': Required[str],
    'type': NotRequired[Literal['all', 'shorts']],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeTagTextResponseParams = TypedDict('YoutubeTagTextResponseParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["text"]],
    'tag': Required[str],
    'type': NotRequired[Literal['all', 'shorts']],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeTagStreamParams = TypedDict('YoutubeTagStreamParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["stream"]],
    'tag': Required[str],
    'type': NotRequired[Literal['all', 'shorts']],
    'continuation_token': NotRequired[str],
}, total=False)

YoutubeTranscriptDefaultParams = TypedDict('YoutubeTranscriptDefaultParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': NotRequired[Literal["auto", "json"]],
    'id': Required[str],
    'lang': NotRequired[str],
    'translate_to': NotRequired[str],
    'format': NotRequired[Literal['json']],
    'timestamps': NotRequired[bool],
}, total=False)

YoutubeTranscriptTextResponseParams = TypedDict('YoutubeTranscriptTextResponseParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["text"]],
    'id': Required[str],
    'lang': NotRequired[str],
    'translate_to': NotRequired[str],
    'format': NotRequired[Literal['text', 'srt', 'vtt']],
    'timestamps': NotRequired[bool],
}, total=False)

YoutubeTranscriptStreamParams = TypedDict('YoutubeTranscriptStreamParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["stream"]],
    'id': Required[str],
    'lang': NotRequired[str],
    'translate_to': NotRequired[str],
    'format': NotRequired[Literal['json', 'text', 'srt', 'vtt']],
    'timestamps': NotRequired[bool],
}, total=False)

YoutubeTranscriptTextParams = TypedDict('YoutubeTranscriptTextParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': NotRequired[Literal["auto", "text"]],
    'id': Required[str],
    'lang': NotRequired[str],
    'translate_to': NotRequired[str],
    'format': Required[Literal['text', 'srt', 'vtt']],
    'timestamps': NotRequired[bool],
}, total=False)

YoutubeTranscriptLanguagesDefaultParams = TypedDict('YoutubeTranscriptLanguagesDefaultParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': NotRequired[Literal["auto", "json"]],
    'id': Required[str],
}, total=False)

YoutubeTranscriptLanguagesTextResponseParams = TypedDict('YoutubeTranscriptLanguagesTextResponseParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["text"]],
    'id': Required[str],
}, total=False)

YoutubeTranscriptLanguagesStreamParams = TypedDict('YoutubeTranscriptLanguagesStreamParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["stream"]],
    'id': Required[str],
}, total=False)

YoutubeVideoDefaultParams = TypedDict('YoutubeVideoDefaultParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': NotRequired[Literal["auto", "json"]],
    'id': Required[str],
}, total=False)

YoutubeVideoTextResponseParams = TypedDict('YoutubeVideoTextResponseParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["text"]],
    'id': Required[str],
}, total=False)

YoutubeVideoStreamParams = TypedDict('YoutubeVideoStreamParams', {
    '_timeout': NotRequired[float],
    '_headers': NotRequired[Mapping[str, str]],
    '_response_type': Required[Literal["stream"]],
    'id': Required[str],
}, total=False)
