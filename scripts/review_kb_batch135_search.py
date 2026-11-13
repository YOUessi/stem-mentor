#!/usr/bin/env python3
"""Local-only, explicit editor review search over 22 pending manuscripts."""
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.kb_batch135_index import public_coverage,editor_preview_search
p=argparse.ArgumentParser()
p.add_argument("query",nargs="?")
p.add_argument("--track")
z=p.parse_args()
if z.query:
    print(json.dumps(editor_preview_search(z.query,scope="EDITOR_LOCAL",track=z.track),
                     ensure_ascii=False,indent=2))
else: print(json.dumps(public_coverage(),ensure_ascii=False,indent=2))
