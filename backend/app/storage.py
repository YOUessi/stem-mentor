"""Demo-only SQLite persistence. No authentication: synthetic/test students only."""
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4
from .catalog import MICRO_POINTS, PROBLEMS


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def db_path():
    return Path(os.environ.get("STEM_MENTOR_DB", str(Path(__file__).parents[1] / "data" / "demo.sqlite3")))


@contextmanager
def database():
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(path), timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS students(id TEXT PRIMARY KEY, alias TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions(
            id TEXT PRIMARY KEY, student_id TEXT NOT NULL REFERENCES students(id),
            problem_id TEXT, custom_problem TEXT, mode TEXT NOT NULL, stage TEXT NOT NULL DEFAULT 'START',
            hint_count INTEGER NOT NULL DEFAULT 0, completed_at TEXT, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS turns(
            id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id),
            student_text TEXT NOT NULL, action TEXT NOT NULL, tutor_message TEXT NOT NULL,
            stage TEXT NOT NULL, hint_level INTEGER NOT NULL, reference_episode_id TEXT,
            created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS turn_annotations(
            turn_id TEXT PRIMARY KEY REFERENCES turns(id),
            diagnosis_json TEXT NOT NULL, decision_trace_json TEXT NOT NULL, knowledge_refs_json TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS episodes(
            id TEXT PRIMARY KEY, student_id TEXT NOT NULL REFERENCES students(id),
            session_id TEXT NOT NULL UNIQUE REFERENCES sessions(id), problem_id TEXT,
            notes TEXT NOT NULL, evidence_status TEXT NOT NULL,
            method_tags TEXT NOT NULL, structure_tags TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS review_state(
            student_id TEXT NOT NULL REFERENCES students(id), point_id TEXT NOT NULL,
            box_level INTEGER NOT NULL DEFAULT 0, due_at TEXT NOT NULL, last_result TEXT,
            PRIMARY KEY(student_id,point_id));
        CREATE TABLE IF NOT EXISTS review_events(
            id TEXT PRIMARY KEY, student_id TEXT NOT NULL REFERENCES students(id),
            point_id TEXT NOT NULL, answer TEXT NOT NULL, correct INTEGER NOT NULL,
            created_at TEXT NOT NULL);
    """)
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def student_create(alias="演示学生"):
    identifier = str(uuid4())
    with database() as db:
        db.execute("INSERT INTO students VALUES(?,?,?)", (identifier, alias, timestamp()))
        db.executemany("INSERT INTO review_state(student_id,point_id,due_at) VALUES(?,?,?)", [(identifier,pid,timestamp()) for pid in MICRO_POINTS])
    return {"id":identifier,"alias":alias,"demo_only":True}


def student_get(student_id):
    with database() as db:
        row = db.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
    return dict(row) if row else None


def session_create(student_id, problem_id, custom_problem, mode):
    sid = str(uuid4())
    with database() as db:
        db.execute("INSERT INTO sessions(id,student_id,problem_id,custom_problem,mode,stage,created_at) VALUES(?,?,?,?,?,'START',?)",
                   (sid,student_id,problem_id,custom_problem,mode,timestamp()))
    return session_get(sid)


def session_get(session_id):
    with database() as db:
        row = db.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
        if not row:
            return None
        turns = db.execute("SELECT * FROM turns WHERE session_id=? ORDER BY rowid", (session_id,)).fetchall()
        annotations = {r['turn_id']:dict(r) for r in db.execute(
            "SELECT * FROM turn_annotations WHERE turn_id IN (SELECT id FROM turns WHERE session_id=?)",(session_id,))}
    record = dict(row)
    record["turns"] = []
    for t in turns:
        row=dict(t)
        annotation=annotations.get(row['id'])
        if annotation:
            row['diagnosis']=json.loads(annotation['diagnosis_json'])
            row['decision_trace']=json.loads(annotation['decision_trace_json'])
            row['knowledge_refs']=json.loads(annotation['knowledge_refs_json'])
        record['turns'].append(row)
    record["problem"] = dict(PROBLEMS[record["problem_id"]]) if record["problem_id"] in PROBLEMS else {"id":None,"title":"自定义题目（未覆盖模板）","prompt":record["custom_problem"],"method_tags":[],"structure_tags":[]}
    return record


def session_mode(session_id, mode):
    with database() as db:
        db.execute("UPDATE sessions SET mode=? WHERE id=?", (mode,session_id))
    return session_get(session_id)


def turn_record(session_id, student_text, response, increment_hint):
    with database() as db:
        turn_id=str(uuid4())
        db.execute("INSERT INTO turns VALUES(?,?,?,?,?,?,?,?,?)",
                   (turn_id, session_id, student_text, response["next_action"],response["message"],
                    response["thinking_stage"],response["hint_level"],response.get("reference_episode_id"),timestamp()))
        trace=response.get('decision_trace',{})
        db.execute("INSERT INTO turn_annotations VALUES(?,?,?,?)",(
            turn_id,
            json.dumps(trace.get('stage_diagnosis',{}),ensure_ascii=False),
            json.dumps(trace,ensure_ascii=False),
            json.dumps(response.get('knowledge_refs',[]),ensure_ascii=False)))
        db.execute("UPDATE sessions SET stage=?, hint_count=hint_count+? WHERE id=?",
                   (response["thinking_stage"],int(increment_hint),session_id))


def episode_complete(session_id, reflection):
    s=session_get(session_id)
    if not s:
        return None
    with database() as db:
        existing=db.execute("SELECT * FROM episodes WHERE session_id=?", (session_id,)).fetchone()
        if existing:
            return dict(existing)
        problem=s["problem"]
        eid=str(uuid4())
        # Student saying "completed" is not independent/correctness evidence.
        db.execute("INSERT INTO episodes VALUES(?,?,?,?,?,?,?,?,?)",
                   (eid,s["student_id"],session_id,s["problem_id"],reflection,"SELF_REPORTED_NOT_VERIFIED",
                    json.dumps(problem.get("method_tags",[])),json.dumps(problem.get("structure_tags",[])),timestamp()))
        db.execute("UPDATE sessions SET completed_at=? WHERE id=?", (timestamp(),session_id))
    return episode_get(eid)


def episode_get(eid):
    with database() as db:
        row=db.execute("SELECT * FROM episodes WHERE id=?",(eid,)).fetchone()
    return dict(row) if row else None


def episodes_list(student_id):
    with database() as db:
        rows=db.execute("SELECT * FROM episodes WHERE student_id=? ORDER BY created_at DESC",(student_id,)).fetchall()
    return [dict(row) for row in rows]


def nearest_own_episode(student_id, current_problem):
    methods=set(current_problem.get("method_tags",[]))
    structure=set(current_problem.get("structure_tags",[]))
    candidates=[]
    for ep in episodes_list(student_id):
        if ep["problem_id"]==current_problem.get("id"):
            continue
        common_methods=methods.intersection(json.loads(ep["method_tags"]))
        common_structure=structure.intersection(json.loads(ep["structure_tags"]))
        if common_methods and len(common_structure)>=2:
            candidates.append((len(common_structure)*2+len(common_methods),ep))
    if not candidates:
        return None
    candidates.sort(key=lambda x:x[0],reverse=True)
    return candidates[0][1]


def reviews_list(student_id, due_only=False):
    with database() as db:
        rows=db.execute("SELECT * FROM review_state WHERE student_id=? ORDER BY due_at,point_id",(student_id,)).fetchall()
    output=[]
    for row in rows:
        record=dict(row)
        record["card"]={k:v for k,v in MICRO_POINTS[record["point_id"]].items() if k not in ("acceptable","answer_hint")}
        if not due_only or record["due_at"]<=timestamp():
            output.append(record)
    return output


def answer_review(student_id, point_id, answer):
    point=MICRO_POINTS[point_id]
    normalized=answer.lower().replace(" ","").replace("₁","1").replace("_","")
    correct=any(s.lower().replace(" ","").replace("₁","1") in normalized for s in point["acceptable"])
    with database() as db:
        row=db.execute("SELECT * FROM review_state WHERE student_id=? AND point_id=?",(student_id,point_id)).fetchone()
        if not row:
            return None
        level=min(4,row["box_level"]+1) if correct else 0
        intervals=[1,3,7,14,30]
        due=(datetime.now(timezone.utc)+timedelta(days=intervals[level])).isoformat()
        db.execute("UPDATE review_state SET box_level=?,due_at=?,last_result=? WHERE student_id=? AND point_id=?",
                   (level,due,"RULE_MATCH" if correct else "RULE_NO_MATCH",student_id,point_id))
        db.execute("INSERT INTO review_events VALUES(?,?,?,?,?,?)",(str(uuid4()),student_id,point_id,answer,int(correct),timestamp()))
    return {"point_id":point_id,"rule_match":correct,"not_a_proof_of_mastery":True,"next_due_at":due,"box_level":level,"reference_answer":point["answer_hint"]}
