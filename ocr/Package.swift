// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "lcr-ocr",
    platforms: [.macOS(.v10_15)],
    targets: [
        .target(name: "LCROCR"),
        .executableTarget(name: "lcr-ocr", dependencies: ["LCROCR"]),
        .testTarget(name: "LCROCRTests", dependencies: ["LCROCR"]),
    ]
)
