#!/usr/bin/env python3
"""Batch132: Mac-only elective scope contextual audit; 39 independently reasoned dossiers.

Original licensed PDF rows are used ONLY to recompute fingerprints on the Mac.
Neither these editable teaching objectives nor the fingerprints are official curriculum
atoms or approvals. Offline CI checks commitments, not unavailable original PDF.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_kb_batch131_contexts as prior
OUT=ROOT/'docs/evaluation/KB_BATCH132_ELECTIVE_CONTEXTS.json'
LOCK=ROOT/'curriculum/highschool_math/k00_batch132_source_fingerprints.json'
MD=ROOT/'docs/evaluation/KB_BATCH132_ELECTIVE_CONTEXTS.md'

# Independent curricular interpretation and a concrete false inference/degeneracy.
# None is presented as a quotation of the copyright source.
R={
'121-a204':('平面的一般方程应由非零法向量和经过点约束确定；法向量整体乘同一非零常数不改变平面。','法向量为零时0x+0y+0z=1无解，不能称为确定了空间平面。'),
'121-a205':('线性等距变换的矩阵必须保持内积，等价于正交条件QᵀQ=I；一般平移须用仿射变换表达。','矩阵diag(2,1)把(1,0)长度从1变为2，绝非等距；把平移说成线性映射也有误。'),
'121-b205':('非齐次方程组Ax=b的可解性要求rank(A)=rank([A|b])，唯一性还需秩等于未知数个数。','0x=1的系数矩阵秩为0而增广矩阵秩为1，无解；秩相等不自动代表唯一解。'),
'121-ec203':('社会调查需从研究问题、目标总体、抽样框、问卷或访谈设计逐步制定质量审查规则。','只抽取自愿答卷却直接将样本比例当作整个地区居民比例，遗漏覆盖与自选偏差。'),
'121-ec204':('单选问卷选项应明确时间界限并互斥、尽量穷尽且措辞中立；多选问题必须明确可重复勾选。','年龄选项10—20岁和20—30岁在20岁处重叠，不能充当互斥的单选分类。'),
'121-ec205':('频数需以样本量核对；相对频率分母是合法有效观测数，分组直方图与普通柱状图必须区分。','不等宽组距下直接比较柱形高度而非频率密度，会误读各组概率质量。'),
'121-ed202':('图形变换中平移是向量加法、旋转通常保持距离、缩放改变长度；应明确旋转中心和坐标系。','平面图形绕原点旋转90度不等于每个点的坐标都加90，负缩放系数还可能反射。'),
'121-ed203':('不同体育成绩比较需首先统一量纲、测量设备和赛事情境；标准化也要说明参考群体与分布假设。','把100米用时12秒直接与跳高1.8米作差，数值没有共同可解释的单位。'),
'122-a301':('二阶导数提供局部弯曲趋势的信息；仅由某一点二阶导数为零不能确定拐点或全局凸性。','f(x)=x⁴在x=0二阶导数为0，但两侧都保持凸性，并非拐点。'),
'122-a302':('若f在闭区间连续，则F(x)=∫aˣf(t)dt可导且F′(x)=f(x)；换元及端点需注意前提。','将不连续被积函数在跳点直接套用F′=f，而不检查连续条件，是不合法的推断。'),
'122-a303':('空间直线参数式r=r₀+tv必须给定一个点和非零方向向量；不同参数化可表示同一直线。','若方向向量v=0，所得轨迹只有一个点，不是通过该点的一整条直线。'),
'122-b301':('黎曼和须含分割宽度Δx，有向积分计符号；将积分解释为几何面积时要分正负区间。','∫₋₁¹x dx=0，但曲线与x轴所围几何面积是1，不能因为有向积分为零而说面积为零。'),
'122-b302':('求二元函数全局极值时应检查内部驻点、不可导内点及全部受约束边界，尤其验证定义域是否紧。','f(x,y)=x在单位圆盘内梯度永不为零，但闭圆盘仍有最大值1和最小值−1。'),
'122-b303':('三元齐次线性方程组总有零解，非零解存在与否由秩和自由变量数决定。','单位矩阵对应x=y=z=0，不能因为是齐次系统就声称一定存在非零解。'),
'122-ec301':('指数情景模型N(t)=N₀eᵏᵗ需规定N₀>0、参数单位和适用区间，并区分模型拟合与预测证据。','用拟合的恒定增长率长期外推有限资源环境，会无依据地产生无限增长结论。'),
'122-ec302':('理想抛体轨迹模型需要恒定重力、指定初速度、忽略空气阻力与坐标轴等前提。','存在强气动力的球或火箭轨迹不能未经校验就套用常加速度无阻力抛体方程。'),
'122-ec303':('圆柱螺旋线可用r(t)=(Rcos t,Rsin t,ct)建模，t需为弧度参数、R和c的长度单位一致。','把t误当角度数而直接代入以弧度为输入的三角函数，会导致周期和位置全错。'),
'122-ed301':('调查方案必须将目标总体、抽样框及实际可接触总体分开记录，并明确代表性缺口。','把只覆盖网络用户的抽样框当成所有老人群体，会遗漏无法上网的目标对象。'),
'122-ed302':('调查可行性需评估样本量、成本、访问许可、未成年人保护和时间安排，并预设不能实施的备选方案。','未经授权收集学生身份证号码即使样本很大，也不构成合规可执行的调查设计。'),
'122-ed303':('观察、访谈和问卷分别可能存在观察者、访员以及措辞和自报告偏差，交叉验证仍需透明记录。','把同一人对有引导性问题的口头答复视为没有测量误差的客观真值，是错误的。'),
'123-a401':('有限极限运算需分别确立各序列的有限极限；商式要求分母极限非零才能使用商法则。','aₙ=1、bₙ=1/n，则aₙ/bₙ=n发散，不能把商极限写为1/0。'),
'123-a402':('闭区间连续函数取极值，求导只能产生内部驻点候选，须比较端点与不可导点的函数值。','f(x)=x在[0,1]最大值出现在端点1，即使区间内没有驻点也仍有全局最大值。'),
'123-a403':('直线与平面的代数判别可将直线参数式代入平面方程，检查方向向量与法向量内积及初始点。','方向向量与法向量内积为0时，直线可能平行且不交，也可能完全在平面内。'),
'123-a404':('连续随机变量的单点概率一般为零，区间概率是密度在区间上的积分；正态σ必须正。','若连续均匀X∼U(0,1)，密度f(0.5)=1但P(X=0.5)=0，不能混为概率1。'),
'123-a405':('带截距一元最小二乘回归须有非零自变量离差平方和；线性拟合不自动证明因果关系。','所有x都等于3时斜率公式分母为零，不能声称由最小二乘唯一确定斜率。'),
'123-b401':('面积计算先分段识别曲线与x轴或两曲线的上下关系，几何面积应对纵向距离取绝对值。','函数f(x)=x在[-1,1]的定积分为0，但绝对面积∫|x|dx=1。'),
'123-b402':('非空紧凸多边形上线性目标至少有顶点达到最优值，边上所有点也可能同时最优。','目标f(x,y)=x在矩形[0,1]²的整条边x=1都最优，不能声称唯一顶点最优。'),
'123-b403':('两条非平行空间直线的最短距离可用连接向量在共同法向量叉积方向上的投影求值。','平行方向向量叉积为零，混合积距离式分母为零；必须改用平行直线距离公式。'),
'123-b404':('三阶行列式为零等价其三个列向量线性相关；该判据只针对方阵和相应维数。','矩阵含两列相同向量时行列式为零，不可据此推断所对应三元方程组一定无解。'),
'123-b405':('三元克拉默法则仅在det(A)≠0时适用；行列式为零应改用秩或行消元分析解空间。','两条重复线性方程使det(A)=0，即使方程相容也不能用0作克拉默分母。'),
'123-ec401':('对数线性生产模型取对数要求原始产出及投入严格为正；系数解释为弹性需要正确函数形式。','当投入量为0时ln(0)不存在，不能把带零值样本无处理地纳入对数线性回归。'),
'123-ec402':('调查数据的相关与回归只支持指定测量及采样条件下的关联描述，因果结论需设计额外识别证据。','发现运动量和睡眠时长正相关，不能直接断言增加运动是睡眠改善的唯一原因。'),
'123-ed401':('运动轨迹的速度是位置对时间的导数、加速度是速度导数；必须明确坐标系和时间单位。','只看相邻视频帧的位移而未除时间间隔，就把像素差称为米每秒速度，是量纲错误。'),
'123-ed402':('体育设施尺度测量需要统一长度、面积及角度单位，图纸比例尺只适用于对应维度的换算。','图纸线性比例放大2倍后面积应放大4倍，不能按线性比例只放大2倍。'),
'124-a501':('一点处导数是差商在该点的双侧有限极限，可导时可解释为切线斜率或瞬时变化率。','f(x)=|x|在0处左右差商极限分别是−1和1，不能声称存在唯一切线斜率。'),
'124-a502':('正交变换与平移组成的欧氏等距变换保持任意两点间距离；普通各向异性缩放不保持距离。','矩阵diag(2,1)把(0,0)与(1,0)的距离从1变成2，不能称为等距。'),
'124-a503':('显著性检验应在观察数据前规定H₀、H₁、显著水平α、统计量与拒绝域，避免事后挑选。','看完样本结果后随意改变拒绝阈值并报告预先控制的I类错误率，是无效的。'),
'124-b501':('三维内积以标量衡量投影，叉积以向量表征有向面积；用夹角要排除零向量。','若u=0，则cosθ=(u·v)/(|u||v|)除零，不能宣称它与任何非零向量夹角为90度。'),
'124-b502':('正交试验设计应检查水平编码、列间平衡及交互作用别名结构；正交列本身不保证无混杂。','只看主效应列互相正交，便声称未安排的交互效应也全部独立可估，缺乏依据。'),
}
TRACKS=prior.previous.prev.TRACKS
def require(ok,msg):
    if not ok: raise ValueError(msg)
def encode(x):return json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+'\n'
def historical():
    c,reviewed=prior.candidate_context()
    reviewed|={'hs-semantic-pilot-'+s for s in prior.R}
    require(len(c)==239 and len(reviewed)==200,'upstream pilot or historical review drift')
    remain=set(c)-reviewed
    require(set('hs-semantic-pilot-'+s for s in R)==remain and len(remain)==39,'not all 39 electives reviewed exactly once')
    return c,reviewed
def fingerprint(pages,src):
    p=src['printed_page'];lo=src['start_line'];hi=src['end_line']
    raw=pages[p][lo-1:hi]
    require(len(raw)==hi-lo+1 and bool(raw),'original source lines missing')
    return {'page':p,'start_line':lo,'end_line':hi,
            'line_sha256':[hashlib.sha256(x.encode()).hexdigest() for x in raw],
            'span_sha256':hashlib.sha256('\n'.join(raw).encode()).hexdigest()}
def build():
    c,reviewed=historical()
    pages=prior.previous.prev.prior.prior.previous.source_pages()
    rows=[]; locks={}
    for suffix,(interpretation,negative) in R.items():
        k='hs-semantic-pilot-'+suffix;v=c[k]
        require(len(interpretation)>=30 and len(negative)>=30,'empty reasoning '+k)
        lock=fingerprint(pages,v['source']);locks[k]=lock
        rows.append(dict(candidate_id=k,track=v['course_track'],proposed_objective=v['proposed_objective'],
                         contextual_interpretation=interpretation,boundary_or_counterexample=negative,
                         source_lock=lock,source_pdf_sha256=prior.previous.prev.prior.prior.provenance.old.previous.base_scope.evidence.PDF_SHA,
                         source_evidence_status='ORIGINAL_LINE_HASH_CHECKED_EDITORIAL_INTERPRETATION_PENDING',
                         teacher_review_status='REVIEW_PENDING',teacher_signature=None,official_atom_id=None,
                         student_authoritative=False,mathematics_formally_certified=False))
    approved=set(locks)|reviewed
    counts={t:{'historical_editorial_candidates':sum(v['course_track']==t for v in c.values()),
               'context_checked':sum(k in approved and v['course_track']==t for k,v in c.items()),
               'not_checked':sum(k not in approved and v['course_track']==t for k,v in c.items()),
               'official_atom_denominator':None,'teacher_approved':0} for t in TRACKS}
    data={'batch':132,'scope':'HISTORICAL_EDITORIAL_CANDIDATE_CONTEXTS_ONLY',
          'historical_editorial_candidates':239,'reviewed_before':200,'new_context_reviews':len(rows),
          'context_reviewed_total':len(approved),'remaining_context_reviews':239-len(approved),
          'curriculum_layout_cues':405,'official_atom_denominator':None,
          'track_official_atom_denominators':{t:None for t in TRACKS},'teacher_approved':0,
          'student_authoritative':0,'source_pdf_text_embedded':False,
          'count_by_track':counts,'records':rows}
    validate(data,locks)
    return data,locks
def validate(d,locks):
    c,reviewed=historical()
    ids={'hs-semantic-pilot-'+s for s in R}
    require(d['batch']==132 and d['scope']=='HISTORICAL_EDITORIAL_CANDIDATE_CONTEXTS_ONLY' and
            d['historical_editorial_candidates']==239 and d['reviewed_before']==200 and
            d['new_context_reviews']==39 and d['context_reviewed_total']==239 and
            d['remaining_context_reviews']==0 and d['curriculum_layout_cues']==405,'false scope statistics')
    require(d['official_atom_denominator'] is None and
            set(d['track_official_atom_denominators'])==set(TRACKS) and
            all(v is None for v in d['track_official_atom_denominators'].values()) and
            d['teacher_approved']==d['student_authoritative']==0 and
            d['source_pdf_text_embedded'] is False,'forged official/teacher/student status')
    require(len(d['records'])==len(locks)==39 and
            {r['candidate_id'] for r in d['records']}==ids==set(locks) and
            ids.isdisjoint(reviewed),'missing/duplicated elective')
    require(set(d['count_by_track'])==set(TRACKS),'missing track')
    for t in TRACKS:
        expected={k for k,v in c.items() if v['course_track']==t}
        v=d['count_by_track'][t]
        require(v=={'historical_editorial_candidates':len(expected),
                    'context_checked':len(expected),'not_checked':0,
                    'official_atom_denominator':None,'teacher_approved':0},'wrong track count '+t)
    for r in d['records']:
        k=r['candidate_id'];s=k.removeprefix('hs-semantic-pilot-')
        require(r['track']==c[k]['course_track'] and r['proposed_objective']==c[k]['proposed_objective'] and
                r['contextual_interpretation']==R[s][0] and
                r['boundary_or_counterexample']==R[s][1],'edited mathematics without review '+k)
        lk=locks[k]
        require(r['source_lock']==lk and lk['page']>0 and lk['start_line']>0 and
                lk['end_line']>=lk['start_line'] and
                len(lk['line_sha256'])==lk['end_line']-lk['start_line']+1 and
                re.fullmatch('[0-9a-f]{64}',lk['span_sha256']) is not None and
                all(re.fullmatch('[0-9a-f]{64}',h) for h in lk['line_sha256']), 'corrupt source commitment '+k)
        require(r['source_pdf_sha256']==prior.previous.prev.prior.prior.provenance.old.previous.base_scope.evidence.PDF_SHA and
                r['source_evidence_status']=='ORIGINAL_LINE_HASH_CHECKED_EDITORIAL_INTERPRETATION_PENDING' and
                r['teacher_review_status']=='REVIEW_PENDING' and r['teacher_signature'] is None and
                r['official_atom_id'] is None and r['student_authoritative'] is False and
                r['mathematics_formally_certified'] is False,'fake authority '+k)
    return True
def render(d):
    lines=['# Batch132 — elective editorial candidate source contextualization',
           '','This is a provisional historical *editorial* source audit, **not** a comprehensive syllabus atom census.',
           'PDFKit original-line digests rehashed on the Mac, not in GitHub CI. Digests prove source identity, not the correctness of an interpretation.',
           'Original protected syllabus text is NOT stored. No teacher approval, formal proof certification or student-authoritative publication.',
           f"Historical contexts: {d['context_reviewed_total']}/239, newly reviewed {d['new_context_reviews']}; pending historical contexts {d['remaining_context_reviews']}.",
           'Every one of the seven track **official knowledge-atom denominators remains UNKNOWN**.','']
    for t in TRACKS:
        a=d['count_by_track'][t]
        lines.append(f"- {t}: {a['context_checked']}/{a['historical_editorial_candidates']} historic contexts; official denominator UNKNOWN")
    for r in d['records']:
        lk=r['source_lock']
        lines.extend(['',f"## {r['candidate_id']} — {r['track']}",
              f"Printed page {lk['page']} lines {lk['start_line']}-{lk['end_line']}; SHA256 {lk['span_sha256']}",
              'Editorial objective: '+r['proposed_objective'],
              'Pending contextual interpretation: '+r['contextual_interpretation'],
              'Counterexample / invalid condition: '+r['boundary_or_counterexample']])
    return '\n'.join(lines)+'\n'
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--write',action='store_true');g.add_argument('--check-mac',action='store_true');g.add_argument('--check-offline',action='store_true')
    a=p.parse_args()
    if a.write:
        d,locks=build()
        OUT.write_text(encode(d),encoding='utf-8')
        LOCK.write_text(encode(locks),encoding='utf-8')
        MD.write_text(render(d),encoding='utf-8')
        print('WROTE',len(d['records']), 'historic elective contextual reviews')
    else:
        d=json.loads(OUT.read_text(encoding='utf-8'))
        locks=json.loads(LOCK.read_text(encoding='utf-8'))
        validate(d,locks);require(MD.read_text(encoding='utf-8')==render(d),'report drift')
        if a.check_mac:
            freshly,fresh_locks=build()
            require(d==freshly and locks==fresh_locks,'Original Mac PDF source line hash mismatch')
        print('PASS',('Mac original source rehashed' if a.check_mac else 'offline committed evidence only'),len(d['records']))
if __name__=='__main__': main()
