#!/usr/bin/env python3
"""Batch60 partial original source leads, not teacher-validated official atoms."""
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
C=ROOT/"curriculum/highschool_math"
R=ROOT/"docs/evaluation"
SEED=C/"k00_batch60_elective_source_spans.tsv"
SNAP=C/"k00_batch60_pdfkit_span_attestations.json"
PAGE=C/"k00_batch51_pdfkit_page_fingerprints.json"
PREV=R/"KB_BATCH59_SELECTIVE_SOURCE_SPAN_REVIEW.json"
OUT=R/"KB_BATCH60_ELECTIVE_SOURCE_REVIEW.json"
MD=R/"KB_BATCH60_ELECTIVE_SOURCE_REVIEW.md"
PDF_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
KINDS=("CONTENT","SCOPE_POLICY","TRACK_BOUNDARY","SYLLABUS_TABLE","TEACHING_GUIDANCE","ASSESSMENT_REQUIREMENT","ACTIVITY_REQUIREMENT","LOCAL_DEFINED_SCOPE")
COMPETENCY_KINDS={"TEACHING_GUIDANCE","ASSESSMENT_REQUIREMENT","ACTIVITY_REQUIREMENT"}
PAGES=set([13,14]+list(range(51,74)))

def require(ok,reason):
    if not ok: raise ValueError(reason)

def load(p): return json.loads(Path(p).read_text(encoding="utf8"))

def seeds():
    out=[]
    for line in SEED.read_text(encoding="utf8").splitlines():
        if not line or line.startswith("#"):continue
        parts=line.split("|")
        require(len(parts)==7,"source field count incorrect")
        p,a,b,track,kind,paraphrase,guard=parts
        require(p.isdecimal() and a.isdecimal() and b.isdecimal(),"invalid source coordinate")
        out.append(dict(page=int(p),start=int(a),end=int(b),track=track,kind=kind,paraphrase=paraphrase,guard=guard))
    return out

def key(s): return f"P{s['page']:03d}-L{s['start']:03d}-{s['end']:03d}"

def track_of(p,a,b):
    if p in (13,14):return "COMPULSORY"
    if p==51 and b<20:return "ELECTIVE_GENERAL"
    if 51<=p<=57 and (p!=57 or b<16):
        require(p!=51 or a>=20,"A boundary crossed")
        return "ELECTIVE_A"
    if 57<=p<=64 and (p!=64 or b<10):
        require(p!=57 or a>=16,"B boundary crossed")
        return "ELECTIVE_B"
    if 64<=p<=69 and (p!=69 or b<6):
        require(p!=64 or a>=10,"C boundary crossed")
        return "ELECTIVE_C"
    if 69<=p<=73 and (p!=73 or b<13):
        require(p!=69 or a>=6,"D boundary crossed")
        return "ELECTIVE_D"
    require(p==73 and a>=13,"E boundary crossed")
    return "ELECTIVE_E"

def attest(pdf,source_dir):
    pdf,source_dir=Path(pdf),Path(source_dir)
    require(pdf.is_file() and sha256(pdf.read_bytes()).hexdigest()==PDF_SHA,"official PDF SHA drift")
    page_data=load(PAGE)
    by_page={v["printed_page"]:v for v in page_data["pages"]}
    require(set(by_page)==set(range(13,74)),"61 source pages absent")
    lines={}
    for p in range(13,74):
        path=source_dir/f"kb56_page_{p}.txt"
        require(path.is_file(),"PDFKit page missing")
        raw=path.read_bytes()
        require(sha256(raw).hexdigest()==by_page[p]["pdfkit_text_sha256"],"PDFKit page SHA mismatch")
        lines[p]=raw.decode("utf8").splitlines()
    hashes={}
    for s in seeds():
        p,a,b=s["page"],s["start"],s["end"]
        require(p in PAGES and 1<=a<=b<=len(lines[p]),"PDFKit span outside page")
        require(key(s) not in hashes,"duplicate source digest coordinates")
        hashes[key(s)]=sha256("\n".join(lines[p][a-1:b]).encode("utf8")).hexdigest()
    return dict(schema_version="kb60-source-digests-v1",pinned_pdf_sha256=PDF_SHA,
                source_passages_or_pdf_committed=False,full_page_human_review_certified=False,
                attestations=dict(sorted(hashes.items())))

def build(rows=None,snapshot=None,previous=None):
    rows=deepcopy(seeds() if rows is None else rows)
    snapshot=deepcopy(load(SNAP) if snapshot is None else snapshot)
    previous=deepcopy(load(PREV) if previous is None else previous)
    page_data=load(PAGE)
    pd={v["printed_page"]:v for v in page_data["pages"]}
    require(page_data["official_pdf_sha256"]==PDF_SHA and len(pd)==61,"source page baseline changed")
    require(previous["new_nonunique_source_spans"]==108 and previous["combined_nonunique_source_spans"]==238 and previous["partially_annotated_pages_combined"]==list(range(15,51)),"previous source baseline changed")
    require(previous["teacher_approved"]==previous["student_published"]==0 and all(v is None for v in previous["official_atomic_denominator"].values()),"prior teacher approval/denominator forged")
    require(snapshot["pinned_pdf_sha256"]==PDF_SHA and not snapshot["source_passages_or_pdf_committed"] and not snapshot["full_page_human_review_certified"],"source attestation provenance forged")
    require(len(rows)==len(snapshot["attestations"])==106,"source record count changed")
    seen=set(); pages=Counter(); tracks=Counter(); kinds=Counter(); built=[]; competencies=[]
    for s in rows:
        p,a,b=s["page"],s["start"],s["end"]
        require(p in PAGES and 1<=a<=b<=100,"source coordinates invalid")
        require(s["track"]==track_of(p,a,b),"incorrect elective track")
        require(s["kind"] in KINDS,"source kind not supported")
        require(20<=len(s["paraphrase"])<=190 and "|" not in s["paraphrase"] and "\n" not in s["paraphrase"],"editorial paraphrase missing")
        require(bool(re.fullmatch(r"[A-Z][A-Z0-9_]{7,83}",s["guard"])),"mathematical/policy guard missing")
        require(s["kind"]!="LOCAL_DEFINED_SCOPE" or s["track"]=="ELECTIVE_E","school-defined elective scope forged")
        require(s["kind"]!="TRACK_BOUNDARY" or (p,a) in ((51,20),(57,16),(64,10),(69,6),(73,13)),"elective boundary forged")
        require(s["kind"]!="SYLLABUS_TABLE" or p in (13,14),"syllabus table location forged")
        k=key(s)
        require(k not in seen,"duplicate source span")
        seen.add(k)
        digest=snapshot["attestations"].get(k)
        require(isinstance(digest,str) and re.fullmatch(r"[a-f0-9]{64}",digest),"source span unattested")
        page=pd[p]
        require(page["pdf_page_index"]==p+7 and page["full_page_human_review"]=="PENDING","page approval forged")
        pages[p]+=1;tracks[s["track"]]+=1;kinds[s["kind"]]+=1
        r=dict(candidate_id=f"KB60-P{p:03d}-R{pages[p]:03d}",source_span_id=k,
               printed_page=p,pdf_page_index=p+7,track=s["track"],source_kind=s["kind"],
               original_editorial_paraphrase=s["paraphrase"],mathematical_or_policy_guard=s["guard"],
               source_pdf_sha256=PDF_SHA,source_page_pdfkit_sha256=page["pdfkit_text_sha256"],
               source_span_pdfkit_sha256=digest,source_lead_is_not_atomic_coverage=True,
               same_topic_is_not_mathematical_equivalence=True,
               nationally_compulsory=False if s["track"].startswith("ELECTIVE") else None,
               requirement_coverage_status="UNMAPPED" if s["kind"] in COMPETENCY_KINDS else "NOT_CLAIMED",
               teacher_review="REVIEW_PENDING",full_page_human_review="PENDING",
               cross_page_mathematical_deduplication="PENDING",official_atom_certified=False,
               formal_general_proof_certified=False,student_publishable=False)
        built.append(r)
        if s["kind"] in COMPETENCY_KINDS:
            competencies.append(dict(candidate_id=r["candidate_id"],source_span_id=k,
                                     status="UNMAPPED",teacher_review="REVIEW_PENDING",
                                     linked_approved_assessments=[]))
    require(set(pages)==PAGES,"some source page lacks a partial location")
    require(seen==set(snapshot["attestations"]),"extra or missing source attestation")
    require(sum(r["source_kind"]=="TRACK_BOUNDARY" for r in built)==5,"not exactly five elective scope boundaries")
    require(set(tracks)=={"COMPULSORY","ELECTIVE_GENERAL","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E"},"scope tracks missing")
    require(all(r["source_kind"] in ("TRACK_BOUNDARY","LOCAL_DEFINED_SCOPE") for r in built if r["track"]=="ELECTIVE_E"),"E fixed curriculum invented")
    combined=sorted(set(previous["partially_annotated_pages_combined"])|PAGES)
    require(combined==list(range(13,74)),"all 61 pages must be partly located")
    return dict(schema_version="kb60-partial-source-leads-v1",
                status="SOURCE_LEADS_ONLY_NOT_OFFICIAL_ATOMS",
                source_pages_total=61,pages_newly_partially_located=sorted(PAGES),
                pages_partially_located_combined=combined,previous_nonunique_source_leads=238,
                new_nonunique_source_leads=len(built),combined_nonunique_source_leads=238+len(built),
                counts_by_track=dict(sorted(tracks.items())),counts_by_kind=dict(sorted(kinds.items())),
                counts_per_page={str(k):v for k,v in sorted(pages.items())},
                official_atomic_denominator={k:None for k in TRACKS},
                official_full_reviewed_pages=0,teacher_approved=0,student_published=0,
                source_passages_or_pdf_committed=False,local_defined_e_is_not_fixed_national_scope=True,
                historical_unverified_proof_steps=538,unresolved_math_conflicts=10,
                new_noncontent_requirement_queue=competencies,pinned_pdf_sha256=PDF_SHA,rows=built)

def render(d):
    lines=["# STEM Mentor Batch60｜选修与缺失页面课程来源定位（部分审查）","",
           "这不是官方完整原子分母，也不是经过教师批准的教学知识。",
           "",f"新增 {d['new_nonunique_source_leads']} 条非去重来源线索，累计 {d['combined_nonunique_source_leads']} 条。",
           "61/61 页仅完成部分定位；全页教师核实为 0/61；七轨正式原子分母均为 null。",
           "选修 E 根据学校开设课程确定范围，不能虚构全国固定分母。",
           f"非内容能力/活动要求 {len(d['new_noncontent_requirement_queue'])} 项仍未映射。",
           "538 步历史证明未获形式认证，10 项数学冲突未解决；教师批准和学生正式发布均为 0。",
           "","## 课程范围定位（未去重）"]
    lines += [f"- {k}: {v}" for k,v in d["counts_by_track"].items()]
    lines += ["","## 页面定位（局部）"]
    lines += [f"- 印刷第{p}页：{v}条；全页教师原子审校 PENDING" for p,v in d["counts_per_page"].items()]
    lines += ["","## 下一步","逐页核对表格和图像证据，完成跨页等价去重及教师审校后才能计算正式知识原子分母。",""]
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--attest",action="store_true");p.add_argument("--write",action="store_true")
    p.add_argument("--check",action="store_true");p.add_argument("--verify-source-pdf")
    p.add_argument("--source-dir",default="/private/tmp")
    args=p.parse_args()
    if args.attest:
        require(args.verify_source_pdf is not None,"source PDF required to attest")
        SNAP.write_text(json.dumps(attest(args.verify_source_pdf,args.source_dir),ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf8")
    if args.verify_source_pdf:
        require(attest(args.verify_source_pdf,args.source_dir)==load(SNAP),"source attestation SHA mismatch")
    d=build(); j=json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2)+"\n";m=render(d)
    if args.write:
        OUT.write_text(j,encoding="utf8");MD.write_text(m,encoding="utf8")
    if args.check:
        require(OUT.read_text(encoding="utf8")==j,"generated JSON mismatch")
        require(MD.read_text(encoding="utf8")==m,"generated Markdown mismatch")
    print("Batch60 source leads",len(d["rows"]),"partial pages",len(d["pages_partially_located_combined"]),"full review 0/61")

if __name__=="__main__":main()
