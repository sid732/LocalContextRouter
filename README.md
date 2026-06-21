# LocalContextRouter

> Stop paying the vision-token tax. Decide locally — text, OCR, or vision — *before* a document ever reaches a multimodal LLM.

LocalContextRouter is a **preflight layer** for document-heavy LLM workflows. Given a
PDF or image, it inspects the content on your machine and decides the cheapest path
that still preserves accuracy:

- **Text-layer PDF** → extract text locally (near-free).
- **Scanned / image-only page** → OCR on-device with Apple Vision.
- **Chart / table / diagram / layout-heavy page** → keep the page as an image for the vision model, where the pixels actually carry meaning.

It never calls an LLM itself. It prepares the cheapest faithful context and hands you
back a routing decision plus a token-savings estimate. Your application still owns the
model call.

## Why

Multimodal models read a PDF by extracting its text *and* rendering every page to an
image, then billing for both. A text-heavy page sent as an image can cost
**1,300–4,800 tokens**; the same page as extracted text costs **400–800**. For
text-dominant documents that is a 2–10× tax for zero added signal.

LocalContextRouter spends cheap local compute to avoid that tax — and only escalates
to vision when the page genuinely needs it.

## Install

```sh
pip install localcontextrouter
```

OCR uses an on-device Swift binary (`lcr-ocr`). Build it from the bundled package
and point the library at it (text extraction, classification, and token estimation
work without it; only pages that need OCR require it):

```sh
swift build -c release --package-path ocr
export LCR_OCR_BIN="$PWD/ocr/.build/release/lcr-ocr"
```

## Use

There is no server and no background process — everything runs on demand and exits.

### Command line

```sh
localctx report.pdf                       # human summary + tokens saved
localctx report.pdf --json                # machine-readable
localctx report.pdf --vision-dir ./out    # render visual pages to ./out
```

### Library

```python
from localcontextrouter import route_pdf, Source

result = route_pdf("report.pdf")
for page in result.pages:
    if page.source is Source.VISION:
        ...  # send the rendered page image to the model
    else:
        ...  # use page.text (extracted or OCR'd)

print(result.text)          # all text-routable pages joined
print(result.tokens_saved)  # tokens avoided vs sending every page as an image
```

### Agent Skill

The `local-context-router` skill (in `.claude/skills/`) runs the same preflight
inside Claude Code or Codex — copy it into your `.claude/skills/` (or `~/.claude/skills/`).

## Requirements

- macOS 10.15+ (on-device OCR uses the Apple Vision framework)
- Python 3.10+

## License

[MIT](LICENSE) © 2026 Siddharth Nashikkar
