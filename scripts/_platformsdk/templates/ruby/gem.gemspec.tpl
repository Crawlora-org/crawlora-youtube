require_relative "lib/crawlora/{{PLATFORM}}/version"

Gem::Specification.new do |spec|
  spec.name = "{{GEM_NAME}}"
  spec.version = Crawlora::{{CLASS_NAME}}::VERSION
  spec.summary = "{{DISPLAY_NAME}} API client for Crawlora ({{OPERATION_COUNT}} endpoints)"
  spec.description = "Ruby client for Crawlora's hosted {{DISPLAY_NAME}} API. Covers {{SEO_SUMMARY}} across {{OPERATION_COUNT}} endpoints."
  spec.authors = ["Crawlora"]
  spec.license = "MIT"
  spec.required_ruby_version = ">= 2.6"
  spec.files = Dir["lib/**/*.rb", "README.md", "CHANGELOG.md", "LICENSE"]
  spec.require_paths = ["lib"]
  spec.homepage = "{{HOMEPAGE_URL}}"
  spec.metadata = { "source_code_uri" => "{{REPOSITORY}}", "documentation_uri" => "{{DOCUMENTATION_URL}}", "rubygems_mfa_required" => "true" }
{{DEPENDENCIES}}
end
