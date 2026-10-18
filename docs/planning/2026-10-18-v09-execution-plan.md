# 高中数学探究工具 v0.9 Implementation Plan

> **For agentic workers:** use superpowers:executing-plans task by task. 当前没有独立子 Agent 工具；实现由当前执行者完成，独立测试进程并发运行，不把并发冒称多 Agent。

**Goal:** 沿 v0.8 已批准路线，在绿色学习实验室交付平面向量、单位圆、动态导数/切线和空间截面，增加 10 个受控场景，并给课程覆盖声明建立可追溯证据。
**Architecture:** 共享纯数学内核 + 两个独立 SVG 模块；复用既有 2D 坐标和 3D 投影/旋转；单一 controller 集成，禁止多个写进程同时修改共享文件。保留当前所有学习会话、学生思维图与教师提示行为。
**Tech Stack:** 原生 JavaScript/SVG，Node 22 node:test，Python/FastAPI，Playwright + 本机 Chrome。
**Spec:** docs/design/HIGH_SCHOOL_MATH_VISUAL_V08.md 第 6 节及本轮用户“列计划，持续执行”的明确授权。

## Global Constraints
- 唯一目录：/Users/youtang/Documents/文件/stem-mentor；只使用 MacBook Air，不使用 Tang。
- 沿用绿色主题；apps/web/styles.css 不变；不引入网络依赖、不调用 LLM API。
- 分支开发、完整测试后才合并；不触碰用户真实数据库，浏览器测试使用临时数据库。
- 113 条知识清单仍是工程拆解、教师审核 PENDING；不以场景数量冒充完整课程覆盖。
- 本轮按用户要求连续执行，不反复要求确认既定路线；新授权/敏感数据/破坏性行为才停下询问。

## Review Focus
- 零向量及投影到零向量：夹角与投影应返回未定义，不显示 NaN 或错误答案。
- 单位圆 90/270 度与多圈负角：正切未定义与象限/坐标轴应区分，度数与弧度一致。
- 割线 h=0、对数点越域、绝对值折点：不得把未定义割线或不可导点画成正确切线。
- 平面截立体过顶点、沿棱、贴合面、无交、五/六边形：去重、共面、面积、类型必须一致。
- 切换场景、手机触控、反复重绘：不得残留上一场景事件；相机变化不得改变截面积；现有 29 场景保持可用。

## Task 1 — 纯数学内核与失败优先测试
**Files:** Create apps/web/lab/exploration_math.js; tests/node/exploration_math.test.cjs.
**Interfaces:** vectorMetrics(a,b,k), unitCircle(degrees), derivativeInfo(kind,x,h), boxGeometry(w,d,H), pyramidGeometry(w,d,H), slicePolyhedron(vertices,edges,normal,offset), sliceSphere(radius,normal,offset).
- [x] 写 node:test：零向量、0/90/180/270 度、对数域、h=0、abs 折点、正方形/三角形/六边形截面、相切与无交、固定随机平面共面性。
- [x] 执行 node --test tests/node/exploration_math.test.cjs，确认因功能缺失失败。
- [x] 实现向量、单位圆、解析导数和凸多面体边-平面相交（排序与面积），无 eval。
- [x] 全部测试通过并提交核心模块。

## Task 2 — 2D 探究工具与场景资料
**Files:** Create apps/web/lab/explorers2d.js; curriculum/highschool_math/extend_v09.py. Modify build_presets.py 及 visual_presets.json。
**Interfaces:** MentorLabExplorers.supports(id), draw(svg,preset,values,view,scene); scene.onParams(values) 同步拖动与参数。
- [x] 新增场景 ID：vec2d-add、vec2d-projection、unit-circle、derivative-quadratic、derivative-cubic、derivative-log、derivative-abs。
- [x] 先写浏览器测试：拖向量端点更新数量积，单位圆联动 sin/cos，h 收敛时割线接近切线，abs(0) 不画切线。
- [x] 实现七场景；只主动开启辅助线/切线，保持猜想优先，不影响解题评价。
- [x] 手机与桌面验收，公式、读数、拖动、参数保持一致。

## Task 3 — 3D 空间截面
**Files:** Create apps/web/lab/sections3d.js; Modify scene3d.js 导出已存在投影工具与扩展钩子。
**Interfaces:** MentorLabSections.supports(id), draw(svg,projection,preset,params); 返回 info。使用 Task1 截面数学内核，不靠画面近似算交点。
- [x] 场景：3d-section-prism、3d-section-pyramid、3d-section-sphere，平面 nx*x+ny*y+nz*z=t。
- [x] 浏览器失败测试：切面顶点、六边形、空集、相切、旋转不变面积、零法向量提醒。
- [x] 实现透明切面/真实交线/截面积读数，凸多面体类型区分 EMPTY/POINT/SEGMENT/POLYGON，球区分 EMPTY/POINT/CIRCLE。
- [x] 测试与截图通过，数学内核复核共面性/边界条件。

## Task 4 — 集成与真实覆盖映射
**Files:** Modify apps/web/lab/controller.js; index.html; math_lab.css; backend/app/math_lab_catalog.py; curriculum_map.json; existing builders/tests.
- [x] 39 场景、5 类工具（增加平面向量）；保持已存在的29场景测试，不通过删除旧测试掩盖回归。
- [x] 课程每个“基础交互”条目需给出 available_presets 和 capability_limits；原先仅有通用场景但无专项工具的二面角/线面角等降为规划，明确记录。
- [x] 课程按钮定位到对应场景，而非随便打开整个类别。
- [x] 清除前一场景指针事件，处理异步数据及减少动态偏好；支持已保存学生会话。
- [x] 每项后端契约与前端验收通过。

## Task 5 — 并行验收、留痕与发布
**Files:** scripts/check_v09.sh; tests/browser/test_math_lab_v09.py; tests/browser/test_math_lab_v09_extremes.py; docs/logs/2026-10-18-v09.md; evaluations/results/2026-10-18-v09.json; CI; README.
- [ ] Node 数学内核和 Python 回归以独立进程并发，分别保存退出码和日志；浏览器使用独立数据库和唯一输出目录，不写真实学习数据。
- [ ] 完整旧版绿色 UI、v0.7 学习工具、v0.8 全场景及 v0.9 新场景与极端测试通过。
- [ ] 人工查看真实截图，禁止拿参考图冒充截图；不把数值测试等同于证明或学习效果。
- [ ] 上传计划、代码、日志、截图；PR CI 通过后合并；Mac main 快进同步并安全更新仅本项目 8000 端口服务。
- [ ] 更新 docs/planning/CONTINUOUS_DELIVERY.md，列出下一批尚未执行任务，无后台无限运行承诺。

## 后续队列（本轮之外）
P1：复平面、数轴区间、集合/逻辑图；P2：数列递推与求和；P3：计数、概率树与统计分布；P4：教学动作/迁移测评、资料授权与教师审核；P5：用户明确授权后再接模型 API。每批都带数值真值测试、教学反例、源数据及版本化验收。

## 2026-10-19 执行补充
保留现有工作，在集成前补充 SVG 重绘后键盘焦点回归。新增失败用例 → 修复 → 同例通过已记录在日期日志。验收及 GitHub 交付继续使用原有计划，不扩展至未授权模型服务。
