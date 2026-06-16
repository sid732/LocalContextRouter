import CoreGraphics
import Foundation
import ImageIO

/// Errors raised while loading an image from disk.
public enum ImageLoadError: Error, CustomStringConvertible {
    case cannotOpen(String)
    case unsupportedFormat(String)

    public var description: String {
        switch self {
        case let .cannotOpen(path):
            return "cannot open image: \(path)"
        case let .unsupportedFormat(path):
            return "unsupported or corrupt image: \(path)"
        }
    }
}

/// Loads bitmaps from disk into `CGImage` using ImageIO.
///
/// ImageIO is used instead of AppKit so the binary runs headless (no window
/// server) — important for CI and for invocation from a CLI.
public enum ImageLoader {
    /// Decode the first image in the file at `path`.
    public static func loadCGImage(atPath path: String) throws -> CGImage {
        guard FileManager.default.fileExists(atPath: path) else {
            throw ImageLoadError.cannotOpen(path)
        }
        let url = URL(fileURLWithPath: path)
        guard let source = CGImageSourceCreateWithURL(url as CFURL, nil) else {
            throw ImageLoadError.cannotOpen(path)
        }
        guard let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
            throw ImageLoadError.unsupportedFormat(path)
        }
        return image
    }
}
