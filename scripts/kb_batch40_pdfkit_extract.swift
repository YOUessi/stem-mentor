// Optional macOS source verification. Emit raw page text only to a process pipe,
// never into Git, logs or the student corpus.
import Foundation
import PDFKit
let args = CommandLine.arguments
guard args.count == 2, let doc = PDFDocument(url: URL(fileURLWithPath: args[1])),
      doc.pageCount == 188 else { fputs("Invalid original PDF or page count\n", stderr); exit(2) }
let pages = [52,53,57,58,59,65,66,71,73]
var items: [[String: Any]] = []
for page in pages {
  guard let content = doc.page(at: page + 7)?.string, !content.isEmpty else {
    fputs("Missing PDFKit text page\n", stderr); exit(2)
  }
  items.append(["printed_page":page, "pdf_page_index":page+7, "text":content])
}
let output = try JSONSerialization.data(withJSONObject: items, options: [.sortedKeys])
FileHandle.standardOutput.write(output)
