#!/usr/bin/env python3
"""Render 12 independently authored B/C/D/E proof drafts, fail closed on edits."""
from pathlib import Path
import argparse,json
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"curriculum/highschool_math/author_draft_batch16.json"
OUT=ROOT/"knowledge/deep/v1/elective_b_c_d_e_batch16.json"

def render():
    items=json.loads(SRC.read_text(encoding="utf8"))
    if len(items)!=12 or len({r["id"] for r in items})!=12:
        raise ValueError("Expected 12 unique deep authored drafts")
    if any(r["kind"]!="theorem" or r["review"]["status"]!="REVIEW_PENDING"
           or r["teacher_solution_visibility"]!="TEACHER_ONLY"
           or r["provenance"]["kind"]!="PROJECT_AUTHORED"
           or len(r["proof_steps"])<3 or len(r["worked_examples"])!=2 for r in items):
        raise ValueError("Math proof drafts cannot bypass review/visibility/structure gate")
    return json.dumps(items,ensure_ascii=False,indent=2)+"\n"

def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
    content=render()
    if a.check:
        if not OUT.is_file() or OUT.read_text(encoding="utf8")!=content:
            raise AssertionError("Batch16 source/render mismatch")
    else:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(content,encoding="utf8")
    print("PASS batch16 12 editorial draft lessons; check=",a.check)
if __name__=="__main__":main()
