// Mac PDFKit provenance for ALL 188 pages. Never export original words or images.
import Foundation
import PDFKit
import CryptoKit

func fail(_ message: String) -> Never {
    fputs("FULL_PDF_MANIFEST_ERROR: \(message)\n", stderr)
    exit(2)
}
func hash(_ bytes: Data) -> String {
    SHA256.hash(data: bytes).map { String(format: "%02x", $0) }.joined()
}
guard CommandLine.arguments.count == 3 else {
    fail("usage: swift SCRIPT AUTHORIZED_PDF OUTPUT_JSON")
}
let src = URL(fileURLWithPath: CommandLine.arguments[1])
let out = URL(fileURLWithPath: CommandLine.arguments[2])
let expected = "cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
guard let sourceBytes = try? Data(contentsOf: src), hash(sourceBytes) == expected,
      let doc = PDFDocument(url: src), doc.pageCount == 188 else {
    fail("188-page authorized source missing, changed, or corrupted")
}
var pages = [[String: Any]]()
for i in 0..<doc.pageCount {
    guard let page = doc.page(at: i), let txt = page.string else { fail("missing PDFKit page \(i)") }
    let scalars = txt.unicodeScalars
    pages.append([
        "pdf_page_index": i,
        "pdfkit_utf8_sha256": hash(Data(txt.utf8)),
        "unicode_scalar_count": scalars.count,
        "newline_count": txt.filter { $0 == "\n" }.count,
        "control_scalar_count": scalars.filter { $0.value < 32 && $0 != "\n" && $0 != "\r" && $0 != "\t" }.count,
        "has_extractable_text": !txt.isEmpty,
        "legacy_61_page_excerpt": (20...80).contains(i)
    ])
}
let manifest: [String: Any] = [
    "pdf_sha256": expected,
    "pdf_page_count": 188,
    "machine_fingerprinted_pages": 188,
    "legacy_excerpt_index_first": 20,
    "legacy_excerpt_index_last": 80,
    "legacy_excerpt_index_count": 61,
    "outside_excerpt_page_count": 127,
    "copyright_source_text_embedded": false,
    "scope_note": "PDF page fingerprints measure source integrity only; 188 physical PDF pages do not equal 188 math lesson pages or official atomic syllabus units",
    "pages": pages
]
guard JSONSerialization.isValidJSONObject(manifest) else { fail("invalid output shape") }
do {
    let json = try JSONSerialization.data(withJSONObject: manifest, options: [.sortedKeys, .prettyPrinted, .withoutEscapingSlashes])
    try json.write(to: out, options: .atomic)
    print("PDFKIT_ALL_188_SHA_LOCKED provenance-only manifest; no source words or images exported")
} catch {
    fail("could not write manifest: \(error)")
}
