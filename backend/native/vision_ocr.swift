import Foundation
import Vision

struct Segment: Codable {
    let text: String
    let bbox: [Double]
}

struct Line: Codable {
    let text: String
    let confidence: Float
    let bbox: [Double]
    let spans: [Segment]
}
struct Payload: Codable {
    let engine: String
    let lines: [Line]
}
func topLeftNormalized(_ rect: CGRect) -> [Double] {
    return [Double(rect.minX), Double(1.0 - rect.maxY),
            Double(rect.width), Double(rect.height)]
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
    let mathSymbols = CharacterSet(charactersIn: "=+-*/^²³√∫∑±×÷≤≥")
    for observation in observations {
        guard let item = observation.topCandidates(1).first else { continue }
        var spans: [Segment] = []
        // When a line contains explanatory text followed by a colon and an
        // equation, expose a more focused region. Geometry/text is not inferred.
        if let colon = item.string.firstIndex(where: {$0 == ":" || $0 == "："}) {
            var start = item.string.index(after: colon)
            while start < item.string.endIndex &&
                    item.string[start].isWhitespace {
                start = item.string.index(after: start)
            }
            if start < item.string.endIndex {
                let tail = String(item.string[start...])
                if tail.rangeOfCharacter(from: mathSymbols) != nil {
                    let range = start..<item.string.endIndex
                    if let rect = try? item.boundingBox(for: range),
                       rect.boundingBox.width > 0.005,
                       rect.boundingBox.height > 0.005 {
                        spans.append(Segment(
                            text: tail, bbox: topLeftNormalized(rect.boundingBox)))
                    }
                }
            }
        }
        lines.append(Line(
            text: item.string,
            confidence: item.confidence,
            bbox: topLeftNormalized(observation.boundingBox),
            spans: spans
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
