# STEM Mentor｜KB Batch09：7 篇数学定理草案与模型草案适配器

2026-11-03，MacBook Air 独立工作树 feat/kb-batch09-safe-tutor，基于 Batch08 Draft PR #34；未经审核的分支尚未进入 GitHub main。

## 一、实质新增
本批完成 7 篇原创 REVIEW_PENDING 深度定理单元，各有明确假设、分步证明草案、反例、2 道教师侧例题、错因和提示及迁移：
- math.hs.calculus.chain-rule：复合函数链式求导；用连续余项避免对零增量非法约分。
- math.hs.calculus.quotient-rule：商法则、分母非零限制、可去间断点。
- math.hs.calculus.fermat-stationary：费马引理、内点可导与逆命题反例。
- math.hs.vector.cauchy-schwarz：实向量不等式、零向量和等号线性相关条件。
- math.hs.counting.binomial-sum：二项式系数和、交错和、n=0 特殊情况。
- math.hs.probability.expectation-linearity：有限样本空间期望线性性无需独立性。
- math.hs.function.bisection-root：连续异号区间二分求根与严格误差界。
构建器 scripts/build_kb_batch09_lessons.py 以 --check 保证源数据可重现。

现有 153 深度草案（73 个定理、66 个概念、14 个方法），上批 146；全部待人工审核、正式教师批准 0、完整定理形式证明 0。未正式验证的证明步骤为 237；10 项冲突不自动合并，23 项语义缺口继续 OPEN；选修 A–E 仅为高层槽位，正式课标原子核对 0。

## 二、模型教学草案接口（严格禁用学生直接输出）
backend/app/model_tutor_draft.py 提供编辑态、默认关闭的 HTTPS OpenAI-compatible Chat Completions 适配器。只有明确编辑态、合法模式、学生请求帮助、明确云端同意、外部签署批准知识存在、显式启用环境变量、凭据和精确安全端点条件全部成立才发起网络请求。禁止重定向、系统代理和非批准 endpoint；有限超时、最大 Token 预算。对模型仅传当前短问题与已批准第一层提示，不传教师证明、题解、学生历史或照片。

模型输出必须符合精确 JSON、引用已批准的知识 ID；任何内容仍是 MODEL_DRAFT_REVIEW_REQUIRED、student_visible=false、model_claims_verified=false。无未经认证的公开 API 路由。当前没有正式教师批准的知识，因此真实模型外发为 0；本批使用 MockTransport 离线测试，不代表已上线学生云端教学 Agent。

## 三、失败与测试证据
新安全测试覆盖独立挑战、用户授权、私有端点、伪造 ID、模型错误 JSON、HTTP 失败、凭据泄露防护；新 SymPy/精确整数与有理数测试覆盖七定理的若干合法边界与反例，绝不代替完整证明审校。

首次专项测试发现非 ASCII 模型名可被 isalnum 错误接纳、Pydantic 布尔宽松强制转换；已修复。数学测试修复了把 SymPy 在 x=0 的符号函数替代双侧差商的错误，以及浮点与 Rational 混用。首次全量 Python 1841 passed / 1 failed：历史 Batch02 对照误将新的 Batch09 文件计入冻结的 39 篇候选分母；已只排除新独立文件，39→29+10 不变。随后完整复验 Python 1842 passed（既有 1 条第三方弃用警告），Node 111 passed。Chrome 工作台、数学交互、iPad 模拟见 evaluations/results/2026-11-03-kb-batch09/browser.log。

审计：docs/evaluation/KB_BATCH09_RELEASE_AUDIT.json；所有学生内容仍 fail-closed；GitHub PR/CI 以真实远端结果为准。

## 四、下一批
优先核对官方必修、选择性必修及选修 A–E 的原子课程范围；对 237 条证明义务、10 个历史冲突做独立证据审查；建设真实教师身份和双签审查流程；在有学生鉴权、云端同意、条件验证和独立模型评测后才逐步上线学生 Tutor。