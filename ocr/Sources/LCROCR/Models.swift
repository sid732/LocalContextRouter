import Foundation

/// A normalized bounding box with a **top-left** origin.
///
/// All values are fractions of the source image dimensions in the range `0...1`.
/// Vision reports boxes with a bottom-left origin; ``OCREngine`` converts them to
/// this top-left convention so downstream consumers can crop without flipping.
public struct BoundingBox: Codable, Equatable, Sendable {
    public let x: Double
    public let y: Double
    public let width: Double
    public let height: Double

    public init(x: Double, y: Double, width: Double, height: Double) {
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    }
}

/// A single recognized line of text together with its location and confidence.
public struct RecognizedLine: Codable, Equatable, Sendable {
    /// The most likely transcription of the line.
    public let text: String
    /// Recognition confidence in the range `0...1`.
    public let confidence: Double
    /// Normalized, top-left-origin bounding box of the line.
    public let boundingBox: BoundingBox

    public init(text: String, confidence: Double, boundingBox: BoundingBox) {
        self.text = text
        self.confidence = confidence
        self.boundingBox = boundingBox
    }
}
