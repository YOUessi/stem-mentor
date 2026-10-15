# 2026-10-15 设备迁移与 v0.5 本地验收记录

## 用户指令与新的唯一开发设备
用户明确要求：本项目停止在 Tang 上实施，并删除 Tang 上相关内容；后续开发与测试全部改为 MacBook Air，项目放在「文件」目录下。

- 设备：YOUTangdeMacBook-Air.local。
- 唯一工作目录：`/Users/youtang/Documents/文件/stem-mentor`。
- GitHub 项目：`YOUessi/stem-mentor`。
- 不再将 Tang 作为本项目的开发、测试、训练或运行设备；未来只有用户重新授权才改变。
- 本地数据：合成学生数据；当前模拟系统不接外部 LLM API。

## 迁移与清理核验
1. 在 Tang 上核实仅有本轮为 STEM Mentor 创建的两个目录：`/home/you/projects/stem-mentor-offline-v05` 和 `/home/you/projects/stem-mentor-v05-checkout`。
2. 将未入 GitHub 的 v0.5 工作整理为本地 Git 提交 `f94e470`。因 GitHub 直连 HTTP/2 报错，转而通过 Tailscale 内网的临时只读文件服务传输项目归档，不在 Tang 继续开发。
3. 归档 SHA-256：`eecd7133294c34acf95405bb28a38b1d4a3cbf370da504c6a41abe700b782d90`，Mac 端校验一致。
4. Mac 端解压后检查 Git 历史、v0.5 新模块与干净工作目录。
5. 终止 Tang 传输服务，仅删除上面两个项目目录以及 `/tmp/stem-mentor-transfer-20261015`，终端返回 `TANG_PROJECT_CLEANUP_VERIFIED`；未触碰 Tang 其他项目。
6. Mac 上先前不存在名为「文件」的目录，因此创建 `~/Documents/文件` 并存入 `stem-mentor`。
7. 创建本地 `.venv`，使用 macOS Python 3.13.13 和 SymPy 1.14.0；虚拟环境被 Git 忽略。

## Mac 实测（离线确定性系统）
- `PYTHONPATH=. ../.venv/bin/python -m pytest -q`：85 通过，1 条 Starlette/AnyIO 弃用警告。
- `evaluate_policy.py`：33/33 合成教学与基本检索检查通过。
- `evaluate_v05.py`：40/40 结构检索硬例通过（22/22 正例位于前三，18/18 负例正确排除）。
- `node --check apps/web/app.js`：通过。
- 所有资料仍标记 `expert_review=PENDING`，没有真实教师盲审与真实学生学习增益测量。

## 仍需注意
- 本项目是按方法/结构标注的离线模拟引擎，不等于真正理解任意题目的大模型。
- 当前仓库为公开仓库，不得上传真实学生信息或未授权教材材料。
- GitHub 与 Mac 本地 Git 连接偶发超时，仓库内容应以成功确认的远端提交为准；如使用连接器提交，需确认提交记录。
- 不在 Tang 恢复任何本项目工作进程。
