"""Batch97 independent K00/K01/K07/K08/K09 regression and failure-path checks."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import json
import sys
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'backend')]
import build_kb_batch97_depth as B
from kb_batch97_authoring import RECORDS
from app.deep_knowledge import DeepLesson, lessons, coverage_report
from app.deep_retrieval import editor_draft_search,editor_draft_full,student_evidence_lookup,EditorOnlyError
from app.kb_batch97_math_oracles import (IDS,check,verify_all,
    distance_sq,line_plane_relation,hyperbola_domain,finite_limit_quotient,
    newton_leibniz_polynomial,rectangle_probability,closed_rectangle_poly_extrema,
    euclidean_sq,zscore,oa_strength2,independent_p_given_q,response_rate,reflect)

@pytest.fixture(scope='module')
def artifact():return B.build()
@pytest.fixture(scope='module')
def prior():return B.B96.build()[1]

def test_full_batch_and_real_denominator_unknown(artifact):
    docs,report=artifact
    assert len(docs)==len(IDS)==12
    assert report['prior_full_deep_drafts']==42
    assert report['cumulative_new_deep_drafts_since_batch94']==54
    assert report['still_without_any_individual_review']==56
    assert report['remaining_without_pairwise_comparison']==134
    assert report['official_atom_denominator'] is None
    assert all(v is None for v in report['official_atom_denominators_by_track'].values())
    assert report['fully_teacher_atomized_pages']==0
    assert report['teacher_approved']==report['student_authoritative_release']==0
    assert report['historical_uncertified_proof_steps']==538
    assert report['P0_historical_steps_without_teacher_cards']==106
    assert report['unresolved_math_conflicts']==10
    assert report['general_theorem_certificates']==0
    assert sum(v['batch97_deep_drafts'] for v in report['per_track'].values())==12
    assert report['per_track']['ELECTIVE_E']['batch97_deep_drafts']==0

def test_anchored_unreviewed_source_is_not_reused(artifact,prior):
    src={x['source_candidate_id'] for x in artifact[1]['canonical_lesson_source_links']}
    old={x['source_candidate_id'] for x in prior['canonical_lesson_source_links']}
    old|={x['source_candidate_id'] for x in B.B94.build()[1]['canonical_lesson_source_links']}
    old|={x['source_candidate_id'] for x in B.B95.build()[1]['canonical_lesson_source_links']}
    assert len(src)==12 and src.isdisjoint(old)
    assert set(IDS)==src

@pytest.mark.parametrize('i',range(12))
def test_schema_proof_counterexample_and_provenance(i,artifact):
    doc,link=artifact[0][i],artifact[1]['canonical_lesson_source_links'][i]
    obj=DeepLesson.model_validate(doc)
    assert obj.id==f'math.hs.batch97.{i+1:02d}'
    assert link['source_candidate_id']==RECORDS[i]['anchor']==IDS[i]
    assert len(link['source_line_sha256'])==64
    assert link['finite_evidence']['general_theorem_certified'] is False
    assert obj.review.status=='REVIEW_PENDING' and obj.review.reviewer_id is None
    assert obj.teacher_solution_visibility=='TEACHER_ONLY'
    assert len(obj.worked_examples)==2 and len(obj.hint_ladder)==3
    assert len(obj.assumptions)>=2 and obj.boundaries and obj.counterexamples and obj.misconceptions
    assert obj.transfer.near!=obj.transfer.far
    assert len(obj.proof_steps)==3 if obj.kind=='theorem' else len(obj.rationale_steps)==3

@pytest.mark.parametrize('i',range(1,13))
def test_independent_positive_and_invalid_case(i):
    v=check(i)
    assert v['finite_positive_case'] is v['invalid_premise_or_overgeneralization'] is True
    assert v['general_theorem_certified'] is v['teacher_approved'] is v['student_publishable'] is False

@pytest.mark.parametrize('bad',[-1,0,13,True,'5',None,1.0])
def test_unknown_oracle_id_rejected(bad):
    with pytest.raises(ValueError):check(bad)

@pytest.mark.parametrize('i',range(12))
def test_student_isolation(i,artifact):
    d=artifact[0][i]
    assert any(x.id==d['id'] for x in lessons())
    assert any(x['knowledge_id']==d['id'] for x in editor_draft_search(d['title'],scope='EDITOR_LOCAL',limit=20))
    with pytest.raises(EditorOnlyError):editor_draft_search(d['title'])
    with pytest.raises(EditorOnlyError):editor_draft_full(d['id'])
    student=student_evidence_lookup(d['title'])
    assert student['status']=='NO_APPROVED_EVIDENCE'
    assert student['teacher_solution_exposed'] is False
    assert student['unverified_content_exposed'] is False
    for e in d['worked_examples']:
        assert e['answer'] not in json.dumps(student,ensure_ascii=False)

@pytest.mark.parametrize('i',range(12))
def test_invalid_source_rejected(i,prior):
    rec=deepcopy(RECORDS);rec[i]['anchor']='FAKE-SHA-ANCHOR'
    with pytest.raises(ValueError,match='source'):B.build(records=rec,prior=prior)

@pytest.mark.parametrize('i',range(12))
def test_duplicate_source_rejected(i,prior):
    rec=deepcopy(RECORDS);rec[i]['anchor']=rec[(i+1)%12]['anchor']
    with pytest.raises(ValueError,match='source'):B.build(records=rec,prior=prior)

@pytest.mark.parametrize('i',range(12))
def test_missing_math_hypotheses_rejected(i,prior):
    rec=deepcopy(RECORDS);rec[i]['assumptions']=[]
    with pytest.raises(ValueError,match='assumptions'):B.build(records=rec,prior=prior)

@pytest.mark.parametrize('i',range(12))
def test_missing_proof_or_rationale_rejected(i,prior):
    rec=deepcopy(RECORDS);rec[i]['steps']=rec[i]['steps'][:2]
    with pytest.raises(ValueError,match='steps'):B.build(records=rec,prior=prior)

@pytest.mark.parametrize('i',range(12))
def test_missing_example_rejected(i,prior):
    rec=deepcopy(RECORDS);rec[i]['examples']=rec[i]['examples'][:1]
    with pytest.raises(ValueError,match='examples'):B.build(records=rec,prior=prior)

@pytest.mark.parametrize('i',range(12))
def test_missing_counterexample_rejected(i,prior):
    rec=deepcopy(RECORDS);rec[i]['negative']=('','','')
    with pytest.raises(ValueError,match='counterexample'):B.build(records=rec,prior=prior)

@pytest.mark.parametrize('i',range(12))
def test_hint_leakage_schema_missing_tiers_rejected(i,prior):
    rec=deepcopy(RECORDS);rec[i]['hints']=rec[i]['hints'][:2]
    with pytest.raises(ValueError,match='hints'):B.build(records=rec,prior=prior)

@pytest.mark.parametrize('i',range(12))
def test_fake_approval_rejected(i,artifact):
    doc=deepcopy(artifact[0][i]);doc['review'].update(status='APPROVED',reviewer_id='fake',reviewed_at='2026-11-11',review_record='fabricated')
    with pytest.raises(ValueError):DeepLesson.model_validate(doc)

@pytest.mark.parametrize('field,value',[
    ('official_atom_denominator',300),('teacher_approved',12),
    ('student_authoritative_release',12),('fully_teacher_atomized_pages',61),
    ('historical_uncertified_proof_steps',0),('unresolved_math_conflicts',0),
    ('still_without_any_individual_review',0),('remaining_without_pairwise_comparison',0)
])
def test_fake_historical_denominator_and_approval_rejected(field,value,prior):
    r=deepcopy(prior);r[field]=value
    with pytest.raises(ValueError,match='drift'):B.build(prior=r)

def test_guarded_independent_math_boundaries():
    assert distance_sq((1,2,3),(4,6,3))==25
    with pytest.raises(ValueError):distance_sq((True,2,3),(4,6,3))
    assert line_plane_relation((0,1,2),(1,0,0),(0,0,0),(0,0,1))==('PARALLEL_DISJOINT',None)
    assert line_plane_relation((0,0,0),(1,0,0),(0,0,0),(0,0,1))==('CONTAINED',None)
    assert line_plane_relation((1,1,1),(0,0,-1),(0,0,0),(0,0,1))==('INTERSECT_ONE',Q(1))
    with pytest.raises(ValueError):line_plane_relation((0,0,0),(0,0,0),(0,0,0),(1,0,0))
    assert hyperbola_domain(10,6)
    with pytest.raises(ValueError):hyperbola_domain(6,8)
    assert finite_limit_quotient(4,2)==2
    with pytest.raises(ValueError):finite_limit_quotient(0,0)
    assert newton_leibniz_polynomial((0,0,1),0,2)==Q(8,3)
    with pytest.raises(ValueError):newton_leibniz_polynomial((1,),0,True)
    assert rectangle_probability(2,Q(1,2),1,Q(1,4),Q(1,2))==Q(1,4)
    with pytest.raises(ValueError):rectangle_probability(2,1,1,1,1)
    assert closed_rectangle_poly_extrema()==(((2,0),1),((0,2),13))
    assert euclidean_sq((1,1000),(2,1010))==101
    with pytest.raises(ValueError):zscore(7,7,0)
    assert oa_strength2([(0,0,0),(0,1,1),(1,0,1),(1,1,0)])
    assert not oa_strength2([(0,0),(0,0),(1,1),(1,1)])
    assert independent_p_given_q('q','p')
    with pytest.raises(ValueError):independent_p_given_q('p','p')
    assert response_rate(500,400)==Q(4,5)
    with pytest.raises(ValueError):response_rate(0,0)
    assert reflect((2,0,1),(0,0,0),(1,1,0))==(0,-2,1)
    with pytest.raises(ValueError):reflect((1,2,3),(0,0,0),(0,0,0))

def test_reflection_involution_and_isometry_finite_exact_grid():
    from itertools import product
    points=list(product((-1,0,1),repeat=3))
    for normal in ((1,0,0),(1,1,0),(1,2,3)):
        mirror=[reflect(p,(0,0,0),normal) for p in points]
        assert all(reflect(q,(0,0,0),normal)==p for p,q in zip(points,mirror))
        for i,p in enumerate(points):
            for j,q in enumerate(points):
                assert distance_sq(p,q)==distance_sq(mirror[i],mirror[j])

@pytest.mark.parametrize('bad',[(1,2,3.5),(1,2),(True,2,3),'bad'])
def test_reflection_invalid_vectors_rejected(bad):
    with pytest.raises(ValueError):reflect(bad,(0,0,0),(1,0,0))

def test_coverage_and_generated_files(artifact):
    report=coverage_report()
    assert report['deep_lesson_documents']>=361
    assert report['human_teacher_review_complete'] is False
    assert report['direct_student_teaching_enabled'] is False
    assert set(verify_all())==set(IDS)
    docs,audit=artifact
    assert json.loads(B.PACK.read_text())==docs
    assert json.loads(B.AUDIT.read_text())==audit
