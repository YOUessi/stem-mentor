# 系统技术架构 v0.2

## 系统边界
浏览器 Web App → FastAPI 业务服务 → 教学策略引擎（状态机）→ 受控数学题卡/规则 → SQLite 本地演示库（后续迁移 PostgreSQL/pgvector）。**无模型 API**，规则不能被称为 LLM 输出。

## 教学运行循环
1. 接收题目、学生原始文本、求助意愿、模式。
2. 读取会话历史和个人学习事件。
3. 对受支持的题目卡进行条件/方法结构匹配；不支持的题目走保守通用启发。
4. 记录当前思维阶段（正推/卡点/逆推/桥梁等）。
5. 评估是否允许提示，优先保持自主思考。
6. 检索且验证可引用的真实旧题经历，避免表面相似误迁移。
7. 根据模式和阶段选择本次唯一的主要教学动作。
8. 展示简短可操作的问题或反馈；持久化事件、提示级别、历史引用与思维节点。
9. 在学生主动结束后记录复盘，按需要展示微考点与候选复习。
10. 后续版本接入真正模型前，每一步都要有独立评价与回退。

## 部署建议
首版单体 FastAPI 服务 + 静态响应式前端 + SQLite 本地存储，Docker 一键运行。未来稳定后可拆 Next.js 前端 + PostgreSQL/pgvector + Redis 异步复习调度。抽象知识检索接口、学生记忆接口和教学决策接口，避免与某个 LLM/Agent 框架绑死。

## 安全边界
浏览器不得接触内部全解数据及任何模型密钥；所有输入均为不可信内容；无身份认证的演示只允许合成数据。正式使用必须增加身份认证、授权隔离、数据删除/导出、年龄/监护人配置与内容审核。

## API 合约（模拟版）
GET /health
GET /api/catalog
POST /api/students
POST /api/sessions
GET /api/sessions/{id}
PATCH /api/sessions/{id}/mode
POST /api/sessions/{id}/turns
POST /api/sessions/{id}/complete
GET /api/students/{id}/episodes
GET /api/students/{id}/reviews
POST /api/students/{id}/reviews/{point_id}/answer

每个教学响应带 action、reason/stage、hint_level、verified、engine=DETERMINISTIC_SIMULATION；与真实 LLM 响应严格区分。
