"""Explicitly deterministic teaching strategy: scoped to authored cards, never an LLM."""
from .catalog import PROBLEMS
from .storage import nearest_own_episode

STUCK_TERMS = ("卡住", "不会", "不知道", "没思路", "想不出", "下一步", "没想法", "stuck")
BACKWARD_TERMS = ("反推", "从目标", "逆向", "要证明")
CALC_TERMS = ("配方", "化简", "展开", "运算", "计算")


def stage_from_text(text, existing_turns):
    lowered = text.lower()
    if any(t in lowered for t in STUCK_TERMS):
        return "STUCK"
    if any(t in lowered for t in BACKWARD_TERMS):
        return "BACKWARD"
    if any(t in lowered for t in CALC_TERMS):
        return "CALCULATION"
    if any(t in lowered for t in ("突破", "想到了", "联系起来", "构造")):
        return "BRIDGE"
    return "FORWARD" if existing_turns else "START"


def tutor_reply(session, student_text, help_requested=False, request_type="hint"):
    mode = session["mode"]
    problem = session["problem"]
    turns = session["turns"]
    stage = stage_from_text(student_text, turns)
    hint_count = session["hint_count"]
    is_curated = problem.get("id") in PROBLEMS
    base = {
        "thinking_stage":stage,
        "hint_level":0,
        "math_verified":False,
        "engine":"DETERMINISTIC_SIMULATION",
        "scope":"CURATED_PROBLEM" if is_curated else "GENERIC_FALLBACK",
        "reference_episode_id":None,
    }

    def result(action, message, level=1, reference=None):
        return {**base,"next_action":action,"message":message,"hint_level":level,"reference_episode_id":reference}

    if mode == "INDEPENDENT" and not help_requested and request_type == "hint":
        return result("WAIT","已保存你的独立尝试。我不会提前告诉你方法；如果需要，可以主动请求一点提示或检查思路。",0)

    if request_type == "recall":
        reference = nearest_own_episode(session["student_id"], problem)
        if reference is None:
            return result("NO_MEMORY","目前没有找到你自己做过、且与这道题结构和方法都足够接近的历史练习。我不会编造旧题。你先试着说出这道题的核心关系。",0)
        old = PROBLEMS.get(reference["problem_id"],{})
        return result("RECALL_EPISODE",f"你以前确实尝试过《{old.get('title','某道练习')}》。先不看当时的方法：回忆你那次为什么改变原来的思路？新题与旧题在条件上有什么异同？",1,reference["id"])

    if request_type == "check":
        return result("CHECK_ATTEMPT","我已保存你的推导。模拟版本不能对任意手写公式做可靠的数学正确性判断；请说明这一步使用了什么条件、是否为等价变形，我们可以检查它的适用范围。",0)

    if request_type == "reflection":
        return result("REFLECT","回顾本题：从哪一步开始原有方法不再有效？你如何找到突破口？以后遇到怎样的结构可以尝试迁移，又有哪些限制？",0)

    if not is_curated:
        return result("ASK_OBSERVATION","这是自定义题目。当前离线模拟只支持通用审题引导，不能假装已经理解和验证完整数学推理。请先区分已知条件、隐含限制和目标，再告诉我你卡在哪里。",1)

    # Proactive past-problem reminder only after an actual stuck phase and prior help.
    if mode != "INDEPENDENT" and stage == "STUCK" and hint_count >= 1:
        reference = nearest_own_episode(session["student_id"],problem)
        if reference is not None and not any(t["reference_episode_id"] for t in turns):
            old = PROBLEMS.get(reference["problem_id"],{})
            return result("RECALL_EPISODE",f"你以前做过《{old.get('title','相关练习')}》。先别看答案，试着想起那次从哪里找到了突破口，并判断这次的条件是否真的允许迁移。",1,reference["id"])

    if mode == "ANALYZE":
        cues = problem["analysis"]
        i = min(hint_count,len(cues)-1)
        return result("ASK_OBSERVATION" if i == 0 else "ASK_STRATEGY",cues[i],i+1)

    cues = problem["guide"]
    if stage == "STUCK":
        # Use the goal direction as a strategy switch rather than finishing the algebra.
        return result("ASK_BACKWARD_GOAL",cues[1],min(3,max(1,hint_count+1)))
    if stage == "BACKWARD":
        return result("ASK_BRIDGE","你已经开始从结论反推了。把你希望得到的中间条件和已经证明的关系并排看，哪一步最可能把它们连起来？先尝试说明理由。",min(3,max(1,hint_count+1)))
    if stage == "CALCULATION":
        return result("CHECK_BOUNDARY","思路接近常规运算阶段。先由你自己完成计算，注意定义域、符号和特殊情形；需要时请指出某个具体式子再核对。",1)
    i = min(hint_count,len(cues)-1)
    return result("ASK_START" if i == 0 else "OFFER_MINIMAL_HINT",cues[i],i+1)
