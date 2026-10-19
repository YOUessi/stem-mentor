# 复平面、集合与数轴不等式 v0.10 Implementation Plan

> **For agentic workers:** execute via superpowers:executing-plans with test-driven-development. 用户已明确授权沿连续路线实施，不在已确定任务之间重复征求确认。无子 Agent 调度工具，独立测试进程可以并行。

**Goal:** 保持绿色 UI 与旧39场景，为高中复数、集合、区间和不等式增加10个受控交互场景，明确数学边界，不将观察行为当成自动掌握。
**Architecture:** 两个纯数学内核（复数/有限集合、实区间/不等式）分别配合两个SVG视图模块，复用现有controller与只读场景目录。共有8个工具族、49场景；共享controller单一集成，不并发写同一文件。
**Tech Stack:** 原生JavaScript/SVG、Node node:test、FastAPI、Python pytest、Playwright+Mac Chrome。无新增网络依赖。
**Spec:** docs/design/FOUNDATION_EXPLORERS_V010.md；上层授权与队列见 docs/planning/CONTINUOUS_DELIVERY.md。

## Global Constraints
- 仅 /Users/youtang/Documents/文件/stem-mentor，MacBook Air；不使用Tang。
- 原绿色/米白主题 apps/web/styles.css 不变；新能力只做增量样式。
- 不接模型API，不改变学生成绩/掌握状态；辅助结果默认隐藏、学生自主显示。
- 113条为项目工程知识拆分，教师审核PENDING；新增支持须映射到具体预设，并注明局限。
- 测试使用临时数据库。先冻结代码、测试与存档，再PR/CI/合并与本地服务更新；原学生模拟数据库保留。

## Review Focus
- 复数除数为零、零复数辐角、负角/多圈旋转：显示未定义，禁止NaN进入SVG。
- 有限全集变化、空集/全集/重复成员：补集必须相对当前U，交/并/差与德摩根对应实际成员。
- 区间端点相同、逆序、开闭相接、无限端点：区分空集与单点，∞永远不闭合，缺失点不得误合并。
- 线性系数零、负系数翻向、二次重根/无实根/退化、绝对值右侧负数：解集与真值测试一致，不只画抛物线。
- 数学选择控件、拖动/连续键盘、手机触控与跨场景切换：控制器正确同步且不残留事件，不写虚假学习事件。

## Task 1 — 数学纯内核与真值测试
**Create:** apps/web/lab/foundations_math.js，apps/web/lab/interval_math.js；tests/node/foundations_math.test.cjs，interval_math.test.cjs。
**Interfaces:** complexInfo(z), complexOp(z,w,op), rotateComplex(z,degrees,scale); finiteSets(U,A,B,op); interval(lo,hi,lc,rc), normalize(parts), contains(parts,x), union/intersect/complement/difference, solveLinear(a,b,relation), solveQuadratic(a,b,c,relation), solveAbs(h,r,relation)。区间结果为规范化数组，无限端点只在数学内核中表示。
- [x] 写缺失模块与数学断言，运行Node确认失败。
- [x] 复数精确坐标测试、乘除逆运算；有限集合全成员规则/256组性质；区间端点与补集性质；200组不等式参数对照采样点真值。
- [x] 实现有限数验证、实际集合成员和解析解集；不eval、不执行用户代码。
- [x] Node全部通过；旧28条测试保持通过，独立提交。

## Task 2 — 场景目录与选择型参数
**Create:** curriculum/highschool_math/extend_v010.py，backend/tests/test_v010_catalog.py。
**Modify:** build_presets.py、build_curriculum.py、math_lab_catalog.py、controller.js。
**Interfaces:** 保留数值参数min/max/step/value；可选 options=[{value:number,label:string}] 提供运算符/端点选择。校验options唯一合法及默认值在候选中。
- [x] 后端失败测试：10个新预设、49总数、8工具族、options边界及可复现生成。
- [x] 新场景 complex-point/operations/rotation、sets-operations/complement、interval-single/operations、ineq-linear/quadratic/absolute。
- [x] 原有39场景继续测试，仅将旧总数断言改为保留旧ID加新版总数检查，禁止删原测试来掩盖回归。
- [x] 课程新增复平面/集合/不等式基础支持，仍不宣称任意命题逻辑、任意参数不等式已实现。

## Task 3 — 复平面与韦恩图
**Create:** apps/web/lab/foundations2d.js；tests/browser/test_math_lab_v010.py（对应部分）。
**Interfaces:** MentorFoundations2D.supports(id), draw(svg,preset,params,view,scene)，scene.onParams与onSceneChange控制参数/有限成员；extraControls容纳可键盘操作的集合归属编辑。
- [x] 浏览器红灯：新场景入口、操作结果隐藏/显示、除零提示、连续键盘端点移动。
- [x] 实现Re/Im轴、复数拖点、共轭/模/辐角、四则运算、旋转缩放；结果超出视口时自适应，标清坐标比例。
- [x] U={1..N}、A/B可编辑成员，四个区域与真实交集对应；结果区域/元素主动高亮，全集改变剔除越界成员并提示。
- [x] 空集、包含关系、全集/补集、德摩根两边相等的实际成员测试；图面积不表示基数。

## Task 4 — 区间数轴与不等式
**Create:** apps/web/lab/numberline.js；browser测试对应部分。
**Interfaces:** MentorNumberLine.supports(id), draw(...); 复用interval_math唯一数学真值，不从像素推断集合。
- [x] 浏览器红灯：空心/实心端点、开放射线、单点/空集、两区间交并差和相对R补集。
- [x] 实现可拖动/键盘移动端点，符号选择与探针成员判定；反转端点不擅自交换。
- [x] 实现一次、二次和绝对值不等式，比较符<、≤、>、≥；学生开启后显示精确集合类型和数轴解集。
- [x] 验证a=0、重根、负系数、r<0、开闭切换；数值根显示近似说明。

## Task 5 — 验收、记录与交付
**Files:** scripts/check_v010.sh、测试runner/CI、README、日期日志、结果JSON与真实截图。
- [ ] 数学Node、Python后端、隔离Chrome独立进程并发，保留PID/退出码/时间/源提交和日志哈希。
- [ ] 旧版绿色教学/v0.7/v0.8/v0.9以及新49场景与极端组合全部通过；实拍桌面/手机截图并查看。
- [ ] 校对源码、数学边界、选项/焦点、课程证据；缺陷先失败测试再修复。无独立agent时如实记录同执行者复查。
- [ ] 上传计划/代码/原始日志；PR和CI通过再合并；同步Mac并只替换本项目8000进程；保留真实模拟库。
- [ ] 看板记录完成及下一批数列任务，不承诺后台无限执行。

## 恢复执行裁决
Task1已存在于72ce8d3，不重做；Task2先观察9项目录测试失败后实现，全部后端127项通过。Task3/4先观察浏览器缺失入口失败，再实现与测试；截图复查的手机裁切、公式不随运算变化和小数重根判别式误差均留下失败→修复→通过证据。接下来从冻结版本执行完整并发验收及发布。
