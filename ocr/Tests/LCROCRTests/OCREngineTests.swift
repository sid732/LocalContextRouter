import CoreGraphics
import CoreText
import Foundation
import XCTest

@testable import LCROCR

final class OCREngineTests: XCTestCase {
    /// Render `text` as black Helvetica on a white background using Core Text.
    /// Done in-process so tests carry no binary fixtures.
    private func renderImage(
        _ text: String,
        width: Int = 600,
        height: Int = 200,
        fontSize: CGFloat = 72
    ) throws -> CGImage {
        let context = try XCTUnwrap(
            CGContext(
                data: nil,
                width: width,
                height: height,
                bitsPerComponent: 8,
                bytesPerRow: 0,
                space: CGColorSpaceCreateDeviceRGB(),
                bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
            )
        )
        context.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
        context.fill(CGRect(x: 0, y: 0, width: width, height: height))

        let font = CTFontCreateWithName("Helvetica" as CFString, fontSize, nil)
        let attributes: [NSAttributedString.Key: Any] = [
            NSAttributedString.Key(kCTFontAttributeName as String): font
        ]
        let attributed = NSAttributedString(string: text, attributes: attributes)
        let line = CTLineCreateWithAttributedString(attributed)
        context.textPosition = CGPoint(x: 30, y: 70)
        CTLineDraw(line, context)

        return try XCTUnwrap(context.makeImage())
    }

    func testRecognizesClearText() throws {
        let image = try renderImage("HELLO")
        let lines = try OCREngine.recognize(in: image)
        let transcript = lines.map(\.text).joined(separator: " ").uppercased()
        XCTAssertTrue(transcript.contains("HELLO"), "unexpected transcript: \(transcript)")
    }

    func testBoundingBoxIsNormalizedTopLeft() throws {
        let image = try renderImage("TEST")
        let line = try XCTUnwrap(try OCREngine.recognize(in: image).first)
        let box = line.boundingBox
        XCTAssert((0.0 ... 1.0).contains(box.x), "x out of range: \(box.x)")
        XCTAssert((0.0 ... 1.0).contains(box.y), "y out of range: \(box.y)")
        XCTAssert(box.width > 0 && box.width <= 1.0, "width out of range: \(box.width)")
        XCTAssert(box.height > 0 && box.height <= 1.0, "height out of range: \(box.height)")
        XCTAssert(line.confidence > 0, "confidence not positive: \(line.confidence)")
    }

    func testFastModeAlsoRecognizes() throws {
        let image = try renderImage("QUICK")
        let lines = try OCREngine.recognize(in: image, options: .init(level: .fast))
        XCTAssertFalse(lines.isEmpty, "fast mode returned no lines")
    }

    func testMissingImagePathThrows() {
        XCTAssertThrowsError(try ImageLoader.loadCGImage(atPath: "/no/such/file.png")) { error in
            guard case ImageLoadError.cannotOpen = error else {
                return XCTFail("expected cannotOpen, got \(error)")
            }
        }
    }
}
