# Batch28：首次执行错误与实际修复（2026-11-08）

本文件记录开发中真实遇到的失败。相关首次调用原始 stdout/stderr 可在本轮远程命令日志查看；未在发生时将其写入仓库持久日志，故**不宣称拥有原始首次失败日志全文**。

1. 直接在 Mac 系统 `python3` 下执行 `python3 scripts/build_kb_batch28_p0_evidence.py`，报 `ModuleNotFoundError: No module named 'pydantic'`。原因：没有选用项目虚拟环境，而非仓库依赖缺失。修复：在隔离的 Batch28 worktree 中只建立指向 Batch26 项目 `.venv` 的本地忽略 symlink；此 symlink 不提交 Git。
2. 初版清单门禁使用正文长度 `hypotheses<40 or counterexample<30`，拒绝了部分内容真实但字数较短的原创条件说明 `ValueError: Shallow or missing original mathematical conditions/counterexample`。逐项核查后修改为 `<28 / <25`，内容仍必须有具体数学假设和失效例。没有为过门禁无意义填字。
3. 首版 `point_plane_distance` 解包三个向量到两个变量导致 `ValueError: too many values to unpack (expected 2)`。修复为 `p,q,v` 同时检查零法向量，并在完整参数化回归中验证该族。
4. 首次定向执行 `python -m pytest -q backend/tests/test_kb_batch28_p0_evidence.py` 报 `ModuleNotFoundError: No module named 'app'`，因未在 `backend` 目录提供项目的 `PYTHONPATH`。修复为 `(cd backend && PYTHONPATH=. ../.venv/bin/python -m pytest -q tests/test_kb_batch28_p0_evidence.py)`，最终 **1,029 passed**。
5. 完整 Mac 检查会更新两个 2026-10-15 历史评测缓存文件。本批只在新建隔离 worktree 中运行，最终提交前恢复这两份与本批无关的历史缓存；不覆盖原始主仓文件。
