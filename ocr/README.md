# lcr-ocr

On-device OCR binary used by LocalContextRouter. Wraps the Apple Vision
framework, fully offline, no network, no entitlements, and no Screen Recording
permission (it reads image files you pass in, it does not capture the screen).

## Build

```sh
swift build -c release
# binary at .build/release/lcr-ocr
```

## Usage

```sh
lcr-ocr <image-path> [options]
```

| Option | Description |
| --- | --- |
| `--json` | Emit JSON (`text`, `confidence`, `boundingBox`) per line instead of plain text. |
| `--fast` | Use the fast recognition path instead of the accurate (neural) one. |
| `--lang <codes>` | Comma-separated language codes, e.g. `en-US,fr-FR`. Disables automatic detection. |
| `--no-correction` | Disable language-based spelling correction (use for codes/IDs). |
| `-h`, `--help` | Show help. |

Plain-text output, one line per recognized line:

```sh
$ lcr-ocr invoice.png
INVOICE 2026
```

JSON output. Bounding boxes are normalized to `0...1` with a **top-left** origin,
ready to crop without flipping:

```sh
$ lcr-ocr invoice.png --json
[
  {
    "boundingBox" : { "height" : 0.288, "width" : 0.611, "x" : 0.037, "y" : 0.400 },
    "confidence" : 1,
    "text" : "INVOICE 2026"
  }
]
```

## Exit codes

Follows the `sysexits.h` convention so callers can branch on failure mode:

| Code | Meaning |
| --- | --- |
| `0` | Success. |
| `64` | Usage error (bad or missing arguments). |
| `66` | Input file could not be read. |
| `70` | Internal recognition error. |

## Layout

- `Sources/LCROCR`, reusable library: image loading, the Vision engine, and the result models.
- `Sources/lcr-ocr`, thin CLI over the library.
- `Tests/LCROCRTests`, engine tests that render text in-process (no binary fixtures).

## Requirements

macOS 10.15+. Automatic language detection is used on macOS 13+ and skipped
gracefully below that.
