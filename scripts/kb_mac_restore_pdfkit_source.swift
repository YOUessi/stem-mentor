// Rebuild Mac-only volatile PDFKit source evidence after a reboot.
// Copyright PDF and extracted passages must NEVER be committed to Git.
import Foundation
import PDFKit
import AppKit
import CryptoKit

func fail(_ message: String) -> Never {
    fputs("PDFKIT_RESTORE_FAILED: \(message)\n", stderr)
    exit(2)
}
func sha256(_ bytes: Data) -> String {
    SHA256.hash(data: bytes).map { String(format: "%02x", $0) }.joined()
}
let args = CommandLine.arguments
guard args.count == 4 else {
    fail("Usage: swift scripts/kb_mac_restore_pdfkit_source.swift ORIGINAL_PDF FINGERPRINT_JSON PRIVATE_CACHE_DIR")
}
let pdf = URL(fileURLWithPath: args[1])
let manifestURL = URL(fileURLWithPath: args[2])
let outDir = URL(fileURLWithPath: args[3], isDirectory: true)
let pinnedPDF = "cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
guard let sourceBytes = try? Data(contentsOf: pdf),
      sha256(sourceBytes) == pinnedPDF,
      let document = PDFDocument(url: pdf),
      document.pageCount == 188 else {
    fail("missing or unauthorized official source PDF: expected pinned 188-page edition")
}
guard let manifestBytes = try? Data(contentsOf: manifestURL),
      let manifest = try? JSONSerialization.jsonObject(with: manifestBytes) as? [String: Any],
      (manifest["official_pdf_sha256"] as? String) == pinnedPDF,
      let pages = manifest["pages"] as? [[String: Any]],
      pages.count == 61 else {
    fail("invalid or outdated versioned PDFKit fingerprint manifest")
}
var staged: [(Int, Data)] = []
var seen: Set<Int> = []
for row in pages {
    guard let page = row["printed_page"] as? Int,
          (13...73).contains(page),
          seen.insert(page).inserted,
          let expected = row["pdfkit_text_sha256"] as? String,
          expected.count == 64,
          let content = document.page(at: page + 7)?.string else {
        fail("missing/duplicate page or malformed recorded fingerprint")
    }
    let bytes = Data(content.utf8)
    guard sha256(bytes) == expected else {
        fail("PDFKit text is not byte-for-byte identical to recorded evidence at printed page \(page)")
    }
    staged.append((page, bytes))
}
guard seen == Set(13...73) else { fail("incomplete required 61-page syllabus range") }
guard let page35 = document.page(at: 42) else { fail("missing exact p35 original image") }
// Historical Batch74 visual attestation: PDFKit image request 1286x1800
// yields exact bitmap 1285x1800. Never replace its pinned image digest.
let page35Preview = page35.thumbnail(of: CGSize(width: 1286, height: 1800), for: .mediaBox)
guard let bitmapTIFF = page35Preview.tiffRepresentation,
      let bitmap = NSBitmapImageRep(data: bitmapTIFF),
      bitmap.pixelsWide == 1285, bitmap.pixelsHigh == 1800,
      let page35PNG = bitmap.representation(using: .png, properties: [:]),
      sha256(page35PNG) == "bfcf80effdcf8289eb4eb1bc006bdad55476d0872a14c43a5ebff1232548b435" else {
    fail("re-rendered p35 PDF image differs from frozen historical visual evidence")
}
do {
    try FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)
    for (page, bytes) in staged {
        try bytes.write(to: outDir.appendingPathComponent("kb56_page_\(page).txt"), options: .atomic)
    }
    try page35PNG.write(to: outDir.appendingPathComponent("kb51_official_page_35.png"), options: .atomic)
} catch {
    fail("failed to write Mac-only scratch files: \(error.localizedDescription)")
}
print("PDFKIT_RESTORED 61/61 pinned pages plus historical p35 original image SHA; PDF SHA \(pinnedPDF); text/image not printed or committed")
