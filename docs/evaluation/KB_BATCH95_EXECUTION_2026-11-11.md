# STEM Mentor｜Batch95 Mac-only 执行及可审计验收记录（2026-11-11）

> 来源事实以 GitHub 独立 Draft PR 和本文件所记录的 Mac 源码、测试日志为准。所有课程材料均为原创教师侧审稿草案，`REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED`。以下数字不构成教师审核或官方课标全量完成。

## 本轮范围、依赖与设备

- 读取并核实母任务 #17 与 K00–K09 的 #18–#27，以及 Draft PR #118/#119 和 GitHub Actions #42961013759。#119 的上一批 CI 已于 2026-11-11 复核为 success（160/160 test steps）。
- 唯一开发/内容/真实测试环境：`YOUTangdeMacBook-Air.local`，工作树 `~/Documents/文件/stem-mentor-kb-batch95`；原 `~/Documents/文件/stem-mentor` 主工作树 11 项未提交修改未触碰，Tang 未参与。
- 上游为 Mac Batch94 源码 `ab0331b`；与 GitHub #119 的远端 head `96a216a8283c63052e223151489a29b708da3e6d` 具有相同 Git Tree。独立递进提交，不合并 main、不强推。
- 完整交付采取在远端 #119 head 派生干净交付工作树再 cherry-pick，本地源码工作树仍保留。最终远端 SHA 和 tree 以 PR/评论及本文件所属 GitHub 版本为准。

## K00/K02–K06：16份完整原创来源锁定数学讲义

- 16份讲义：**5 theorem、8 method、3 concept**，覆盖必修2、选择性必修4、选修A3/B3/C2/D2、选修E0。严格以**项目来源行及临时标签**为来源，不将其冒充官方知识原子。
- 具体主题：斜二测画法；两相交平面的交线；等比增长模型；常数函数导数；加法/乘法计数原理；分布列及方差；链式求导；拉格朗日中值定理；两类假设检验错误；二元函数定义域；线性规划顶点法；参数轨迹消元；肯定前件/肯定后件辨析；抽样框覆盖；正弦振幅频率；多节拍同步。
- 每份均含来源候选ID/行 SHA/课程标准版本和轨道、适用域/前提、分步证明或方法合法性依据、反例与错误修复、两道原创教师例题、三级提示和近远迁移。累计 **32 道例题、48 级提示、32 条迁移任务**。所有教师完整解答仍仅供编辑侧。
- 正式审核：每份 `REVIEW_PENDING`，审核员为空；未标记 APPROVED；不能以自动测试代替人类教研确认。
- 来源证据与七轨矩阵见 `docs/evaluation/KB_BATCH95_SOURCE_LESSON_MATRIX.json`；内容见 `knowledge/deep/v1/batch95_deep_scope_16.json` 和 `docs/evaluation/KB_BATCH95_DEEP_LESSONS.md`；可重复生成器 `scripts/build_kb_batch95_depth.py`。
- 428 来源行 ≠ 300 临时主题 ≠ 官方课程知识原子分母。Batch94尚未单项编辑审查的临时主题96，Batch95新增16份初稿后 **80 个仍无单项审查**；**134 个仍无成对比较**。七轨正式原子分母仍均为 null；真人逐页原子化审核仍 **0/61 页**；教师批准0，学生权威发布0。

## K01/K07/K08：Schema、可调用数学域校验和访问门禁

- 生成器强制 DeepLesson 的类型字段、非空前提、分步论证、两道不同例题、反例/错因、提示/迁移、来源ID及 SHA、审核状态，并防止重复/未知来源和虚高覆盖数字。CI 和 Mac 运行器均新增 `--check` 生成漂移校验。
- 为16个知识主题配16组受控有限正例及失效情形；Fraction/SymPy/模逆解同余，仅支持有限验证，**0份一般定理形式证书**。
- 实际修改真实可调用验证器：`real_log_domain` 和 `real_sqrt_disk_domain` 不再将超大整数/有理数强行转成浮点；圆盘判定采用有限实数转换后的精确平方和，防止 `inf <= inf` 错把域外点接纳。`next_sync` 改用广义中国剩余定理处理负初相、大偏移、互不相容周期，不再依赖有漏洞的枚举上界。
- 追补 Batch94 两类验证债务：`valid_line_normal` 真正判定二维直线法向量非零；`induction_base_valid` 真正核对指定归纳基例，不再使用硬编码布尔常量模拟域拒绝；附真实拒绝负测。
- 审核隔离：新16份能在编辑环境检索；学生查询不能取得 `REVIEW_PENDING` 全文或教师答案，返回 `NO_APPROVED_EVIDENCE`。学生自由解题步骤**不宣称已验证**。
- 首次补丁暴露 `Fraction` 与导入别名 `F` 不一致，触发运行时报错，已立即修复，重新执行生成器 + 联合专项后 **305 passed**；审稿及失败案例已留存本报告。相关新测试覆盖精确域大整数/巨大 Fraction、负相位 CRT、历史假造布尔门禁等。

## 实际 Mac 验收（最终日志可复现）

- 联合专项：`backend/tests/test_kb_batch94_deep_scope.py` + `backend/tests/test_kb_batch95_depth.py` = **305 passed**，见 `evaluations/results/2026-11-11-kb-batch95/mac_specialty_final.log` 与退出码。
- Batch95初始专项 164 passed、初始全量 Python 62,664 passed / 5 skipped / Node 111 passed；这属于**补丁前**基线，不可冒充补丁后重新运行结果，原日志分别存档。
- **补丁后最终 Mac 全量**：`scripts/mac_check.sh` 真实重跑通过；Python **62,674 passed / 5 skipped / 0 failed**（1条第三方依赖警告）；Node **111/111 passed**；退出码0。完整日志 `mac_full.log`、`mac_full.exit`。专项305项属于全量62,674项的子集，不重复累计。
- **Chrome 15脚本+浏览器 pytest2**：实际重新运行 `scripts/mac_browser_check.sh`，**15/15 脚本通过、2 passed（pytest）**，退出码0；未触达真实iPad，仅为Chrome模拟。见 `mac_browser.log` 和 `mac_browser.exit`。
- GitHub CI：本报告在新PR创建前已冻结本地源码与真实Mac验收；远端状态以PR对应Actions实时结果与Issue验收评论为事实源，尚未声称通过。CI通过也只能说明软件回归通过，不能自动授予教师认证。

## 未完成门槛及下一批

- 七轨**官方课标知识原子分母仍未知**；其独立编辑审查、跨页跨轨去重、教师逐页审校是 K00 的阻塞。将80个单项未审查、134个成对关系未比较的临时主题继续与实质内容建设并行，不能用“300临时主题”当官方分母。
- 历史 **538 未认证证明步骤、106 无直接审稿材料的 P0步骤、10组未裁决数学冲突**未受本轮数量变更。独立教师批准0；学生权威发布0。
- Batch96 应优先建立有可复核课标证据的七轨原子候选台账，针对数学错误高风险的未见题补充可调用前提守卫，继续批量扩展尚无完整讲义的领域，并建设独立检索和教师审核闭环。
- 禁止复制版权教材全文、上传真实学生数据或以 LLM 文本替代数学证明/教师签名。
