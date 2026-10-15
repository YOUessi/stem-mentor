"""Real local corpus retrieval (FTS5 BM25 + structured applicability checks).

No LLM, embedding model, external service, or claims about unindexed materials.
The corpus is original, project-authored content awaiting teacher review.
"""
from __future__ import annotations

import json
import re
import sqlite3
from functools import lru_cache
from pathlib import Path

from .catalog import PROBLEMS

CORPUS = Path(__file__).resolve().parents[2] / 'knowledge' / 'corpus' / 'methods.json'
_STOP = {'什么', '怎么', '怎样', '一个', '可以', '是否', '如何', '考虑', '分析', '题目', '方法', '然后', '已经', '还有', '哪种', '这个', '那个', '请问'}
_NEGATIONS = ('曲线外', '不在曲线上', '不属于曲线', '奇异点', '不在椭圆上')


def _terms(text: str) -> list[str]:
    # Unicode CJK bigrams + latin math words; an inverted index works offline.
    normalized = text.lower().replace('−', '-').replace('²', '2')
    raw = []
    for segment in re.findall(r'[\u3400-\u9fff]+|[a-z0-9_]+', normalized):
        if re.fullmatch(r'[\u3400-\u9fff]+', segment):
            raw.extend(segment[i:i+2] for i in range(len(segment)-1))
            if len(segment) == 1:
                raw.append(segment)
        else:
            raw.append(segment)
    return list(dict.fromkeys(t for t in raw if t not in _STOP and len(t) < 36))[:48]


@lru_cache(maxsize=1)
def corpus() -> tuple[dict, ...]:
    records = json.loads(CORPUS.read_text(encoding='utf8'))
    ids = [r['id'] for r in records]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate knowledge document id')
    for card in records:
        if not card.get('source', {}).get('permission') or not card.get('boundary'):
            raise ValueError(f'Missing permission or boundary: {card["id"]}')
    return tuple(records)


@lru_cache(maxsize=1)
def _index():
    db = sqlite3.connect(':memory:', check_same_thread=False)
    db.execute('CREATE VIRTUAL TABLE docs USING fts5(tokens, tokenize="unicode61")')
    for card in corpus():
        searchable = ' '.join(str(card.get(k, '')) for k in ('title', 'subject', 'content', 'boundary', 'hint'))
        searchable += ' ' + ' '.join(card.get('aliases', []) + card.get('prerequisites', []) + card.get('methods', []))
        db.execute('INSERT INTO docs(tokens) VALUES(?)', (' '.join(_terms(searchable)),))
    db.commit()
    return db


def _guard_violation(card: dict, query: str) -> str | None:
    """Detect a few explicit counterexamples. No general natural-language understanding."""
    q = query.lower().replace(' ', '').replace('非奇异点', '').replace('非零向量', '')
    card_id = card['id']
    guard = {
      'method-conic-tangent': [('曲线外','给定点在曲线外，不能直接套用曲线上一点的切线公式'),
                              ('不在曲线上','切点不在曲线上'),('奇异点','奇异点需要另外分析')],
      'method-parabola-tangent': [('曲线外','给定点在曲线外'),
                                  ('不在曲线上','给定点不在曲线上'),('p=0','抛物线参数退化')],
      'method-apollonius': [('距离比为1','此时轨迹退化为垂直平分线'),
                           ('比值为1','此时不能将轨迹称为圆'),
                           ('比例等于1','此时不能将轨迹称为圆')],
      'method-sine-area': [('不是夹角','缺少两边的夹角，不可直接使用对应的面积公式'),
                          ('非夹角','角与两边不构成夹角')],
      'method-interval-extrema': [('开区间','闭区间端点比较规则不能原样用于开区间')],
      'method-vector-dot': [('零向量','零向量没有定义好的几何夹角')],
      'method-log-base': [('底数为1','对数底数必须不等于 1'),('底数=1','对数底数必须不等于 1'),
                          ('底数为负','实数对数底数必须大于零')],
      'method-angle-bisector': [('外角平分线','内角平分线定理不可直接替代外角情况')],
      'method-ssa-ambiguity': [('sss','三边已知并非 SSA 多解条件')],
      'method-ssa-branch': [('sss','三边已知并非 SSA 多解条件')],
      'method-cosine-rule': [('无法构成三角形','三边不满足三角形不等式')],
    }
    # Handle a small class of explicit negations; unknown language remains unchecked.
    if '不是曲线外' in q or '不在曲线外' in q:
        q=q.replace('不是曲线外','').replace('不在曲线外','')
    for marker, why in guard.get(card_id, []):
        if marker in q:
            return why
    return None


def _applicability(card: dict, problem: dict | None, query: str) -> tuple[str, list[str]]:
    blocked = _guard_violation(card, query)
    if blocked:
        return 'CONTRAINDICATED', [blocked, '该结论必须另查适用条件']
    if problem is None:
        return 'CONDITION_UNCHECKED', ['没有经标注的题目结构，尚不能断言方法适用']
    known = set(problem.get('structure_tags', []))
    needed = set(card.get('requires', []))
    missing = sorted(needed - known)
    if missing:
        return 'CONDITIONS_NOT_ESTABLISHED', ['缺少由题目材料支持的结构条件: '+', '.join(missing)]
    if not needed:
        return 'GENERAL_STRATEGY', ['通用策略，不意味着具体数学结论已被证明']
    return 'CURATED_CONTEXT_MATCH', ['只核对了题卡标注的结构，尚未验证学生具体推导']


def retrieve(query: str, problem_id: str | None = None, limit: int = 8, show_excluded: bool = False):
    if not 1 <= len(query.strip()) <= 200:
        raise ValueError('Knowledge search requires 1-200 characters')
    if problem_id is not None and problem_id not in PROBLEMS:
        raise ValueError('Unknown curated problem')
    problem = PROBLEMS.get(problem_id)
    terms = _terms(query)
    ranks = {}
    if terms:
        # Only our own alphanumeric ngrams ever reach FTS query grammar.
        expression = ' OR '.join(f'"{t}"' for t in terms)
        for row in _index().execute('SELECT rowid, bm25(docs) AS bm FROM docs WHERE docs MATCH ? LIMIT 40', (expression,)):
            ranks[row[0]-1] = abs(float(row[1]))
    results, excluded = [], []
    for i, card in enumerate(corpus()):
        linked = bool(problem and set(card.get('methods', [])) & set(problem.get('method_tags', [])))
        # A linked card is NOT a query match. Never return unrelated content
        # solely because the currently open exercise uses that method.
        if (terms and i not in ranks) or (not terms and not linked):
            continue
        applicability, reasons = _applicability(card, problem, query)
        matched = sorted(set(terms) & set(_terms(' '.join([card['title'],card['content'], ' '.join(card['aliases'])]))))
        # Weighted ranking is inspectable and deterministic; no fabricated embedding similarity.
        bm = ranks.get(i, 0.0)
        score = round((4 if linked else 0) + min(bm, 12) + min(len(matched), 8) * .25, 4)
        result = {
            'id': card['id'], 'kind': card['kind'], 'title': card['title'], 'subject': card['subject'],
            'snippet': card['content'][:180], 'boundary': card['boundary'], 'hint': card['hint'],
            'method_ids': card['methods'], 'matched_tokens': matched[:12], 'structure_linked': linked,
            'applicability': applicability, 'applicability_reasons': reasons, 'score': score,
            'score_components': {'bm25': round(bm, 4), 'structure_boost': 4 if linked else 0},
            'source': card['source'], 'version': card['version'],
        }
        (excluded if applicability in ('CONTRAINDICATED', 'CONDITIONS_NOT_ESTABLISHED') else results).append(result)
    results.sort(key=lambda r: (-r['score'], r['id']))
    excluded.sort(key=lambda r: (-r['score'], r['id']))
    return {
        'hits': results[:limit], 'excluded': excluded[:limit] if show_excluded else [],
        'engine': 'LOCAL_FTS5_BM25_AND_STRUCTURE_V1', 'corpus_size': len(corpus()),
        'note': '真实本地索引检索；未使用向量或 LLM。适用标签是候选证据，不代表已证明学生解法正确。',
    }


def retrieve_for_tutor(problem_id: str):
    """Only identifiers to the policy; never give the tutor the full ready-made solution."""
    problem = PROBLEMS.get(problem_id)
    if not problem:
        return []
    result = retrieve(problem['title'], problem_id=problem_id, limit=5)
    return [{'id': x['id'], 'applicability': x['applicability'], 'source': x['source']['reference']}
            for x in result['hits']]
