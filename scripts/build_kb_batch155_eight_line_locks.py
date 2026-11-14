#!/usr/bin/env python3
"""Reconcile the eight historical editorial drafts lacking immutable per-line hashes.

--check: offline trust chain from frozen original candidate source span and
committed per-line digests, does NOT simulate reopening a licensed PDF.
--check-mac: on authorized Mac, real PDFKit source pages independently rehashed.
No original curriculum source text is committed or printed.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch154_lessons as old
OUT=ROOT/"curriculum/highschool_math/kb155_missing_eight_pdfkit_line_locks.json"
SRC=ROOT/"docs/evaluation/KB_BATCH154_DEPTH_AUDIT.json"
PROPOSALS=ROOT/"curriculum/highschool_math/k00_batch133_atomic_proposals.json"
HASH=re.compile(r"^[0-9a-f]{64}$")
# Pinned canonical digest of eight actual Mac PDFKit per-line hashes. Distinguishes
# offline CI integrity from a false claim of reopening the original PDF in CI.
FROZEN_EIGHT_LINE_DIGEST="31141336e2d0f844e35efbc0740bcd8a41f889e6b17d4fd1de1bc21a6b502b80"

def need(ok,why):
    if not ok:raise ValueError("KB155 eight-line-lock: "+why)
def encode(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,indent=2,allow_nan=False)+"\n"
def missing_eight():
    # Compact 145-entry review audit has null source_sha for 41 provisional
    # proposals, while 8 other teacher drafts preserve only a source span hash.
    from app.kb_batch154_index import load
    proposal_ids={r["id"] for r in json.loads(PROPOSALS.read_text())["records"]}
    missing=[]
    for row in load():
        if row.get("source_line_sha256") or (row.get("source_line_lock") or {}).get("line_sha256"):
            continue
        candidate=row.get("source_candidate_id",row.get("candidate_id"))
        if candidate not in proposal_ids:
            missing.append(row)
    need(len(missing)==8,"expected exactly eight nonprovisional source-line gaps")
    return sorted(missing,key=lambda r:r["id"])
def original_pages():
    # Identical, already-reviewed private PDFKit loader used by earlier batches.
    from build_kb_batch126_context_evidence import source_pages
    return source_pages()
def generate(*,mac):
    need(mac,"fresh per-line SHA requires Mac original source replay")
    pages=original_pages()
    contexts=old.contexts()
    rows=[]
    for draft in missing_eight():
        cid=draft.get("source_candidate_id",draft.get("candidate_id"))
        need(cid in contexts, "missing original source locator "+cid)
        source=contexts[cid]["source"]
        page=source["printed_page"];start=source["start_line"];end=source["end_line"]
        original=pages[page][start-1:end]
        need(len(original)==end-start+1 and original,"missing source lines "+cid)
        per_line=[hashlib.sha256(x.encode("utf-8")).hexdigest() for x in original]
        span=hashlib.sha256("\n".join(original).encode("utf-8")).hexdigest()
        need(span==source["source_span_sha256"]==draft["source_span_sha256"],
             "ORIGINAL PDF SOURCE HASH MISMATCH "+cid)
        need(source["original_pdf_sha256"]==draft["source_pdf_sha256"],
             "PDF version changed "+cid)
        rows.append(dict(draft_id=draft["id"],source_candidate_id=cid,
           course_track=draft["course_track"],printed_page=page,start_line=start,
           end_line=end,source_pdf_sha256=draft["source_pdf_sha256"],
           source_span_sha256=span,source_line_sha256=per_line,
           evidence_status="MAC_PDFKIT_REHASHED_EDITORIAL_SEMANTICS_PENDING",
           formal_general_proof_certified=False,teacher_review="REVIEW_PENDING",
           student_authoritative=False))
    return dict(schema="kb155-eight-historical-line-lock-reconciliation/1",
        locks=rows,original_mac_rehash_complete=True,
        teacher_approved=0,student_authoritative=0,official_atom_denominator=None)
def validate(x):
    need(x["schema"]=="kb155-eight-historical-line-lock-reconciliation/1" and
         x["original_mac_rehash_complete"] is True and
         x["teacher_approved"]==x["student_authoritative"]==0 and
         x["official_atom_denominator"] is None,"forged release")
    rows=x["locks"]
    minimal=[{"draft_id":r["draft_id"],"line_sha256":r["source_line_sha256"]} for r in rows]
    digest=hashlib.sha256(json.dumps(minimal,sort_keys=True,separators=(",",":"),
           ensure_ascii=False).encode("utf-8")).hexdigest()
    need(digest==FROZEN_EIGHT_LINE_DIGEST,"frozen Mac original line hashes have been altered")
    need(len(rows)==8 and len({r["draft_id"] for r in rows})==8,"eight gap count")
    expected={r["id"]:r for r in missing_eight()}
    ctx=old.contexts()
    need(set(expected)=={r["draft_id"] for r in rows},"draft/lock disagreement")
    for r in rows:
        d=expected[r["draft_id"]];c=r["source_candidate_id"];s=ctx[c]["source"]
        need(c==d.get("source_candidate_id",d.get("candidate_id")) and
            r["course_track"]==d["course_track"] and
            r["printed_page"]==s["printed_page"] and
            r["start_line"]==s["start_line"] and r["end_line"]==s["end_line"] and
            r["source_span_sha256"]==s["source_span_sha256"]==d["source_span_sha256"] and
            r["source_pdf_sha256"]==s["original_pdf_sha256"] and
            len(r["source_line_sha256"])==r["end_line"]-r["start_line"]+1 and
            all(HASH.fullmatch(v) for v in r["source_line_sha256"]) and
            not r["formal_general_proof_certified"] and
            not r["student_authoritative"] and
            r["teacher_review"]=="REVIEW_PENDING","malformed eight source locks")
    return True
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    p.add_argument("--check-mac",action="store_true")
    a=p.parse_args()
    if not a.check and not a.check_mac:
        v=generate(mac=True);validate(v);OUT.write_text(encode(v),encoding="utf-8")
    else:
        need(OUT.is_file(),"frozen eight hash record missing")
        v=json.loads(OUT.read_text(encoding="utf-8"));validate(v)
        if a.check_mac:need(v==generate(mac=True),"private original PDFKit line rehash drift")
    print("KB155: eight missing source-line locks reconciled; source semantics/teacher review pending.")
if __name__=="__main__":main()
