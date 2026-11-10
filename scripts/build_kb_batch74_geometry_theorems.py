#!/usr/bin/env python3
"""Four teacher-only original Euclidean-space criterion review packets.

Bounded exact-coordinate witnesses are NOT universal theorem certification.
Original written proofs require independent mathematics/teacher review.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
from pathlib import Path
import json
import build_kb_batch74_unmarked_review as U

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "curriculum/highschool_math/kb_batch74_spatial_criteria_teacher_drafts.json"
P29_ID = "KB73-P029-L001-008"
REVIEW = U.OUTPUT

THEOREMS = [
 dict(id="KB74-SP-01", name="直线与平面平行的判定",
  prerequisites=["平面与其方向空间","平行直线","直线与平面位置关系"],
  assumptions=[
   "欧氏三维空间中给定平面α、直线a、直线b。",
   "b包含于α，a不包含于α，且a与b为不同的平行直线（方向向量共线）。"],
  statement="在上述前提下，a与α无公共点，因此a平行于α。",
  proof_steps=[
   "设u为a、b共同的非零方向向量。因为b包含于α，u是α的一个方向向量。",
   "反设存在点X既属于a又属于α。因a上的点相差的向量为u的倍数，a上任一点R满足R=X+tu，仍属于α。",
   "这与a不包含于α矛盾。所以a与α没有交点，即a∥α。"],
  boundary="“a不包含于α”不能省略；只说方向平行不能区分直线含于平面与直线在平面外。",
  counterexample="α为z=0，b为x轴，a=b：a与b方向平行，但a包含于α，并非与α无交点。",
  common_error="仅凭方向相同直接宣布a∥α，遗漏a可能就在α中。",
  hints=["先判断直线是否可能落在平面内。","若有交点，平面中的方向向量加法会推出什么？","尝试用反证法排除a与α相交。"],
  examples=[
   "α:z=0，b=(t,0,0)，a=(t,1,2)，由b在α且a在α外得a∥α。",
   "α:y=0，b=(0,0,t)，a=(1,3,t)，因此a∥α。"],
  near_transfer="把α写成2x+y-z=0，用法向量检查方向且检查起点不在平面。",
  far_transfer="在三维建筑模型中判断一根梁与墙面平行时，为什么只看梁的方向不够？"
 ),
 dict(id="KB74-SP-02", name="两平面平行的判定",
  prerequisites=["平面平行","两相交直线确定平面","平面法向量"],
  assumptions=[
   "给定不同平面α、β，α内有相交于P的两条不同直线a、b。",
   "a、b均与β无公共点（各自严格平行于β）。"],
  statement="在上述前提下，平面α与平面β无公共点，故α∥β。",
  proof_steps=[
   "取a、b非零方向向量u、v；因两线相交而不同，u、v线性无关，张成α的整个方向空间。",
   "设n为β的法向量。a、b分别与β平行，故n·u=0及n·v=0。",
   "α内任何方向w=su+tv均满足n·w=0，所以α与β的法向量共线，两平面平行或重合。",
   "a、b与β无交点，α不可能与β重合；因此只能是两平面无交点。"],
  boundary="两条直线须在同一平面内且相交。若它们平行，方向不能张成平面。",
  counterexample="β:z=0，α:xz平面（y=0），选α内z=1与z=2的两条沿x方向的平行直线；两线都不交β，但α与β相交。",
  common_error="把“两条相交直线”偷换成“任意两条直线”，会使方向维数降为1。",
  hints=["想想两个方向能否张成整个平面。","为什么相交条件排除了共线方向？","用法向量及重合情形完成结论。"],
  examples=[
   "α:z=2，β:z=0，α内交于(0,0,2)的x、y方向直线均与β平行。",
   "α:y=3，β:y=0，α内交于(0,3,0)的x、z方向直线均与β平行。"],
  near_transfer="如果已知α内两条直线不相交，构造两平面不平行的例子。",
  far_transfer="验证两块平行平台时，如何利用两组独立方向的水平梁来确保平面不倾斜？"
 ),
 dict(id="KB74-SP-03", name="直线与平面垂直的判定",
  prerequisites=["方向向量点积","不共线向量张成平面","线面垂直定义"],
  assumptions=[
   "平面α内有两条相交直线b、c，其非零方向向量u、v线性无关。",
   "直线a的方向向量t与u、v均垂直（t·u=t·v=0）。"],
  statement="在上述前提下，直线a的方向垂直于α内任一方向，因此a⊥α。",
  proof_steps=[
   "b、c相交且不同，u、v线性无关；由空间平面方向性质，α内任一方向w可以表示为su+tv。",
   "由点积线性性，t·w=s(t·u)+t(t·v)=0。",
   "因此a与α内每个方向均成直角，按线面垂直的方向定义，有a⊥α。"],
  boundary="只垂直于同一平面内两条平行直线不足以推出线面垂直。若要求相交型线线垂直，可令a、b、c共过交点。",
  counterexample="α:z=0，b与c是两条平行于x轴的不同直线，a为y轴；a方向同时垂直两条线的方向，却处于α内而不垂直α。",
  common_error="把两条不同直线误当作两个独立方向，遗漏相交（不平行）条件。",
  hints=["平面中任一方向怎样由两个不共线向量表示？","利用点积的线性性推广两次垂直。","独立性条件为何关键？"],
  examples=[
   "α:z=0，b为x轴、c为y轴，a为z轴，a⊥α。",
   "α:y=0，b为x轴、c为z轴，a为y轴，a⊥α。"],
  near_transfer="若只给一条线垂直于a，找出与a不垂直的另一个平面方向。",
  far_transfer="三维机器人姿态估计中，怎样用两个独立的平面切向基向量检测表面法线？"
 ),
 dict(id="KB74-SP-04", name="两平面垂直的判定",
  prerequisites=["平面法向量","线面垂直","面面夹角"],
  assumptions=[
   "α和β是欧氏三维空间中的平面。",
   "α包含一条直线a，且a垂直于平面β。"],
  statement="在上述前提下，α与β相交成直二面角，即α⊥β。",
  proof_steps=[
   "令t为a的非零方向向量，nβ为β的法向量。a⊥β意味着t与nβ共线。",
   "由于a包含在α中，t属于α的方向空间，因而α的法向量nα与t垂直。",
   "于是nα·nβ=0。两法向量垂直，平面夹角为直角；α与β垂直。"],
  boundary="“包含垂直于β的直线”不能误写为“包含平行于β的直线”。",
  counterexample="α:z=1、β:z=0，α包含沿x方向的直线且该线平行β，但α与β平行而非垂直。",
  common_error="仅检验α内一条线平行β便推出面面垂直，把平行和垂直颠倒。",
  hints=["先把线面垂直改写为方向与法向量平行。","α内任意方向与α法向量有何关系？","两法向量点积为0说明什么？"],
  examples=[
   "β:z=0，α:x=0含z轴，故α⊥β。",
   "β:y=0，α:z=0含y轴，故α⊥β。"],
  near_transfer="改变α为z=2，检验为什么结论不再成立。",
  far_transfer="建筑转角设计中如何通过一个竖直边方向判断两片墙板是否正交？"
 )
]
# Every fixture is an integer-coordinate exact witness for the specific rule.
# It is not a proof of the general theorem.
# plane = (normal, offset), line = (point, direction).
FIXTURES = [
 dict(rule="LINE_PLANE", plane=([0,0,1],0),
      refs=[([0,0,0],[1,0,0])], line=([0,1,2],[1,0,0]),
      bad=([0,0,0],[1,0,0])),
 dict(rule="PLANES", plane=([0,0,1],0),
      refs=[([0,0,2],[1,0,0]),([0,0,2],[0,1,0])],
      bad=[([0,0,1],[1,0,0]),([0,0,2],[1,0,0])]),
 dict(rule="LINE_PERP", plane=([0,0,1],0),
      refs=[([0,0,0],[1,0,0]),([0,0,0],[0,1,0])],
      line=([0,0,0],[0,0,1]),
      bad=([0,0,0],[0,1,0])),
 dict(rule="PLANES_PERP", plane=([0,0,1],0),
      # α:x=0 -> normal [1,0,0], contained a along z.
      other_normal=[1,0,0], other_offset=0, line=([0,0,0],[0,0,1]),
      bad_other_normal=[0,0,1], bad_other_offset=1, bad_line=([0,0,1],[1,0,0])),
]

def exact_scalar(value):
    # Reject floats even if a binary float happens to equal an integer.
    # These fixtures are finite rational *witnesses*, not approximate measurements.
    if isinstance(value, bool) or not isinstance(value, (int, F)):
        raise ValueError("exact coordinates must be integer or Fraction")
    return F(value)


def vector3(a):
    if not isinstance(a, (tuple, list)) or len(a) != 3:
        raise ValueError("requires a 3D vector; no zip truncation")
    return tuple(exact_scalar(v) for v in a)


def dot(a, b):
    x, y = vector3(a), vector3(b)
    return sum(u * v for u, v in zip(x, y))


def cross(a, b):
    a, b = vector3(a), vector3(b)
    return (a[1]*b[2]-a[2]*b[1],
            a[2]*b[0]-a[0]*b[2],
            a[0]*b[1]-a[1]*b[0])


def nonzero(a):
    return any(vector3(a))


def in_plane(pt, plane):
    n, d = plane
    return dot(pt, n) == exact_scalar(d)


def evaluates(rule, fixture, invalid=False):
    # Malformed geometric evidence must never count as a verified witness.
    try:
        return _evaluate_strict(rule, fixture, invalid)
    except (ValueError, TypeError, IndexError, KeyError, ZeroDivisionError):
        return False


def _evaluate_strict(rule, fixture, invalid=False):
    p=(fixture["plane"][0],fixture["plane"][1])
    # Reject malformed offsets even when a particular rule only needs normals.
    exact_scalar(p[1])
    if not nonzero(p[0]): return False
    if rule=="LINE_PLANE":
        point,direction=fixture["bad" if invalid else "line"]
        bp,bd=fixture["refs"][0]
        return (in_plane(bp,p) and dot(bd,p[0])==0
                and not in_plane(point,p) and
                nonzero(bd) and nonzero(direction)
                and not nonzero(cross(direction,bd)))
    if rule=="PLANES":
        a,b=fixture["bad" if invalid else "refs"]
        (ap,ad),(bp,bd)=a,b
        return (not in_plane(ap,p) and not in_plane(bp,p) and
                dot(ad,p[0])==dot(bd,p[0])==0 and
                nonzero(cross(ad,bd)) and
                dot([bp[i]-ap[i] for i in range(3)],cross(ad,bd))==0)
    if rule=="LINE_PERP":
        d=fixture["bad" if invalid else "line"][1]
        a,b=fixture["refs"]
        return (in_plane(a[0],p) and in_plane(b[0],p) and
                nonzero(cross(a[1],b[1])) and
                dot(a[1],p[0])==dot(b[1],p[0])==0 and
                dot(d,a[1])==dot(d,b[1])==0 and nonzero(d))
    if rule=="PLANES_PERP":
        other=fixture["bad_other_normal" if invalid else "other_normal"]
        other_offset=fixture["bad_other_offset" if invalid else "other_offset"]
        line=fixture["bad_line" if invalid else "line"]
        return (nonzero(other) and nonzero(line[1]) and in_plane(line[0],(other,other_offset)) and
                dot(other,line[1])==0 and
                not nonzero(cross(line[1],p[0])) and dot(other,p[0])==0)
    raise ValueError(rule)

def build():
    review=U.B73.load(REVIEW)
    assert review["schema_version"]=="kb74-56-unanchored-editorial-v1"
    source=next(x for x in review["records"] if x["segment_id"]==P29_ID)
    assert source["classification"]=="MIXED_REQUIRES_SPLIT"
    for j,(t,f) in enumerate(zip(THEOREMS,FIXTURES)):
        assert t["id"]==f"KB74-SP-{j+1:02d}"
        assert evaluates(f["rule"],f), f"wrong valid exact witness {t['id']}"
        assert not evaluates(f["rule"],f,invalid=True), f"invalid witness accepted {t['id']}"
        assert len(t["assumptions"])>=2 and len(t["proof_steps"])>=3
        assert len(t["examples"])==2 and len(t["hints"])==3
        assert all(t.get(k) for k in ("boundary","counterexample","common_error",
                            "near_transfer","far_transfer","statement","name","prerequisites"))
    return dict(
        schema_version="kb74-spatial-criterion-v1",
        source_pdf_sha256=U.PDF_SHA,
        source_segment_id=P29_ID,
        source_span_sha256=source["span_sha256"],
        teacher_review="REVIEW_PENDING",
        distribution="TEACHER_ONLY",
        mathematical_certification="NOT_FORMALLY_CERTIFIED",
        finite_witness_status="EXACT_COORDINATE_FIXTURES_ONLY",
        official_curriculum_atom_count=None,
        student_publishable=False,
        proof_packets=THEOREMS,
        exact_valid_fixtures=4,
        exact_invalid_fixtures=4,
    )

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    x=build()
    encoded=json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if a.check:
        assert TARGET.read_text(encoding="utf8")==encoded,"geometry draft out of date"
    else:
        TARGET.write_text(encoded,encoding="utf8")
    print(f"Batch74 4 geometry theorem review packets / 8 exact finite fixtures; official approvals=0")

if __name__=="__main__":
    main()
