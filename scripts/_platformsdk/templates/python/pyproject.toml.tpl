[build-system]
requires = ["setuptools>=77", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{{PYTHON_NAME}}"
version = "{{VERSION}}"
description = "Typed {{DISPLAY_NAME}} client for the Crawlora hosted API"
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"
license-files = ["LICENSE"]
authors = [{ name = "Crawlora" }]
classifiers = [
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.10",
  "Typing :: Typed",
]
dependencies = ["typing-extensions>=4.7; python_version < '3.11'"]

[project.optional-dependencies]
async = ["httpx>=0.27"]
test = ["mypy>=1.11", "pytest>=8"]

[project.urls]
Homepage = "{{REPOSITORY}}"
Repository = "{{REPOSITORY}}"

[tool.setuptools.packages.find]
where = ["."]
include = ["{{MODULE_NAME}}"]

[tool.setuptools.package-data]
"{{MODULE_NAME}}" = ["py.typed", "*.pyi"]
