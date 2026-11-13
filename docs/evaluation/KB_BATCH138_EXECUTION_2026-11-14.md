# STEM Mentor｜Batch138 实际执行与证据（2026-11-14）

> 审查状态：DRAFT / REVIEW_PENDING / TEACHER_ONLY。MacBook Air 是唯一源码开发、数据生产及测试环境；Tang未使用。GitHub Draft PR #164；没有合并main、强推或伪造教师签字。

## 可复核范围与源码

- 测试起点源码 commit: `9e038e95d1c2e253ddfe1bbf9b90844cc7ccf666`; Git Tree: `4fe5e605c9e79ce1b1392a2c63818b38d4cebe4d`（随后证据独立提交，测试源码文件不变）。
- 继承Batch137已有41份有限候审稿，新增加8份原创选修B/C/D/E教师候审讲义，B/C/D/E各两份；本地编辑端限定稿累计49份。不是全国课标正式原子总数。
- 8份均有来源行指纹、论域和定理/方法前提、四步理由、退化反例、典型误解、教师示例各2、答案分离提示三级、近远迁移；合计16例/24级提示/16项迁移。
- 原文仅在Mac PDFKit本地对照，未上传版权课标原文；原文行指纹通过`scripts/build_kb_batch138_electives.py --check-mac`。课标语义支持仍需真实教师复核。
- 数学`scripts/check_kb_batch138_math.py --check`：独立精确有限32项（24合法/边界，8无效前提），不等于一般定理形式证明；学生自由书写步骤未经验证。
- K08：49份候审稿仅本地编辑FTS5；学生默认`NO_APPROVED_EVIDENCE`；公开API仅匿名聚合；`scope=EDITOR_LOCAL`不是真实鉴权机制，不可公开部署教师预览。

## 实际 Mac 运行日志与退出码

| 测试 | 真实退出码 | 原始日志SHA-256 | bytes | 提取到的完成统计 |
|---|---:|---|---:|---|
| `KB_BATCH138_FOCUS` | 0 | `1b3d32363a02d28ce025ea4bbec7cd6196cf028b5707cd243d307b9deb9baea5` | 791 | 201 passed, 1 warning |
| `KB_BATCH138_BROWSER` | 0 | `cb7d42f2befa66c079b67fdb5908b286033fd3c75efd0451085eaf9be2051b7a` | 2443 | 9 passed, 2 passed |
| `KB_BATCH138_MAC_CHECK` | 0 | `7e3f0c713a8c1bd90674498766dd591b0a6868c0cf073f563c784c6afe0e65e8` | 131087 | 258 passed, 1 warning, 188 passed, 1 warning, 201 passed, 1 warning, 110 passed, 66293 passed, 5 skipped, 1 warning |

- 完整脚本日志中Node TAP摘要: tests=111, pass=111, fail=0；若原始日志无该摘要，不能代替人工验收。
- Chrome/Playwright为模拟浏览器/笔压场景，不是实体iPad或真实学生测试。
- 上述专项与完整脚本存在重叠，**不得简单相加**。退出码来自真实`.exit`文件，不使用预估。

## 当前范围与正式门槛

- 正式七轨课程知识原子分母：COMPULSORY、SELECTIVE_COMPULSORY、ELECTIVE_A/B/C/D/E全部UNKNOWN；全国课程覆盖率不可计算。
- 全部新增资料`REVIEW_PENDING`，真实教师APPROVED 0；定理普遍证明形式认证0；学生自由答案认证0；学生权威公开课程0。
- 历史遗留的证明、先修及数学冲突必须在最新范围重新核验，不能因本批有限验证自动结案。

## 下批建议（不代表本批已完成）

1. K00：全量课标编号要求→正式原子拆分与跨页去重，设定官方七轨可审计分母并由真实教师语义复核。
2. K07：分优先级逐步检查538条历史未认证证明步骤、172条先修提案和10条冲突；记录反例证据与实质裁决，不自动批准。
3. K02–K06：继续补齐概率、立体几何、数列、函数、建模等缺失的全量知识单元与变式，不把49份有限提案当作正式完成。
4. K08/K09：引入真实鉴权与最小授权、冻结离线检索/未见题基准、教师审核流程和学生拒答对照；正式上线前禁止让候审稿获得权威身份。

记录生成时间（Mac）：2026-11-14T01:51:49.967605+08:00.
