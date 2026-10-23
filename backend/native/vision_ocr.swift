import Foundation
import Vision

// All coordinates use normalized top-left origin, matching the Python pipeline.
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
    [Double(rect.minX), Double(1.0 - rect.maxY),
     Double(rect.width), Double(rect.height)]
}

private let formulaMarks = CharacterSet(charactersIn: "=<>≤≥≠≈±×÷√∫∑∏∂∞∠∥⊥πθΔ△∈∉∪∩^_²³⁴⁵⁶⁷⁸⁹⁰¹+-*/")
private let separators = CharacterSet(charactersIn: "，。；;：:！？!?")
private let leadingInstruction = try! NSRegularExpression(
    pattern: #"(?i)^(?:(?:given|solve|compute|calculate|find|prove|show|simplify|evaluate|let)\s+)+"#
)

func isHan(_ ch: Character) -> Bool {
    ch.unicodeScalars.contains {
        (0x3400...0x9fff).contains(Int($0.value)) ||
        (0x20000...0x2fa1f).contains(Int($0.value))
    }
}
func isBreak(_ ch: Character, depth: Int) -> Bool {
    if isHan(ch) { return true }
    if ch == "," && depth == 0 { return true }
    return ch.unicodeScalars.contains { separators.contains($0) }
}
func strippedRange(_ range: Range<String.Index>, in text: String) -> Range<String.Index>? {
    var a = range.lowerBound, b = range.upperBound
    while a < b && text[a].isWhitespace { a = text.index(after: a) }
    while b > a && text[text.index(before: b)].isWhitespace {
        b = text.index(before: b)
    }
    return a < b ? a..<b : nil
}
func formulaRanges(_ text: String) -> [Range<String.Index>] {
    var intervals: [Range<String.Index>] = []
    var cursor = text.startIndex
    var segmentStart = cursor
    var depth = 0
    while cursor < text.endIndex {
        let ch = text[cursor]
        if isBreak(ch, depth: depth) {
            intervals.append(segmentStart..<cursor)
            segmentStart = text.index(after: cursor)
        } else if ch == "(" || ch == "[" || ch == "{" {
            depth += 1
        } else if ch == ")" || ch == "]" || ch == "}" {
            depth = max(depth - 1, 0)
        }
        cursor = text.index(after: cursor)
    }
    intervals.append(segmentStart..<text.endIndex)

    var results: [Range<String.Index>] = []
    for interval in intervals {
        guard var range = strippedRange(interval, in: text) else { continue }
        // Remove conventional English instructions, not formula characters.
        let raw = String(text[range])
        let full = NSRange(raw.startIndex..<raw.endIndex, in: raw)
        if let match = leadingInstruction.firstMatch(in: raw, options: [], range: full),
           let prefix = Range(match.range, in: raw) {
            let offset = raw.distance(from: raw.startIndex, to: prefix.upperBound)
            if let adjusted = text.index(range.lowerBound, offsetBy: offset,
                                         limitedBy: range.upperBound) {
                range = adjusted..<range.upperBound
            }
        }
        guard let clean = strippedRange(range, in: text) else { continue }
        let candidate = String(text[clean])
        guard candidate.count >= 3 && candidate.count <= 350 else { continue }
        guard candidate.rangeOfCharacter(from: formulaMarks) != nil else { continue }
        // Explicitly avoid lone operator marks and short accidental OCR noise.
        let lexicalCount = candidate.filter({ $0.isLetter || $0.isNumber }).count
        let possibleOCRSymbolSwap = candidate.contains("×") &&
            candidate.contains("=") && lexicalCount >= 1
        guard lexicalCount >= 2 || possibleOCRSymbolSwap else { continue }
        results.append(clean)
    }
    return Array(results.prefix(8))
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
        var spans: [Segment] = []
        for range in formulaRanges(item.string) {
            // Vision's substring box is grounded in image pixels, never derived
            // from arbitrary text length or model-predicted geometry.
            if let observation = try? item.boundingBox(for: range) {
                let rect = observation.boundingBox
                if rect.width > 0.004 && rect.height > 0.004 {
                    spans.append(Segment(
                        text: String(item.string[range]),
                        bbox: topLeftNormalized(rect)
                    ))
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
    let output = try JSONEncoder().encode(Payload(
        engine: "apple_vision", lines: lines
    ))
    FileHandle.standardOutput.write(output)
} catch {
    fputs("Vision OCR failed: \(error.localizedDescription)\n", stderr)
    exit(1)
}
