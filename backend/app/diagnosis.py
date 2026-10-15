"""Transparent, conservative stage diagnosis. Never presents keyword matches as mind reading."""

STAGES = ('START','FORWARD','STUCK','BACKWARD','BRIDGE','CALCULATION','REFLECTION')
STUCK_TERMS = ('卡住','不会','不知道','没思路','想不出','下一步','没想法','stuck')
BACKWARD_TERMS = ('反推','从目标','逆向','要证明','从结论')
BRIDGE_TERMS = ('突破','想到了','联系起来','构造','桥梁')
CALC_TERMS = ('配方','化简','展开','运算','计算')


def diagnose(text, existing_turns, self_report_stage=None):
    """Explicit self-report > conservative phrase rule > START/FORWARD default.

    This is not a validated cognitive-state classifier. Evidence is recorded.
    """
    if self_report_stage is not None:
        if self_report_stage not in STAGES:
            raise ValueError('Unsupported stage')
        return {'stage':self_report_stage,'source':'STUDENT_SELF_REPORT','matched_terms':[],
                'confidence_kind':'USER_DECLARED_NOT_VERIFIED'}
    lowered=text.lower()
    # Negated colloquial mentions must not trigger a false stuck diagnosis.
    for neg in ('没有卡住','没卡住','不是卡住','不卡住','不再卡住'):
        lowered=lowered.replace(neg, '')
    for stage, terms in [('STUCK',STUCK_TERMS),('BACKWARD',BACKWARD_TERMS),
                         ('BRIDGE',BRIDGE_TERMS),('CALCULATION',CALC_TERMS)]:
        matched=[term for term in terms if term in lowered]
        if matched:
            return {'stage':stage,'source':'PHRASE_HEURISTIC','matched_terms':matched,
                    'confidence_kind':'UNCERTAIN_RULE_CLASSIFICATION'}
    return {'stage':'FORWARD' if existing_turns else 'START','source':'DEFAULT_SEQUENCE',
            'matched_terms':[],'confidence_kind':'NO_COGNITIVE_INFERENCE'}
