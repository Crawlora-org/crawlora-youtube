{
  "name": "{{PACKAGE_NAME}}",
  "description": "{{DISPLAY_NAME}} client for the Crawlora hosted API",
  "type": "library",
  "license": "MIT",
  "require": {
    "php": ">=8.1",
    "ext-curl": "*",
    "ext-json": "*"
  },
  "autoload": {
    "psr-4": {
      "Crawlora\\{{CLASS_NAME}}\\": "src/Crawlora/{{CLASS_NAME}}/"
    }
  },
  "autoload-dev": {
    "psr-4": {
      "Crawlora\\{{CLASS_NAME}}\\Tests\\": "tests/"
    }
  },
  "scripts": {
    "test": "php tests/client_test.php"
  },
  "homepage": "{{HOMEPAGE_URL}}",
  "support": {
    "source": "{{REPOSITORY}}",
    "docs": "{{DOCUMENTATION_URL}}"
  }
}
