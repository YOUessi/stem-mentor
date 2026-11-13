#!/usr/bin/env python3
"""Batch130: human-authored curricular contextual judgments, with Mac-source re-attestation.

Every interpretation is deliberately provisional. The official knowledge-atom denominator
is not inferred from layout, the count of candidates, or a digest of a line.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_kb_batch129_scope_reviews as prev
OUT=ROOT/'docs/evaluation/KB_BATCH130_CORE_CONTEXTS.json'
REPORT=ROOT/'docs/evaluation/KB_BATCH130_CORE_CONTEXTS.md'
LOCKS=ROOT/'curriculum/highschool_math/k00_batch130_original_line_fingerprints.json'
# Each interpretation / test-to-invalidate was separately authored after viewing Mac PDFKit lines.
# These are pedagogical hypotheses NOT official atom enumerations.
R={
'121-c201':('集合与元素的属于关系；先选定对象是否为元素，不可混同子集与成员。','3∈{1,2}为假；{1}∈{1,2}为假，但{1}⊆{1,2}为真。'),
'121-c202':('并交运算依赖元素判据；图示是辅助而不是替代元素所属证明。','集合{1,2}与{2,3}交集为{2}，不是{1,2,3}。'),
'121-c203':('全称命题的否定必须把任意改成存在并否定谓词。','「所有实数平方为正」的否定是存在x使x²≤0；x=0为见证。'),
'121-c204':('二次不等式利用抛物线符号区间之前先核对开口系数和实根数。','x²+1>0在实数域恒真，不能擅自假设两个实根。'),
'121-c205':('函数是从定义域到陪域的单值对应；同一输入不准出现两个不同输出。','x=0同时指定f(0)=1与f(0)=2的关系不是函数。'),
'122-c301':('列举与描述法需要指向同一论域；重复列举不产生新集合元素。','{x∈Z:0<x<3}={1,2}，若把论域改为R则不相等。'),
'122-c302':('空集没有元素；全集相对于给定问题定义，不能省略研究范围。','全集U={1,2}时{3}不可能是U的子集。'),
'122-c303':('补集运算必须包含指定全集U和U内子集A；变更U将变更结果。','U={1,2,3},A={1}的补集为{2,3}，不是无限整数集。'),
'122-c304':('对命题P是Q的必要条件，核验方向应为Q⇒P。','整数为偶数是可被4整除的必要条件，反方向不成立。'),
'122-c305':('对命题P是Q的充分条件，核验方向应为P⇒Q。','可被4整除充分保证偶数，偶数不充分保证可被4整除。'),
'122-c306':('充要条件要求两个方向都真，单方向的蕴含不能当成等价。','x²=4与x=2不是充要：x=-2也是平方等于4。'),
'122-c307':('分段函数按自变量归属唯一分支求值，接缝点的左右规则须清楚。','f(x)=x(x<0),x+1(x≥0)时f(0)=1，不是0。'),
'122-c308':('单调性是给定区间任意两点的比较，不由单个采样对替代。','f(x)=x²在整个实数域并不单调，虽然在[0,∞)递增。'),
'122-c309':('指数函数模型需确认底数正且不等于1，现实增长还须时间单位一致。','y=(-2)^x在全部实数上不是实值指数函数。'),
'122-c310':('单位圆坐标分别对应sin、cos；tan需cos不为零。','在θ=π/2处sinθ有定义，但tanθ无定义。'),
'122-c311':('零点存在定理需要闭区间连续及两端严格异号才给出开区间内零点。','f(x)=1/x在[-1,1]两端异号但不连续，区间内无零点。'),
'122-c312':('频率估计概率依赖可重复稳定随机机制，单次频率不等于真概率。','一枚公平硬币一次抛出正面频率是0或1，理论概率仍1/2。'),
'123-c401':('韦恩图以交并补的元素关系为准，不可用不按比例的图形面积推概率。','A={1,2},B={2,3}，A∪B含3个元素而非4个。'),
'123-c402':('存在量词命题的否定应为全称并否定性质，且论域与原命题严格一致。','「存在实数x使x²<0」的否定是所有实数x都有x²≥0。'),
'123-c403':('图解二次不等式需要将抛物线与x轴交点、重根或无根情形区分。','(x-1)²<0无解，不能把x=1当作解。'),
'123-c404':('奇偶性必须先保证定义域关于原点对称，再核验f(-x)=±f(x)。','f(x)=x²但只在x≥0定义时不称偶函数。'),
'123-c405':('周期是非零平移保持函数值，最小正周期不一定存在。','常值函数所有正数都是周期，却没有最小正周期。'),
'123-c406':('实数有理指数幂的根式定义需要对负底、偶次根进行区分。','(-1)^(1/2)在实数范围未定义。'),
'123-c407':('换底公式的真数和新旧底必须正，底不等于1；对数分母非零。','log_1 2无定义，不能套换底公式。'),
'123-c409':('和差角公式是全实角恒等式；若推导中使用正切要另核对分母。','tan(π/2)无定义，不能把正切加法式当作全实角恒等式。'),
'123-c411':('古典概型需要有限、等可能基本结果；结果类别不代表等可能。','两骰点数和为2与和为7不等可能，不能按11种和值等分。'),
'123-c412':('平均数、中位数和众数对应不同集中趋势，异常值使均值失真。','样本{1,2,100}的均值为103/3，而中位数是2。'),
'124-c501':('函数模型的图表解析式应保持同一定义域和单位，不可把有限描点当恒等证明。','仅通过(0,0),(1,1)不能确定函数在所有实数上是f(x)=x。'),
'124-c502':('指数函数底数a>1时递增，0<a<1时递减；绘制需核对图像范围。','y=(1/2)^x递减，并非所有指数函数递增。'),
'124-c503':('对数函数真数x>0；底数a>0且a≠1，其单调性依底数分段。','log_2(-1)实数域无定义，不能画到负x轴。'),
'124-c504':('对数与指数互为反函数须维持x、y对应的域和底数合法性。','log_1 x不构成函数，不能作y=1^x的反函数。'),
'124-c505':('正弦余弦正切图像的周期及正切渐近线不同，不可整套套用同一周期。','tan x的最小正周期为π，cos x为2π。'),
'124-c506':('正弦模型的振幅取|A|，角频率ω≠0才有2π/|ω|的最小正周期。','A=0时常值函数无最小正周期，不能填2π/|ω|。'),
'124-c507':('差角余弦公式来自单位圆内积，所有实角有效；不能遗漏减号方向。','cos(π/2-π/2)=1，而cos(π/2)cos(π/2)-sin(π/2)sin(π/2)=-1。'),
'124-c508':('三角恒等变换需说明代数等价和原定义域，消去分母可能引入无定义点。','把sin x/cos x改写tan x时须排除cos x=0。'),
'124-c509':('函数零点是定义域内满足f(x)=0的输入，与方程根为同一个集合。','f(x)=1/x没有零点，x=0却是禁止输入而非根。'),
'124-c510':('建模须明确量的单位与物理定义域，数学表达式不自动支持无限外推。','人口指数模型不能在未说明范围时推断无限时间人口。'),
'124-c511':('比较增长先给相同尺度和正参数范围，再区分局部交叉与渐近增长。','在小区间内x²可小于或大于2^x，不能凭一个点给全局排名。'),
'124-c512':('力、速度、位移的向量表示必须区分物理单位和方向，不把不同量相加。','5m位移与5N力不能直接相加成10。'),
'124-c513':('平面向量有模和方向；零向量模为0但方向不确定。','零向量和非零向量之间的夹角不能定义。'),
'119-s15':('最小二乘斜率需样本自变量离差平方和严格正；预测不等于因果。','所有x_i都相等时带截距回归斜率无法唯一确定。'),
'119-s16':('二乘二列联表必须有合法的非负计数；独立性检验不能直接宣布因果。','样本量为0或边际频数为0时通常卡方近似条件不满足。'),
'120-s101':('等差数列公差相同，取n从规定起始整数递推；与一次函数只是在离散点联系。','{n²}相邻差为2n+1，不是等差数列。'),
'120-s102':('等比数列公比按标准定义需合法且相邻项商有定义；与指数函数关系保留离散域。','数列1,0,0不能按相邻项商定义非零公比等比数列。'),
'120-s103':('平均变化率到导数须说明h→0极限存在；图像看似光滑不足证明导数存在。','f(x)=|x|在0左右差商分别±1，故不可导。'),
'120-s104':('常见函数用定义求导逐个核验定义域；根函数和倒数函数在边界不适用。','1/x在x=0未定义，√x在0没有有限双侧实导数。'),
'120-s105':('空间两点距离由各坐标差平方和开方得到，三维坐标轴必须正交单位尺度一致。','两点相同时距离为0，不能做以距离为分母的方向单位化。'),
'120-s106':('空间向量在正交标准基上的展开唯一；若基退化则不可以直接按正交公式投影。','三向量中有零向量或线性相关时不构成空间基。'),
'120-s107':('斜率是直线倾斜的正切，竖直直线倾斜角有定义但斜率无定义。','x=2是合法竖直直线，却不能写成y=kx+b。'),
'120-s108':('以斜率判平行垂直须分开核验竖直、水平直线和重合情形。','x=1与x=2平行但两者都没有斜率。'),
'120-s109':('点斜式要求斜率存在，一般式Ax+By+C=0要求(A,B)不全零。','A=B=0,C=1得到0=1不是直线。'),
'120-s110':('两直线交点解方程组可能无解、唯一或无穷多解，分清平行和重合。','x=0与x=1无交点；两条相同直线有无穷多公共点。'),
'120-s111':('椭圆距离和定义须常数大于两焦点距离；等于时退化线段。','两焦点相距4而距离和为4不构成非退化椭圆。'),
}
def req(b,msg):
    if not b: raise ValueError(msg)
def encode(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n'
def build():
    _,candidates=prev.prior.prior.originals()
    pages=prev.prior.prior.previous.source_pages()
    already={'hs-semantic-pilot-'+s[0] for s in prev.prior.prior.DETAILS}
    already|={s[0] for s in prev.prior.prior.previous.SPECS}
    already|={'hs-semantic-pilot-'+s[0] for s in prev.prior.SPECS}
    already|={'hs-semantic-pilot-'+s[0] for s in prev.SPECS}
    already &= set(candidates)
    req(len(already)==104,'prior Batch129 reviewed census changed')
    records=[];locks={}
    for suffix,(context,negative) in R.items():
        k='hs-semantic-pilot-'+suffix
        req(k not in already and k in candidates and k not in locks,'duplicate/missing candidate '+k)
        c=candidates[k];src=c['source'];p=src['printed_page'];lo=src['start_line'];hi=src['end_line']
        raw=pages[p][lo-1:hi]
        req(len(raw)==hi-lo+1,'missing original private source lines')
        q={'page':p,'start_line':lo,'end_line':hi,
           'line_sha256':[hashlib.sha256(s.encode()).hexdigest() for s in raw],
           'span_sha256':hashlib.sha256('\n'.join(raw).encode()).hexdigest()}
        req(len(context)>=22 and len(negative)>=18,'insufficient editorial reasoning '+suffix)
        locks[k]=q
        records.append({'candidate_id':k,'track':c['course_track'],'proposed_objective':c['proposed_objective'],
           'contextual_interpretation':context,'boundary_or_counterexample':negative,
           'source_lock':q,'source_pdf_sha256':prev.prior.prior.provenance.old.previous.base_scope.evidence.PDF_SHA,
           'source_may_be_partial_line':lo==hi,'source_evidence_status':'ORIGINAL_LINE_HASH_CHECKED_EDITORIAL_INTERPRETATION_PENDING',
           'official_atom_id':None,'teacher_review_status':'REVIEW_PENDING','teacher_signature':None,
           'student_authoritative':False,'mathematics_formally_certified':False})
    counts={}
    reviewed=already|set(locks)
    for t in prev.TRACKS:
        ids={k for k,v in candidates.items() if v['course_track']==t}
        counts[t]={'historical_editorial_candidates':len(ids),'context_checked':len(ids&reviewed),
                   'not_checked':len(ids-reviewed),'official_atom_denominator':None,
                   'teacher_approved':0}
    d={'batch':130,'standard_version':'2017 edition, 2020 revision',
       'historical_editorial_candidates':len(candidates),'reviewed_before':104,
       'new_context_reviews':len(records),'context_reviewed_total':len(reviewed),
       'remaining_context_reviews':len(candidates)-len(reviewed),
       'curriculum_layout_cues':405,'official_atom_denominator':None,
       'track_official_atom_denominators':{t:None for t in prev.TRACKS},
       'teacher_approved':0,'student_authoritative':0,
       'source_pdf_text_embedded':False,'counts_by_track':counts,'records':records}
    validate(d,locks,False)
    return d,locks
def validate(d,locks,regen=True):
    req(d['batch']==130 and d['historical_editorial_candidates']==239 and
        d['reviewed_before']==104 and d['new_context_reviews']==len(R) and
        d['context_reviewed_total']==104+len(R) and
        d['remaining_context_reviews']==135-len(R) and d['curriculum_layout_cues']==405,'scope census drift')
    req(d['official_atom_denominator'] is None and d['teacher_approved']==0 and
        d['student_authoritative']==0 and d['source_pdf_text_embedded'] is False and
        set(d['track_official_atom_denominators'])==set(prev.TRACKS) and
        all(x is None for x in d['track_official_atom_denominators'].values()),'forged scope authority')
    req(len(d['records'])==len(R) and len(locks)==len(R) and
        len({x['candidate_id'] for x in d['records']})==len(R),'duplicated/omitted context')
    req(sum(x['historical_editorial_candidates'] for x in d['counts_by_track'].values())==239 and
        sum(x['context_checked'] for x in d['counts_by_track'].values())==104+len(R) and
        sum(x['not_checked'] for x in d['counts_by_track'].values())==135-len(R) and
        all(x['official_atom_denominator'] is None and x['teacher_approved']==0 for x in d['counts_by_track'].values()),'per-track fraud')
    for r in d['records']:
        req(r['candidate_id'] in locks and r['source_lock']==locks[r['candidate_id']] and
            len(r['contextual_interpretation'])>=22 and len(r['boundary_or_counterexample'])>=18 and
            r['source_evidence_status']=='ORIGINAL_LINE_HASH_CHECKED_EDITORIAL_INTERPRETATION_PENDING' and
            r['teacher_review_status']=='REVIEW_PENDING' and r['official_atom_id'] is None and
            r['teacher_signature'] is None and r['student_authoritative'] is False and
            r['mathematics_formally_certified'] is False,'missing negative/forged review')
    if regen:
        wanted,fingerprints=build()
        req(d==wanted and locks==fingerprints,'private source/context drift')
    return True
def render(d):
    lines=['# Batch130 — Mac original-source contextual review','',
      f"{d['new_context_reviews']} manually reasoned contextual review cases; {d['context_reviewed_total']}/239 previously drafted editorial candidates checked, {d['remaining_context_reviews']} still unchecked.",
      'Each associated fingerprint can be compared to the original privately held Mac PDFKit lines.',
      'A line hash is not a proof of complete normative support. Single source line may be a fragment.',
      'Official denominator UNKNOWN in all seven tracks; teacher approved=0; student authority=0.','']
    for t in prev.TRACKS:
        c=d['counts_by_track'][t]
        lines.append(f"- {t}: {c['context_checked']}/{c['historical_editorial_candidates']} reviewed, {c['not_checked']} pending; official atom denominator UNKNOWN")
    for r in d['records']:
        s=r['source_lock']; lines+=['',f"## {r['candidate_id']} ({r['track']})",
          f"Original PDF printed p.{s['page']} lines {s['start_line']}-{s['end_line']}; SHA256 {s['span_sha256']}",
          'Objective (editorial): '+r['proposed_objective'],
          'Context interpretation (pending): '+r['contextual_interpretation'],
          'Invalid edge / negative case: '+r['boundary_or_counterexample']]
    return '\n'.join(lines).rstrip()+'\n'
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');a=p.parse_args()
    d,locks=build()
    for f,s in [(OUT,encode(d)),(LOCKS,encode(locks)),(REPORT,render(d))]:
        if a.write:f.parent.mkdir(parents=True,exist_ok=True);f.write_text(s,encoding='utf-8')
        else:req(f.exists() and f.read_text(encoding='utf-8')==s,'stale artifact '+str(f))
    print(f"Batch130: {len(R)} new Mac source contexts; {d['context_reviewed_total']}/239 checked, {d['remaining_context_reviews']} unreviewed; official 7-track denominator UNKNOWN")
if __name__=='__main__':main()
