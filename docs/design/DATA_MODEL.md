# 数据设计 v0.2

## 核心实体
student(id, alias, created_at)
session(id, student_id, problem_id, custom_problem, mode, stage, hint_count, created_at, completed_at)
turn(id, session_id, student_text, action, tutor_message, stage, hint_level, reference_episode_id, created_at)
episode(id, student_id, session_id, problem_id, method_tags_json, structure_tags_json, notes, evidence_status, created_at)
review_state(student_id, point_id, box_level, due_at, last_result, updated_at)
review_event(id, student_id, point_id, is_correct, answer_text, created_at)
mind_node(id, session_id, kind, content, verification_status, created_at)

## 方法/题目内容
problem_card(id, title, prompt, grade, subject, known/goal, method_tags, structure_tags, hint_scaffolds, boundary_conditions, source)
method_card(id, name, trigger_features, prerequisites, related_methods, failure_conditions, explanation, source)
micro_point(id, topic_tags, condition, prompt, reference_answer, applicable_exam_region/period, source)

## 设计原则
- 真实学生原文和证据链不应由模型摘要覆盖；摘要另存版本。
- episode 是某次实际学习的经历，不等于“已经掌握方法”；独立正确需要额外证明。
- 能回忆的历史题必须来自同一 student_id，避免跨学生引用。
- 复习结果必须来自有明确答案的检查，不能仅凭“我会了”增加强度。
- 默认不保存姓名、手机号、年龄等真实个人资料（公开演示）。
- 数据迁移脚本应可重跑、可测试，数据库修改不混写项目文档。
