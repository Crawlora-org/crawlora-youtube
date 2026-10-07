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
  spec.homepage = "https://github.com/Crawlora-org/crawlora-youtube"
  spec.metadata = { "source_code_uri" => "https://github.com/Crawlora-org/crawlora-youtube", "rubygems_mfa_required" => "true" }

end
