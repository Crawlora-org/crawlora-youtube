require_relative "lib/crawlora/youtube/version"

Gem::Specification.new do |spec|
  spec.name = "crawlora-youtube"
  spec.version = Crawlora::Youtube::VERSION
  spec.summary = "YouTube API client for Crawlora (14 endpoints)"
  spec.description = "Ruby client for Crawlora's hosted YouTube API. Covers search, channels, videos, playlists, comments, captions, and transcripts across 14 endpoints."
  spec.authors = ["Crawlora"]
  spec.license = "MIT"
  spec.required_ruby_version = ">= 2.6"
  spec.files = Dir["lib/**/*.rb", "README.md", "CHANGELOG.md", "LICENSE"]
  spec.require_paths = ["lib"]
  spec.homepage = "https://crawlora.net/?utm_source=rubygems&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-ruby-homepage"
  spec.metadata = { "source_code_uri" => "https://github.com/Crawlora-org/crawlora-youtube", "documentation_uri" => "https://github.com/Crawlora-org/crawlora-youtube/blob/main/ruby/README.md", "rubygems_mfa_required" => "true" }

end
