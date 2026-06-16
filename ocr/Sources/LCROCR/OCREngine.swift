import CoreGraphics
import Foundation
import Vision

/// Speed/accuracy trade-off for recognition.
public enum RecognitionLevel: String, Sendable {
    /// Neural recognition: handles multi-line and skewed text. Slower.
    case accurate
    /// Faster, character-based recognition. Less accurate.
    case fast
}

/// Tunables for a recognition pass.
public struct RecognitionOptions: Sendable {
    public var level: RecognitionLevel
    /// Ordered ISO language codes (e.g. `["en-US", "fr-FR"]`). Empty uses defaults.
    public var languages: [String]
    /// Apply a language model to correct spelling. Disable for codes/IDs.
    public var usesLanguageCorrection: Bool
    /// Let Vision pick the language automatically (macOS 13+). Ignored if
    /// ``languages`` is non-empty.
    public var automaticallyDetectsLanguage: Bool

    public init(
        level: RecognitionLevel = .accurate,
        languages: [String] = [],
        usesLanguageCorrection: Bool = true,
        automaticallyDetectsLanguage: Bool = true
    ) {
        self.level = level
        self.languages = languages
        self.usesLanguageCorrection = usesLanguageCorrection
        self.automaticallyDetectsLanguage = automaticallyDetectsLanguage
    }
}

/// Errors raised by the recognition pass.
public enum OCRError: Error, CustomStringConvertible {
    case recognitionFailed(String)

    public var description: String {
        switch self {
        case let .recognitionFailed(message):
            return "text recognition failed: \(message)"
        }
    }
}

/// On-device text recognition backed by the Apple Vision framework.
public enum OCREngine {
    /// Recognize text in `image`, returning one ``RecognizedLine`` per detected
    /// line in Vision's reading order.
    public static func recognize(
        in image: CGImage,
        options: RecognitionOptions = .init()
    ) throws -> [RecognizedLine] {
        let request = VNRecognizeTextRequest()
        request.recognitionLevel = options.level == .fast ? .fast : .accurate
        request.usesLanguageCorrection = options.usesLanguageCorrection
        if !options.languages.isEmpty {
            request.recognitionLanguages = options.languages
        }
        if #available(macOS 13.0, *) {
            request.automaticallyDetectsLanguage =
                options.languages.isEmpty && options.automaticallyDetectsLanguage
        }

        let handler = VNImageRequestHandler(cgImage: image, orientation: .up, options: [:])
        do {
            try handler.perform([request])
        } catch {
            throw OCRError.recognitionFailed(error.localizedDescription)
        }

        let observations = request.results ?? []
        return observations.compactMap { observation -> RecognizedLine? in
            guard let candidate = observation.topCandidates(1).first else { return nil }
            return RecognizedLine(
                text: candidate.string,
                confidence: Double(candidate.confidence),
                boundingBox: topLeftBox(from: observation.boundingBox)
            )
        }
    }

    /// Convert a Vision bottom-left normalized rect to a top-left normalized box.
    private static func topLeftBox(from rect: CGRect) -> BoundingBox {
        BoundingBox(
            x: Double(rect.origin.x),
            y: Double(1.0 - rect.origin.y - rect.height),
            width: Double(rect.width),
            height: Double(rect.height)
        )
    }
}
