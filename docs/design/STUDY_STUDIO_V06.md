# STEM Mentor · Study Studio v0.6 前端调研与设计记录

日期：2026-10-15
开发设备：MacBook Air，项目目录：/Users/youtang/Documents/文件/stem-mentor
交付目标：提升学生数学工作台视觉、交互与移动端体验；保留全部教学业务逻辑，零模型 API 调用。

## 1. 现有网页问题（改造前截图检查）

- 左侧导航、教学模式、题目、草稿、导师均为相似白色卡片，缺少清晰主次；深度阅读时不易定位正在思考的关键区域。
- 双栏固定，面对较长题目或导师解释不能调整比例。
- 空对话区没有可用的入门引导操作；移动端首次访问的初始化浮层可能遮挡题目。
- 原始学生草稿若在提交之前刷新，会丢失尚未记录的想法。
- 页面缺少可快速跳转的键盘导航，动效缺少明确的状态意义。

## 2. 实际参考资料与取舍

| 参考 | 来源 | 取用思路 |
|---|---|---|
| 数学练习界面 EduCare | https://dribbble.com/shots/27136650-EduCare-AI-Powered-Personal-Tutor-Dashboard | 练习内容优先，而非只展示统计数字 |
| TAITOR AI Learning Platform | https://www.behance.net/gallery/242183167/-TAITOR-AI-LEARNING-PLATFORM-WEB-DESIGN | 中央学习场景与对话并行 |
| Dribbble Learning Dashboard | https://dribbble.com/tags/learning-dashboard | 清晰卡片结构与视觉层级 |
| Reddit 设计灵感清单 | https://www.reddit.com/r/webdesign/comments/1i3go8q/25_best_ui_design_inspiration_websites_for_2025/ | 参考 Mobbin、Godly、SaaSpo 等来源 |
| Reddit 动画讨论 | https://www.reddit.com/r/reactjs/comments/1lgylud | 避免只为炫技而加入无关动效 |
| shadcn/ui Sidebar | https://ui.shadcn.com/docs/components/aria/sidebar | 可复用、可折叠的工作台导航 |
| shadcn/ui Resizable | https://ui.shadcn.com/docs/components/base/resizable | 拖动调整教学分栏，可键盘操作 |
| Motion for React | https://motion.dev/docs/react | 状态切换、共享布局、手势动画 |
| Motion 可访问性 | https://motion.dev/docs/react-accessibility | 响应用户减少动态效果偏好 |
| React Bits | https://reactbits.dev/ | 局部动效和状态变化表达 |
| Motion Primitives | https://motion-primitives.com/docs | 克制的微动画组件 |
| Magic UI | https://magicui.design/docs/components | Bento 网格和局部强调元素 |
| Aceternity UI | https://ui.aceternity.com/ | 展示型交互及未来官网设计 |

这些库本轮用于研究，未直接复制第三方组件源代码、版权设计或商业模板。未来真正引入组件前需核对版本、协议及包大小。

## 3. 本轮实施的设计系统

- 深海军蓝导航配合柔和浅色数学画布，蓝紫表示当前选择或思维引导，青绿色表示确认或进度。
- Hero 区域的已知→探索→突破→迁移路径是概念性示意，不是假造学生能力报告。
- 题目、学生草稿、导师对话和思路路径四种层级的标题、标识、间距与配色不同，避免所有内容一样重。
- 保留三模式，使用更清楚的卡片状态而不是多一个菜单。
- 可调整宽度的双栏（滑鼠拖动/键盘方向键，使用本地存储恢复），在狭窄设备自动变单栏。
- Ctrl+K / Command+K 快捷导航，有搜索、键盘上下选择、Enter 执行、Escape 关闭。
- 导师空态提供三种可点击的草稿起点；会话草稿刷新可恢复，发送后才清空。
- 采用 CSS 动效、视图过渡、思维轨迹更新动画，并通过 prefers-reduced-motion 尊重减少动态效果设置。
- 所有后端 API 与规则教学决策保持兼容，用户数据仍是合成演示。

## 4. 为什么暂时不直接迁移 React / Next.js

目前 FastAPI + 原生 HTML/CSS/JS 工作台已经有稳定 API、持久化和自动测试。为视觉改造全量迁移前端框架，容易引入大范围状态回归、外部依赖和构建风险。

因此 v0.6 采用低依赖的原生交互。需要复杂图形编辑、更多组件复用或团队协作时，再评估 React + shadcn/ui + Motion；不是说已经集成了这些包。

## 5. 检验与限制

- Mac Chrome 真浏览器桌面 1440px；手机/平板/桌面 390、768、1024、1280px，均检查无页面横向溢出。
- 手动/自动检查：键盘快捷导航、三种模式、草稿保存恢复、消息提交、思考轨迹、分栏大小持久化、移动端交互。
- 真浏览器 JavaScript pageerror 为零。
- 离线规则教学并不意味着真实 LLM 的教学质量已被验证；必须后续做真实学生与教师测评。
