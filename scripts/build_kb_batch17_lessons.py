#!/usr/bin/env python3
"""Render Batch17 author's 11 drafts, preserving teacher-only unapproved state."""
from pathlib import Path
import sys,json,argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.deep_knowledge import DeepLesson
SRC=ROOT/"curriculum/highschool_math/author_draft_batch17.json"
OUT=ROOT/"knowledge/deep/v1/cross_track_batch17.json"
def render():
    raw=json.loads(SRC.read_text(encoding="utf8"))
    if len(raw)!=11 or len({x["id"] for x in raw})!=11:raise ValueError("11 distinct drafts expected")
    for r in raw:
        obj=DeepLesson.model_validate(r)
        if obj.review.status!="REVIEW_PENDING" or obj.teacher_solution_visibility!="TEACHER_ONLY" or len(obj.worked_examples)!=2:
            raise ValueError("Unsafe lesson or missing worked examples")
    return json.dumps(raw,ensure_ascii=False,indent=2)+"\n"
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
    content=render()
    if a.check:
        if not OUT.is_file() or OUT.read_text(encoding="utf8")!=content:
            raise AssertionError("Batch17 author/knowledge render mismatch")
    else:OUT.write_text(content,encoding="utf8")
    print("PASS 11 unapproved Batch17 drafts; check=",a.check)
if __name__=="__main__":main()
