#!/usr/bin/env python3
"""Review-pending *editorial suggestions* connecting sampled standards objectives to draft lessons.

Never upgrades learning objectives, lesson proofs, or teacher approval. No fuzzy
matching: every suggested association is an explicit project-authored editorial
candidate, and its exact source/object lesson bytes are integrity-pinned.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.standard_scope import source_inventory
from app.deep_knowledge import lessons

OUT = ROOT / "curriculum/highschool_math/objective_lesson_proposals_batch13.json"

# Keys are Batch12 ORIGINAL objectives, not official numbered clauses.
# Zero matching entries means not yet proposed, NOT "content not in curriculum".
MATCHES = {
    "COMPULSORY-001": ("math.hs.sets.representations",),
    "COMPULSORY-003": ("math.hs.sets.union-intersection", "math.hs.sets.de-morgan-laws"),
    "COMPULSORY-004": ("math.hs.logic.implication",),
    "COMPULSORY-005": ("math.hs.logic.quantifier",),
    "COMPULSORY-006": ("math.hs.inequality.transformation-obligations",),
    "COMPULSORY-007": ("math.hs.inequality.amgm",),
    "COMPULSORY-008": ("math.hs.quadratic.sign", "math.hs.quadratic.discriminant-roots"),
    "COMPULSORY-009": ("math.hs.function.domain", "math.hs.function.range"),
    "COMPULSORY-011": ("math.hs.function.piecewise",),
    "COMPULSORY-012": ("math.hs.function.monotonicity",),
    "COMPULSORY-013": ("math.hs.function.parity",),
    "COMPULSORY-014": ("math.hs.function.periodicity",),
    "COMPULSORY-015": ("math.hs.function.power-domain",),
    "COMPULSORY-017": ("math.hs.exponent.monotone",),
    "COMPULSORY-018": ("math.hs.logarithm.inverse",),
    "COMPULSORY-019": ("math.hs.logarithm.change-base", "math.hs.logarithm.product-law"),
    "COMPULSORY-020": ("math.hs.trig.radians-unit-circle",),
    "COMPULSORY-021": ("math.hs.trig.tangent-domain", "math.hs.trig.radians-unit-circle"),
    "COMPULSORY-022": ("math.hs.trig.reduction",),
    "COMPULSORY-023": ("math.hs.trig.pythagorean", "math.hs.trig.sum-angle", "math.hs.trig.double-angle-reduction"),
    "COMPULSORY-024": ("math.hs.trig.phase-transform",),
    "COMPULSORY-025": ("math.hs.function.bisection-root",),
    "COMPULSORY-026": ("math.hs.vector.free-coordinates", "math.hs.vector.linear-operations"),
    "COMPULSORY-027": ("math.hs.vector.dot-product",),
    "COMPULSORY-028": ("math.hs.triangle.sine-law", "math.hs.triangle.cosine-law", "math.hs.triangle.ssa-ambiguity"),
    "COMPULSORY-029": ("math.hs.complex.algebraic-basics", "math.hs.complex.operations"),
    "COMPULSORY-030": ("math.hs.space.polyhedron-types", "math.hs.space.solids-revolution"),
    "COMPULSORY-031": ("math.hs.space.parallel-perpendicular-criteria",),
    "COMPULSORY-032": ("math.hs.probability.sample-space-event",),
    "COMPULSORY-033": ("math.hs.probability.laplace",),
    "COMPULSORY-034": ("math.hs.probability.independence",),
    "COMPULSORY-035": ("math.hs.statistics.sampling",),
    "COMPULSORY-036": ("math.hs.statistics.simple-random-sampling",),
    "COMPULSORY-037": ("math.hs.statistics.variance", "math.hs.statistics.percentiles"),
    "COMPULSORY-038": ("math.hs.modeling.workflow",),
    "SELECTIVE_COMPULSORY-001": ("math.hs.sequence.recurrence",),
    "SELECTIVE_COMPULSORY-002": ("math.hs.sequence.arithmetic-nth-term", "math.hs.sequence.arithmetic-sum"),
    "SELECTIVE_COMPULSORY-003": ("math.hs.sequence.geometric-sum",),
    "SELECTIVE_COMPULSORY-004": ("math.hs.proof.induction",),
    "SELECTIVE_COMPULSORY-005": ("math.hs.calculus.derivative-definition",),
    "SELECTIVE_COMPULSORY-006": ("math.hs.calculus.power-rule", "math.hs.calculus.product-derivative"),
    "SELECTIVE_COMPULSORY-007": ("math.hs.calculus.chain-rule",),
    "SELECTIVE_COMPULSORY-008": ("math.hs.calculus.derivative-monotonicity", "math.hs.calculus.extrema"),
    "SELECTIVE_COMPULSORY-009": ("math.hs.calculus.extrema",),
    "SELECTIVE_COMPULSORY-010": ("math.hs.geometry.line-slope",),
    "SELECTIVE_COMPULSORY-011": ("math.hs.geometry.line-general",),
    "SELECTIVE_COMPULSORY-012": ("math.hs.geometry.line-relations",),
    "SELECTIVE_COMPULSORY-013": ("math.hs.geometry.point-line-distance",),
    "SELECTIVE_COMPULSORY-014": ("math.hs.geometry.circle-complete-square",),
    "SELECTIVE_COMPULSORY-015": ("math.hs.geometry.ellipse-focus",),
    "SELECTIVE_COMPULSORY-016": ("math.hs.geometry.parabola-focus", "math.hs.geometry.hyperbola-foci"),
    "SELECTIVE_COMPULSORY-017": ("math.hs.space.coordinate-distance",),
    "SELECTIVE_COMPULSORY-019": ("math.hs.geometry.space-dot",),
    "SELECTIVE_COMPULSORY-020": ("math.hs.space.line-plane-normal",),
    "SELECTIVE_COMPULSORY-021": ("math.hs.space.angle-distance",),
    "SELECTIVE_COMPULSORY-022": ("math.hs.geometry.circle-intersections",),
    "SELECTIVE_COMPULSORY-023": ("math.hs.geometry.conic-focal-directrix",),
    "SELECTIVE_COMPULSORY-024": ("math.hs.counting.product-rule",),
    "SELECTIVE_COMPULSORY-025": ("math.hs.counting.permutation-combination",),
    "SELECTIVE_COMPULSORY-026": ("math.hs.counting.binomial",),
    "SELECTIVE_COMPULSORY-027": ("math.hs.probability.multiplication",),
    "SELECTIVE_COMPULSORY-028": ("math.hs.probability.discrete-variable",),
    "SELECTIVE_COMPULSORY-029": ("math.hs.probability.binomial-distribution", "math.hs.probability.hypergeometric"),
    "SELECTIVE_COMPULSORY-030": ("math.hs.probability.normal-density",),
    "SELECTIVE_COMPULSORY-031": ("math.hs.statistics.correlation-regression",),
    "SELECTIVE_COMPULSORY-032": ("math.hs.statistics.chi-square",),
    # Elective examples are even more tentative: overlap is NOT sufficient coverage.
    # Batch14: explicit, unverified partial overlaps; never count as certified coverage.
    "ELECTIVE_A-001": ("math.hs.elective.sequence.epsilon-n",),
    "ELECTIVE_A-002": ("math.hs.elective.sequence.convergent-bounded",),
    "ELECTIVE_A-003": ("math.hs.elective.sequence.monotone-bounded",),
    "ELECTIVE_A-004": ("math.hs.elective.sequence.limit-sum-law",),
    "ELECTIVE_A-005": ("math.hs.elective.function.epsilon-delta-square",),
    "ELECTIVE_A-009": ("math.hs.elective.calculus.mean-value-theorem",),
    "ELECTIVE_A-011": ("math.hs.elective.calculus.riemann-linear-integral",),
    "ELECTIVE_A-012": ("math.hs.elective.calculus.ftc-integral-derivative",),
    "ELECTIVE_A-014": ("math.hs.elective.linear.standard-basis-independence",),
    "ELECTIVE_A-016": ("math.hs.elective.matrix.inverse-two-by-two",),
    "ELECTIVE_A-017": ("math.hs.elective.matrix.gaussian-row-equivalence",),
    "ELECTIVE_B-005": ("math.hs.elective.multivariable.partial-polynomial",),
    "ELECTIVE_B-011": ("math.hs.elective.statistics.bernoulli-mle",),
    "ELECTIVE_A-007": ("math.hs.elective.function.ivt-intermediate", "math.hs.function.zero-ivt",),
    "ELECTIVE_A-008": ("math.hs.elective.calculus.differentiable-continuous", "math.hs.calculus.derivative-definition",),
    "ELECTIVE_A-013": ("math.hs.extension.cross-product",),
    "ELECTIVE_A-018": ("math.hs.space.line-plane-normal",),
    "ELECTIVE_B-009": ("math.hs.probability.normal-density",),
    "ELECTIVE_B-010": ("math.hs.elective.statistics.covariance-affine", "math.hs.probability.variance-covariance",),
    "ELECTIVE_B-013": ("math.hs.statistics.correlation-regression","math.hs.elective.statistics.ols-two-parameter"),
    # Batch15: independent editorial suggestions; neither official coverage nor teacher proof review.
    "ELECTIVE_A-006": ("math.hs.elective.limit.sin-x-over-x",),
    "ELECTIVE_A-010": ("math.hs.elective.calculus.monotonicity-mvt",),
    "ELECTIVE_A-015": ("math.hs.elective.matrix.product-dimensions",),
    "ELECTIVE_B-006": ("math.hs.elective.multivariable.stationary-boundary",),
    "ELECTIVE_B-007": ("math.hs.elective.linear.rank-vectors",),
    "ELECTIVE_B-008": ("math.hs.elective.linear.cramer-three",),
    "ELECTIVE_B-012": ("math.hs.elective.statistics.pvalue-null",),
    "ELECTIVE_B-015": ("math.hs.elective.model.parametric-circle",),
    "ELECTIVE_C-001": ("math.hs.logic.implication",),
    "ELECTIVE_C-003": ("math.hs.modeling.inquiry-claim",),
    "ELECTIVE_C-010": ("math.hs.statistics.sampling",),
    "ELECTIVE_D-001": ("math.hs.geometry.ellipse-focus",),
    "ELECTIVE_D-003": ("math.hs.trig.phase-transform",),
    "ELECTIVE_D-005": ("math.hs.trig.wave-transformation",),
    "ELECTIVE_D-008": ("math.hs.vector.free-coordinates",),
    "ELECTIVE_D-009": ("math.hs.statistics.sampling",),
    "ELECTIVE_E-001": ("math.hs.modeling.workflow",),
    "ELECTIVE_E-003": ("math.hs.extension.algorithm-invariant",),
    "ELECTIVE_E-005": ("math.hs.modeling.workflow",),
    "ELECTIVE_E-007": ("math.hs.space.coordinate-distance",),
    "ELECTIVE_E-008": ("math.hs.probability.discrete-variable",),
    # Batch17: 11 new deep draft candidates plus two carefully bounded links
    # to EXISTING proofs, since duplicate content is not evidence of quality.
    "COMPULSORY-002": ("math.hs.sets.inclusion-empty-equality",),
    "COMPULSORY-010": ("math.hs.function.same-mapping-three-representations",),
    "COMPULSORY-016": ("math.hs.exponent.real-exponent-domain",),
    "SELECTIVE_COMPULSORY-018": ("math.hs.space.basis-three-unique",),
    "ELECTIVE_B-003": ("math.hs.elective.calculus.monotonicity-mvt",),
    "ELECTIVE_C-002": ("math.hs.elective.logic.classical-laws",),
    "ELECTIVE_C-004": ("math.hs.elective.logic.proof-strategies",),
    "ELECTIVE_C-005": ("math.hs.elective.logic.axiom-consistency-independence",),
    "ELECTIVE_C-009": ("math.hs.elective.model.scores-not-causes",),
    "ELECTIVE_C-011": ("math.hs.elective.statistics.survey-audit-report",),
    "ELECTIVE_D-007": ("math.hs.elective.music.rhythm-cycle-lcm",),
    "ELECTIVE_D-010": ("math.hs.elective.graph.round-robin-schedule",),
    "ELECTIVE_E-006": ("math.hs.elective.calculus.ftc-integral-derivative",),
    # Batch16, editorial matches, NOT certified syllabus coverage.
    "ELECTIVE_B-001": ("math.hs.elective.limit.sequence-continuity",),
    "ELECTIVE_B-002": ("math.hs.elective.calculus.second-derivative-convexity",),
    "ELECTIVE_B-004": ("math.hs.elective.calculus.integral-area-ftc",),
    "ELECTIVE_B-014": ("math.hs.elective.model.time-rescaling",),
    "ELECTIVE_C-006": ("math.hs.elective.model.compound-effective-rate",),
    "ELECTIVE_C-007": ("math.hs.elective.model.input-output-triangular",),
    "ELECTIVE_C-008": ("math.hs.elective.model.logistic-discrete-bounds",),
    "ELECTIVE_D-002": ("math.hs.elective.geometry.euclidean-isometries",),
    "ELECTIVE_D-004": ("math.hs.elective.sequence.fibonacci-golden-ratio",),
    "ELECTIVE_D-006": ("math.hs.elective.music.equal-temperament",),
    "ELECTIVE_E-002": ("math.hs.elective.algebra.square-rotations-group",),
    "ELECTIVE_E-004": ("math.hs.elective.finance.annuity-present-value",),
}

def digest(v: object) -> str:
    return hashlib.sha256(json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",",":")).encode("utf-8")).hexdigest()

def build():
    src=source_inventory()
    student_scope={x["id"]:x for x in src["items"]}
    deep={x.id:x.model_dump(mode="json") for x in lessons()}
    rows=[]
    for item in src["items"]:
        small=item["id"].replace("HS-STD2020-","")
        refs=MATCHES.get(small,())
        if len(set(refs))!=len(refs):
            raise ValueError("Duplicate suggested lesson for "+small)
        for ref in refs:
            if ref not in deep:
                raise ValueError("Unknown lesson suggestion "+ref)
            if deep[ref]["review"]["status"]!="REVIEW_PENDING":
                raise ValueError("Unexpected certified/rejected lesson in author-only suggestions "+ref)
        rows.append({
            "candidate_id":item["id"],
            "candidate_track":item["track"],
            "candidate_source_page":item["source"]["printed_page"],
            "objective_snapshot_sha256":digest(item),
            "match_status":"EDITORIAL_PROPOSAL_NOT_VERIFIED" if refs else "NO_PROPOSAL_NOT_A_COVERAGE_DECISION",
            "proposed_deep_lessons":[{
                "lesson_id":ref,
                "lesson_snapshot_sha256":digest(deep[ref]),
                "scope":"TOPIC_OVERLAP_PARTIAL_UNKNOWN",
                "source_grounding_review":"NOT_CHECKED",
                "math_proof_review":"NOT_CERTIFIED",
                "teacher_review":"PENDING",
            } for ref in refs],
            "review_questions":[
                "逐条核对官方正文要求、所在页和本项目拆分是否对应？",
                "该草案的定义、所有适用前提、证明、例题、反例是否覆盖这一目标？",
                "是否需要拆为更多教材级原子知识、避免借题目名称冒充覆盖？",
            ],
            "review_state":"QUEUED_FOR_HUMAN_REVIEW",
        })
    invalid_keys=set(MATCHES)-{k.removeprefix("HS-STD2020-") for k in student_scope}
    if invalid_keys:
        raise ValueError("Unknown objective identifiers "+str(sorted(invalid_keys)))
    counts=Counter()
    by_track={}
    for track in src["summary"]["by_track"]:
        part=[x for x in rows if x["candidate_track"]==track]
        proposed=sum(bool(x["proposed_deep_lessons"]) for x in part)
        by_track[track]={"objective_candidates":len(part),
                         "has_unreviewed_suggestion":proposed,
                         "without_suggestion":len(part)-proposed,
                         "suggestion_edges":sum(len(x["proposed_deep_lessons"]) for x in part),
                         "independently_approved":0}
        counts["suggestion_edges"]+=by_track[track]["suggestion_edges"]
        counts["has_unreviewed_suggestion"]+=proposed
    return {
        "schema_version":"1.0.0",
        "inventory_status":"EDITORIAL_MATCH_QUEUE_NOT_APPROVED",
        "base_source_digest_sha256":digest(src),
        "official_atomic_denominator":None,
        "official_coverage_percent":None,
        "independent_teacher_approved_matches":0,
        "student_published_knowledge_count":0,
        "total_source_objective_candidates":len(rows),
        "total_deep_draft_lessons":len(deep),
        "proposed_objectives":counts["has_unreviewed_suggestion"],
        "proposed_edges":counts["suggestion_edges"],
        "by_track":by_track,
        "items":rows,
        "warnings":[
            "The official standard has not been atomized completely or independently signed.",
            "Suggestions are authored topic overlaps, not reviewed evidence that a lesson satisfies a source clause.",
            "All deep lessons remain REVIEW_PENDING; no student teaching publication is authorized.",
            "Null official denominator and null course coverage percent must remain null."
        ]
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    s=json.dumps(build(),ensure_ascii=False,indent=2)+"\n"
    if args.check:
        if OUT.read_text(encoding="utf-8")!=s:
            raise AssertionError("Batch13 review queue differs from source and deep lesson snapshots")
        print("PASS batch13 editorial mapping proposal hash guards")
    else:
        OUT.write_text(s,encoding="utf-8")
        print("WROTE",OUT)

if __name__=="__main__":
    main()
