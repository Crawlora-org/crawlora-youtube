# Crawlora YouTube Rust SDK Operations

Generated from `openapi/public.json`. Deprecated, admin, and internal operations are excluded from this SDK contract.

Total operations: `14`

| Group | SDK method | Operation ID | HTTP | Params | Auth | Response | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| youtube | `youtube.captions` | `youtube-captions` | `GET /youtube/captions/{id}` | `id` (path String required)<br>`lang` (query String) | `ApiKeyAuth` | `YoutubeCaptionsResponse` |  |
| youtube | `youtube.channel_playlists` | `youtube-channel-playlists` | `GET /youtube/channel/{id}/playlists` | `id` (path String required)<br>`continuation_token` (query String) | `ApiKeyAuth` | `YoutubeChannelPlaylistsResponse` |  |
| youtube | `youtube.channel_search` | `youtube-channel-search` | `GET /youtube/channel/{id}/search` | `id` (path String required)<br>`q` (query String required)<br>`continuation_token` (query String) | `ApiKeyAuth` | `YoutubeChannelSearchResponse` |  |
| youtube | `youtube.channel_shorts` | `youtube-channel-shorts` | `GET /youtube/channel/{id}/shorts` | `id` (path String required) | `ApiKeyAuth` | `YoutubeChannelShortsResponse` |  |
| youtube | `youtube.channel_videos` | `youtube-channel-videos` | `GET /youtube/channel/{id}/videos` | `id` (path String required)<br>`continuation_token` (query String) | `ApiKeyAuth` | `YoutubeChannelVideosResponse` |  |
| youtube | `youtube.comments` | `youtube-comments` | `GET /youtube/comments/{id}` | `id` (path String required)<br>`continuation_token` (query String) | `ApiKeyAuth` | `YoutubeCommentsResponse` |  |
| youtube | `youtube.playlist` | `youtube-playlist` | `GET /youtube/playlist/{id}` | `id` (path String required)<br>`continuation_token` (query String) | `ApiKeyAuth` | `YoutubePlaylistResponse` |  |
| youtube | `youtube.profile` | `youtube-profile` | `GET /youtube/profile/{id}` | `id` (path String required) | `ApiKeyAuth` | `YoutubeProfileResponse` |  |
| youtube | `youtube.search` | `youtube-search` | `GET /youtube/search` | `q` (query String)<br>`search_query` (query String)<br>`continuation_token` (query String)<br>`type` (query String enum{video, shorts, channel, playlist, movie})<br>`sort_by` (query String enum{relevance, upload_date, view_count, popularity, rating})<br>`upload_date` (query String enum{last_hour, today, this_week, this_month, this_year})<br>`duration` (query String enum{under_3_minutes, three_to_20_minutes, over_20_minutes, under_3, three_to_20, over_20, short, medium, long})<br>`features` (query String)<br>`hl` (query String)<br>`gl` (query String)<br>`params` (query String) | `ApiKeyAuth` | `YoutubeSearchResponse` |  |
| youtube | `youtube.suggest` | `youtube-suggest` | `GET /youtube/suggest` | `q` (query String required)<br>`count` (query i64)<br>`hl` (query String)<br>`gl` (query String) | `ApiKeyAuth` | `YoutubeSuggestResponse` |  |
| youtube | `youtube.tag` | `youtube-tag` | `GET /youtube/tag/{tag}` | `tag` (path String required)<br>`type` (query String enum{all, shorts})<br>`continuation_token` (query String) | `ApiKeyAuth` | `YoutubeTagResponse` |  |
| youtube | `youtube.transcript` | `youtube-transcript` | `GET /youtube/transcript/{id}` | `id` (path String required)<br>`lang` (query String)<br>`translate_to` (query String)<br>`format` (query String enum{json, text, srt, vtt})<br>`timestamps` (query bool) | `ApiKeyAuth` | `YoutubeTranscriptResponse` | Supports text response mode. |
| youtube | `youtube.transcript_languages` | `youtube-transcript-languages` | `GET /youtube/transcript/{id}/languages` | `id` (path String required) | `ApiKeyAuth` | `YoutubeTranscriptLanguagesResponse` |  |
| youtube | `youtube.video` | `youtube-video` | `GET /youtube/video/{id}` | `id` (path String required) | `ApiKeyAuth` | `YoutubeVideoResponse` |  |
