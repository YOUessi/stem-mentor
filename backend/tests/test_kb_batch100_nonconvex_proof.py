"""Reject the false inference that every nonconvex polygon equals its vertex hull."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def test_nonconvex_polygon_vertex_hull_proof_boundaries():
    lessons=json.loads((ROOT/"knowledge/deep/v1/batch100_deep_source_20.json").read_text(encoding="utf8"))
    lesson=next(x for x in lessons if x["id"]=="math.hs.batch100.11")
    proof=lesson["proof_steps"][0]
    assert "三角剖分" in proof["claim"]
    assert "不能把非凸多边形整体等同于顶点凸包" in proof["reason"]
    # Concave pentagon has area 3; its convex hull is a 2x2 square of area 4.
    poly=((0,0),(2,0),(2,2),(1,1),(0,2))
    hull=((0,0),(2,0),(2,2),(0,2))
    def double_area(points):
        return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(points,points[1:]+points[:1])))
    assert double_area(poly)==6
    assert double_area(hull)==8
