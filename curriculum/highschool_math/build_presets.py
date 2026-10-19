"""High-school mathematics visual lab presets; no arbitrary user code evaluation."""
import json
from extend_v09 import extra_presets
from extend_v010 import extra_presets as foundation_presets
from extend_v011 import extra_presets as sequence_presets
from extend_v011b import extra_presets as extrema_presets
from extend_v012 import extra_presets as probability_presets
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def P(key,label,lo,hi,value,step=.1):
    return {"key":key,"label":label,"min":lo,"max":hi,"value":value,"step":step}

PRESETS=[
("fn-linear","function_2d","一次函数与斜率","y=mx+b","y=mx+b",[P("m","斜率 m",-3,3,1),P("b","截距 b",-4,4,0)],"线性参数"),
("fn-quadratic","function_2d","二次函数及顶点","y=a(x-h)^2+k","y=a(x-h)^2+k",[P("a","开口 a",-2,2,.7),P("h","顶点横坐标 h",-4,4,1),P("k","顶点纵坐标 k",-4,4,-1)],"顶点、对称轴与极值"),
("fn-cubic","function_2d","三次函数与导数","y=a(x^3-3x)+k","y=a(x^3-3x)+k",[P("a","系数 a",-.6,.6,.2,.05),P("k","纵向平移 k",-4,4,0)],"函数变化与驻点"),
("fn-exp","function_2d","指数函数","y=a^x","y=a^x",[P("a","底数 a",.2,4,2)],"底数不能取 1，且必须为正"),
("fn-log","function_2d","对数函数","y=log_a(x)","y=\\log_a x",[P("a","底数 a",.2,4,2)],"自变量必须大于零；底数不等于 1"),
("fn-sin","function_2d","正弦曲线参数变换","y=A*sin(wx+φ)+k","y=A\\sin(\\omega x+\\varphi)+k",[P("A","振幅 A",.2,3,1),P("w","角频率 ω",.2,4,1),P("phi","相位 φ",-3.14,3.14,0,.05),P("k","平移 k",-3,3,0)],"弧度制与振幅、周期、相位"),
("fn-cos","function_2d","余弦函数","y=A*cos(wx+φ)","y=A\\cos(\\omega x+\\varphi)",[P("A","振幅 A",.2,3,1),P("w","角频率 ω",.2,4,1),P("phi","相位 φ",-3.14,3.14,0,.05)],"周期与相位"),
("fn-tan","function_2d","正切函数与渐近线","y=tan(wx+φ)","y=\\tan(\\omega x+\\varphi)",[P("w","频率 ω",.2,3,1),P("phi","相位 φ",-3.14,3.14,0,.05)],"每条渐近线两侧必须分段绘制"),
("fn-abs","function_2d","绝对值函数","y=a|x-h|+k","y=a|x-h|+k",[P("a","比例 a",-2,2,1),P("h","折点横坐标 h",-4,4,1),P("k","平移 k",-4,4,0)],"折点与分段性质"),
("fn-inverse","function_2d","反比例与渐近线","y=a/(x-h)+k","y=\\frac{a}{x-h}+k",[P("a","系数 a",-5,5,2),P("h","竖直渐近线 x=h",-4,4,0),P("k","水平渐近线 y=k",-4,4,0)],"分母零点不可取"),
("fn-sqrt","function_2d","根式函数与定义域","y=sqrt(x-h)+k","y=\\sqrt{x-h}+k",[P("h","定义域起点 h",-4,4,0),P("k","平移 k",-4,4,0)],"定义域限制 x>=h"),
("fn-piecewise","function_2d","分段函数连续性","y={mx+b(x<h);a(x-h)^2+k(x>=h)}","f(x)=\\begin{cases}mx+b,&x<h\\\\a(x-h)^2+k,&x\\ge h\\end{cases}",[P("m","左段斜率 m",-3,3,.5),P("b","左段截距 b",-4,4,1),P("a","右段二次系数 a",-2,2,.5),P("h","分段点 h",-4,4,0),P("k","右段截距 k",-4,4,1)],"分段点连续性的必要条件"),
("conic-line","conic_2d","直线及斜率截距","y=mx+b","y=mx+b",[P("m","斜率 m",-4,4,1),P("b","截距 b",-5,5,0)],"解析几何的直线位置关系"),
("conic-circle","conic_2d","圆的方程与半径","(x-h)^2+(y-k)^2=r^2","(x-h)^2+(y-k)^2=r^2",[P("h","圆心横坐标 h",-4,4,0),P("k","圆心纵坐标 k",-4,4,0),P("r","半径 r",.5,5,3)],"圆心、半径、直径"),
("conic-ellipse","conic_2d","椭圆与焦点","(x-h)^2/a^2+(y-k)^2/b^2=1","\\frac{(x-h)^2}{a^2}+\\frac{(y-k)^2}{b^2}=1",[P("a","半长轴 a",1,6,4),P("b","半短轴 b",.5,5,2),P("h","平移 h",-3,3,0),P("k","平移 k",-3,3,0)],"要求 a>b，焦距 c²=a²-b²"),
("conic-hyperbola","conic_2d","双曲线与渐近线","(x-h)^2/a^2-(y-k)^2/b^2=1","\\frac{(x-h)^2}{a^2}-\\frac{(y-k)^2}{b^2}=1",[P("a","实半轴 a",.5,5,2.5),P("b","虚半轴 b",.5,4,1.5),P("h","平移 h",-3,3,0),P("k","平移 k",-3,3,0)],"渐近线斜率 ±b/a，焦距 c²=a²+b²"),
("conic-parabola","conic_2d","抛物线与准线","(y-k)^2=4p(x-h)","(y-k)^2=4p(x-h)",[P("p","焦距参数 p",.3,3,1),P("h","顶点横坐标 h",-3,3,0),P("k","顶点纵坐标 k",-3,3,0)],"焦点 (h+p,k)，准线 x=h-p"),
("conic-intersection","conic_2d","直线与圆的位置关系","circle+line","(x-h)^2+y^2=r^2,\\ y=mx+b",[P("h","圆心横坐标 h",-3,3,0),P("r","半径 r",.5,5,3),P("m","直线斜率 m",-3,3,.5),P("b","截距 b",-4,4,0)],"通过观察交点情况区分相交、相切、相离"),
("tri-free","triangle_2d","三角形边角与面积","triangle-free","S=\\frac12 ab\\sin C",[],"自由拖动 A、B、C，观察边角与面积"),
("tri-right","triangle_2d","直角三角形与三角函数","triangle-right","a^2+b^2=c^2",[], "保留直角，观察斜边、锐角及三角比"),
("tri-ssa","triangle_2d","SSA 条件可能不唯一","triangle-ssa","\\frac{a}{\\sin A}=\\frac{b}{\\sin B}",[P("a","A 的对边 a",2,9,6),P("b","B 的对边 b",2,10,8),P("A","角 A（度）",15,145,40,1)],"检查 0、1、2 种可能情形，不能只凭 sin B 定唯一角"),
("3d-point","space_3d","空间直角坐标系与点投影","point3d","P(x,y,z)",[P("x","x 坐标",-4,4,2),P("y","y 坐标",-4,4,2),P("z","z 坐标",-4,5,3)],"右手坐标系，XY 平面投影"),
("3d-vectors","space_3d","空间向量与夹角","vectors3d","\\vec a\\cdot\\vec b=|a||b|\\cos\\theta",[P("ax","a_x",-3,3,2),P("ay","a_y",-3,3,1),P("az","a_z",-3,3,2),P("bx","b_x",-3,3,-1),P("by","b_y",-3,3,2),P("bz","b_z",-3,3,1)],"注意零向量不定义夹角"),
("3d-plane","space_3d","平面与法向量","plane3d","z=px+qy+r",[P("p","倾斜 p",-2,2,.4),P("q","倾斜 q",-2,2,-.3),P("r","截距 r",-3,3,1)],"可视法向量 (-p,-q,1) 与平面"),
("3d-prism","space_3d","棱柱：顶点、面与体积","prism3d","V=S_{底}\\cdot h",[P("w","底边长 w",1,5,3),P("d","底边宽 d",1,5,2),P("h","高 h",1,6,3)],"观察平行底面与立体空间位置关系"),
("3d-pyramid","space_3d","棱锥：顶点与体积","pyramid3d","V=\\frac13 S_{底}\\cdot h",[P("w","底边长 w",1,5,3),P("d","底边宽 d",1,5,2),P("h","高 h",1,6,4)],"高是顶点到底面距离，勿混侧棱"),
("3d-sphere","space_3d","球体与截面","sphere3d","x^2+y^2+z^2=R^2",[P("r","半径 r",1,4,2.8)],"截面半径与球半径的关系"),
("3d-cylinder","space_3d","圆柱及轴向截面","cylinder3d","V=\\pi r^2h",[P("r","底圆半径 r",.5,4,2),P("h","高度 h",1,6,4)],"圆形底面与平行母线"),
("3d-cone","space_3d","圆锥及轴向截面","cone3d","V=\\frac13\\pi r^2h",[P("r","底圆半径 r",.5,4,2),P("h","高度 h",1,6,4)],"顶点到底面的高与母线"),
]
def build():
  scenes=[]
  for (id,tool,title,equation,latex,params,description) in PRESETS:
      scenes.append(dict(id=id,tool=tool,title=title,equation=equation,latex=latex,
             params=params,description=description,source="PROJECT_AUTHORED",
             expert_review="PENDING",simulation=True))
  scenes.extend(extra_presets())
  scenes.extend(foundation_presets())
  scenes.extend(sequence_presets())
  scenes.extend(extrema_presets())
  scenes.extend(probability_presets())
  from collections import Counter
  assert len({p['id'] for p in scenes})==len(scenes)
  (ROOT/"visual_presets.json").write_text(json.dumps({
     "version":"2026-10-19.1","notice":"受控数学演示、非自动解答；部分高中知识仍规划中",
     "presets":scenes},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
  print("Interactive scene presets",len(scenes),Counter(p['tool'] for p in scenes))
if __name__=="__main__":build()
