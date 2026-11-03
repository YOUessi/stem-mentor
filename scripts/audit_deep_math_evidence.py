#!/usr/bin/env python3
"""Read-only K07 mathematical subclaim audit; nonzero exit on falsified claims.

This checks a *narrow author-frozen expression subset*. In particular,
zero failures must never be interpreted as full textbook proof approval.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.deep_math_evidence import evidence_audit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail CI if any fixed claim is contradicted")
    parser.add_argument("--output", help="Write versioned JSON evidence; default prints to stdout")
    args = parser.parse_args()
    result = evidence_audit()
    text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print(f"{output}: {result['claims']} authored claims, {len(result['failures'])} mismatches")
    else:
        print(text, end="")
    return 1 if args.check and result["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
