package net.crawlora.youtube;

import net.crawlora.Json;

import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeSet;

/** Client for the YouTube endpoints hosted by Crawlora. */
public final class Client implements AutoCloseable {
    public static final String DEFAULT_BASE_URL = "https://api.crawlora.net/api/v1";
    public static final int OPERATION_COUNT = 14;
    public static final List<String> OPERATION_IDS = List.of(
            "youtube-captions",
            "youtube-channel-playlists",
            "youtube-channel-search",
            "youtube-channel-shorts",
            "youtube-channel-videos",
            "youtube-comments",
            "youtube-playlist",
            "youtube-profile",
            "youtube-search",
            "youtube-suggest",
            "youtube-tag",
            "youtube-transcript",
            "youtube-transcript-languages",
            "youtube-video"
    );

    private static final Map<String, Operation> OPERATIONS;
    static {
        Map<String, Operation> operations = new LinkedHashMap<>();
        operations.put("youtube-captions", new Operation("youtube-captions", "GET", "/youtube/captions/{id}", Map.ofEntries(Map.entry("id", new Param("id", "path", true, "string", List.of(), "csv")), Map.entry("lang", new Param("lang", "query", false, "string", List.of(), "csv"))), List.of("application/json")));
        operations.put("youtube-channel-playlists", new Operation("youtube-channel-playlists", "GET", "/youtube/channel/{id}/playlists", Map.ofEntries(Map.entry("id", new Param("id", "path", true, "string", List.of(), "csv")), Map.entry("continuation_token", new Param("continuation_token", "query", false, "string", List.of(), "csv"))), List.of("application/json")));
        operations.put("youtube-channel-search", new Operation("youtube-channel-search", "GET", "/youtube/channel/{id}/search", Map.ofEntries(Map.entry("id", new Param("id", "path", true, "string", List.of(), "csv")), Map.entry("q", new Param("q", "query", true, "string", List.of(), "csv")), Map.entry("continuation_token", new Param("continuation_token", "query", false, "string", List.of(), "csv"))), List.of("application/json")));
        operations.put("youtube-channel-shorts", new Operation("youtube-channel-shorts", "GET", "/youtube/channel/{id}/shorts", Map.ofEntries(Map.entry("id", new Param("id", "path", true, "string", List.of(), "csv"))), List.of("application/json")));
        operations.put("youtube-channel-videos", new Operation("youtube-channel-videos", "GET", "/youtube/channel/{id}/videos", Map.ofEntries(Map.entry("id", new Param("id", "path", true, "string", List.of(), "csv")), Map.entry("continuation_token", new Param("continuation_token", "query", false, "string", List.of(), "csv"))), List.of("application/json")));
        operations.put("youtube-comments", new Operation("youtube-comments", "GET", "/youtube/comments/{id}", Map.ofEntries(Map.entry("id", new Param("id", "path", true, "string", List.of(), "csv")), Map.entry("continuation_token", new Param("continuation_token", "query", false, "string", List.of(), "csv"))), List.of("application/json")));
        operations.put("youtube-playlist", new Operation("youtube-playlist", "GET", "/youtube/playlist/{id}", Map.ofEntries(Map.entry("id", new Param("id", "path", true, "string", List.of(), "csv")), Map.entry("continuation_token", new Param("continuation_token", "query", false, "string", List.of(), "csv"))), List.of("application/json")));
        operations.put("youtube-profile", new Operation("youtube-profile", "GET", "/youtube/profile/{id}", Map.ofEntries(Map.entry("id", new Param("id", "path", true, "string", List.of(), "csv"))), List.of("application/json")));
        operations.put("youtube-search", new Operation("youtube-search", "GET", "/youtube/search", Map.ofEntries(Map.entry("q", new Param("q", "query", false, "string", List.of(), "csv")), Map.entry("search_query", new Param("search_query", "query", false, "string", List.of(), "csv")), Map.entry("continuation_token", new Param("continuation_token", "query", false, "string", List.of(), "csv")), Map.entry("type", new Param("type", "query", false, "string", List.of("video", "shorts", "channel", "playlist", "movie"), "csv")), Map.entry("sort_by", new Param("sort_by", "query", false, "string", List.of("relevance", "upload_date", "view_count", "popularity", "rating"), "csv")), Map.entry("upload_date", new Param("upload_date", "query", false, "string", List.of("last_hour", "today", "this_week", "this_month", "this_year"), "csv")), Map.entry("duration", new Param("duration", "query", false, "string", List.of("under_3_minutes", "three_to_20_minutes", "over_20_minutes", "under_3", "three_to_20", "over_20", "short", "medium", "long"), "csv")), Map.entry("features", new Param("features", "query", false, "string", List.of(), "csv")), Map.entry("hl", new Param("hl", "query", false, "string", List.of(), "csv")), Map.entry("gl", new Param("gl", "query", false, "string", List.of(), "csv")), Map.entry("params", new Param("params", "query", false, "string", List.of(), "csv"))), List.of("application/json")));
        operations.put("youtube-suggest", new Operation("youtube-suggest", "GET", "/youtube/suggest", Map.ofEntries(Map.entry("q", new Param("q", "query", true, "string", List.of(), "csv")), Map.entry("count", new Param("count", "query", false, "integer", List.of(), "csv")), Map.entry("hl", new Param("hl", "query", false, "string", List.of(), "csv")), Map.entry("gl", new Param("gl", "query", false, "string", List.of(), "csv"))), List.of("application/json")));
        operations.put("youtube-tag", new Operation("youtube-tag", "GET", "/youtube/tag/{tag}", Map.ofEntries(Map.entry("tag", new Param("tag", "path", true, "string", List.of(), "csv")), Map.entry("type", new Param("type", "query", false, "string", List.of("all", "shorts"), "csv")), Map.entry("continuation_token", new Param("continuation_token", "query", false, "string", List.of(), "csv"))), List.of("application/json")));
        operations.put("youtube-transcript", new Operation("youtube-transcript", "GET", "/youtube/transcript/{id}", Map.ofEntries(Map.entry("id", new Param("id", "path", true, "string", List.of(), "csv")), Map.entry("lang", new Param("lang", "query", false, "string", List.of(), "csv")), Map.entry("translate_to", new Param("translate_to", "query", false, "string", List.of(), "csv")), Map.entry("format", new Param("format", "query", false, "string", List.of("json", "text", "srt", "vtt"), "csv")), Map.entry("timestamps", new Param("timestamps", "query", false, "boolean", List.of(), "csv"))), List.of("application/json", "text/plain")));
        operations.put("youtube-transcript-languages", new Operation("youtube-transcript-languages", "GET", "/youtube/transcript/{id}/languages", Map.ofEntries(Map.entry("id", new Param("id", "path", true, "string", List.of(), "csv"))), List.of("application/json")));
        operations.put("youtube-video", new Operation("youtube-video", "GET", "/youtube/video/{id}", Map.ofEntries(Map.entry("id", new Param("id", "path", true, "string", List.of(), "csv"))), List.of("application/json")));
        OPERATIONS = Collections.unmodifiableMap(operations);
    }

    private final String apiKey;
    private final String baseUrl;
    private final Duration timeout;
    private final HttpClient http;
    private volatile boolean closed;

    /** Create a client using Crawlora's hosted API and the default 30 second timeout. */
    public Client(String apiKey) {
        this(apiKey, DEFAULT_BASE_URL, Duration.ofSeconds(30));
    }

    /** Create a client with an explicit hosted API base URL and request timeout. */
    public Client(String apiKey, String baseUrl, Duration timeout) {
        if (apiKey == null || apiKey.isBlank()) throw new IllegalArgumentException("apiKey is required");
        if (baseUrl == null || baseUrl.isBlank()) throw new IllegalArgumentException("baseUrl is required");
        this.apiKey = apiKey;
        this.baseUrl = baseUrl.replaceAll("/+$", "");
        this.timeout = Objects.requireNonNull(timeout, "timeout");
        if (timeout.isZero() || timeout.isNegative()) throw new IllegalArgumentException("timeout must be positive");
        this.http = HttpClient.newBuilder().connectTimeout(timeout).build();
    }

    public String getBaseUrl() { return baseUrl; }
    public Duration getTimeout() { return timeout; }
    public int getOperationCount() { return OPERATION_COUNT; }
    public List<String> getOperationIds() { return OPERATION_IDS; }
    public static Map<String, Operation> operations() { return OPERATIONS; }

    /** Dispatch a selected operation by id. Parameters use the exact OpenAPI names. */
    public Object request(String operationId, Map<String, ?> params) {
        if (closed) throw new IllegalStateException("client is closed");
        Operation operation = OPERATIONS.get(operationId);
        if (operation == null) throw new IllegalArgumentException("unknown YouTube operation: " + operationId);
        Map<String, ?> values = params == null ? Map.of() : params;
        Set<String> unknown = new TreeSet<>(values.keySet());
        unknown.removeAll(operation.params().keySet());
        if (!unknown.isEmpty()) throw new IllegalArgumentException("unknown parameters for " + operationId + ": " + unknown);

        String path = operation.path();
        List<Map.Entry<String, String>> query = new ArrayList<>();
        for (Param param : operation.params().values()) {
            Object value = values.get(param.name());
            if (value == null) {
                if (param.required()) throw new IllegalArgumentException("missing required parameter: " + param.name());
                continue;
            }
            validateEnum(param, value);
            if (param.location().equals("path")) {
                path = path.replace("{" + param.name() + "}", pathEncode(value.toString()));
            } else {
                addQuery(query, param, value);
            }
        }
        if (path.matches(".*\\{[^}]+}.*")) throw new IllegalArgumentException("missing path parameter for " + operationId);
        StringBuilder url = new StringBuilder(baseUrl).append(path);
        for (int i = 0; i < query.size(); i++) {
            url.append(i == 0 ? '?' : '&').append(queryEncode(query.get(i).getKey()))
                    .append('=').append(queryEncode(query.get(i).getValue()));
        }
        HttpRequest request = HttpRequest.newBuilder(URI.create(url.toString()))
                .timeout(timeout)
                .header("x-api-key", apiKey)
                .header("Accept", acceptHeader(operation))
                .GET().build();
        try {
            HttpResponse<String> response = http.send(request, HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
            String body = response.body();
            String contentType = response.headers().firstValue("content-type").orElse("").toLowerCase();
            Object parsed = body;
            if (contentType.contains("application/json") && !body.isEmpty()) {
                try { parsed = Json.parse(body); }
                catch (RuntimeException error) { throw new CrawloraException("Crawlora returned invalid JSON", error); }
            }
            if (response.statusCode() < 200 || response.statusCode() >= 300) {
                String message = "Crawlora request failed with HTTP " + response.statusCode();
                if (parsed instanceof Map<?, ?> map && map.get("msg") != null) message = map.get("msg").toString();
                throw new CrawloraException(message, response.statusCode(), parsed);
            }
            return parsed;
        } catch (InterruptedException error) {
            Thread.currentThread().interrupt();
            throw new CrawloraException("Crawlora request interrupted", error);
        } catch (IOException error) {
            throw new CrawloraException("Crawlora network request failed", error);
        }
    }

    public Object captions(Map<String, ?> params) { return request("youtube-captions", params); }
    public Object channelPlaylists(Map<String, ?> params) { return request("youtube-channel-playlists", params); }
    public Object channelSearch(Map<String, ?> params) { return request("youtube-channel-search", params); }
    public Object channelShorts(Map<String, ?> params) { return request("youtube-channel-shorts", params); }
    public Object channelVideos(Map<String, ?> params) { return request("youtube-channel-videos", params); }
    public Object comments(Map<String, ?> params) { return request("youtube-comments", params); }
    public Object playlist(Map<String, ?> params) { return request("youtube-playlist", params); }
    public Object profile(Map<String, ?> params) { return request("youtube-profile", params); }
    public Object search(Map<String, ?> params) { return request("youtube-search", params); }
    public Object suggest(Map<String, ?> params) { return request("youtube-suggest", params); }
    public Object tag(Map<String, ?> params) { return request("youtube-tag", params); }
    public Object transcript(Map<String, ?> params) { return request("youtube-transcript", params); }
    public Object transcriptLanguages(Map<String, ?> params) { return request("youtube-transcript-languages", params); }
    public Object video(Map<String, ?> params) { return request("youtube-video", params); }

    private static String acceptHeader(Operation operation) {
        return operation.produces().isEmpty() ? "application/json" : String.join(", ", operation.produces());
    }

    private static void validateEnum(Param param, Object value) {
        if (param.enumValues().isEmpty()) return;
        for (Object item : items(value)) {
            if (!param.enumValues().contains(String.valueOf(item))) {
                throw new IllegalArgumentException("invalid " + param.name() + ": expected one of " + param.enumValues());
            }
        }
    }

    private static void addQuery(List<Map.Entry<String, String>> query, Param param, Object value) {
        List<?> values = items(value);
        String delimiter = switch (param.collectionFormat()) {
            case "ssv" -> " ";
            case "tsv" -> "\t";
            case "pipes" -> "|";
            default -> ",";
        };
        if (value instanceof Iterable<?> || value.getClass().isArray()) {
            String joined = String.join(delimiter, values.stream().map(String::valueOf).toList());
            query.add(Map.entry(param.name(), joined));
        } else {
            query.add(Map.entry(param.name(), String.valueOf(value)));
        }
    }

    private static List<?> items(Object value) {
        if (value instanceof Iterable<?> iterable) {
            List<Object> result = new ArrayList<>();
            iterable.forEach(result::add);
            return result;
        }
        if (value != null && value.getClass().isArray()) {
            int length = java.lang.reflect.Array.getLength(value);
            List<Object> result = new ArrayList<>(length);
            for (int i = 0; i < length; i++) result.add(java.lang.reflect.Array.get(value, i));
            return result;
        }
        return List.of(value);
    }

    private static String pathEncode(String value) {
        return URLEncoder.encode(value, StandardCharsets.UTF_8).replace("+", "%20");
    }

    private static String queryEncode(String value) {
        return URLEncoder.encode(value, StandardCharsets.UTF_8);
    }

    @Override public void close() { closed = true; }
}
