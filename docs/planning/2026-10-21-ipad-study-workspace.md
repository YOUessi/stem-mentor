# v0.14A iPad Study Workspace / 笔记式做题（2026-10-21）

状态：MAC PILOT IMPLEMENTED; GITHUB PR & iPad HARDWARE QA PENDING。只在 MacBook Air 的 ~/Documents/文件/stem-mentor-ipad-v014 独立 Git worktree 开发，保留 ~/Documents/文件/stem-mentor 中未提交的旧工作。正式版 ~/Documents/文件/stem-mentor-release 只有经完整CI后的合并才能更新。禁用Tang和LLM API。

## 产品路径与验收
- /ipad：绿色学习首页、继续上次学习、合成学生近期已完成题目、待复习数量、进入手写做题。错题没有数学评分时只能显示“待核实的思路”，不能虚构错题与掌握率。
- /ipad/study：横屏优先全幅手写画布；题目顶部可折叠。Agent默认收起，主动打开时侧栏分配25%-30%宽；窄屏底部抽屉。收起后视图位置与笔迹不变。
- 手写：笔迹/压感基础支持、橡皮（整笔擦除）、套索选中移动、多页面、撤销重做、颜色/笔宽、单指平移、双指平移缩放、独立保存与刷新恢复。手掌事件只有启发式隔离，不宣称真实Apple Pencil压感/防误触验证。
- 数据：使用IndexedDB保存向量笔迹；按合成student_id + session_id区分。不得直接把手写笔迹上传后端或声称它已被识别、评分、审核。只有用户填写说明并主动发送时才调用现有 Tutor API。
- Agent侧栏：学生写题时零自动消息；可以先套索选中某部分笔迹，主动打开侧栏再填写文字说明。没有OCR/数学式理解，不编造对笔迹的诊断。
- 学习事件：原有v0.13会话与历史保持兼容，用户按需将文字想法提交。完成前先显示“手写记录只是草稿，未自动评分”。
- 用户体验：按钮适合iPad触屏（44px触控目标）、主题#174938、离线资源、iPad Safari需单独真机验收。本轮Chrome模拟触控和笔事件只保证基础功能，不证明真机低延迟、精确防手掌误触。

## TDD/集成任务
1. 测试先行：vector stroke/history/eraser/lasso/math坐标转换纯JS；PyTest路由/与旧版兼容，Chrome真实交互脚本（Home -> Paper -> Agent -> reload）。
2. 前端依赖为零：apps/web/ipad/ink_core.js、storage.js、app.js、ipad.css 和 index.html；单入口HTML依据window.location.pathname显示首页/书写。
3. FastAPI增加 /ipad 与 /ipad/study，旧/及原assets不改，旧绿色学习工作台上仅新增可选入口。
4. 回归：Node全部、Python全部、完整老浏览器、独立Chrome 1024/768/390与触控笔/鼠标，检查没有学习成绩/写入虚假报告。
5. 提交GitHub PR；CI通过再合并，稳定版通过独立worktree升级；保留合成学生数据库。研发记录要区分功能完成、Chrome测试与iPad真机验证。

## 2026-10-22 本地实施进度

- [x] 向量笔迹不可变内核、缩放锚点、压感采样、上限及会话归属测试。
- [x] 绿色首页、默认关闭的 Agent、横屏右栏和竖屏底部抽屉。
- [x] IndexedDB、刷新恢复、多页、撤销/恢复、整笔擦除和套索移动。
- [x] Chrome 1024/834/390px；双指缩放1×→2×无误写；CDP合成笔压力采样。
- [x] 仅主动提交文字进入离线规则 Tutor，画布笔迹默认不上传。
- [x] Node/Python 单测与完整 Chrome 历史回归（以最终日志退出码为准）。
- [ ] GitHub PR / 远端 CI 与合并验证。
- [ ] 实际 iPad Safari 和 Apple Pencil 书写延迟、掌托误触、长时间本地存储验证。
- [ ] 生产账户认证、隐私合规、云备份及手写数学识别。

**注意：** 当前仅可选 Web Pilot，不代表用户已批准全面替换 v0.13 稳定版。
