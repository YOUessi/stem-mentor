// On-device source page evidence only. This tool NEVER emits curriculum passages.
// Run against the legally accessed, SHA-256-pinned official PDF on the Mac only.
// Usage: swift scripts/kb_batch51_pdfkit_page_scan.swift /tmp/source.pdf > /tmp/scan.json
import Foundation
import PDFKit
import CryptoKit

guard CommandLine.arguments.count == 2 else {
    fputs("Expected exactly one local PDF path\n", stderr); exit(2)
}
let url = URL(fileURLWithPath: CommandLine.arguments[1])
guard let original = try? Data(contentsOf: url),
      let document = PDFDocument(url: url), document.pageCount == 188 else {
    fputs("Missing source or incorrect PDF page count\n", stderr); exit(2)
}
let documentSHA = SHA256.hash(data: original).map { String(format: "%02x", $0) }.joined()
guard documentSHA == "cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195" else {
    fputs("Unexpected official source SHA256\n", stderr); exit(3)
}
var pages: [[String: Any]] = []
for printed in 13...73 {
    let pageIndex = printed + 7
    guard let pageText = document.page(at: pageIndex)?.string, !pageText.isEmpty else {
        fputs("Empty/unreadable PDFKit source page\n", stderr); exit(4)
    }
    let hash = SHA256.hash(data: Data(pageText.utf8)).map { String(format: "%02x", $0) }.joined()
    let unprintable = pageText.unicodeScalars.filter {
        CharacterSet.controlCharacters.contains($0) && !CharacterSet.whitespacesAndNewlines.contains($0)
    }.count
    pages.append([
        "printed_page": printed,
        "pdf_page_index": pageIndex,
        "pdfkit_text_sha256": hash,
        "unicode_scalar_count": pageText.unicodeScalars.count,
        "control_scalar_count": unprintable,
        "content_keyword_seen": pageText.contains("内容要求"),
        "achievement_keyword_seen": pageText.contains("学业要求"),
        "teaching_keyword_seen": pageText.contains("教学提示"),
        "full_page_human_review": "PENDING"
    ])
}
let result: [String: Any] = [
    "schema_version": "kb51-pdfkit-original-page-scan-v1",
    "official_pdf_sha256": documentSHA,
    "pdf_total_pages": document.pageCount,
    "source_content_page_start": 13,
    "source_content_page_end": 73,
    "tool": "macOS PDFKit, on the pinned original PDF",
    "copyright_source_text_embedded": false,
    "pages": pages
]
let json = try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys])
FileHandle.standardOutput.write(json)
FileHandle.standardOutput.write(Data("\n".utf8))
