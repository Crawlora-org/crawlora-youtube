require_relative "lib/crawlora/{{PLATFORM}}/version"

Gem::Specification.new do |spec|
  spec.name = "{{GEM_NAME}}"
  spec.version = Crawlora::{{CLASS_NAME}}::VERSION
  spec.summary = "{{DISPLAY_NAME}} client for the Crawlora hosted API"
  spec.description = "Credential-free {{DISPLAY_NAME}} API access through Crawlora's hosted service."
  spec.authors = ["Crawlora"]
  spec.license = "MIT"
  spec.required_ruby_version = ">= 2.6"
  spec.files = Dir["lib/**/*.rb", "README.md", "CHANGELOG.md", "LICENSE"]
  spec.require_paths = ["lib"]
  spec.homepage = "{{REPOSITORY}}"
  spec.metadata = { "source_code_uri" => "{{REPOSITORY}}", "rubygems_mfa_required" => "true" }
{{DEPENDENCIES}}
end
