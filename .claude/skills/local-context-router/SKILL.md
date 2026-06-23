---
name: local-context-router
description: >-
  Preflight a PDF, scan, or screenshot locally before sending it to the model.
  Extracts the embedded text layer, OCRs image-only pages on-device with Apple
  Vision, and flags genuinely visual pages (tables, charts, diagrams) for the
  vision model, which cuts vision-token cost. Use whenever the user shares a PDF
  or image to read, summarize, or extract from.
---

# Local Context Router

A multimodal model reads a PDF by extracting its text and rendering every page to
an image, then paying for both. On a page that is mostly prose, the image is
wasted spend. Run this preflight first and send the model only what each page
needs.

## When to use

Before reading, summarizing, or extracting from a PDF, scan, or screenshot the
user has shared.

## Requirements

The `localcontextrouter` package must be installed (`pip install localcontextrouter`,
macOS). It provides the `localctx` command used below.

## Run

Route the document and read the JSON, rendering any visual pages into a folder:

```sh
localctx <path-to-document> --json --vision-dir ./lcr-pages
```

If the `localctx` command is not available, run the bundled script with a Python
that has `localcontextrouter` installed (the script imports the same package):

```sh
python scripts/preflight.py <path-to-document> --json --vision-dir ./lcr-pages
```

## Use the result

The JSON has `tokens_saved` and a `pages` array. Each page carries `source`,
`text`, `text_tokens`, `image_tokens`, and `image`:

- `source: "text"`: use `text` directly; do not attach the image.
- `source: "ocr"`: the page was image-only and has been OCR'd on-device; use `text`.
- `source: "vision"`: the page is a table, chart, or diagram; attach the image at
  `image` so the model can read it. The `text` is a rough fallback only.

Assemble the text and OCR pages in reading order, attach images only for the
vision pages, and mention `tokens_saved` if the user cares about cost.

## Notes

Everything runs locally and offline; the document does not leave the machine.
