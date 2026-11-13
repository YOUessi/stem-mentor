#!/usr/bin/env python3
"""Honest GitHub CI: published artifact/content gates ONLY; source PDF only checked on Mac."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
import build_kb_batch130_core_source as source
import build_kb_batch130_deep_lessons as deep
import build_kb_batch129_scope_reviews as prev
def require(b,msg):
    if not b:raise ValueError(msg)
def check():
    d=json.loads(source.OUT.read_text(encoding='utf-8'))
    locks=json.loads(source.LOCKS.read_text(encoding='utf-8'))
    source.validate(d,locks,regen=False)
    require(d['source_pdf_text_embedded'] is False,'copyright source text included')
    require({r['candidate_id'].removeprefix('hs-semantic-pilot-') for r in d['records']}==set(source.R),'unapproved scope entry')
    for r in d['records']:
        suff=r['candidate_id'].removeprefix('hs-semantic-pilot-')
        context,negative=source.R[suff]
        require(r['contextual_interpretation']==context and r['boundary_or_counterexample']==negative,
                'published interpretation differs from authored code')
        fingerprint=r['source_lock']
        require(re.fullmatch(r'[0-9a-f]{64}',fingerprint['span_sha256']) is not None and
            len(fingerprint['line_sha256'])==fingerprint['end_line']-fingerprint['start_line']+1 and
            all(re.fullmatch(r'[0-9a-f]{64}',h) for h in fingerprint['line_sha256']),
            'bad source fingerprint representation')
        require(r['source_pdf_sha256']==prev.prior.prior.provenance.old.previous.base_scope.evidence.PDF_SHA,
                'pinned original PDF SHA changed')
    require(source.REPORT.read_text(encoding='utf-8')==source.render(d),
            'source human review report diverged from committed JSON')
    lessons=json.loads(deep.OUT.read_text(encoding='utf-8'))
    deep.validate(lessons,regen=False)
    cmap={r['candidate_id']:r for r in d['records']}
    require({q['candidate_id'] for q in lessons}=={'hs-semantic-pilot-'+t['suffix'] for t in deep.LESSONS},
            'unowned teacher lesson or missing lesson')
    specs={t['suffix']:t for t in deep.LESSONS}
    for q in lessons:
        suffix=q['candidate_id'].removeprefix('hs-semantic-pilot-')
        spec=specs[suffix]
        expected={
          'formal_definition_or_theorem':spec['formal'],
          'notation_and_domain':spec['notation'],
          'applicability_and_hypotheses':spec['assumptions'],
          'nonexample_or_failure':spec['nonexample_or_failure'],
          'typical_wrong_solution':spec['typical_wrong_solution'],
          'why_wrong_and_repair':spec['why_wrong_and_repair'],
          'teacher_examples':spec['examples'],
          'student_hint_ladder':spec['hints'],
          'near_transfer':spec['near_transfer'],
          'far_transfer':spec['far_transfer'],
          'reasoned_steps':[{'step':a,'justification':b} for a,b in spec['reasoned_steps']],
          'source_line_lock':locks[q['candidate_id']],
          'course_track':cmap[q['candidate_id']]['track'],
          'objective':cmap[q['candidate_id']]['proposed_objective'],
          'prerequisite_candidate_ids':['hs-semantic-pilot-'+x for x in deep.PREREQUISITES[suffix]],
        }
        require(all(q.get(k)==v for k,v in expected.items()),'lesson authorial content/fingerprint drift '+suffix)
    o=json.loads(deep.ORACLE.read_text(encoding='utf-8'))
    require(o==deep.exact_oracles(),'math oracle stored output differs from real exact check')
    require(deep.REPORT.read_text(encoding='utf-8')==deep.render(lessons,o),
            'rendered teacher manuscript diverged from source')
    return {'batch':130,'original_mac_pdf_rehashed_by_CI':False,
            'context_reviews':d['new_context_reviews'],'cumulative_context_checked':d['context_reviewed_total'],
            'historical_editorial_candidates':239,'official_atom_denominator':None,
            'complete_teacher_pending_manuscripts':len(lessons),
            'independent_exact_example_checks':o['independently_checked_teacher_examples'],
            'invalid_counterexample_checks':o['boundary_counterexamples'],
            'student_authority_releases':0,'teacher_approvals':0}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true',required=True);p.parse_args()
    print(json.dumps(check(),ensure_ascii=False,indent=2,sort_keys=True))
