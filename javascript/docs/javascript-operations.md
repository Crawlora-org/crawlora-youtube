# Crawlora YouTube JavaScript Client Operations

Generated from `openapi/public.json`. Deprecated, admin, and internal operations are excluded from this SDK contract.

Total operations: `14`

| Group | SDK method | Operation ID | HTTP | Params | Auth | Response | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| youtube | `youtube.captions` | `youtube-captions` | `GET /youtube/captions/{id}` | `id` (path string required)<br>`lang` (query string) | `ApiKeyAuth` | `YoutubeCaptionsResponse` |  |
| youtube | `youtube.channelPlaylists` | `youtube-channel-playlists` | `GET /youtube/channel/{id}/playlists` | `id` (path string required)<br>`continuation_token` (query string) | `ApiKeyAuth` | `YoutubeChannelPlaylistsResponse` |  |
| youtube | `youtube.channelSearch` | `youtube-channel-search` | `GET /youtube/channel/{id}/search` | `id` (path string required)<br>`q` (query string required)<br>`continuation_token` (query string) | `ApiKeyAuth` | `YoutubeChannelSearchResponse` |  |
| youtube | `youtube.channelShorts` | `youtube-channel-shorts` | `GET /youtube/channel/{id}/shorts` | `id` (path string required) | `ApiKeyAuth` | `YoutubeChannelShortsResponse` |  |
| youtube | `youtube.channelVideos` | `youtube-channel-videos` | `GET /youtube/channel/{id}/videos` | `id` (path string required)<br>`continuation_token` (query string) | `ApiKeyAuth` | `YoutubeChannelVideosResponse` |  |
| youtube | `youtube.comments` | `youtube-comments` | `GET /youtube/comments/{id}` | `id` (path string required)<br>`continuation_token` (query string) | `ApiKeyAuth` | `YoutubeCommentsResponse` |  |
| youtube | `youtube.playlist` | `youtube-playlist` | `GET /youtube/playlist/{id}` | `id` (path string required)<br>`continuation_token` (query string) | `ApiKeyAuth` | `YoutubePlaylistResponse` |  |
| youtube | `youtube.profile` | `youtube-profile` | `GET /youtube/profile/{id}` | `id` (path string required) | `ApiKeyAuth` | `YoutubeProfileResponse` |  |
| youtube | `youtube.search` | `youtube-search` | `GET /youtube/search` | `q` (query string)<br>`search_query` (query string)<br>`continuation_token` (query string)<br>`type` (query "video" \| "shorts" \| "channel" \| "playlist" \| "movie")<br>`sort_by` (query "relevance" \| "upload_date" \| "view_count" \| "popularity" \| "rating")<br>`upload_date` (query "last_hour" \| "today" \| "this_week" \| "this_month" \| "this_year")<br>`duration` (query "under_3_minutes" \| "three_to_20_minutes" \| "over_20_minutes" \| "under_3" \| "three_to_20" \| "over_20" \| "short" \| "medium" \| "long")<br>`features` (query string)<br>`hl` (query string)<br>`gl` (query string)<br>`params` (query string) | `ApiKeyAuth` | `YoutubeSearchResponse` |  |
| youtube | `youtube.suggest` | `youtube-suggest` | `GET /youtube/suggest` | `q` (query string required)<br>`count` (query number)<br>`hl` (query string)<br>`gl` (query string) | `ApiKeyAuth` | `YoutubeSuggestResponse` |  |
| youtube | `youtube.tag` | `youtube-tag` | `GET /youtube/tag/{tag}` | `tag` (path string required)<br>`type` (query "all" \| "shorts")<br>`continuation_token` (query string) | `ApiKeyAuth` | `YoutubeTagResponse` |  |
| youtube | `youtube.transcript` | `youtube-transcript` | `GET /youtube/transcript/{id}` | `id` (path string required)<br>`lang` (query string)<br>`translate_to` (query string)<br>`format` (query "json" \| "text" \| "srt" \| "vtt")<br>`timestamps` (query boolean) | `ApiKeyAuth` | `YoutubeTranscriptResponse` | Supports text response mode. |
| youtube | `youtube.transcriptLanguages` | `youtube-transcript-languages` | `GET /youtube/transcript/{id}/languages` | `id` (path string required) | `ApiKeyAuth` | `YoutubeTranscriptLanguagesResponse` |  |
| youtube | `youtube.video` | `youtube-video` | `GET /youtube/video/{id}` | `id` (path string required) | `ApiKeyAuth` | `YoutubeVideoResponse` |  |
