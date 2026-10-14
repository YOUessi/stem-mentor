"""Full-stack offline simulation API; intentionally no LLM integration."""
from enum import Enum
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, model_validator
from .catalog import PROBLEMS, METHODS, MICRO_POINTS, public_problem
from .math_tools import known_identity_check
from . import storage
from .tutor import tutor_reply

app=FastAPI(title="STEM Mentor — 离线模拟",version="0.3.0")
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

class SessionComplete(BaseModel):
    reflection:str=Field(default="",max_length=3000)

class ReviewAnswer(BaseModel):
    answer:str=Field(min_length=1,max_length=1000)

class KnowledgeQuery(BaseModel):
    query:str=Field(min_length=1,max_length=200)
    problem_id:str|None=None


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
    return {"problems":[public_problem(v) for v in PROBLEMS.values()],"methods":METHODS,
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
    result=tutor_reply(session,payload.student_text,payload.help_requested,payload.request_type)
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


@app.get("/api/sessions/{session_id}/review-suggestion")
def session_review_suggestion(session_id:str):
    session=get_session_or_404(session_id)
    if not session["completed_at"]:
        return {"suggestion":None,"why":"不打断正在进行的解题"}
    point_id=session["problem"].get("micro_point_id")
    for card in storage.reviews_list(session["student_id"],due_only=True):
        if card["point_id"]==point_id:
            return {"suggestion":card["card"],"why":"本题关联且已到复习时机，放在题后而不是中途打断"}
    return {"suggestion":None,"why":"关联考点未到复习时间或当前无适配考点"}

@app.post("/api/knowledge/search")
def search_curated_knowledge(payload:KnowledgeQuery):
    if payload.problem_id and payload.problem_id not in PROBLEMS:
        raise HTTPException(422,"不存在的示例题")
    query=payload.query.lower().strip()
    current=PROBLEMS.get(payload.problem_id,{})
    scored=[]
    for method in METHODS:
        searchable=" ".join(str(method[k]).lower() for k in ("id","name","description","trigger","boundary"))
        terms=[term for term in query.replace("，"," ").replace(","," ").split(" ") if term]
        lexical=any(term in searchable for term in terms)
        # Strict curated tag link; no fake embedding/semantic inference.
        linked=method["id"] in current.get("method_tags",[])
        if lexical or linked:
            scored.append((2 if linked else 1,method))
    scored.sort(key=lambda pair:-pair[0])
    return {"methods":[m for _,m in scored],"engine":"CURATED_TAG_AND_LITERAL_SEARCH",
            "note":"这是确定性演示检索，不是向量 RAG；结果并不保证适合任意新题。"}
