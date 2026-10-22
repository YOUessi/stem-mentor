#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE="$ROOT/backend/native/vision_ocr.swift"
OUT="$ROOT/backend/native/.build/vision_ocr"
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Apple Vision OCR requires macOS" >&2
  exit 2
fi
mkdir -p "$(dirname "$OUT")"
swiftc -O "$SOURCE" -o "$OUT"
echo "Apple Vision OCR ready: $OUT"
