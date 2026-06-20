---
name: local-context-router
description: >-
  Preflight a PDF, scan, or screenshot locally before sending it to the model.
  Extracts the embedded text layer for free, OCRs image-only pages on-device
  with Apple Vision, and flags only genuinely visual pages (tables, charts,
  diagrams) for the vision model — cutting vision-token cost. Use whenever the
  user shares a PDF or image to read, summarize, or extract from.
---

# Local Context Router

Multimodal models read a PDF by extracting its text *and* rendering every page
to an image, billing for both. For text-heavy pages that is a 2–10× token tax
for no added signal. This skill spends cheap local compute first and only pays
for vision when a page's meaning actually lives in its pixels.

## When to use

Use this **before** attaching a PDF, scan, or screenshot to the conversation —
whenever the user wants you to read, summarize, or extract from a document.

## How to run

Run the preflight script on the file. It picks the cheapest faithful source per
page and prints the result as JSON:

```sh
python "${CLAUDE_SKILL_DIR}/scripts/preflight.py" <path-to-document> --json --vision-dir "${CLAUDE_SKILL_DIR}/.cache"
```

- `<path-to-document>` is the PDF or image to analyze.
- `--vision-dir` is where rendered images of visual pages are written.

## How to use the result

The JSON has a `pages` array and a `tokens_saved` total. For each page:

- **`source: "text"`** — use the page's `text` directly. Do **not** attach the
  image; it adds cost without information.
- **`source: "ocr"`** — the page was image-only and has been OCR'd on-device;
  use the returned `text`.
- **`source: "vision"`** — the page is a table, chart, or diagram whose meaning
  is visual. Attach the rendered image at `image` to the conversation so the
  vision model can read it. The `text` is a rough fallback only.

Assemble the per-page text in order for the parts you can read as text, and
attach images only for the `vision` pages. Mention `tokens_saved` if the user
cares about cost.

## Notes

- Everything runs locally and offline; no document leaves the machine during
  preflight.
- Requires macOS (on-device OCR uses Apple Vision) and the `localcontextrouter`
  package importable by the Python interpreter.
