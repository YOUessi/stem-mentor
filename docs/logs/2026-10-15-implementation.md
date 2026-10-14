# 2026-10-15 模拟版开发与验证记录

## 范围
按照需求 v0.2 构建无需任何大模型 API 的、题卡驱动的本地 Web 模拟系统。支持三模式、SQLite 持久化、结构关联的真实历史题回忆、微考点间隔复习、思维轨迹和限定数学恒等式检查。

## 实现
- `backend/app/catalog.py`: 六道人工编排示例题、四张方法卡、五个微考点。
- `backend/app/tutor.py`: 规则化思维阶段/教学动作，明确边界和提示等级。
- `backend/app/storage.py`: SQLite 保存虚拟学生、会话、轮次、历史经历、复习状态和复习事件。
- `backend/app/math_tools.py`: 固定审核公式示例的 SymPy 验证，不解析执行任意学生代码。
- `backend/app/main.py`: FastAPI 接口与响应式工作台。
- `apps/web`: 学习、旧题、考点、方法四个视图。
- `backend/tests/test_flow.py`: 模式/迁移/隔离/复习/边界/数学验证/持久化回归。

## 本地测试
- `cd backend && PYTHONPATH=. pytest -q` → **10 passed**。
- `node --check apps/web/app.js` → 语法检查通过。

## 限制
- 任意学生推导未实现可靠证明；教学回复均明确标记 `math_verified=false`。
- 自述完成只写 `SELF_REPORTED_NOT_VERIFIED`，不能代替独立掌握证据。
- 历史迁移需要真实 episode、共同方法和两条以上结构特征，不以题面词语判断。
- 微知识点的答案校验仅是规则匹配，不代表真正掌握。
- 首版为静态原生 JS 前端，未接入 Next.js，避免无必要依赖并可离线运行。
- 无模型 API、身份系统、正式教材、完整数学 RAG、手写识别、真实教学试验。

## 下一步
扩大题卡/误迁移负例、真实浏览器端到端与安全测试；获批准后再考虑模型接入和未成年人合规试点。
