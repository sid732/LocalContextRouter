# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims
to follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0]

First release.

### Added

- On-device OCR binary (`lcr-ocr`) wrapping Apple Vision: image to text with
  bounding boxes and confidence, offline and without entitlements.
- Page classification (`digital` / `scanned` / `garbled`) from cheap text
  signals.
- PDF text extraction and page rendering via pypdfium2.
- Vision-worthy detection (tables, charts, diagrams, figure-heavy layouts) from
  image and vector-path signals.
- Token-cost estimation for Claude and OpenAI image inputs, plus a text
  estimate, following each provider's documented tokenization.
- `route_pdf`, which routes each page to text, OCR, or vision and reports the
  tokens saved versus sending every page as an image.
- Routed text is normalized — stray control characters (e.g. PDF discretionary
  hyphens) are stripped and line endings collapsed — while classification still
  runs on the raw text layer.
- `localctx` command-line interface.
- A `local-context-router` Agent Skill for Claude Code and Codex.

### Notes

- macOS only; OCR uses the Apple Vision framework.
- The macOS wheel is a `universal2` platform wheel that bundles the `lcr-ocr`
  binary, so OCR works out of the box. `LCR_OCR_BIN` overrides the bundled copy.

[0.1.0]: https://github.com/sid732/LocalContextRouter/releases/tag/v0.1.0
