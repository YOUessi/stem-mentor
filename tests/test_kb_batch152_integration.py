"""KB152 end-to-end regression: source, original depth, finite math, CDE overlap and student denial."""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'backend')]
import author_kb_batch152_data as authored
import build_kb_batch152_lessons as lessons
import build_kb_batch152_crosswalk as crosswalk
import build_kb_batch152_semantic_gate as gate
import build_kb_batch150_de_boundary as source
import check_kb_batch152_math as oracle
from app import kb_batch152_index as index
from app.main import app

@pytest.fixture(scope='module')
def rows():return json.loads(lessons.OUT.read_text(encoding='utf-8'))

@pytest.fixture(scope='module')
def ledger():return json.loads(lessons.AUDIT.read_text(encoding='utf-8'))

@pytest.fixture(scope='module')
def semantic():return json.loads(gate.OUT.read_text(encoding='utf-8'))

def test_original_authoring_and_manuscript_byte_reconstruction(rows,ledger):
 assert rows==lessons.build() and lessons.validate(rows)
 assert ledger==lessons.audit(rows) and ledger['total_teacher_only_drafts']==125
 assert len(ledger['rows'])==125 and len({r['candidate'] for r in ledger['rows']})==125
 assert all(v is None for v in ledger['official_atom_denominators'].values())
 assert ledger['teacher_approved']==ledger['student_authoritative']==0
 assert lessons.REPORT.read_text(encoding='utf-8')==lessons.render(rows,ledger)
 assert json.loads(lessons.SAFE.read_text(encoding='utf-8'))==lessons.student_safe()
 assert authored.OUT.read_text(encoding='utf-8')==authored.json.dumps(authored.R,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+'\n'

def test_k00_239_125_crosswalk_machine_auditable():
 old=crosswalk.build();crosswalk.validate(old)
 assert old==json.loads(crosswalk.OUT.read_text(encoding='utf-8'))
 assert crosswalk.REPORT.read_text(encoding='utf-8')==crosswalk.render(old)
 assert old['matched_editorial_candidates']==84 and old['missing_editorial_candidates']==155
 assert old['editorial_source_candidate_total']==239
 assert old['total_pending_teacher_manuscripts']==125
 assert all(v is None for v in old['official_atom_denominators'].values())
 assert old['teacher_approved']==old['student_authoritative']==0

@pytest.mark.parametrize('i',range(10))
def test_ten_distinct_rigorous_teacher_manuscripts(i,rows):
 r=rows[i];a=authored.R[i]
 assert r['source_candidate_id']==a['id'] and r['course_track']==lessons.EXPECTED[a['id']]
 assert r['source_evidence_status']==lessons.EVIDENCE and r['source_pdf_sha256']==lessons.PDF
 assert r['teacher_review_status']==r['prerequisite_math_review']=='REVIEW_PENDING'
 assert r['teacher_solution_visibility']=='TEACHER_ONLY' and r['teacher_review_evidence'] is None
 assert r['official_atom_id'] is None and not r['source_semantics_human_approved']
 assert not r['formal_proof_certified'] and not r['student_authoritative'] and not r['free_student_step_verified']
 assert len(r['reasoned_steps'])==4 and len(r['teacher_examples'])==2
 assert len(r['student_hint_ladder'])==3
 assert len(r['source_line_sha256'])==r['source_end_line']-r['source_start_line']+1
 assert r['elective_e_optional_example']==(i==9)

FORGE=[
 ('teacher_review_status','APPROVED'),('teacher_review_evidence',{'fake':'teacher'}),
 ('student_authoritative',True),('teacher_solution_visibility','STUDENT'),
 ('official_atom_id','fake-official-id'),('source_semantics_human_approved',True),
 ('formal_proof_certified',True),('free_student_step_verified',True),
 ('prerequisite_math_review','APPROVED'),('source_evidence_status','APPROVED'),
 ('source_pdf_sha256','0'*64),('source_span_sha256','0'*64),
 ('source_start_line',1000),('source_line_sha256',[]),
 ('reasoned_steps',[]),('teacher_examples',[]),('student_hint_ladder',[]),
 ('formal_definition_or_theorem',''),('nonexample_or_failure','')]
@pytest.mark.parametrize('i',range(10))
@pytest.mark.parametrize('field,bad',FORGE)
def test_all_ten_reject_fake_authority_and_missing_math_fields(i,field,bad,rows):
 corrupt=copy.deepcopy(rows);corrupt[i][field]=bad
 with pytest.raises(ValueError):lessons.validate(corrupt)

@pytest.mark.parametrize('i',range(40))
def test_all_exact_finite_witnesses_have_no_general_proof_authority(i):
 v=oracle.oracle();actual=json.loads(oracle.OUT.read_text(encoding='utf-8'))
 assert v==actual
 c=v['cases'][i]
 assert c['candidate_id']==lessons.IDS[i//4]
 assert c['outcome']==('EXACT_FINITE_WITNESS' if i%4<2 else 'REJECT_INVALID_PRECONDITION')
 assert c['passed'] and not c['general_formal_proof_certified']
 assert not c['teacher_approved'] and not c['student_free_step_verified']

@pytest.mark.parametrize('i',range(7))
def test_official_seven_track_denominator_stays_unknown(i):
 t=lessons.TRACKS[i]
 v=crosswalk.build()
 assert v['official_atom_denominators'][t] is None
 assert v['by_track'][t]['official_atom_denominator'] is None
 assert v['by_track'][t]['teacher_approved']==0
 assert v['by_track'][t]['student_authoritative']==0


def test_cde_proposal_gate_and_line_overlaps_are_not_auto_deduplicated(semantic):
 assert semantic==gate.build() and gate.validate(semantic)
 assert gate.REPORT.read_text(encoding='utf-8')==gate.render(semantic)
 assert semantic['provisional_semantic_proposals']==32
 assert semantic['source_line_partition_count']==122
 assert semantic['distinct_pair_count']>0
 assert semantic['semantic_duplicates_teacher_confirmed']==0 and semantic['auto_merged_atoms']==0
 assert semantic['teacher_approved']==semantic['student_authoritative']==0
 assert all(p['disposition']=='HUMAN_REVIEW_REQUIRED_NOT_AUTO_MERGED' for p in semantic['same_source_review_pairs'])
 assert all(v is None for v in semantic['official_atom_denominators'].values())

@pytest.mark.parametrize('i',range(32))
def test_cde_source_proposals_are_unapproved_and_sha_matched(i):
 doc=source.build()
 p=doc['proposals'][i]
 assert p['official_knowledge_atom_id'] is None
 assert p['teacher_review']=='REVIEW_PENDING' and not p['teacher_approved']
 assert p['source_track'] in {'ELECTIVE_C','ELECTIVE_D','ELECTIVE_E'}
 assert len(p['source_line_ids'])==len(p['source_line_sha256'])>0

@pytest.mark.parametrize('mutation',[
 lambda p:p.update(teacher_approved=True),
 lambda p:p.update(official_knowledge_atom_id='fake'),
 lambda p:p.update(source_pdf_sha256='0'*64),
 lambda p:p.update(source_track='COMPULSORY'),
 lambda p:p.update(mathematical_conditions_review='APPROVED'),
 lambda p:p.update(source_line_sha256=['0'*64]*len(p['source_line_sha256'])),
 lambda p:p.update(source_line_ids=[]),
])
def test_cde_gate_rejects_source_or_approval_forgery(mutation):
 corrupt=copy.deepcopy(source.build());mutation(corrupt['proposals'][0])
 with pytest.raises((gate.GateError,AssertionError,ValueError,KeyError)):
  gate.build(source=corrupt)

@pytest.mark.parametrize('query',['空间平面','单调有界','点到平面','排中律','采样周期','伯努利'])
def test_editor_internal_fts_metadata_only_and_students_denied(query):
 results=index.editor_preview_search(query,scope='EDITOR_LOCAL',limit=20)
 assert results,query
 for item in results:
  assert set(item)=={'id','course_track','source_candidate_id','review_status','condition_status','student_publishable','rank'}
  assert item['review_status']=='REVIEW_PENDING' and not item['student_publishable']
  assert item['condition_status']=='CONDITIONS_NOT_ESTABLISHED'
 assert index.student_evidence_lookup(query)==dict(status='NO_APPROVED_EVIDENCE',candidates=[],teacher_solution_exposed=False,unverified_content_exposed=False)

@pytest.mark.parametrize('scope',['',None,'STUDENT','TEACHER','APPROVED','ADMIN'])
def test_non_editor_scope_cannot_read_private_draft_metadata(scope):
 with pytest.raises(index.LocalEditorOnlyError):index.editor_preview_search('数学',scope=scope)

def test_http_endpoint_aggregate_only_and_no_teacher_answers():
 res=TestClient(app).get('/api/knowledge/kb152-review-coverage')
 assert res.status_code==200
 obj=res.json()
 assert obj['editorial_review_manuscripts']==125
 assert obj['editorial_source_candidates']==239
 assert obj['editorial_candidates_linked']==84 and obj['editorial_candidates_unlinked']==155
 assert obj['teacher_approved']==obj['student_authoritative']==0
 assert obj['official_course_coverage_rate'] is None
 assert all(v is None for v in obj['official_atom_denominators'].values())
 assert not obj['teacher_solution_or_manuscript_included']
 s=json.dumps(obj,ensure_ascii=False)
 for forbidden in ('teacher_examples','reasoned_solution','student_hint_ladder','公式证明','参考答案','source_line_sha256'):
  assert forbidden not in s
