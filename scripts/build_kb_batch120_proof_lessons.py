#!/usr/bin/env python3
"""Six original condition-complete, teacher-only proof-plus-problem-family manuscripts."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch120_semantic_expansion as candidate
OUT=ROOT/"knowledge/editorial_review/kb_batch120_six_proof_families.json"
MD=ROOT/"docs/evaluation/KB_BATCH120_PROOF_FAMILIES.md"
MATH=ROOT/"docs/evaluation/KB_BATCH120_PROOF_EXAMPLE_EXACT.json"
def e(q,steps,result,check):
    return {"question":q,"steps":steps,"answer":result,"check":check}
def p(key,title,hyp,claim,steps,boundary,negative,examples,hints,near,far):
    return locals()
ROWS=[
p("C105","平面两独立向量唯一分解",
["u,v是同一实二维向量空间中的两个向量，且det[u v]≠0","w是同一实二维向量空间的任意向量；标量系数在实数域"],
"存在唯一实数α,β使w=αu+βv。",
[("建立坐标矩阵","以u,v为列建立2×2矩阵A；行列式不为零，故A有逆矩阵。"),
 ("构造分解","取列向量(α,β)^T=A^{-1}w，则A(α,β)^T=w，即存在分解。"),
 ("证明唯一","若另有一组α',β'，两式相减得A(α-α',β-β')^T=0；左乘A^{-1}知两差皆为零。")],
"两向量线性相关时，不能保证任意w可表示，更不能保证唯一表示。",
"u=(1,0),v=(2,0)时w=(0,1)不可表达；w=(1,0)又有(α,β)=(1,0)和(-1,1)两种分解。",
[e("u=(1,0),v=(0,1),w=(3,-2)，求分解系数。",["矩阵A为单位阵，故A^{-1}w=w。","分别得到α=3,β=-2。"],"(3,-2)","3(1,0)-2(0,1)=(3,-2)。"),
 e("u=(1,1),v=(1,-1),w=(4,0)，求分解系数。",["列出α+β=4，α-β=0。","两式相加得2α=4，继而β=2。"],"(2,2)","2(1,1)+2(1,-1)=(4,0)。")],
["先检查基向量是否真的不共线。","把未知系数写成二元线性方程组，核对行列式。","求出一组系数后，使用可逆性证明它唯一。"],
"改变w为(2,6)，在u=(1,1),v=(1,-1)的同一基下求系数。",
"在二维屏幕坐标变换中，若两个轴方向几乎平行，虽不完全相同，计算会有什么数值稳定性问题？"),
p("C107","余弦定理的向量证明",
["ABC为非退化的欧氏平面三角形，三边a=|BC|、b=|CA|、c=|AB|均正","A为边b和c的夹角，0<A<π；数量积及向量模长使用欧氏度量"],
"a²=b²+c²−2bc cos A。",
[("构造同起点向量","从A点出发置u=向量AB，v=向量AC，其模长分别为c和b，夹角为A。"),
 ("表达对边","向量BC=v-u，故a²=|v-u|²=(v-u)·(v-u)。"),
 ("展开数量积","双线性、对称性给出|v-u|²=|v|²+|u|²−2u·v。"),
 ("代入角度","u·v=bc cos A，得到a²=b²+c²−2bc cos A。")],
"边长无法组成非退化三角形时不能使用三角形内角解释该式；A必须是两条从A出发边的夹角。",
"a=5,b=1,c=2不满足三角形不等式，不能把由代数倒推的余弦值当作真实三角形内角。",
[e("b=3,c=4,A=π/2，求a。",["代入cos(π/2)=0。","a²=3²+4²=25，a取正值得5。"],"5","正交两边构成3-4-5直角三角形。"),
 e("b=2,c=2,A=2π/3，求a²。",["cos(2π/3)=-1/2。","a²=4+4−8(-1/2)=12。"],"12","构成的三角形非退化且a=2sqrt(3)满足三角形不等式。")],
["先确定所求边的对角，不要把邻角错配。","用两条从同一顶点出发的向量表示第三边。","平方展开并代入点积定义，最后检查长度非负。"],
"已知b=4,c=5,A=π/3，求a并检查三角形不等式。",
"机器人两条连杆末端间距可由夹角计算，但若坐标中混用弧度与角度会产生什么错误？"),
p("S105","空间两点距离公式",
["空间两点P,Q的坐标属于同一正交直角坐标系","三个坐标轴单位长度一致，坐标差Δx,Δy,Δz均为实数"],
"|PQ|=sqrt((x_Q-x_P)²+(y_Q-y_P)²+(z_Q-z_P)²)。",
[("确定位移","同一坐标系下的差向量为Q-P=(Δx,Δy,Δz)。"),
 ("利用正交性","位移的平方模长是点积(Q-P)·(Q-P)=Δx²+Δy²+Δz²。"),
 ("取非负平方根","欧氏距离按定义非负，因此取平方和的非负平方根作为距离。")],
"在斜交坐标或各轴单位尺度不同的情况下，平方和一般不是物理距离平方。",
"若横轴一坐标单位代表2米，P=(0,0,0)、Q=(1,0,0)，实际距离2米而直接平方和给1。",
[e("P=(1,2,3),Q=(4,6,15)，求PQ。",["坐标差为(3,4,12)。","距离sqrt(9+16+144)=13。"],"13","13²=3²+4²+12²=169。"),
 e("P=(0,0,0),Q=(1,2,2)，求PQ。",["位移向量(1,2,2)。","距离sqrt(1+4+4)=3。"],"3","3²=1²+2²+2²。")],
["先确保两个点位于同一正交坐标系。","逐轴作坐标差，不能错把坐标相加。","平方求和后取非负平方根，检验单位。"],
"计算P=(-2,1,1)与Q=(2,4,13)的欧氏距离。",
"无人机地理定位经纬度是球面角度，为什么不能直接把角度差代入三维米制距离公式？"),
p("S106","三维标准正交基坐标分解",
["e1,e2,e3是R³上的正交单位基，彼此内积δij","v是同一个带欧氏内积的三维实向量"],
"v=(v·e1)e1+(v·e2)e2+(v·e3)e3，而且这三个系数唯一。",
[("正交投影系数","设v=Σ c_i e_i，对等式点乘e_j，正交单位条件使v·e_j=c_j。"),
 ("说明分解存在","三条两两正交的非零向量在三维空间线性无关，因此构成R³一组基，任意v可分解。"),
 ("代回得明确形式","将c_i=v·e_i代回得到所列正交分解公式。"),
 ("唯一性","若还有另一组系数，同一向量对每个e_j点乘所得结果不变，故两组坐标相等。")],
"在非单位正交基下投影系数要除以|ei|²；在非正交基下直接套点积系数是错误的。",
"取e1=(2,0,0),e2=(0,1,0),e3=(0,0,1)，v=(2,0,0)时v·e1=4，直接乘e1得到(8,0,0)而非v。",
[e("标准基下v=(2,-3,4)，写成ei之和。",["标准正交基的点积坐标就是2,-3,4。","v=2e1-3e2+4e3。"],"(2,-3,4)","按坐标分量逐项相加，最终所得向量仍为v。"),
 e("e1=(0,1,0),e2=(-1,0,0),e3=(0,0,1)，v=(3,2,-1)，求系数。",["点积得v·e1=2，v·e2=-3，v·e3=-1。","代回2e1-3e2-e3=(3,2,-1)。"],"(2,-3,-1)","旋转的正交基保持点积和长度。")],
["检查正交、单位、维度和是否为基。","对每个基向量求点积得到对应坐标。","代回线性组合验证，不可在非正交基直接使用该方法。"],
"标准正交基下v=(1,2,2)的坐标与长度分别是多少？",
"惯导传感器坐标旋转后仍为正交基，但如果标定矩阵含缩放，坐标公式需要怎样修正？"),
p("A108","三阶克拉默法则及分母条件",
["A为实3×3方阵，b属于R³，D=det(A)≠0","A_i表示用b替换A的第i列得到的方阵，i=1,2,3"],
"方程Ax=b存在唯一解，且x_i=det(A_i)/D。",
[("先确认可逆","D不为0保证A可逆，故存在唯一解x=A^{-1}b。"),
 ("用列线性组合","因为b=Σ_j x_j a_j（a_j为A第j列），将它代入A_i的第i列。"),
 ("利用行列式多线性","det(A_i)=Σ_j x_j det(a1,…,a_j,…,a3)；其中j≠i时有相同的两列，行列式为零。"),
 ("保留唯一非零项","只余j=i的项，得det(A_i)=x_i det(A)=x_iD；D≠0，合法相除即得公式。")],
"当D=0时不能直接计算商；线性系统可能无解或有无穷解，需要增广矩阵秩判别。",
"A=diag(1,1,0)，b=(0,0,1)时系统无解；b=(0,0,0)时存在无穷多解，均不能用克拉默分式。",
[e("A=diag(2,3,4),b=(4,6,8)，求x。",["D=24≠0，系统唯一可解。","逐行得到2x1=4，3x2=6，4x3=8。"],"(2,2,2)","Ax=(4,6,8)，也与克拉默列替换的detAi/D一致。"),
 e("A=diag(1,2,5),b=(3,4,10)，求x。",["D=10≠0。","分别得到x1=3,x2=2,x3=2。"],"(3,2,2)","代回Ax=(3,4,10)，符合唯一解条件。")],
["核实系数矩阵必须是方阵且D不为零。","用b替换要找的未知量对应列，不是对应行。","求每个det(Ai)/D后代回原方程，若D=0改用秩分析。"],
"已知A=diag(3,2,1),b=(9,4,-2)，用克拉默法求x。",
"三元数据拟合中系数矩阵高度接近奇异，即使D非零，数值计算仍可能不稳定，为什么？"),
p("ED105","十二平均律的等比频率比",
["一个八度被分成12个等频率比的半音级，基础频率f0>0","每一级的倍率r为正实数，十二级后的频率规定是2f0"],
"唯一正倍率r=2^(1/12)，因此第k级频率为f_k=f0·2^(k/12)，k为整数。",
[("把相同倍率转成递推","相邻级满足f_{k+1}=r f_k，反复应用得f_{12}=f0 r^12。"),
 ("使用八度条件","依据f12=2f0并且f0>0，约去f0得r^12=2。"),
 ("唯一正解","r>0时函数r↦r^12严格递增，因此正解唯一为2^(1/12)。"),
 ("导出通项","从f0出发连乘k次得到f_k=f0·2^(k/12)，负k由反向倍率同理成立。")],
"该结论依赖十二等分和每步相同频率比；不等同于每步加相同Hz，也不能直接套到不同调律系统。",
"从440Hz到880Hz若每步加440/12Hz，虽然末端仍是880Hz，但相邻频率比逐步改变，不满足十二平均律。",
[e("基频440Hz，升12个半音是多少Hz？",["每一级频率乘2^(1/12)。","十二次连乘恰为2，故440×2=880Hz。"],"880","(2^(1/12))^12=2。"),
 e("基频220Hz，升24个半音是多少Hz？",["24半音是两个八度，倍率为2^(24/12)=4。","220×4=880Hz。"],"880","两次八度倍频220→440→880。")],
["先区分等比频率与等差Hz。","根据12次相同倍率后翻倍建立r^12=2。","取正根并连乘次数，检查指数与频率单位。"],
"基频330Hz，降12个半音的频率是多少？",
"若某音阶有19等分八度，频率比的公式需要怎样重新推导？"),
]
def demand(ok,msg):
    if not ok: raise ValueError(msg)
def build():
    catalog={r["local_key"]:r for r in json.loads(candidate.OUT.read_text(encoding="utf-8"))["candidates"]}
    rows=[]
    for unit in ROWS:
        key=unit["key"]
        demand(key in catalog and catalog[key]["kind"]=="theorem" or key=="ED105" and key in catalog,"unmatched candidate "+key)
        demand(len(unit["hyp"])>=2 and len(unit["steps"])>=3 and len(unit["examples"])==2
               and len(unit["hints"])==3 and len(unit["near"])>=20 and len(unit["far"])>=20,
               "incomplete proof/teacher problem family "+key)
        c=catalog[key]
        rows.append({"review_id":"kb120-proof-family-"+key.lower(),
          "candidate_id":c["id"],"course_track":c["course_track"],"source":c["source"],
          "title":unit["title"],"hypotheses":unit["hyp"],"claim":unit["claim"],
          "proof_steps":[{"claim":a,"justification":b} for a,b in unit["steps"]],
          "boundary":unit["boundary"],"counterexample":unit["negative"],
          "teacher_examples":unit["examples"],"hint_ladder":unit["hints"],
          "transfer":{"near":unit["near"],"far":unit["far"]},
          "review_status":"REVIEW_PENDING","teacher_evidence":None,
          "general_formal_proof_certified":False,"student_authoritative":False,
          "visibility":"TEACHER_ONLY"})
    validate(rows)
    return rows
def validate(rows):
    expected={u["key"] for u in ROWS}
    demand(len(rows)==len(expected)==6 and {r["review_id"].rsplit("-",1)[1].upper() for r in rows}==expected,
           "duplicate/missing review family")
    for r in rows:
        demand(r["review_status"]=="REVIEW_PENDING" and r["teacher_evidence"] is None
               and r["general_formal_proof_certified"] is False and r["student_authoritative"] is False
               and r["visibility"]=="TEACHER_ONLY","fake proof/authority certification")
        demand(len(r["hypotheses"])>=2 and len(r["proof_steps"])>=3 and
               all(len(x["justification"])>=17 for x in r["proof_steps"]) and
               len(r["boundary"])>=20 and len(r["counterexample"])>=25,
               "missing mathematical conditions or counterexample")
        demand(len(r["teacher_examples"])==2 and
               all(len(x["steps"])>=2 and len(x["check"])>=12 for x in r["teacher_examples"])
               and len(r["hint_ladder"])==3 and len(r["transfer"]["near"])>=20
               and len(r["transfer"]["far"])>=20, "missing complete problem-family components")
        original=next(u for u in ROWS if "kb120-proof-family-"+u["key"].lower()==r["review_id"])
        c=next(x for x in json.loads(candidate.OUT.read_text(encoding="utf-8"))["candidates"]
               if x["local_key"]==original["key"])
        demand(r["candidate_id"]==c["id"] and r["course_track"]==c["course_track"]
               and r["source"]==c["source"],"source/candidate mismatch")
        demand(r["title"]==original["title"] and r["hypotheses"]==original["hyp"]
               and r["claim"]==original["claim"]
               and r["proof_steps"]==[{"claim":a,"justification":b} for a,b in original["steps"]]
               and r["teacher_examples"]==original["examples"]
               and r["hint_ladder"]==original["hints"]
               and r["transfer"]=={"near":original["near"],"far":original["far"]}
               and r["boundary"]==original["boundary"] and r["counterexample"]==original["negative"],
               "manuscript/catalog mismatch")
    return True
def exact_examples():
    M=S.Matrix; R=S.Rational
    examples={
        "C105":[M.hstack(M([1,0]),M([0,1])).inv()*M([3,-2])==M([3,-2]),
                M.hstack(M([1,1]),M([1,-1])).inv()*M([4,0])==M([2,2])],
        "C107":[S.simplify(S.sqrt(3**2+4**2-2*3*4*S.cos(S.pi/2)))==5,
                S.simplify(2**2+2**2-2*2*2*S.cos(2*S.pi/3))==12],
        "S105":[S.sqrt(3**2+4**2+12**2)==13,S.sqrt(1**2+2**2+2**2)==3],
        "S106":[2*M([1,0,0])-3*M([0,1,0])+4*M([0,0,1])==M([2,-3,4]),
                2*M([0,1,0])-3*M([-1,0,0])-M([0,0,1])==M([3,2,-1])],
        "A108":[M.diag(2,3,4).inv()*M([4,6,8])==M([2,2,2]),
                M.diag(1,2,5).inv()*M([3,4,10])==M([3,2,2])],
        "ED105":[S.simplify((S.Integer(2)**R(1,12))**12)==2,
                 S.simplify(220*(S.Integer(2)**R(24,12)))==880],
    }
    for key, checks in examples.items():
        demand(all(bool(x) for x in checks),"invalid exact worked example "+key)
    return {"batch":120,"exact_teacher_example_checks":sum(map(len,examples.values())),
            "general_formal_proofs_certified":0,"teacher_approved":0,
            "examples_by_candidate":{key:len(checks) for key,checks in examples.items()}}
def render(rows):
    out=["# Batch120｜6份严格条件证明及题族（教师候审）","",
         "**原创编辑稿，未获数学教师认证；有限SymPy例题验证不构成通用定理证明；教师完整答案不能进入学生独立挑战。**",""]
    for r in rows:
        out += ["## "+r["title"],"","**前提**："+"；".join(r["hypotheses"]),"",
                "**结论**："+r["claim"],""]
        for i,x in enumerate(r["proof_steps"],1):
            out += [f"{i}. **{x['claim']}**：{x['justification']}"]
        out += ["","**不适用边界**："+r["boundary"],"",
                "**反例**："+r["counterexample"],"","### 教师例题",""]
        for i,x in enumerate(r["teacher_examples"],1):
            out += [f"{i}. {x['question']}","  - "+"；".join(x["steps"]),
                    "  - 答案："+x["answer"],"  - 独立核对："+x["check"]]
        out += ["","**阶梯提示**："+ " → ".join(r["hint_ladder"]), "",
                "**近迁移**："+r["transfer"]["near"],"",
                "**远迁移**："+r["transfer"]["far"],""]
    return "\n".join(out)
def main():
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true")
    g.add_argument("--check",action="store_true")
    mode=ap.parse_args()
    rows=build()
    products={OUT:candidate.serial(rows),MD:render(rows),MATH:candidate.serial(exact_examples())}
    for path,txt in products.items():
        if mode.write:path.write_text(txt,encoding="utf-8")
        else:demand(path.exists() and path.read_text(encoding="utf-8")==txt,
                    "proof family or exact oracle drift "+str(path))
    print("Batch120 six teacher-only proof families, 12 exact worked-example checks, zero formal certification")
if __name__=="__main__":main()
