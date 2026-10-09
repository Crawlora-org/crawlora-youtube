require_relative "lib/crawlora/youtube/version"

Gem::Specification.new do |spec|
  spec.name = "crawlora-youtube"
  spec.version = Crawlora::Youtube::VERSION
  spec.summary = "YouTube client for the Crawlora hosted API"
  spec.description = "Credential-free YouTube API access through Crawlora's hosted service."
  spec.authors = ["Crawlora"]
  spec.license = "MIT"
  spec.required_ruby_version = ">= 2.6"
  spec.files = Dir["lib/**/*.rb", "README.md", "CHANGELOG.md", "LICENSE"]
  spec.require_paths = ["lib"]
  spec.homepage = "https://crawlora.net/?utm_source=rubygems&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-ruby-homepage"
  spec.metadata = { "source_code_uri" => "https://github.com/Crawlora-org/crawlora-youtube", "documentation_uri" => "https://crawlora.net/docs?utm_source=rubygems&utm_medium=referral&utm_campaign=platform-clients&utm_content=youtube-ruby-api-docs", "rubygems_mfa_required" => "true" }

end
