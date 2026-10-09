require "json"
require "net/http"
require "uri"

module Crawlora
  module Youtube
    module Errors
      class Error < StandardError
        attr_reader :status, :operation_id, :body

        def initialize(message, status: nil, operation_id: nil, body: nil)
          super(message)
          @status, @operation_id, @body = status, operation_id, body
        end
      end
      class ClientError < Error; end
      class ServerError < Error; end
      class NetworkError < Error; end
    end

    OPERATIONS = JSON.parse(<<~'JSON').freeze
      {"youtube-captions": {"id": "youtube-captions", "method": "GET", "params": [{"description": "YouTube video ID (11-character code)", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "YbJOTdZBX1g"}, {"default": "en", "description": "Caption language code (ISO 639-1), defaults to **en**", "in": "query", "name": "lang", "type": "string"}], "path": "/youtube/captions/{id}", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [{"in": "query", "name": "lang", "type": "string"}], "security": ["ApiKeyAuth"]}, "youtube-channel-playlists": {"id": "youtube-channel-playlists", "method": "GET", "params": [{"description": "Channel ID, @handle, /c path, /user path, or full YouTube channel URL", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "UCXZCJLdBC09xxGZ6gcdrc6A"}, {"description": "Pagination token returned by a previous request", "in": "query", "name": "continuation_token", "type": "string"}], "path": "/youtube/channel/{id}/playlists", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [{"in": "query", "name": "continuation_token", "type": "string"}], "security": ["ApiKeyAuth"]}, "youtube-channel-search": {"id": "youtube-channel-search", "method": "GET", "params": [{"description": "Channel ID, @handle, /c path, /user path, or full YouTube channel URL", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "UCXZCJLdBC09xxGZ6gcdrc6A"}, {"description": "Search query", "in": "query", "name": "q", "required": true, "type": "string", "x-example": "gpt"}, {"description": "Pagination token returned by a previous request", "in": "query", "name": "continuation_token", "type": "string"}], "path": "/youtube/channel/{id}/search", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [{"in": "query", "name": "q", "required": true, "type": "string"}, {"in": "query", "name": "continuation_token", "type": "string"}], "security": ["ApiKeyAuth"]}, "youtube-channel-shorts": {"id": "youtube-channel-shorts", "method": "GET", "params": [{"description": "Channel ID, @handle, /c path, /user path, or full YouTube channel URL", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "UCXZCJLdBC09xxGZ6gcdrc6A"}], "path": "/youtube/channel/{id}/shorts", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [], "security": ["ApiKeyAuth"]}, "youtube-channel-videos": {"id": "youtube-channel-videos", "method": "GET", "params": [{"description": "Channel ID, @handle, /c path, /user path, or full YouTube channel URL", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "UCXZCJLdBC09xxGZ6gcdrc6A"}, {"description": "Pagination token returned by a previous request", "in": "query", "name": "continuation_token", "type": "string"}], "path": "/youtube/channel/{id}/videos", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [{"in": "query", "name": "continuation_token", "type": "string"}], "security": ["ApiKeyAuth"]}, "youtube-comments": {"id": "youtube-comments", "method": "GET", "params": [{"description": "YouTube video ID (11-character code)", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "YbJOTdZBX1g"}, {"description": "Pagination token returned by a previous request, first page if empty", "in": "query", "name": "continuation_token", "type": "string"}], "path": "/youtube/comments/{id}", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [{"in": "query", "name": "continuation_token", "type": "string"}], "security": ["ApiKeyAuth"]}, "youtube-playlist": {"id": "youtube-playlist", "method": "GET", "params": [{"description": "YouTube playlist ID or full playlist URL", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "PL-szjqIBRvM_aWOj-uXCVm28l-ZZFa4D2"}, {"description": "Pagination token returned by a previous request", "in": "query", "name": "continuation_token", "type": "string"}], "path": "/youtube/playlist/{id}", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [{"in": "query", "name": "continuation_token", "type": "string"}], "security": ["ApiKeyAuth"]}, "youtube-profile": {"id": "youtube-profile", "method": "GET", "params": [{"description": "Channel ID, @handle, /c path, /user path, bare username, or full YouTube channel URL", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "UCXZCJLdBC09xxGZ6gcdrc6A"}], "path": "/youtube/profile/{id}", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [], "security": ["ApiKeyAuth"]}, "youtube-search": {"id": "youtube-search", "method": "GET", "params": [{"description": "Search query", "in": "query", "name": "q", "type": "string", "x-example": "gpt"}, {"description": "Alias for q", "in": "query", "name": "search_query", "type": "string", "x-example": "gpt"}, {"description": "Pagination token returned by a previous request", "in": "query", "name": "continuation_token", "type": "string"}, {"description": "Filter by type", "enum": ["video", "shorts", "channel", "playlist", "movie"], "in": "query", "name": "type", "type": "string"}, {"description": "Sort results", "enum": ["relevance", "upload_date", "view_count", "popularity", "rating"], "in": "query", "name": "sort_by", "type": "string"}, {"description": "Filter by upload date", "enum": ["last_hour", "today", "this_week", "this_month", "this_year"], "in": "query", "name": "upload_date", "type": "string"}, {"description": "Filter by duration; short, medium, and long preserve their previous upstream encodings", "enum": ["under_3_minutes", "three_to_20_minutes", "over_20_minutes", "under_3", "three_to_20", "over_20", "short", "medium", "long"], "in": "query", "name": "duration", "type": "string"}, {"description": "Comma-separated feature filters. Allowed values: live, 4k, hd, subtitles, cc, creative_commons, 360, vr180, 3d, hdr, location, purchased", "in": "query", "name": "features", "type": "string", "x-example": "hd,subtitles"}, {"description": "YouTube interface language", "in": "query", "name": "hl", "type": "string", "x-example": "en"}, {"description": "Two-letter YouTube region code", "in": "query", "name": "gl", "type": "string", "x-example": "US"}, {"description": "Raw protobuf-encoded search filter (base64)", "in": "query", "name": "params", "type": "string"}], "path": "/youtube/search", "pathParams": [], "produces": ["application/json"], "queryParams": [{"in": "query", "name": "q", "type": "string"}, {"in": "query", "name": "search_query", "type": "string"}, {"in": "query", "name": "continuation_token", "type": "string"}, {"enum": ["video", "shorts", "channel", "playlist", "movie"], "in": "query", "name": "type", "type": "string"}, {"enum": ["relevance", "upload_date", "view_count", "popularity", "rating"], "in": "query", "name": "sort_by", "type": "string"}, {"enum": ["last_hour", "today", "this_week", "this_month", "this_year"], "in": "query", "name": "upload_date", "type": "string"}, {"enum": ["under_3_minutes", "three_to_20_minutes", "over_20_minutes", "under_3", "three_to_20", "over_20", "short", "medium", "long"], "in": "query", "name": "duration", "type": "string"}, {"in": "query", "name": "features", "type": "string"}, {"in": "query", "name": "hl", "type": "string"}, {"in": "query", "name": "gl", "type": "string"}, {"in": "query", "name": "params", "type": "string"}], "security": ["ApiKeyAuth"]}, "youtube-suggest": {"id": "youtube-suggest", "method": "GET", "params": [{"description": "Search query prefix", "in": "query", "name": "q", "required": true, "type": "string", "x-example": "openai"}, {"description": "Suggestions to return; defaults to 10, clamped to 1..20", "in": "query", "maximum": 20, "minimum": 1, "name": "count", "type": "integer", "x-example": 10}, {"description": "YouTube interface language, such as en, de, or pt-BR; defaults to en", "in": "query", "name": "hl", "type": "string", "x-example": "en"}, {"description": "Two-letter YouTube region code; defaults to US", "in": "query", "name": "gl", "type": "string", "x-example": "US"}], "path": "/youtube/suggest", "pathParams": [], "produces": ["application/json"], "queryParams": [{"in": "query", "name": "q", "required": true, "type": "string"}, {"in": "query", "name": "count", "type": "integer"}, {"in": "query", "name": "hl", "type": "string"}, {"in": "query", "name": "gl", "type": "string"}], "security": ["ApiKeyAuth"]}, "youtube-tag": {"id": "youtube-tag", "method": "GET", "params": [{"description": "Tag to filter videos", "in": "path", "name": "tag", "required": true, "type": "string", "x-example": "openai"}, {"default": "all", "description": "Result tab to load", "enum": ["all", "shorts"], "in": "query", "name": "type", "type": "string"}, {"description": "Continuation token for pagination, first page if empty", "in": "query", "name": "continuation_token", "type": "string"}], "path": "/youtube/tag/{tag}", "pathParams": ["tag"], "produces": ["application/json"], "queryParams": [{"enum": ["all", "shorts"], "in": "query", "name": "type", "type": "string"}, {"in": "query", "name": "continuation_token", "type": "string"}], "security": ["ApiKeyAuth"]}, "youtube-transcript": {"id": "youtube-transcript", "method": "GET", "params": [{"description": "YouTube video ID (11-character code)", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "YbJOTdZBX1g"}, {"default": "en", "description": "Preferred transcript language", "in": "query", "name": "lang", "type": "string"}, {"description": "Translate transcript to this language code", "in": "query", "name": "translate_to", "type": "string"}, {"default": "json", "description": "Response format", "enum": ["json", "text", "srt", "vtt"], "in": "query", "name": "format", "type": "string"}, {"default": true, "description": "Include timestamps in the JSON response", "in": "query", "name": "timestamps", "type": "boolean"}], "path": "/youtube/transcript/{id}", "pathParams": ["id"], "produces": ["application/json", "text/plain"], "queryParams": [{"in": "query", "name": "lang", "type": "string"}, {"in": "query", "name": "translate_to", "type": "string"}, {"enum": ["json", "text", "srt", "vtt"], "in": "query", "name": "format", "type": "string"}, {"in": "query", "name": "timestamps", "type": "boolean"}], "security": ["ApiKeyAuth"]}, "youtube-transcript-languages": {"id": "youtube-transcript-languages", "method": "GET", "params": [{"description": "YouTube video ID (11-character code)", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "YbJOTdZBX1g"}], "path": "/youtube/transcript/{id}/languages", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [], "security": ["ApiKeyAuth"]}, "youtube-video": {"id": "youtube-video", "method": "GET", "params": [{"description": "YouTube video ID (11-char code)", "in": "path", "name": "id", "required": true, "type": "string", "x-example": "YbJOTdZBX1g"}], "path": "/youtube/video/{id}", "pathParams": ["id"], "produces": ["application/json"], "queryParams": [], "security": ["ApiKeyAuth"]}}
    JSON
    OPERATION_IDS = JSON.parse(<<~'JSON').freeze
      ["youtube-captions", "youtube-channel-playlists", "youtube-channel-search", "youtube-channel-shorts", "youtube-channel-videos", "youtube-comments", "youtube-playlist", "youtube-profile", "youtube-search", "youtube-suggest", "youtube-tag", "youtube-transcript", "youtube-transcript-languages", "youtube-video"]
    JSON
    OPERATION_COUNT = OPERATION_IDS.length

    class Client
      attr_reader :base_url

      def initialize(api_key: ENV["CRAWLORA_API_KEY"], base_url: "https://api.crawlora.net/api/v1", timeout: 30, user_agent: "crawlora-youtube-ruby/0.1.6", transport: nil)
        @api_key = api_key
        @base_url = base_url.to_s.sub(%r{/+$}, "")
        @timeout = Float(timeout)
        @user_agent = user_agent
        @transport = transport
        @closed = false
      end

      def request(operation_id, params = {}, response_type: :auto)
        raise Errors::ClientError, "client is closed" if @closed
        operation_id = operation_id.to_s
        operation = OPERATIONS[operation_id]
        raise Errors::ClientError.new("unknown operation: #{operation_id}", operation_id: operation_id) unless operation
        raise Errors::ClientError.new("Crawlora API key is required", operation_id: operation_id) if @api_key.nil? || @api_key.to_s.empty?
        normalized = params.each_with_object({}) { |(key, value), out| out[key.to_s] = value }
        url = build_url(operation, normalized)
        uri = URI.parse(url)
        request = Net::HTTP::Get.new(uri)
        request["x-api-key"] = @api_key
        request["User-Agent"] = @user_agent
        request["Accept"] = operation["produces"].include?("text/plain") ? "application/json, text/plain" : "application/json"
        begin
          if @transport
            response = @transport.call(url, request.to_hash, @timeout)
            status = Integer(response.fetch(:status) { response.fetch("status") })
            body = response.fetch(:body) { response.fetch("body", "") }
            headers = response.fetch(:headers) { response.fetch("headers", {}) }
            content_type = headers["content-type"] || headers["Content-Type"]
          else
            http = Net::HTTP.new(uri.host, uri.port)
            http.use_ssl = uri.scheme == "https"
            http.open_timeout = @timeout
            http.read_timeout = @timeout
            response = http.start { |connection| connection.request(request) }
            status = response.code.to_i
            body = response.body
            content_type = response["content-type"]
          end
        rescue Timeout::Error, SocketError, SystemCallError, IOError, EOFError, Net::HTTPBadResponse, Net::ProtocolError, OpenSSL::SSL::SSLError => error
          raise Errors::NetworkError.new("Crawlora request failed: #{error.message}", operation_id: operation_id)
        end
        unless status >= 200 && status < 300
          klass = status >= 500 ? Errors::ServerError : Errors::ClientError
          raise klass.new("Crawlora returned HTTP #{status}", status: status, operation_id: operation_id, body: body)
        end
        parse_response(body, content_type, operation, normalized, response_type)
      end

      def close
        @closed = true
      end

      def closed?
        @closed
      end

      def with
        return self unless block_given?
        yield self
      ensure
        close if block_given?
      end

      def self.operation_count
        OPERATION_COUNT
      end

      def self.operation_ids
        OPERATION_IDS
      end

      def self.operations
        OPERATIONS
      end

            define_method('captions') do |**params|
        response_type = params.delete(:response_type) || params.delete(:_response_type) || :auto
        request('youtube-captions', params, response_type: response_type)
      end
      define_method('channel_playlists') do |**params|
        response_type = params.delete(:response_type) || params.delete(:_response_type) || :auto
        request('youtube-channel-playlists', params, response_type: response_type)
      end
      define_method('channel_search') do |**params|
        response_type = params.delete(:response_type) || params.delete(:_response_type) || :auto
        request('youtube-channel-search', params, response_type: response_type)
      end
      define_method('channel_shorts') do |**params|
        response_type = params.delete(:response_type) || params.delete(:_response_type) || :auto
        request('youtube-channel-shorts', params, response_type: response_type)
      end
      define_method('channel_videos') do |**params|
        response_type = params.delete(:response_type) || params.delete(:_response_type) || :auto
        request('youtube-channel-videos', params, response_type: response_type)
      end
      define_method('comments') do |**params|
        response_type = params.delete(:response_type) || params.delete(:_response_type) || :auto
        request('youtube-comments', params, response_type: response_type)
      end
      define_method('playlist') do |**params|
        response_type = params.delete(:response_type) || params.delete(:_response_type) || :auto
        request('youtube-playlist', params, response_type: response_type)
      end
      define_method('profile') do |**params|
        response_type = params.delete(:response_type) || params.delete(:_response_type) || :auto
        request('youtube-profile', params, response_type: response_type)
      end
      define_method('search') do |**params|
        response_type = params.delete(:response_type) || params.delete(:_response_type) || :auto
        request('youtube-search', params, response_type: response_type)
      end
      define_method('suggest') do |**params|
        response_type = params.delete(:response_type) || params.delete(:_response_type) || :auto
        request('youtube-suggest', params, response_type: response_type)
      end
      define_method('tag') do |**params|
        response_type = params.delete(:response_type) || params.delete(:_response_type) || :auto
        request('youtube-tag', params, response_type: response_type)
      end
      define_method('transcript') do |**params|
        response_type = params.delete(:response_type) || params.delete(:_response_type) || :auto
        request('youtube-transcript', params, response_type: response_type)
      end
      define_method('transcript_languages') do |**params|
        response_type = params.delete(:response_type) || params.delete(:_response_type) || :auto
        request('youtube-transcript-languages', params, response_type: response_type)
      end
      define_method('video') do |**params|
        response_type = params.delete(:response_type) || params.delete(:_response_type) || :auto
        request('youtube-video', params, response_type: response_type)
      end

      private

      def build_url(operation, params)
        known = operation["params"].map { |param| param["name"] }
        unknown = params.keys - known
        raise Errors::ClientError.new("unknown parameters: #{unknown.join(', ')}", operation_id: operation["id"]) unless unknown.empty?
        path = operation["path"].dup
        operation["params"].select { |param| param["in"] == "path" }.each do |param|
          value = params[param["name"]]
          raise Errors::ClientError.new("missing path parameter: #{param['name']}", operation_id: operation["id"]) if value.nil?
          path.sub!("{" + param["name"] + "}", percent_encode(value.to_s))
        end
        pairs = []
        operation["queryParams"].each do |param|
          name = param["name"]
          value = params.key?(name) ? params[name] : param["default"]
          if value.nil?
            raise Errors::ClientError.new("missing query parameter: #{name}", operation_id: operation["id"]) if param["required"]
            next
          end
          enum_values = param["enum"] || (param["items"] && param["items"]["enum"])
          if enum_values && !(value.is_a?(Array) ? value : [value]).all? { |item| enum_values.map(&:to_s).include?(item.to_s) }
            raise Errors::ClientError.new("invalid value for #{name}", operation_id: operation["id"])
          end
          if value.is_a?(Array)
            format = param["collectionFormat"] || "csv"
            if format == "multi"
              value.each { |item| pairs << [name, scalar(item)] }
            else
              separator = {"csv" => ",", "ssv" => " ", "tsv" => "\t", "pipes" => "|"}[format] || ","
              pairs << [name, value.map { |item| scalar(item) }.join(separator)]
            end
          else
            pairs << [name, scalar(value)]
          end
        end
        query = pairs.map { |name, value| "#{percent_encode(name)}=#{percent_encode(value)}" }.join("&")
        @base_url + path + (query.empty? ? "" : "?" + query)
      end

      def scalar(value)
        value == true ? "true" : (value == false ? "false" : value.to_s)
      end

      def percent_encode(value)
        URI::DEFAULT_PARSER.escape(value.to_s, /[^A-Za-z0-9\-._~]/)
      end

      def parse_response(body, content_type, operation, params, response_type)
        type = response_type.to_s
        raise Errors::ClientError.new("response_type must be auto, json, or text", operation_id: operation["id"]) unless %w[auto json text].include?(type)
        format = operation["params"].find { |param| param["name"] == "format" }
        text_formats = format && format["enum"] ? format["enum"].reject { |value| %w[json application/json].include?(value.to_s.downcase) } : []
        raw_format = params["format"] && text_formats.include?(params["format"].to_s)
        json_format = format && format["enum"] && format["enum"].any? { |value| %w[json application/json].include?(value.to_s.downcase) } && %w[json application/json].include?(params["format"].to_s.downcase)
        is_json = json_format || content_type.to_s.downcase.include?("json") || operation["produces"] == ["application/json"]
        return body if type == "text" || raw_format || (type == "auto" && !is_json)
        JSON.parse(body)
      rescue JSON::ParserError => error
        raise Errors::Error.new("invalid JSON response from Crawlora: #{error.message}", operation_id: operation["id"], body: body)
      end

      public
    end
  end
end
