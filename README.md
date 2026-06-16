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

## Use

LocalContextRouter ships in two forms that share one core engine and one on-device OCR
binary. There is no server and no background process — everything runs on demand and
exits.

- **Python library + `localctx` CLI** — `pip install localcontextrouter`
- **Agent Skill** — a `SKILL.md` that runs the same preflight step inside Claude Code or Codex

## Requirements

- macOS 10.15+ (on-device OCR uses the Apple Vision framework)
- Python 3.10+

## License

[MIT](LICENSE) © 2026 Siddharth Nashikkar
