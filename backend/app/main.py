"""Full-stack offline simulation API; intentionally no LLM integration."""
from enum import Enum
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, model_validator
from .catalog import PROBLEMS, METHODS, MICRO_POINTS, public_problem
from .math_tools import known_identity_check, verify_equivalence
from . import storage
from .tutor import tutor_reply
from .reasoning import student_map
from .retrieval import retrieve, corpus
from .study_visuals import visual_for, visuals

app=FastAPI(title="STEM Mentor — 离线模拟",version="0.7.0")
ROOT=Path(__file__).resolve().parents[2]
WEB=ROOT/"apps"/"web"
app.mount("/assets",StaticFiles(directory=str(WEB)),name="assets")

class Mode(str,Enum):
    ANALYZE="ANALYZE"
    GUIDE="GUIDE"
    INDEPENDENT="INDEPENDENT"

class StudentCreate(BaseModel):
    alias:str=Field(default="演示学生",min_length=1,max_length=40)

class SessionCreate(BaseModel):
    student_id:str
    mode:Mode=Mode.GUIDE
    problem_id:str|None=None
    custom_problem:str|None=Field(default=None,max_length=4000)
    @model_validator(mode="after")
    def has_problem(self):
        if not self.problem_id and not self.custom_problem:
            raise ValueError("请选择示例题或输入自定义题目")
        return self

class ModeChange(BaseModel):
    mode:Mode

class TurnCreate(BaseModel):
    student_text:str=Field(min_length=1,max_length=4000)
    help_requested:bool=False
    request_type:str=Field(default="hint",pattern="^(hint|recall|check|reflection)$")
    self_report_stage:str|None=Field(default=None,pattern="^(START|FORWARD|STUCK|BACKWARD|BRIDGE|CALCULATION|REFLECTION)$")

class SessionComplete(BaseModel):
    reflection:str=Field(default="",max_length=3000)

class ReviewAnswer(BaseModel):
    answer:str=Field(min_length=1,max_length=1000)

class KnowledgeQuery(BaseModel):
    query:str=Field(min_length=1,max_length=200)
    problem_id:str|None=None
    include_excluded:bool=False
    top_k:int=Field(default=8,ge=1,le=10)

class AlgebraEquivalence(BaseModel):
    expr_left:str=Field(min_length=1,max_length=180)
    expr_right:str=Field(min_length=1,max_length=180)
    problem_id:str


def get_student_or_404(student_id):
    student=storage.student_get(student_id)
    if not student:
        raise HTTPException(404,"演示学生不存在")
    return student


def get_session_or_404(sid):
    session=storage.session_get(sid)
    if not session:
        raise HTTPException(404,"学习会话不存在")
    return session

@app.get("/")
def index():
    return FileResponse(str(WEB/"index.html"))

@app.get("/health")
def health():
    return {"status":"ok","engine":"DETERMINISTIC_SIMULATION","llm_api_used":False}

@app.get("/api/catalog")
def catalog():
    return {"problems":[public_problem(v) for v in PROBLEMS.values()],
            "methods":[{'id':c['id'],'title':c['title'],'name':c['title'],
                        'description':c['content'][:180],'boundary':c['boundary'],
                        'hint':c['hint'],'source':c['source']}
                       for c in corpus()],
            "modes":[{"value":m.value,"label":label} for m,label in [(Mode.ANALYZE,"逻辑分析"),(Mode.GUIDE,"推理陪练"),(Mode.INDEPENDENT,"自主挑战")]],
            "simulation":True}

@app.post("/api/students",status_code=201)
def create_student(payload:StudentCreate):
    return storage.student_create(payload.alias)

@app.get("/api/students/{student_id}/dashboard")
def dashboard(student_id:str):
    get_student_or_404(student_id)
    episodes=storage.episodes_list(student_id)
    reviews=storage.reviews_list(student_id,due_only=True)
    return {"episodes_count":len(episodes),"reviews_due_count":len(reviews),"independent_mastery_verified":False,
            "simulation":True}

@app.post("/api/sessions",status_code=201)
def create_session(payload:SessionCreate):
    get_student_or_404(payload.student_id)
    if payload.problem_id and payload.problem_id not in PROBLEMS:
        raise HTTPException(422,"示例题编号不存在")
    return storage.session_create(payload.student_id,payload.problem_id,payload.custom_problem,payload.mode.value)

@app.get("/api/sessions/{session_id}")
def get_session(session_id:str):
    return get_session_or_404(session_id)

@app.patch("/api/sessions/{session_id}/mode")
def change_mode(session_id:str,payload:ModeChange):
    session=get_session_or_404(session_id)
    if session["completed_at"]:
        raise HTTPException(409,"已结束的会话不能继续操作")
    return storage.session_mode(session_id,payload.mode.value)

@app.post("/api/sessions/{session_id}/turns")
def new_turn(session_id:str,payload:TurnCreate):
    session=get_session_or_404(session_id)
    if session["completed_at"]:
        raise HTTPException(409,"已结束的会话不能继续提问")
    result=tutor_reply(session,payload.student_text,payload.help_requested,payload.request_type,payload.self_report_stage)
    storage.turn_record(session_id,payload.student_text,result,result["hint_level"]>0)
    return result

@app.post("/api/sessions/{session_id}/complete")
def complete(session_id:str,payload:SessionComplete):
    get_session_or_404(session_id)
    return {"episode":storage.episode_complete(session_id,payload.reflection),"notes":"只记录学生自述完成，未验证答案正确或独立掌握。"}

@app.get("/api/students/{student_id}/episodes")
def episodes(student_id:str):
    get_student_or_404(student_id)
    output=[]
    for ep in storage.episodes_list(student_id):
        ep=ep.copy()
        ep["problem_title"]=PROBLEMS.get(ep["problem_id"],{}).get("title","自定义练习")
        output.append(ep)
    return {"episodes":output,"simulation":True}

@app.get("/api/students/{student_id}/reviews")
def reviews(student_id:str,due_only:bool=True):
    get_student_or_404(student_id)
    return {"reviews":storage.reviews_list(student_id,due_only=due_only),"simulation":True}

@app.post("/api/students/{student_id}/reviews/{point_id}/answer")
def review_answer(student_id:str,point_id:str,payload:ReviewAnswer):
    get_student_or_404(student_id)
    if point_id not in MICRO_POINTS:
        raise HTTPException(404,"考点不存在")
    return storage.answer_review(student_id,point_id,payload.answer)

@app.get("/api/math/known-check/{identity_id}")
def known_check(identity_id:str):
    result=known_identity_check(identity_id)
    if not result:
        raise HTTPException(404,"仅支持预先审核过的公式检验案例")
    return result


@app.get("/api/sessions/{session_id}/reasoning-map")
def reasoning_map(session_id:str):
    return student_map(get_session_or_404(session_id))

class ThinkingLinkCreate(BaseModel):
    source: str=Field(pattern=r"^(given|goal|student-step-[1-9][0-9]*)$",max_length=36)
    target: str=Field(pattern=r"^(given|goal|student-step-[1-9][0-9]*)$",max_length=36)
    label: str=Field(default="",max_length=100)

    @model_validator(mode="after")
    def different_ends(self):
        if self.source==self.target:
            raise ValueError("关联必须连接两条不同的思路")
        return self


@app.post("/api/sessions/{session_id}/thinking-links",status_code=201)
def create_thinking_link(session_id:str,payload:ThinkingLinkCreate):
    session=get_session_or_404(session_id)
    if session['completed_at']:
        raise HTTPException(409,"已结束的会话不能新增思路关联")
    available={n['id'] for n in student_map(session)['nodes']}
    if payload.source not in available or payload.target not in available:
        raise HTTPException(422,"关联只能使用当前学生当前会话里可见的题目条件、目标和实际尝试")
    try:
        link=storage.thinking_link_add(session_id,payload.source,payload.target,payload.label.strip())
    except ValueError as e:
        raise HTTPException(409,str(e)) from e
    return {**link,'verified':False,'is_proof':False}



@app.post("/api/math/equivalence")
def math_equivalence(payload:AlgebraEquivalence):
    if payload.problem_id not in PROBLEMS:
        raise HTTPException(422,"只能选择受控示例题作为条件上下文")
    return verify_equivalence(payload.expr_left,payload.expr_right,payload.problem_id)

@app.post("/api/knowledge/search")
def search_curated_knowledge(payload:KnowledgeQuery):
    if payload.problem_id is not None and payload.problem_id not in PROBLEMS:
        raise HTTPException(422,"不存在的示例题")
    retrieved=retrieve(payload.query,payload.problem_id,payload.top_k,payload.include_excluded)
    matched_ids={method_id for x in retrieved['hits'] for method_id in x['method_ids']}
    return {**retrieved,'methods':[m for m in METHODS if m['id'] in matched_ids]}

@app.get("/api/study/visual/{problem_id}")
def curated_study_visual(problem_id: str):
    """Public givens only: no teacher-only reasoning scaffold or worked solutions."""
    if problem_id not in PROBLEMS:
        raise HTTPException(404, "题目不存在")
    visual=visual_for(problem_id)
    if visual is None:
        raise HTTPException(404,"该题尚无数学可视资料")
    return {"problem_id":problem_id, **visual, "teacher_solution_included":False,
            "curated":True, "engine":"OFFLINE_MATH_VISUALIZATION"}


@app.get("/api/sessions/{session_id}/review-suggestion")
def session_review_suggestion(session_id:str):
    session=get_session_or_404(session_id)
    if not session['completed_at']:
        return {'suggestion':None,'why':'不打断正在进行的解题'}
    point_id=session['problem'].get('micro_point_id')
    for card in storage.reviews_list(session['student_id'],due_only=True):
        if card['point_id']==point_id:
            return {'suggestion':card['card'],'why':'本题相关且已到复习时机，安排在题后'}
    return {'suggestion':None,'why':'当前没有到期的关联考点'}


@app.get('/api/knowledge/quality')
def knowledge_quality_report():
    from .knowledge_quality import validate_knowledge
    return validate_knowledge()


@app.get('/api/math/proof-coverage')
def limited_proof_coverage():
    from .proof_obligations import coverage
    return coverage()
