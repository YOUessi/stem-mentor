"""Auditable teaching policy in offline mode; no model calls or answer generation.

Each action is selected from student evidence, mode, prior actions, and a safe
curated reasoning scaffold. The decision trace is persisted for regression.
"""
from .catalog import PROBLEMS
from .diagnosis import diagnose
from .reasoning import guide_for
from .retrieval import retrieve_for_tutor
from .storage import nearest_own_episode


def stage_from_text(text, existing_turns):
    return diagnose(text, existing_turns)['stage']


def tutor_reply(session, student_text, help_requested=False, request_type='hint', self_report_stage=None):
    mode, problem, turns = session['mode'], session['problem'], session['turns']
    evidence = diagnose(student_text, turns, self_report_stage)
    stage = evidence['stage']
    hint_count = session['hint_count']
    is_curated = problem.get('id') in PROBLEMS
    previous_actions = [x['action'] for x in turns]
    knowledge_refs = retrieve_for_tutor(problem['id']) if is_curated else []
    trace = {'policy_version':'2026-10-15.v1','mode':mode,'stage_diagnosis':evidence,
             'previous_action':previous_actions[-1] if previous_actions else None,
             'rule_id':None,'knowledge_candidate_count':len(knowledge_refs),
             'student_answer_math_status':'NOT_VERIFIED'}
    base = {'thinking_stage':stage,'hint_level':0,'math_verified':False,
            'engine':'DETERMINISTIC_SIMULATION','scope':'CURATED_PROBLEM' if is_curated else 'GENERIC_FALLBACK',
            'reference_episode_id':None,'knowledge_refs':[]}

    def decision(action, message, level=1, reference=None, rule=None):
        trace['rule_id'] = rule or action
        return {**base,'next_action':action,'message':message,'hint_level':level,
                'reference_episode_id':reference,'decision_reason':_human_reason(rule or action),
                'decision_trace':trace}

    # Autonomy precedes proactive reminders: no intervention without actual help request.
    if mode=='INDEPENDENT' and request_type=='hint' and not help_requested:
        return decision('WAIT','已记录你的独立尝试。我不会提前透露方法；需要时可以主动请求提示或检查。',0,rule='P00_PROTECT_AUTONOMY')

    if request_type=='recall':
        ref=nearest_own_episode(session['student_id'],problem)
        if not ref:
            return decision('NO_MEMORY','目前没有找到你自己确实做过、且数学结构和方法都相近的历史练习。不会编造学习经历。你可以先说说当前题的核心结构。',0,rule='P10_NO_VALID_EPISODE')
        past=PROBLEMS.get(ref['problem_id'],{})
        return decision('RECALL_EPISODE',f'你之前确实尝试过《{past.get("title","一项相关练习")}》。先不要回看答案：当时你在哪个地方改变思路？这次又有哪些条件不同？',1,ref['id'],'P11_RECALL_VERIFIED_EXISTENCE')

    if request_type=='check':
        return decision('CHECK_ATTEMPT','已保存你的推导，但这段自由文本尚未得到数学验证。请选出具体的两侧表达式，用「等价检查」逐一核实，特别关注变形所需条件。',0,rule='P20_DO_NOT_FAKE_GRADING')
    if request_type=='reflection':
        return decision('REFLECT','回顾本题：最初沿什么方向推导？在哪一步发生了策略切换？真正的突破口是什么？以后什么条件下可以迁移？',0,rule='P21_REFLECT_STRATEGY')
    if not is_curated:
        return decision('ASK_OBSERVATION','这是未纳入题卡的自定义题。离线模拟引擎无法确认其数学结构；请先分开写明已知条件、限制和目标，不会假装给出可靠解法。',1,rule='P30_UNSUPPORTED_PROBLEM')

    if mode!='INDEPENDENT' and stage=='STUCK' and hint_count>=1:
        if not any(x.get('reference_episode_id') for x in turns):
            ref=nearest_own_episode(session['student_id'],problem)
            if ref is not None:
                past=PROBLEMS.get(ref['problem_id'],{})
                return decision('RECALL_EPISODE',f'你以前做过《{past.get("title","相关练习")}》。先想想那时怎样找到关键突破口，并判断新题条件是否允许迁移。',1,ref['id'],'P31_CONTEXTUAL_REAL_MEMORY')

    if mode=='ANALYZE':
        analysis_turns=sum(x['action'] in ('ASK_OBSERVATION','ASK_STRATEGY') for x in turns)
        cues=problem['analysis']
        index=min(analysis_turns,len(cues)-1)
        return decision('ASK_OBSERVATION' if not analysis_turns else 'ASK_STRATEGY',cues[index],index+1,rule='P40_ANALYZE_BEFORE_METHOD')

    # Repeated stuck state causes strategy adaptation, not identical questioning forever.
    last_stuck=bool(turns and turns[-1]['stage']=='STUCK')
    if stage=='STUCK' and last_stuck:
        msg='你已连续两次提到卡点。先暂停当前计算，分别写下「已经得到的关系」和「最终目标要求的条件」；两边只差哪一种联系？'
        return decision('ASK_BRIDGE',msg,min(3,hint_count+1),rule='P50_REPEATED_STUCK_SWITCH')
    if stage=='STUCK':
        return decision('ASK_BACKWARD_GOAL',guide_for(problem['id'],'STUCK') or problem['guide'][1],
                        min(3,max(1,hint_count+1)),rule='P51_STUCK_TO_BACKWARD')
    if stage=='BACKWARD':
        return decision('ASK_BRIDGE',guide_for(problem['id'],'BACKWARD'),min(3,hint_count+1),rule='P52_BACKWARD_TO_BRIDGE')
    if stage=='BRIDGE':
        return decision('VERIFY_BRIDGE',guide_for(problem['id'],'BRIDGE'),1,rule='P53_VALIDATE_BREAKTHROUGH')
    if stage=='CALCULATION':
        return decision('CHECK_BOUNDARY',guide_for(problem['id'],'CALCULATION'),1,rule='P54_ROUTINE_COMPUTATION')
    if stage=='REFLECTION':
        return decision('REFLECT','你能总结本题最值得迁移的策略转折，而不是列出全部运算步骤吗？',0,rule='P55_REFLECTION')
    start_index=min(hint_count,len(problem['guide'])-1)
    return decision('ASK_START' if hint_count==0 else 'OFFER_MINIMAL_HINT',
                    problem['guide'][start_index],min(3,hint_count+1),rule='P56_GRADED_START')


def _human_reason(rule):
    reasons={
      'P00_PROTECT_AUTONOMY':'自主挑战未经求助，不主动提供解法提示',
      'P10_NO_VALID_EPISODE':'没有通过同学生、同结构、同方法验证的历史记录',
      'P11_RECALL_VERIFIED_EXISTENCE':'学生主动要求回忆且存在真实个人学习经历',
      'P20_DO_NOT_FAKE_GRADING':'自由文本尚无法可靠自动评判数学正确性',
      'P21_REFLECT_STRATEGY':'学生要求总结策略和突破口',
      'P30_UNSUPPORTED_PROBLEM':'尚无受控题卡，避免伪造数学理解',
      'P31_CONTEXTUAL_REAL_MEMORY':'遇到瓶颈后有真实结构相似的个人学习记录',
      'P40_ANALYZE_BEFORE_METHOD':'逻辑分析模式优先让学生自己识别条件、目标和策略',
      'P50_REPEATED_STUCK_SWITCH':'连续停滞时切换成正逆两端桥梁问题，避免重复追问',
      'P51_STUCK_TO_BACKWARD':'正向遇阻，从目标倒推一个较小的中间目标',
      'P52_BACKWARD_TO_BRIDGE':'从目标逆推后，需要与已知条件建立连接',
      'P53_VALIDATE_BREAKTHROUGH':'发现突破口后先验证适用条件，而不是立即宣布解完',
      'P54_ROUTINE_COMPUTATION':'常规计算尽量交给学生，检查条件边界',
      'P55_REFLECTION':'侧重方法动机而非整题标准答案',
      'P56_GRADED_START':'从少量提示开始，不自动给出全部解题路径',
    }
    return reasons.get(rule,'受控离线教学策略')
