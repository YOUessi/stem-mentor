"""Auditable teaching policy in offline mode; no model calls or answer generation.

Each action is selected from student evidence, mode, prior actions, and a safe
curated reasoning scaffold. The decision trace is persisted for regression.
"""
from .catalog import PROBLEMS
from .diagnosis import diagnose
from .reasoning import guide_for
from .proof_obligations import teacher_certificate
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
    certificate=teacher_certificate(problem.get('id')) if is_curated else None
    trace['teacher_scaffold_status']='LIMITED_SYMBOLIC_CHECKED' if certificate and certificate['all_symbolic_checks_pass'] else 'ANNOTATED_NOT_FORMALLY_PROVEN'
    trace['student_work_verified']=False
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
        analysis_turns=sum(x['action'] in ('ASK_OBSERVATION','ASK_STRATEGY','ASK_METHOD_JUSTIFICATION') for x in turns)
        cues=problem['analysis']
        if analysis_turns >= len(cues)+1:
            return decision('OFFER_MODE_SWITCH','审题和方法选择已讨论多轮。你愿意切换到推理陪练，尝试自己推导，还是选择自主挑战？不需要重复回答相同问题。',0,rule='P60_ANALYSIS_FATIGUE')
        if analysis_turns >= len(cues):
            return decision('ASK_METHOD_JUSTIFICATION','你已经梳理了若干次条件和目标。现在请自己选择一个候选方法，说说它为什么适用，以及有哪些可能使它失效的情况。',1,rule='P59_ANALYSIS_TO_JUSTIFICATION')
        index=min(analysis_turns,len(cues)-1)
        return decision('ASK_OBSERVATION' if not analysis_turns else 'ASK_STRATEGY',cues[index],index+1,rule='P40_ANALYZE_BEFORE_METHOD')

    # Repeated stuck state causes strategy adaptation, not identical questioning forever.
    last_stuck=bool(turns and turns[-1]['stage']=='STUCK')
    trailing_stuck = 0
    for old_turn in reversed(turns):
        if old_turn['stage']!='STUCK': break
        trailing_stuck+=1
    if stage=='STUCK' and trailing_stuck>=3:
        return decision('OFFER_TEACHING_CHOICE','我们已经反复尝试同一路径。你希望先看一个更小的类似例子、补一个前置知识点，还是换一种解题策略？选择一种，我只展开你需要的部分。',0,rule='P58_ESCALATE_WITH_CONSENT')
    if stage=='STUCK' and trailing_stuck>=2:
        return decision('ASK_SPECIFIC_OBSTACLE','你已经连续卡在这里。请指出最早无法解释的一条变形，或明确是“缺条件、缺方法、还是计算障碍”，我们换针对性的帮助。',1,rule='P57_DIAGNOSE_REPEATED_BLOCK')
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
      'P57_DIAGNOSE_REPEATED_BLOCK':'连续多轮停滞，应诊断具体障碍而不是重复同一句提示',
      'P58_ESCALATE_WITH_CONSENT':'长期停滞提供不同支持选项，未经选择不强制完整讲解',
      'P59_ANALYSIS_TO_JUSTIFICATION':'审题提示已经足够，改让学生解释候选方法的适用理由',
      'P60_ANALYSIS_FATIGUE':'连续相同分析已经饱和，允许学生改变活动而不是重复提问',
    }
    return reasons.get(rule,'受控离线教学策略')
