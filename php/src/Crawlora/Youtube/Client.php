<?php

declare(strict_types=1);

namespace Crawlora\Youtube;

class CrawloraException extends \RuntimeException
{
    public function __construct(string $message, public readonly ?int $status = null, public readonly ?string $operationId = null, public readonly ?string $responseBody = null, ?\Throwable $previous = null)
    {
        parent::__construct($message, 0, $previous);
    }
}

class ClientException extends CrawloraException {}
class ServerException extends CrawloraException {}
class NetworkException extends CrawloraException {}

final class Client
{
    private static array $operations;
    private bool $closed = false;
    private string $apiKey;
    private string $baseUrl;
    private float $timeout;
    private ?\Closure $transport;

    public const PLATFORM = 'youtube';
    public const VERSION = '0.1.8';
    public const OPERATION_COUNT = 14;
    public const OPERATION_IDS = ["youtube-captions", "youtube-channel-playlists", "youtube-channel-search", "youtube-channel-shorts", "youtube-channel-videos", "youtube-comments", "youtube-playlist", "youtube-profile", "youtube-search", "youtube-suggest", "youtube-tag", "youtube-transcript", "youtube-transcript-languages", "youtube-video"];

    public function __construct(?string $apiKey = null, string $baseUrl = 'https://api.crawlora.net/api/v1', float $timeout = 30.0, ?callable $transport = null)
    {
        $this->apiKey = $apiKey ?? (getenv('CRAWLORA_API_KEY') ?: '');
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->timeout = $timeout;
        $this->transport = $transport === null ? null : \Closure::fromCallable($transport);
        self::$operations ??= json_decode(<<<'JSON'
{"youtube-captions": {"id": "youtube-captions", "method": "GET", "params": [{"description": "YouTube video ID (11-character code)", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "YbJOTdZBX1g"}, {"default": "en", "description": "Caption language code (ISO 639-1), defaults to **en**", "in": "query", "name": "lang", "type": "string"}], "path": "/youtube/captions/{id}", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [{"in": "query", "name": "lang", "type": "string"}], "security": ["ApiKeyAuth"]}, "youtube-channel-playlists": {"id": "youtube-channel-playlists", "method": "GET", "params": [{"description": "Channel ID, @handle, /c path, /user path, or full YouTube channel URL", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "UCXZCJLdBC09xxGZ6gcdrc6A"}, {"description": "Pagination token returned by a previous request", "in": "query", "name": "continuation_token", "type": "string"}], "path": "/youtube/channel/{id}/playlists", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [{"in": "query", "name": "continuation_token", "type": "string"}], "security": ["ApiKeyAuth"]}, "youtube-channel-search": {"id": "youtube-channel-search", "method": "GET", "params": [{"description": "Channel ID, @handle, /c path, /user path, or full YouTube channel URL", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "UCXZCJLdBC09xxGZ6gcdrc6A"}, {"description": "Search query", "in": "query", "name": "q", "required": true, "type": "string", "x-example": "gpt"}, {"description": "Pagination token returned by a previous request", "in": "query", "name": "continuation_token", "type": "string"}], "path": "/youtube/channel/{id}/search", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [{"in": "query", "name": "q", "required": true, "type": "string"}, {"in": "query", "name": "continuation_token", "type": "string"}], "security": ["ApiKeyAuth"]}, "youtube-channel-shorts": {"id": "youtube-channel-shorts", "method": "GET", "params": [{"description": "Channel ID, @handle, /c path, /user path, or full YouTube channel URL", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "UCXZCJLdBC09xxGZ6gcdrc6A"}], "path": "/youtube/channel/{id}/shorts", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [], "security": ["ApiKeyAuth"]}, "youtube-channel-videos": {"id": "youtube-channel-videos", "method": "GET", "params": [{"description": "Channel ID, @handle, /c path, /user path, or full YouTube channel URL", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "UCXZCJLdBC09xxGZ6gcdrc6A"}, {"description": "Pagination token returned by a previous request", "in": "query", "name": "continuation_token", "type": "string"}], "path": "/youtube/channel/{id}/videos", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [{"in": "query", "name": "continuation_token", "type": "string"}], "security": ["ApiKeyAuth"]}, "youtube-comments": {"id": "youtube-comments", "method": "GET", "params": [{"description": "YouTube video ID (11-character code)", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "YbJOTdZBX1g"}, {"description": "Pagination token returned by a previous request, first page if empty", "in": "query", "name": "continuation_token", "type": "string"}], "path": "/youtube/comments/{id}", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [{"in": "query", "name": "continuation_token", "type": "string"}], "security": ["ApiKeyAuth"]}, "youtube-playlist": {"id": "youtube-playlist", "method": "GET", "params": [{"description": "YouTube playlist ID or full playlist URL", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "PL-szjqIBRvM_aWOj-uXCVm28l-ZZFa4D2"}, {"description": "Pagination token returned by a previous request", "in": "query", "name": "continuation_token", "type": "string"}], "path": "/youtube/playlist/{id}", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [{"in": "query", "name": "continuation_token", "type": "string"}], "security": ["ApiKeyAuth"]}, "youtube-profile": {"id": "youtube-profile", "method": "GET", "params": [{"description": "Channel ID, @handle, /c path, /user path, bare username, or full YouTube channel URL", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "UCXZCJLdBC09xxGZ6gcdrc6A"}], "path": "/youtube/profile/{id}", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [], "security": ["ApiKeyAuth"]}, "youtube-search": {"id": "youtube-search", "method": "GET", "params": [{"description": "Search query", "in": "query", "name": "q", "type": "string", "x-example": "gpt"}, {"description": "Alias for q", "in": "query", "name": "search_query", "type": "string", "x-example": "gpt"}, {"description": "Pagination token returned by a previous request", "in": "query", "name": "continuation_token", "type": "string"}, {"description": "Filter by type", "enum": ["video", "shorts", "channel", "playlist", "movie"], "in": "query", "name": "type", "type": "string"}, {"description": "Sort results", "enum": ["relevance", "upload_date", "view_count", "popularity", "rating"], "in": "query", "name": "sort_by", "type": "string"}, {"description": "Filter by upload date", "enum": ["last_hour", "today", "this_week", "this_month", "this_year"], "in": "query", "name": "upload_date", "type": "string"}, {"description": "Filter by duration; short, medium, and long preserve their previous upstream encodings", "enum": ["under_3_minutes", "three_to_20_minutes", "over_20_minutes", "under_3", "three_to_20", "over_20", "short", "medium", "long"], "in": "query", "name": "duration", "type": "string"}, {"description": "Comma-separated feature filters. Allowed values: live, 4k, hd, subtitles, cc, creative_commons, 360, vr180, 3d, hdr, location, purchased", "in": "query", "name": "features", "type": "string", "x-example": "hd,subtitles"}, {"description": "YouTube interface language", "in": "query", "name": "hl", "type": "string", "x-example": "en"}, {"description": "Two-letter YouTube region code", "in": "query", "name": "gl", "type": "string", "x-example": "US"}, {"description": "Raw protobuf-encoded search filter (base64)", "in": "query", "name": "params", "type": "string"}], "path": "/youtube/search", "pathParams": [], "produces": ["application/json"], "queryParams": [{"in": "query", "name": "q", "type": "string"}, {"in": "query", "name": "search_query", "type": "string"}, {"in": "query", "name": "continuation_token", "type": "string"}, {"enum": ["video", "shorts", "channel", "playlist", "movie"], "in": "query", "name": "type", "type": "string"}, {"enum": ["relevance", "upload_date", "view_count", "popularity", "rating"], "in": "query", "name": "sort_by", "type": "string"}, {"enum": ["last_hour", "today", "this_week", "this_month", "this_year"], "in": "query", "name": "upload_date", "type": "string"}, {"enum": ["under_3_minutes", "three_to_20_minutes", "over_20_minutes", "under_3", "three_to_20", "over_20", "short", "medium", "long"], "in": "query", "name": "duration", "type": "string"}, {"in": "query", "name": "features", "type": "string"}, {"in": "query", "name": "hl", "type": "string"}, {"in": "query", "name": "gl", "type": "string"}, {"in": "query", "name": "params", "type": "string"}], "security": ["ApiKeyAuth"]}, "youtube-suggest": {"id": "youtube-suggest", "method": "GET", "params": [{"description": "Search query prefix", "in": "query", "name": "q", "required": true, "type": "string", "x-example": "openai"}, {"description": "Suggestions to return; defaults to 10, clamped to 1..20", "in": "query", "maximum": 20, "minimum": 1, "name": "count", "type": "integer", "x-example": 10}, {"description": "YouTube interface language, such as en, de, or pt-BR; defaults to en", "in": "query", "name": "hl", "type": "string", "x-example": "en"}, {"description": "Two-letter YouTube region code; defaults to US", "in": "query", "name": "gl", "type": "string", "x-example": "US"}], "path": "/youtube/suggest", "pathParams": [], "produces": ["application/json"], "queryParams": [{"in": "query", "name": "q", "required": true, "type": "string"}, {"in": "query", "name": "count", "type": "integer"}, {"in": "query", "name": "hl", "type": "string"}, {"in": "query", "name": "gl", "type": "string"}], "security": ["ApiKeyAuth"]}, "youtube-tag": {"id": "youtube-tag", "method": "GET", "params": [{"description": "Tag to filter videos", "in": "path", "name": "tag", "required": true, "type": "string", "x-example": "openai"}, {"default": "all", "description": "Result tab to load", "enum": ["all", "shorts"], "in": "query", "name": "type", "type": "string"}, {"description": "Continuation token for pagination, first page if empty", "in": "query", "name": "continuation_token", "type": "string"}], "path": "/youtube/tag/{tag}", "pathParams": ["tag"], "produces": ["application/json"], "queryParams": [{"enum": ["all", "shorts"], "in": "query", "name": "type", "type": "string"}, {"in": "query", "name": "continuation_token", "type": "string"}], "security": ["ApiKeyAuth"]}, "youtube-transcript": {"id": "youtube-transcript", "method": "GET", "params": [{"description": "YouTube video ID (11-character code)", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "YbJOTdZBX1g"}, {"default": "en", "description": "Preferred transcript language", "in": "query", "name": "lang", "type": "string"}, {"description": "Translate transcript to this language code", "in": "query", "name": "translate_to", "type": "string"}, {"default": "json", "description": "Response format", "enum": ["json", "text", "srt", "vtt"], "in": "query", "name": "format", "type": "string"}, {"default": true, "description": "Include timestamps in the JSON response", "in": "query", "name": "timestamps", "type": "boolean"}], "path": "/youtube/transcript/{id}", "pathParams": ["id"], "produces": ["application/json", "text/plain"], "queryParams": [{"in": "query", "name": "lang", "type": "string"}, {"in": "query", "name": "translate_to", "type": "string"}, {"enum": ["json", "text", "srt", "vtt"], "in": "query", "name": "format", "type": "string"}, {"in": "query", "name": "timestamps", "type": "boolean"}], "security": ["ApiKeyAuth"]}, "youtube-transcript-languages": {"id": "youtube-transcript-languages", "method": "GET", "params": [{"description": "YouTube video ID (11-character code)", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "YbJOTdZBX1g"}], "path": "/youtube/transcript/{id}/languages", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [], "security": ["ApiKeyAuth"]}, "youtube-video": {"id": "youtube-video", "method": "GET", "params": [{"description": "YouTube video ID (11-char code)", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "YbJOTdZBX1g"}], "path": "/youtube/video/{id}", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [], "security": ["ApiKeyAuth"]}}
JSON, true, 512, JSON_THROW_ON_ERROR);
    }

    public function request(string $operationId, array $params = [], string $responseType = 'auto'): mixed
    {
        if ($this->closed) {
            throw new ClientException('Client is closed', null, $operationId);
        }
        $operation = self::$operations[$operationId] ?? null;
        if ($operation === null) {
            throw new ClientException('Unknown operation: ' . $operationId, null, $operationId);
        }
        if ($this->apiKey === '') {
            throw new ClientException('Crawlora API key is required', null, $operationId);
        }
        $url = $this->buildUrl($operation, $params);
        $headers = [
            'x-api-key: ' . $this->apiKey,
            'User-Agent: crawlora-youtube-php/0.1.8',
            'Accept: ' . (in_array('text/plain', $operation['produces'], true) ? 'application/json, text/plain' : 'application/json'),
        ];
        try {
            [$status, $contentType, $body] = $this->send($url, $headers, $operationId);
        } catch (CrawloraException $exception) {
            throw $exception;
        } catch (\Throwable $exception) {
            throw new NetworkException('Crawlora request failed: ' . $exception->getMessage(), null, $operationId, null, $exception);
        }
        if ($status < 200 || $status >= 300) {
            $class = $status >= 500 ? ServerException::class : ClientException::class;
            throw new $class('Crawlora returned HTTP ' . $status, $status, $operationId, $body);
        }
        return $this->parseResponse($body, $contentType, $operation, $params, $responseType);
    }

    public function close(): void
    {
        $this->closed = true;
    }

    public function isClosed(): bool
    {
        return $this->closed;
    }

    public function operationCount(): int
    {
        return self::OPERATION_COUNT;
    }

    public function operationIds(): array
    {
        return self::OPERATION_IDS;
    }

    public function operations(): array
    {
        return self::$operations;
    }

    public function captions(mixed ...$params): mixed
    {
        $responseType = $params['_response_type'] ?? $params['response_type'] ?? 'auto';
        unset($params['_response_type'], $params['response_type']);
        return $this->request("youtube-captions", $params, $responseType);
    }
    public function channel_playlists(mixed ...$params): mixed
    {
        $responseType = $params['_response_type'] ?? $params['response_type'] ?? 'auto';
        unset($params['_response_type'], $params['response_type']);
        return $this->request("youtube-channel-playlists", $params, $responseType);
    }
    public function channel_search(mixed ...$params): mixed
    {
        $responseType = $params['_response_type'] ?? $params['response_type'] ?? 'auto';
        unset($params['_response_type'], $params['response_type']);
        return $this->request("youtube-channel-search", $params, $responseType);
    }
    public function channel_shorts(mixed ...$params): mixed
    {
        $responseType = $params['_response_type'] ?? $params['response_type'] ?? 'auto';
        unset($params['_response_type'], $params['response_type']);
        return $this->request("youtube-channel-shorts", $params, $responseType);
    }
    public function channel_videos(mixed ...$params): mixed
    {
        $responseType = $params['_response_type'] ?? $params['response_type'] ?? 'auto';
        unset($params['_response_type'], $params['response_type']);
        return $this->request("youtube-channel-videos", $params, $responseType);
    }
    public function comments(mixed ...$params): mixed
    {
        $responseType = $params['_response_type'] ?? $params['response_type'] ?? 'auto';
        unset($params['_response_type'], $params['response_type']);
        return $this->request("youtube-comments", $params, $responseType);
    }
    public function playlist(mixed ...$params): mixed
    {
        $responseType = $params['_response_type'] ?? $params['response_type'] ?? 'auto';
        unset($params['_response_type'], $params['response_type']);
        return $this->request("youtube-playlist", $params, $responseType);
    }
    public function profile(mixed ...$params): mixed
    {
        $responseType = $params['_response_type'] ?? $params['response_type'] ?? 'auto';
        unset($params['_response_type'], $params['response_type']);
        return $this->request("youtube-profile", $params, $responseType);
    }
    public function search(mixed ...$params): mixed
    {
        $responseType = $params['_response_type'] ?? $params['response_type'] ?? 'auto';
        unset($params['_response_type'], $params['response_type']);
        return $this->request("youtube-search", $params, $responseType);
    }
    public function suggest(mixed ...$params): mixed
    {
        $responseType = $params['_response_type'] ?? $params['response_type'] ?? 'auto';
        unset($params['_response_type'], $params['response_type']);
        return $this->request("youtube-suggest", $params, $responseType);
    }
    public function tag(mixed ...$params): mixed
    {
        $responseType = $params['_response_type'] ?? $params['response_type'] ?? 'auto';
        unset($params['_response_type'], $params['response_type']);
        return $this->request("youtube-tag", $params, $responseType);
    }
    public function transcript(mixed ...$params): mixed
    {
        $responseType = $params['_response_type'] ?? $params['response_type'] ?? 'auto';
        unset($params['_response_type'], $params['response_type']);
        return $this->request("youtube-transcript", $params, $responseType);
    }
    public function transcript_languages(mixed ...$params): mixed
    {
        $responseType = $params['_response_type'] ?? $params['response_type'] ?? 'auto';
        unset($params['_response_type'], $params['response_type']);
        return $this->request("youtube-transcript-languages", $params, $responseType);
    }
    public function video(mixed ...$params): mixed
    {
        $responseType = $params['_response_type'] ?? $params['response_type'] ?? 'auto';
        unset($params['_response_type'], $params['response_type']);
        return $this->request("youtube-video", $params, $responseType);
    }

    private function buildUrl(array $operation, array $params): string
    {
        $known = array_column($operation['params'], 'name');
        $unknown = array_diff(array_keys($params), $known, ['response_type', '_response_type']);
        if ($unknown !== []) {
            throw new ClientException('Unknown parameters: ' . implode(', ', $unknown), null, $operation['id']);
        }
        $path = $operation['path'];
        foreach ($operation['params'] as $param) {
            if ($param['in'] !== 'path') {
                continue;
            }
            $name = $param['name'];
            if (!array_key_exists($name, $params) || $params[$name] === null) {
                throw new ClientException('Missing path parameter: ' . $name, null, $operation['id']);
            }
            $path = str_replace('{' . $name . '}', rawurlencode((string) $params[$name]), $path);
        }
        $pairs = [];
        foreach ($operation['queryParams'] as $param) {
            $name = $param['name'];
            $value = $params[$name] ?? ($param['default'] ?? null);
            if ($value === null) {
                if ($param['required'] ?? false) {
                    throw new ClientException('Missing query parameter: ' . $name, null, $operation['id']);
                }
                continue;
            }
            $enumValues = $param['enum'] ?? ($param['items']['enum'] ?? null);
            $values = is_array($value) ? $value : [$value];
            $invalidEnum = false;
            foreach ($values as $item) {
                if ($enumValues !== null && !in_array((string) $item, array_map('strval', $enumValues), true)) {
                    $invalidEnum = true;
                    break;
                }
            }
            if ($invalidEnum) {
                throw new ClientException('Invalid value for ' . $name, null, $operation['id']);
            }
            if (is_array($value)) {
                $format = $param['collectionFormat'] ?? 'csv';
                if ($format === 'multi') {
                    foreach ($value as $item) {
                        $pairs[] = [rawurlencode($name), rawurlencode($this->stringify($item))];
                    }
                } else {
                    $separator = ['csv' => ',', 'ssv' => ' ', 'tsv' => "\t", 'pipes' => '|'][$format] ?? ',';
                    $pairs[] = [rawurlencode($name), rawurlencode(implode($separator, array_map([$this, 'stringify'], $value)))];
                }
            } else {
                $pairs[] = [rawurlencode($name), rawurlencode($this->stringify($value))];
            }
        }
        $query = implode('&', array_map(static fn(array $pair): string => $pair[0] . '=' . $pair[1], $pairs));
        return $this->baseUrl . $path . ($query === '' ? '' : '?' . $query);
    }

    private function stringify(mixed $value): string
    {
        if (is_bool($value)) {
            return $value ? 'true' : 'false';
        }
        if (is_array($value)) {
            return json_encode($value, JSON_THROW_ON_ERROR);
        }
        return (string) $value;
    }

    private function send(string $url, array $headers, string $operationId): array
    {
        if ($this->transport !== null) {
            $result = ($this->transport)($url, $headers, $this->timeout);
            return [(int) $result['status'], (string) ($result['content_type'] ?? ''), (string) ($result['body'] ?? '')];
        }
        $handle = curl_init($url);
        if ($handle === false) {
            throw new NetworkException('Could not initialize cURL', null, $operationId);
        }
        curl_setopt_array($handle, [
            CURLOPT_HTTPGET => true,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => $headers,
            CURLOPT_TIMEOUT_MS => (int) ($this->timeout * 1000),
            CURLOPT_CONNECTTIMEOUT_MS => (int) ($this->timeout * 1000),
        ]);
        $body = curl_exec($handle);
        if ($body === false) {
            $message = curl_error($handle);
            curl_close($handle);
            throw new NetworkException('Crawlora request failed: ' . $message, null, $operationId);
        }
        $status = (int) curl_getinfo($handle, CURLINFO_RESPONSE_CODE);
        $contentType = (string) curl_getinfo($handle, CURLINFO_CONTENT_TYPE);
        curl_close($handle);
        return [$status, $contentType, (string) $body];
    }

    private function parseResponse(string $body, string $contentType, array $operation, array $params, string $responseType): mixed
    {
        if (!in_array($responseType, ['auto', 'json', 'text'], true)) {
            throw new ClientException('responseType must be auto, json, or text', null, $operation['id']);
        }
        $format = null;
        foreach ($operation['params'] as $param) {
            if ($param['name'] === 'format') {
                $format = $param;
                break;
            }
        }
        $textFormats = array_values(array_filter($format['enum'] ?? [], static fn($value): bool => !in_array(strtolower((string) $value), ['json', 'application/json'], true)));
        $rawFormat = isset($params['format']) && in_array((string) $params['format'], array_map('strval', $textFormats), true);
        $jsonFormat = isset($params['format']) && in_array(strtolower((string) $params['format']), ['json', 'application/json'], true);
        $isJson = $jsonFormat || stripos($contentType, 'json') !== false || $operation['produces'] === ['application/json'];
        if ($responseType === 'text' || $rawFormat || ($responseType === 'auto' && !$isJson)) {
            return $body;
        }
        try {
            return json_decode($body, true, 512, JSON_THROW_ON_ERROR);
        } catch (\JsonException $exception) {
            throw new CrawloraException('Invalid JSON response from Crawlora: ' . $exception->getMessage(), null, $operation['id'], $body, $exception);
        }
    }
}
