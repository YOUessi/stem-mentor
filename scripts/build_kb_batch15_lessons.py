#!/usr/bin/env python3
"""Render project-authored Batch15 draft lessons with exact byte-level source checks."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"curriculum/highschool_math/author_draft_batch15.json"
OUT=ROOT/"knowledge/deep/v1/elective_a_b_advanced_batch15.json"
def render():
    rows=json.loads(SOURCE.read_text(encoding="utf-8"))
    if len(rows)!=9 or len({r["id"] for r in rows})!=9:
        raise ValueError("Need nine unique authored proof drafts")
    if any(r["review"]["status"]!="REVIEW_PENDING" or r["teacher_solution_visibility"]!="TEACHER_ONLY" for r in rows):
        raise ValueError("Student authority forbidden without real review")
    return json.dumps(rows,ensure_ascii=False,indent=2)+"\n"
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    args=p.parse_args(); data=render()
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf8")!=data:
            raise AssertionError("Batch15 source/render mismatch")
    else: OUT.write_text(data,encoding="utf8")
    print("PASS Batch15 9 authored lessons",args.check)
if __name__=="__main__":main()
