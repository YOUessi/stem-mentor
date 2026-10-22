import Foundation
import Vision

struct Line: Codable {
    let text: String
    let confidence: Float
    let bbox: [Double]
}
struct Payload: Codable {
    let engine: String
    let lines: [Line]
}

guard CommandLine.arguments.count == 2 else {
    fputs("Usage: vision_ocr <image-path>\n", stderr)
    exit(2)
}
let imageURL = URL(fileURLWithPath: CommandLine.arguments[1])
do {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["zh-Hans", "en-US"]
    request.usesLanguageCorrection = true
    let handler = VNImageRequestHandler(url: imageURL, options: [:])
    try handler.perform([request])
    let observations = request.results ?? []
    var lines: [Line] = []
    for observation in observations {
        guard let item = observation.topCandidates(1).first else { continue }
        let rect = observation.boundingBox
        lines.append(Line(
            text: item.string,
            confidence: item.confidence,
            bbox: [Double(rect.minX),
                   Double(1.0 - rect.maxY),
                   Double(rect.width),
                   Double(rect.height)]
        ))
    }
    lines.sort { a, b in
        let ay = a.bbox[1], by = b.bbox[1]
        if abs(ay - by) > 0.022 { return ay < by }
        return a.bbox[0] < b.bbox[0]
    }
    let result = Payload(engine: "apple_vision", lines: lines)
    let encoded = try JSONEncoder().encode(result)
    FileHandle.standardOutput.write(encoded)
} catch {
    fputs("Vision OCR failed: \(error.localizedDescription)\n", stderr)
    exit(1)
}
