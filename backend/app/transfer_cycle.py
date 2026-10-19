"""Transfer practice protocol, demo-only. Records evidence; never grades free text.

No new model/RAG lookup: matches real same-student completed episodes only.
"""
import sqlite3
from uuid import uuid4
from .catalog import PROBLEMS
from .storage import database, nearest_own_episode, timestamp

EVIDENCE_NO_HINTS="NO_IN_APP_HINTS_OBSERVED_NOT_PROOF"
EVIDENCE_AFTER_RECALL="STUDENT_POST_RECALL_NOT_VERIFIED"
DISCLAIMER=("学生的文字和回忆过程只是学习证据；未自动验证数学正确性、"
            "真实独立掌握、跨题迁移成功或无外部帮助。仅供合成学生模拟。")

class TransferConflict(ValueError):
    pass

class TransferNotFound(LookupError):
    pass


def records(session_id):
    with database() as db:
        rows=db.execute(
            "SELECT * FROM transfer_attempts WHERE session_id=? "
            "ORDER BY CASE phase WHEN 'BEFORE_RECALL' THEN 0 ELSE 1 END",
            (session_id,)).fetchall()
    return [dict(x) for x in rows]


def authentic_candidate(session):
    """A completed same-student episode, not a claimed-correct method."""
    problem=session["problem"]
    if problem.get("id") not in PROBLEMS:
        return None
    ep=nearest_own_episode(session["student_id"],problem,
                           completed_before=session["created_at"])
    if ep is None:
        return None
    previous=PROBLEMS.get(ep["problem_id"])
    if not previous or ep["student_id"]!=session["student_id"]:
        return None
    return {
        "source_episode_id":ep["id"],
        "prior_problem_title":previous["title"],
        "evidence_status":ep["evidence_status"],
        "hint_visibility":"HISTORY_TITLE_ONLY",
        "why_candidate":"本人真实历史题目，与当前题的受控方法和结构标签存在交集；仅供回忆，不是已证明方法。"
    }


def get_transfer_state(session):
    rows=records(session["id"])
    has_baseline=any(r["phase"]=="BEFORE_RECALL" for r in rows)
    after=any(r["phase"]=="AFTER_RECALL" for r in rows)
    candidate=authentic_candidate(session) if has_baseline else None
    if after:
        phase="RECORDED_UNVERIFIED"
    elif not has_baseline:
        phase="BEFORE_RECALL"
    elif candidate is None:
        phase="NO_MATCHING_HISTORY"
    elif any(t["action"]=="RECALL_EPISODE" and
             t.get("reference_episode_id")==candidate["source_episode_id"]
             for t in session["turns"]):
        phase="AFTER_RECALL_READY"
    else:
        phase="RECALL_AVAILABLE"
    return {
        "session_id":session["id"],
        "target_problem_id":session["problem"].get("id"),
        "phase":phase,
        "history_candidate":candidate,
        "records":rows,
        "math_verified":False,
        "independent_mastery_verified":False,
        "grade_assigned":False,
        "disclaimer":DISCLAIMER,
        "simulation":True
    }


def record_attempt(session,phase,attempt_text,self_report_stage,source_episode_id):
    if session["completed_at"]:
        raise TransferConflict("结束的会话无法再新增迁移尝试")
    current=records(session["id"])
    if any(row["phase"]==phase for row in current):
        raise TransferConflict("当前阶段已经冻结记录，不能覆盖原始思路")
    if phase=="BEFORE_RECALL":
        if source_episode_id is not None:
            raise TransferConflict("基线阶段不能引用旧题来源")
        if (session["mode"]!="INDEPENDENT" or session["hint_count"]!=0 or
            any(t["action"]!="WAIT" for t in session["turns"])):
            raise TransferConflict("无提示基线只能在自主挑战、尚未获得导师提示或回忆时冻结；请重新开始新题")
        source=None
        evidence=EVIDENCE_NO_HINTS
    elif phase=="AFTER_RECALL":
        if not any(row["phase"]=="BEFORE_RECALL" for row in current):
            raise TransferConflict("必须先冻结无提示的独立尝试")
        candidate=authentic_candidate(session)
        if candidate is None or candidate["source_episode_id"]!=source_episode_id:
            raise TransferNotFound("未找到本人符合结构要求的真实历史练习")
        if not any(t["action"]=="RECALL_EPISODE" and
                   t.get("reference_episode_id")==source_episode_id
                   for t in session["turns"]):
            raise TransferConflict("需先主动请求历史回忆，不能伪造已接受的提示")
        source=source_episode_id
        evidence=EVIDENCE_AFTER_RECALL
    else:
        raise TransferConflict("未知的迁移记录阶段")
    record={
        "id":str(uuid4()),"student_id":session["student_id"],
        "session_id":session["id"],"phase":phase,
        "source_episode_id":source,
        "attempt_text":attempt_text.strip(),
        "self_report_stage":self_report_stage,
        "mode_at_submission":session["mode"],
        "hint_count_at_submission":session["hint_count"],
        "turn_count_at_submission":len(session["turns"]),
        "evidence_status":evidence,"created_at":timestamp()
    }
    try:
        with database() as db:
            db.execute(
            "INSERT INTO transfer_attempts "
            "(id,student_id,session_id,phase,source_episode_id,attempt_text,"
            "self_report_stage,mode_at_submission,hint_count_at_submission,"
            "turn_count_at_submission,evidence_status,created_at) "
            "VALUES (:id,:student_id,:session_id,:phase,:source_episode_id,:attempt_text,"
            ":self_report_stage,:mode_at_submission,:hint_count_at_submission,"
            ":turn_count_at_submission,:evidence_status,:created_at)",record)
    except sqlite3.IntegrityError as error:
        # Concurrent duplicate stage submission must be a handled conflict, never HTTP 500.
        raise TransferConflict("本阶段记录已存在或不符合数据库约束") from error
    return {**record,"math_verified":False,"independent_mastery_verified":False,
            "grade_assigned":False}


def student_summary(student_id):
    with database() as db:
        groups=db.execute(
            "SELECT phase,COUNT(*) AS count FROM transfer_attempts "
            "WHERE student_id=? GROUP BY phase",(student_id,)).fetchall()
        sessions=db.execute(
            "SELECT COUNT(DISTINCT session_id) FROM transfer_attempts "
            "WHERE student_id=?",(student_id,)).fetchone()[0]
    totals={x["phase"]:x["count"] for x in groups}
    return {
        "student_id":student_id,
        "sessions_with_transfer_records":sessions,
        "baseline_attempts":totals.get("BEFORE_RECALL",0),
        "post_recall_attempts":totals.get("AFTER_RECALL",0),
        "mathematically_verified_attempts":0,
        "independent_mastery_verified":False,
        "scope":"RECORDED_PROCESS_NOT_LEARNING_OUTCOME",
        "simulation":True,
        "disclaimer":DISCLAIMER
    }
