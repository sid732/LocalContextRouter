import CoreGraphics
import Foundation
import LCROCR

// Subset of sysexits.h so callers can distinguish failure modes.
private let exitUsage: Int32 = 64 // EX_USAGE: bad arguments
private let exitNoInput: Int32 = 66 // EX_NOINPUT: input file could not be read
private let exitSoftware: Int32 = 70 // EX_SOFTWARE: internal recognition error

private let usage = """
usage: lcr-ocr <image-path> [options]

Recognize text in an image using the on-device Apple Vision framework.

Options:
  --json            Emit JSON (text, confidence, bounding box) per line.
  --fast            Use the fast recognition path instead of accurate.
  --lang <codes>    Comma-separated language codes, e.g. en-US,fr-FR.
                    Disables automatic language detection.
  --no-correction   Disable language-based spelling correction.
  -h, --help        Show this help.
"""

private func fail(_ message: String, code: Int32, showUsage: Bool = false) -> Never {
    var text = "error: \(message)"
    if showUsage { text += "\n\n\(usage)" }
    FileHandle.standardError.write(Data((text + "\n").utf8))
    exit(code)
}

private struct Arguments {
    var inputPath: String
    var asJSON = false
    var level: RecognitionLevel = .accurate
    var languages: [String] = []
    var usesCorrection = true
    var autoDetect = true
}

private func parse(_ argv: [String]) -> Arguments {
    if argv.contains("-h") || argv.contains("--help") {
        print(usage)
        exit(0)
    }

    var inputPath: String?
    var asJSON = false
    var level: RecognitionLevel = .accurate
    var languages: [String] = []
    var usesCorrection = true
    var autoDetect = true

    var index = 0
    while index < argv.count {
        let arg = argv[index]
        switch arg {
        case "--json":
            asJSON = true
        case "--fast":
            level = .fast
        case "--no-correction":
            usesCorrection = false
        case "--lang":
            index += 1
            guard index < argv.count else {
                fail("--lang requires a value", code: exitUsage, showUsage: true)
            }
            languages = argv[index]
                .split(separator: ",")
                .map { $0.trimmingCharacters(in: .whitespaces) }
                .filter { !$0.isEmpty }
            autoDetect = false
        default:
            if arg.hasPrefix("-") {
                fail("unknown option \(arg)", code: exitUsage, showUsage: true)
            }
            if inputPath == nil {
                inputPath = arg
            } else {
                fail("unexpected argument \(arg)", code: exitUsage, showUsage: true)
            }
        }
        index += 1
    }

    guard let path = inputPath else {
        fail("missing image path", code: exitUsage, showUsage: true)
    }

    return Arguments(
        inputPath: path,
        asJSON: asJSON,
        level: level,
        languages: languages,
        usesCorrection: usesCorrection,
        autoDetect: autoDetect
    )
}

private func emit(_ lines: [RecognizedLine], asJSON: Bool) {
    guard asJSON else {
        for line in lines { print(line.text) }
        return
    }
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes]
    do {
        let data = try encoder.encode(lines)
        FileHandle.standardOutput.write(data)
        FileHandle.standardOutput.write(Data("\n".utf8))
    } catch {
        fail("failed to encode JSON: \(error)", code: exitSoftware)
    }
}

private let arguments = parse(Array(CommandLine.arguments.dropFirst()))

private let image: CGImage
do {
    image = try ImageLoader.loadCGImage(atPath: arguments.inputPath)
} catch {
    fail("\(error)", code: exitNoInput)
}

private let options = RecognitionOptions(
    level: arguments.level,
    languages: arguments.languages,
    usesLanguageCorrection: arguments.usesCorrection,
    automaticallyDetectsLanguage: arguments.autoDetect
)

do {
    let lines = try OCREngine.recognize(in: image, options: options)
    emit(lines, asJSON: arguments.asJSON)
} catch {
    fail("\(error)", code: exitSoftware)
}
