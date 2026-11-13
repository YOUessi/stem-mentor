# Batch29｜真实失败、诊断与修复

所有命令仅在授权的 MacBook Air、独立 `stem-mentor-kb-batch29` worktree 执行；Tang 未参与。初始化基线为 Batch28 GitHub SHA `db762e81841d01ad8a5d7bde2885ae5af7134003`。本文件是独立版本化的失败记录，不能只保留成功日志。

1. **第一次执行命令包装错误**：macOS 默认 zsh 中 `status` 是只读特殊参数，在尝试保存测试退出码时触发 `zsh: read-only variable: status`，测试日志未能被正常汇报。改为 `rc`，没有修改数学内容。
2. **第一次 pytest 收集失败**：从仓库根路径用 `PYTHONPATH=.` 执行导致 `ModuleNotFoundError: No module named 'app'`。改用既有项目标准命令 `(cd backend && PYTHONPATH=. ../.venv/bin/python -m pytest ...)`。这是路径设置错误，不代表测试通过。
3. **第一次有效 Batch29 定向运行出现 42 项失败**：`3483 passed, 42 failed`，见 `python-initial-failure.log`。全部来自复数除法交叉核验中直接对比 SymPy 两个结构不同、但数学上等价的未充分化简表达式，例如 `-1+2I` 与 `I(2+I)`。初版测试使用 Python `==` 比较表达式结构而非数学等价。修复为 `sympy.simplify(lhs-rhs)==0`，保留独立的乘回原复数的精确检验，并对全部参数复测。**修复的是测试断言，不是为了避开错误样本而删除案例。**
4. 第二次 Batch29 定向在 Mac 验证：**3525 passed / 0 failed**，见 `python-targeted.log`。测试包括 48 项原风险 SHA/审核字段门禁、20 类正反受控样本、源数据篡改负例以及约 3400 项有限枚举和 SymPy 交叉验证。
5. 尚待的全量/浏览器/远端 CI 结果记录在本批正式执行报告中，若出现新失败须继续追加此文件并保留原日志。

**证据边界**：所有正例是精确有限实例，40 项正/负 fixture 对不意味着 40 条完整数学定理被证明。历史 538 条自然语言证明步骤继续未形式认证；不会自动批准任何知识单元。
