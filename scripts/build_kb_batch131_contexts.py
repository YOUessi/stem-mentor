#!/usr/bin/env python3
"""Batch131: contextual adjudication on the Mac PDFKit source, never public authority.

The JSON holds editorial reasoning and source digests, NOT copyrighted text or
a fabricated atom denominator. Offline CI checks only committed evidence.
"""
from __future__ import annotations
import argparse, collections, copy, hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch130_core_source as previous

DATA = ROOT / "docs/evaluation/KB_BATCH131_CONTEXT_ADJUDICATION.json"
LOCKS = ROOT / "curriculum/highschool_math/k00_batch131_line_fingerprints.json"
REPORT = ROOT / "docs/evaluation/KB_BATCH131_CONTEXT_ADJUDICATION.md"

# All two-sentence interpretations and invalid boundary cases written independently
# after comparing the proposed objective to the original PDFKit line on the Mac.
# Neither a line fingerprint nor a partial line certifies an official atom.
R = {
'124-c514': ('向量分解解几何或力学问题时，应先选择正交或其他确实线性无关的方向，并在力学模型内保留物理量单位。', '沿两条平行方向不能唯一分解任意平面向量；位移与力不能因坐标都为二元组而直接相加。'),
'124-c515': ('辨认柱锥台球先依据底面、母线及截面等定义，透视效果只能辅助识别，不能替代几何性质。', '斜视图中的圆看似椭圆，但这不意味着原立体的圆形底面实际变成椭圆。'),
'124-c516': ('柱锥台和球的体积与表面积公式都应核对对应体型、正高度、半径与单位，不能跨模型套用。', '半径为2、高为3的圆锥体积是4π，不是与同底同高圆柱相等的12π。'),
'124-c517': ('斜二测绘制空间直观图采用特定倾角和坐标方向的比例规则，投影图不保存所有真实长度和角度。', '斜二测图上的45度并不能直接证明原空间两条棱的真实夹角也是45度。'),
'124-c518': ('点线面基本位置关系应使用几何定义及可引用的基本事实推理，长方体只提供直观参照而非逻辑证据。', '一条直线的投影落在平面内，不足以证明空间中该直线本身属于该平面。'),
'124-c519': ('判定线面平行需检查平面内的参照直线与原直线确实平行且原直线不在该平面内，避免偷换定义。', '同一平面内两条平行直线不应据此判定其中一条与该平面严格平行。'),
'124-c520': ('线面垂直与面面垂直判定须给出被包含在相应平面内的直线及其垂直条件，不能由图上直角直接推出。', '两个平面在透视图里交线看似成直角，不足以证明这两个平面垂直。'),
'124-c521': ('事件的并交补概率必须相对同一样本空间和同一个概率测度解释；并集采用容斥而非无条件相加。', 'P(A)=0.6、P(B)=0.5且P(A∩B)=0.3时P(A∪B)=0.8而非1.1。'),
'124-c522': ('说明数据来源应明确统计总体、时间窗口、采集途径、合法授权与抽样偏差，不把便利获取的数据当随机样本。', '只在某校自愿参与者中调查，不能不做偏差分析就推论所有全国高中生。'),
'124-c523': ('总体、样本与样本量是不同概念，样本的随机性来自采样机制而不是仅凭观测值大小无序。', '有序排列的独立随机样本仍然来自随机抽样；把数据打乱不使方便样本成为随机样本。'),
'124-c524': ('样本方差可按描述型分母n或无偏估计型分母n−1定义，标准差应与选定定义配套并说明单位。', '样本{1,3}的均值2，分母2方差为1，分母1方差为2；不能两个数混报为同一统计量。'),
'124-c525': ('经验百分位数依排序结果、百分位点定义和插值约定而定；不同约定可产生不同估计值。', '样本{1,2,10,11}的中间百分位可因定义不同而不同，未指明规则不能声称唯一定值。'),
'121-s201': ('使用导数公式表之前必须逐个检查函数定义域、组合结构、内函数可导及求导区间，不可抹去链式法则。', '对f(x)=ln(x²)在x≠0求导得2/x，不是1/x；在x=0函数根本未定义。'),
'121-s202': ('空间向量坐标运算按分量进行，与平面向量同样满足加法和数乘规律，但不能遗漏第三个坐标。', '向量(1,2,3)+(2,0,-1)=(3,2,2)，不是平面截断计算得到的(3,2,3)。'),
'121-s203': ('不同两点才能唯一确定直线；斜率式不覆盖竖直直线，须保留一般式的合法系数条件。', '两点(2,0)、(2,3)确定x=2，但斜率分母为零，不能强写成y=kx+b。'),
'121-s204': ('圆的圆心与半径须通过方程完成平方识别，半径平方必须严格为正才能得到非退化实圆。', 'x²+y²+1=0在实平面无点，不能将其视为半径1的圆。'),
'121-s205': ('直线与圆位置可用圆心到直线距离比较半径；若讨论圆与圆还需两圆心距及半径和差。', '圆心距等于两半径之和时两圆外切，不能因为两个圆半径都正就判为相交两点。'),
'121-s206': ('离散随机变量的取值集必须清楚且各概率非负并总和为一；取值名称不等于事件互不相交的证明。', '随机变量取0和1而概率分别为0.7和0.4时总和1.1，不能构成合法分布列。'),
'121-s207': ('空间向量投影到非零方向使用内积与方向范数平方；目标为零向量时该投影公式不合法。', '把向量(1,2,0)投影到零向量时分母为零，不能人为约定投影长度为2。'),
'122-s301': ('空间向量推广保持加法、数乘和数量积的代数结构，但空间向量方向需用三维分量或空间基标识。', '两个向量前三个坐标中前两项相同，并不保证空间向量相等；第三分量也必须相等。'),
'122-s302': ('空间直线的方向向量和平面的法向量必须非零，平行垂直关系由合法内积或参数约束判断。', '法向量(0,0,0)不能定义唯一平面，不能用零内积直接推任何直线与其垂直。'),
'122-s303': ('抛物线和双曲线标准方程均有独立定义条件和参数范围，先确认焦距等量再讨论开口或分支。', '把x²/a²−y²/b²=1的a设为0会造成分母为零，不构成双曲线方程。'),
'122-s304': ('二项分布需要固定次数、每次只有成败两类、概率不变且各次独立；不能把超几何抽样直接套二项。', '不放回抽取两个球时第二次成功率可能改变，故一般不满足同参数独立伯努利试验。'),
'122-s305': ('超几何分布以有限总体N、成功数K、无放回抽取n建立，k的上下限须随参数同步约束。', '总共5个球且只有1红球，不放回抽2个不可能出现2个红球；不能按独立二项分布计算。'),
'122-s306': ('正态标准化Z=(X−μ)/σ需要σ>0，方差为零属于退化常量而不是可直接使用的标准正态。', '当σ=0时公式除零，不能把常量变量代入标准正态分布表。'),
'122-s307': ('Pearson样本相关系数须双方样本方差非零且成对观测，数值范围为[-1,1]而非因果强度。', '若所有x均为5，则样本x离差平方和为0，Pearson相关系数不可定义而不是等于0。'),
'122-s308': ('比较相关系数的方向与线性强度应区分符号和绝对值，并检查各组样本范围、异常值与可比性。', 'r=-0.9的线性相关强度高于r=0.2，不能用有符号数的大小给强度排序。'),
'123-s402': ('用圆心到直线距离解决位置问题先检查直线一般式中(A,B)非零且圆半径合法。', 'A=B=0的式子0x+0y+1=0不是直线，距离公式分母为零不能继续计算。'),
'123-s404': ('正态分布的均值决定中心、方差决定离散程度；参数标准差必须正而不能等于负数。', '方差4对应标准差2，不是标准差4；负方差没有合法概率解释。'),
'124-s501': ('圆锥曲线几何定义与相应二次方程之间需严格匹配参数约束，退化方程不能沿用非退化焦点性质。', 'x²+y²=0仅表示原点，不是具有正半径的圆或普通非退化二次曲线。'),
'124-s502': ('抛物线距离应用应明确点到焦点与点到准线的等距条件、焦点不在准线上，避免错误取绝对距离。', '焦点与准线距离为零时轨迹可能退化，不能直接套用p>0标准抛物线焦点参数公式。'),
'120-a107': ('三元线性系统应以系数矩阵秩及增广矩阵秩判断有解性，并用自由变量描述齐次解空间。', '系数矩阵为零而常数向量非零的非齐次系统无解，并非一定存在自由变量解。'),
'120-a108': ('三元克拉默法则要求三阶系数行列式不为零，否则即使有解也不能通过除以行列式求出唯一解。', '两行完全相同的三阶系数矩阵行列式为0，克拉默分式分母为0，不能用它求解。'),
'121-a201': ('数列有限极限的和积可按极限运算，商式还需分母极限非零；每项操作必须声明收敛前提。', '若a_n=1，b_n=1/n，则a_n/b_n=n发散，不能写成1/0的合法极限值。'),
'121-a202': ('自然常数e可通过经典收敛数列近似引入，但数值前几项不是对极限存在性的完整证明。', '仅计算(1+1/n)^n在n=1,2,3的值不足以证明其极限存在或等于e。'),
'121-a203': ('微分dy=f′(x)dx是一阶线性主部，须以函数在该点可微为前提，并区分有限增量与微分。', 'f(x)=|x|在x=0不可微，不能在那里写dy=f′(0)dx。'),
'121-b201': ('连续函数在闭区间取最值，可比较驻点、不可导内点和端点；导数算法只生成候选而非自动答案。', 'f(x)=|x|在[-1,1]最小值位于不可导点0，单找f′=0会漏掉。'),
'121-b202': ('特殊黎曼和的等分区间求值要写出网格宽度及取样点，并确认被积函数可积。', '把∑_{k=1}^n k/n当成积分近似而不乘网格宽1/n会得到发散数量级。'),
'121-b203': ('闭圆与闭椭圆是紧集，连续二次函数能取最值；内部驻点及受约束边界须分别求解。', 'f(x,y)=x在闭单位圆盘上最大值1发生在边界而不是内部驻点。'),
'121-b204': ('线性相关指存在不全为零的系数使向量线性组合为零，不能把所有系数为零的平凡组合当证据。', '任意向量组都存在全零系数组合，这不能证明所有向量组线性相关。'),
'121-ec201': ('经济增长的简单线性回归需给出成对样本、残差、变量单位及外推边界；回归显著不自动证明因果。', '仅两期数据拟合出上升直线，不能据此认定政策干预导致了增长。'),
'121-ec202': ('二分类Logistic模型的预测是0到1之间概率，通过对数几率建立线性关系；系数不是概率本身。', '线性预测得分3不是概率3；应经sigmoid变换后再解释为概率。'),
'121-ed201': ('乐器周期性振动模型可用频率f=1/T联系周期与音高，但实测波形可能含谐波和非周期噪声。', '一段含噪录音有强峰值，不足以证明乐器发声是严格单频纯正弦波。'),
}
def require(ok, why):
    if not ok: raise ValueError(why)
def encode(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n'
def candidate_context():
    _,c=previous.prev.prior.prior.originals()
    d=json.loads(previous.OUT.read_text(encoding='utf-8'))
    reviewed={r['candidate_id'] for r in d['records']}
    # The previous checker verifies the 104 earlier reviews, and the 53 new ones.
    # Use the original census formulas to avoid trusting self-reported counters.
    p=previous.prev
    already={'hs-semantic-pilot-'+s[0] for s in p.prior.prior.DETAILS}
    already|={s[0] for s in p.prior.prior.previous.SPECS}
    already|={'hs-semantic-pilot-'+s[0] for s in p.prior.SPECS}
    already|={'hs-semantic-pilot-'+s[0] for s in p.SPECS}
    reviewed|=already & set(c)
    require(len(reviewed)==157,'upstream reviewed set drift')
    return c,reviewed
def build():
    c,reviewed=candidate_context()
    pages=previous.prev.prior.prior.previous.source_pages()
    rows=[]; locks={}
    for suffix,(context,negative) in R.items():
        k='hs-semantic-pilot-'+suffix
        require(k in c and k not in reviewed,'unknown or previously reviewed '+k)
        require(len(context)>=30 and len(negative)>=26,'unreasoned dossier '+k)
        src=c[k]['source'];page=src['printed_page'];lo=src['start_line'];hi=src['end_line']
        raw=pages[page][lo-1:hi]
        require(len(raw)==hi-lo+1 and raw,'unavailable original lines '+k)
        lock={'page':page,'start_line':lo,'end_line':hi,
              'line_sha256':[hashlib.sha256(t.encode()).hexdigest() for t in raw],
              'span_sha256':hashlib.sha256('\n'.join(raw).encode()).hexdigest()}
        locks[k]=lock
        rows.append({'candidate_id':k,'track':c[k]['course_track'],
              'proposed_objective':c[k]['proposed_objective'],
              'contextual_interpretation':context,'boundary_or_counterexample':negative,
              'source_lock':lock,'source_pdf_sha256':previous.prev.prior.prior.provenance.old.previous.base_scope.evidence.PDF_SHA,
              'source_evidence_status':'ORIGINAL_LINE_HASH_CHECKED_EDITORIAL_INTERPRETATION_PENDING',
              'source_may_be_partial_line':lo==hi,
              'teacher_review_status':'REVIEW_PENDING','teacher_signature':None,
              'official_atom_id':None,'student_authoritative':False,'mathematics_formally_certified':False})
    checked=reviewed|set(locks)
    tracks=previous.prev.TRACKS
    by={t: {'historical_editorial_candidates':sum(v['course_track']==t for v in c.values()),
            'context_checked':sum(k in checked and v['course_track']==t for k,v in c.items()),
            'not_checked':sum(k not in checked and v['course_track']==t for k,v in c.items()),
            'official_atom_denominator':None,'teacher_approved':0} for t in tracks}
    d={'batch':131,'standard_version':'2017 edition, 2020 revision',
       'historical_editorial_candidates':239,'reviewed_before':157,
       'new_context_reviews':len(rows),'context_reviewed_total':len(checked),
       'remaining_context_reviews':239-len(checked),'curriculum_layout_cues':405,
       'official_atom_denominator':None,'track_official_atom_denominators':{t:None for t in tracks},
       'teacher_approved':0,'student_authoritative':0,'source_pdf_text_embedded':False,
       'counts_by_track':by,'records':rows}
    validate_offline(d,locks)
    return d,locks
def validate_offline(d,locks):
    require(d['batch']==131 and d['historical_editorial_candidates']==239 and
            d['reviewed_before']==157 and d['new_context_reviews']==len(R) and
            d['context_reviewed_total']==157+len(R) and
            d['remaining_context_reviews']==82-len(R) and
            d['curriculum_layout_cues']==405,'inflated historical scope')
    require(d['official_atom_denominator'] is None and
            d['teacher_approved']==d['student_authoritative']==0 and
            d['source_pdf_text_embedded'] is False and
            all(v is None for v in d['track_official_atom_denominators'].values()),'forged official completion')
    require(len(d['records'])==len(locks)==len(R) and
            len({r['candidate_id'] for r in d['records']})==len(R),
            'duplicated/dropped adjudication')
    c,reviewed=candidate_context()
    submitted={r['candidate_id'] for r in d['records']}
    require(submitted.isdisjoint(reviewed),'overlapping historic reviews')
    tracks=previous.prev.TRACKS
    require(set(d['counts_by_track'])==set(tracks) and
            set(d['track_official_atom_denominators'])==set(tracks) and
            sum(v['historical_editorial_candidates'] for v in d['counts_by_track'].values())==239 and
            sum(v['context_checked'] for v in d['counts_by_track'].values())==157+len(R) and
            sum(v['not_checked'] for v in d['counts_by_track'].values())==82-len(R),
            'track census mismatch')
    for track,v in d['counts_by_track'].items():
        expected=[k for k,item in c.items() if item['course_track']==track]
        require(v['historical_editorial_candidates']==len(expected) and
                v['context_checked']==len(set(expected)&(reviewed|submitted)) and
                v['not_checked']==len(set(expected)-(reviewed|submitted)),
                'track membership mismatch '+track)
        require(v['historical_editorial_candidates']==v['context_checked']+v['not_checked'] and
                v['official_atom_denominator'] is None and v['teacher_approved']==0,
                'fake per-track approval '+track)
    for r in d['records']:
        k=r['candidate_id'];suff=k.removeprefix('hs-semantic-pilot-')
        require(suff in R and k in c and k not in reviewed and
                r['track']==c[k]['course_track'] and
                r['proposed_objective']==c[k]['proposed_objective'] and
                r['source_lock']==locks[k] and
                r['contextual_interpretation']==R[suff][0] and
                r['boundary_or_counterexample']==R[suff][1], 'authorial change '+k)
        lock=locks[k]
        require(lock['page']>0 and lock['start_line']>0 and lock['end_line']>=lock['start_line'] and
                len(lock['line_sha256'])==lock['end_line']-lock['start_line']+1 and
                all(re.fullmatch('[0-9a-f]{64}', x) for x in lock['line_sha256']) and
                re.fullmatch('[0-9a-f]{64}',lock['span_sha256']) is not None and
                r['source_pdf_sha256']==previous.prev.prior.prior.provenance.old.previous.base_scope.evidence.PDF_SHA,
                'invalid locked source shape '+k)
        require(r['track'] in tracks and
                r['source_evidence_status']=='ORIGINAL_LINE_HASH_CHECKED_EDITORIAL_INTERPRETATION_PENDING' and
                r['teacher_review_status']=='REVIEW_PENDING' and
                r['teacher_signature'] is None and r['official_atom_id'] is None and
                r['student_authoritative'] is False and
                r['mathematics_formally_certified'] is False,
                'forged teacher or student authority '+k)
    return True
def render(d):
    lines=['# Batch131 — original-line contextual adjudication, not teacher approval','',
      f"New contextual interpretations: {d['new_context_reviews']}; reviewed {d['context_reviewed_total']}/239; remaining {d['remaining_context_reviews']}.",
      'PDFKit source line hashes are recomputed only on authorized Mac. A short source line is not proof of exhaustive official meaning.',
      'Every one of seven official track-level atom denominators remains UNKNOWN. Teacher approvals and student authority remain ZERO.',
      '']
    for t in previous.prev.TRACKS:
        x=d['counts_by_track'][t]
        lines.append(f"- {t}: {x['context_checked']}/{x['historical_editorial_candidates']}; pending {x['not_checked']}; official denominator UNKNOWN")
    for r in d['records']:
        lock=r['source_lock']
        lines.extend(['',f"## {r['candidate_id']} ({r['track']})",
          f"Original PDF printed page {lock['page']} lines {lock['start_line']}-{lock['end_line']}; SHA256 {lock['span_sha256']}",
          'Editorial objective: '+r['proposed_objective'],
          'Pending interpretation: '+r['contextual_interpretation'],
          'Boundary / invalid example: '+r['boundary_or_counterexample']])
    return '\n'.join(lines)+'\n'
def main():
    parser=argparse.ArgumentParser()
    g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument('--write',action='store_true')
    g.add_argument('--check-mac',action='store_true')
    g.add_argument('--check-offline',action='store_true')
    a=parser.parse_args()
    if a.check_offline:
        d=json.loads(DATA.read_text(encoding='utf-8'))
        locks=json.loads(LOCKS.read_text(encoding='utf-8'))
        validate_offline(d,locks)
        require(REPORT.read_text(encoding='utf-8')==render(d),'rendered source audit differs')
        print('OFFLINE_B131_OK; PDF NOT REHASHED; '+str(d['context_reviewed_total'])+'/239 reviewed')
        return
    d,locks=build()
    for p,s in ((DATA,encode(d)),(LOCKS,encode(locks)),(REPORT,render(d))):
        if a.write:
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(s,encoding='utf-8')
        else:
            require(p.exists() and p.read_text(encoding='utf-8')==s,
                    'Mac source fingerprint or editorial content drift '+str(p))
    print('MAC_B131_OK; PDF REHASHED; '+str(d['context_reviewed_total'])+'/239 reviewed; '+str(d['remaining_context_reviews'])+' pending')
if __name__=='__main__':main()
