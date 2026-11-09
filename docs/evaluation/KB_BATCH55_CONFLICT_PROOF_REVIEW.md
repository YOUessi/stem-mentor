# Batch55｜十组数学版本冲突：有限见证与人工复核清单

仅供教师/教研审查。十组冲突全部OPEN；538条历史证明步骤未形式认证。
其中127条只有文本SHA完整性证据，不能推导出数学内容正确。
七轨官方课标分母仍未认证，教师批准、学生发布均为零。

| 项目 | 数量 | 数学认证 |
| --- | ---: | --- |
| 来源版本冲突 | 10 | 0项裁决 |
| 条件敏感的受控实例 | 20 | 不证明一般定理 |
| 历史待核证明步骤 | 538 | 0项形式认证 |
| 高优先级文本指纹核对 | 127 | 只确认文本未漂移 |

## math.hs.function.composition-domain

**人工审查问题**：先证明 g(x) 属于 f 的定义域；在零分母处停止，不允许约分后补点。

候选SHA：0a9eba9335bd48642d1bee6df94f9e391060c06d6d6492b61dbf9100b5a6e8f9；当前稿SHA：8f4ca2c9ffe46431847027164f7eca2ecb203272cb3057f2e6eaedb3e4c3ab26。
两版均未裁决，不选择其中之一作为学生端权威事实源。

**受控案例 1**：{"shift": -2, "x": 3}
状态：FINITE_EXACT_CASE_ONLY；有限输出：{"composition": "1/1", "conflict_decision": "OPEN_REQUIRES_HUMAN_MATHEMATICAL_REVIEW", "inner": "1/1", "reverse_composition": "NOT_CLAIMED", "status": "FINITE_EXACT_CASE_ONLY", "student_solution_verified": false, "teacher_approved": false, "universal_proof_certified": false}

**受控案例 2**：{"shift": -2, "x": 2}
状态：CONDITIONS_NOT_ESTABLISHED；有限输出：{"reason": "f(t)=1/t requires g(x) != 0", "status": "CONDITIONS_NOT_ESTABLISHED"}

## math.hs.function.parity

**人工审查问题**：先核实定义域关于原点对称；零多项式既奇且偶，非零奇偶分类量词是否正确？

候选SHA：dfbfc8ec6b1fb25484c4f6b5c49a56fd893a99559da77416a533d1f380b669c3；当前稿SHA：557000e248fa20439817d7c1f36d08490dfc57156a96ae40a2971bcf659e8575。
两版均未裁决，不选择其中之一作为学生端权威事实源。

**受控案例 1**：{"coefficients": [0, 0, 0, 0], "domain": "ALL_REAL"}
状态：FINITE_EXACT_CASE_ONLY；有限输出：{"classification_scope": "DEGREE_AT_MOST_THREE_POLYNOMIAL_ON_REAL_LINE", "conflict_decision": "OPEN_REQUIRES_HUMAN_MATHEMATICAL_REVIEW", "is_even": true, "is_odd": true, "status": "FINITE_EXACT_CASE_ONLY", "student_solution_verified": false, "teacher_approved": false, "universal_proof_certified": false, "zero_polynomial": true}

**受控案例 2**：{"coefficients": [1, 1], "domain": "POSITIVE_REAL"}
状态：CONDITIONS_NOT_ESTABLISHED；有限输出：{"reason": "Polynomial parity classification here requires full real domain", "status": "CONDITIONS_NOT_ESTABLISHED"}

## math.hs.function.piecewise

**人工审查问题**：分界点可重叠但赋值必须一致；既不属于任何分支时不在定义域。

候选SHA：b7cd6eeb5feaeca859c90061d20359b23d3c76edf2b89ab1df599a1a2f1f1116；当前稿SHA：d2398e513adc2e80ef2de3fdf604960c48f90907d50e1cc44354008b1a5fe30c。
两版均未裁决，不选择其中之一作为学生端权威事实源。

**受控案例 1**：{"left_inclusive": true, "left_value": 1, "right_inclusive": true, "right_value": 2}
状态：FINITE_EXACT_CASE_ONLY；有限输出：{"ambiguous_if_different": true, "boundary_defined": true, "boundary_value": null, "conflict_decision": "OPEN_REQUIRES_HUMAN_MATHEMATICAL_REVIEW", "gap": false, "overlap": true, "status": "FINITE_EXACT_CASE_ONLY", "student_solution_verified": false, "teacher_approved": false, "universal_proof_certified": false}

**受控案例 2**：{"left_inclusive": false, "left_value": 1, "right_inclusive": false, "right_value": 2}
状态：FINITE_EXACT_CASE_ONLY；有限输出：{"ambiguous_if_different": false, "boundary_defined": false, "boundary_value": null, "conflict_decision": "OPEN_REQUIRES_HUMAN_MATHEMATICAL_REVIEW", "gap": true, "overlap": false, "status": "FINITE_EXACT_CASE_ONLY", "student_solution_verified": false, "teacher_approved": false, "universal_proof_certified": false}

## math.hs.function.zero-ivt

**人工审查问题**：连续且端点异号保证至少一根；两端同号仍可能有根，唯一性不由异号保证。

候选SHA：5b2775f2eac0269a11e2bfe96e6b3e729d31978a2800d79f9299f473082e472e；当前稿SHA：a711b76c4db2777645835732e23494aa378ed3a123ea1b8cc86d96dd7a3e247c。
两版均未裁决，不选择其中之一作为学生端权威事实源。

**受控案例 1**：{"coefficients": [-1, 0, 1], "left": -2, "right": 0}
状态：FINITE_EXACT_CASE_ONLY；有限输出：{"conflict_decision": "OPEN_REQUIRES_HUMAN_MATHEMATICAL_REVIEW", "continuity": "POLYNOMIAL_ON_REAL_LINE", "existence_guaranteed_by_bracket": true, "left_value": "3/1", "right_value": "-1/1", "same_sign_does_not_imply_no_roots": true, "status": "FINITE_EXACT_CASE_ONLY", "student_solution_verified": false, "teacher_approved": false, "uniqueness": "UNDETERMINED", "universal_proof_certified": false}

**受控案例 2**：{"coefficients": [-1, 0, 1], "left": -2, "right": 2}
状态：FINITE_EXACT_CASE_ONLY；有限输出：{"conflict_decision": "OPEN_REQUIRES_HUMAN_MATHEMATICAL_REVIEW", "continuity": "POLYNOMIAL_ON_REAL_LINE", "existence_guaranteed_by_bracket": false, "left_value": "3/1", "right_value": "3/1", "same_sign_does_not_imply_no_roots": true, "status": "FINITE_EXACT_CASE_ONLY", "student_solution_verified": false, "teacher_approved": false, "uniqueness": "UNDETERMINED", "universal_proof_certified": false}

## math.hs.geometry.point-line-distance

**人工审查问题**：直线法向量非零是必要前提；距离是否需要无理数表达？

候选SHA：fe6966d4605d4097363eb1a7ad94d3c8a156d11177fecbaf4a1e411818be8b47；当前稿SHA：dac0d1540d6b01096ffa722c34f4c548181d6f02d8de3d3c2117981beda5838e。
两版均未裁决，不选择其中之一作为学生端权威事实源。

**受控案例 1**：{"A": 3, "B": 4, "C": 0, "x": 1, "y": 2}
状态：FINITE_EXACT_CASE_ONLY；有限输出：{"conflict_decision": "OPEN_REQUIRES_HUMAN_MATHEMATICAL_REVIEW", "exact_distance": "11/5", "irrational_distance": null, "squared_distance": "121/25", "status": "FINITE_EXACT_CASE_ONLY", "student_solution_verified": false, "teacher_approved": false, "universal_proof_certified": false}

**受控案例 2**：{"A": 0, "B": 0, "C": 1, "x": 1, "y": 2}
状态：CONDITIONS_NOT_ESTABLISHED；有限输出：{"reason": "A=B=0 cannot define a line", "status": "CONDITIONS_NOT_ESTABLISHED"}

## math.hs.probability.binomial-distribution

**人工审查问题**：独立同分布试验是否真正给定？退化成功概率p=0或1如何处理？

候选SHA：2f19452fc3bfb0c0f595365e7c2b1580c9e7b0b242a6f07df9d866a5e494d0d0；当前稿SHA：699a78f5f5518ded8f9277535f670acb28a4cfd15bbddc20930a0d014276e3ae。
两版均未裁决，不选择其中之一作为学生端权威事实源。

**受控案例 1**：{"independent_identical": true, "k": 2, "n": 2, "p": "1/2"}
状态：FINITE_EXACT_CASE_ONLY；有限输出：{"conflict_decision": "OPEN_REQUIRES_HUMAN_MATHEMATICAL_REVIEW", "model": "BINOMIAL_ONLY_UNDER_EXPLICIT_IID_ASSUMPTION", "probability": "1/4", "status": "FINITE_EXACT_CASE_ONLY", "student_solution_verified": false, "teacher_approved": false, "universal_proof_certified": false}

**受控案例 2**：{"independent_identical": false, "k": 2, "n": 2, "p": "1/2"}
状态：CONDITIONS_NOT_ESTABLISHED；有限输出：{"reason": "i.i.d. Bernoulli with p in [0,1] required", "status": "CONDITIONS_NOT_ESTABLISHED"}

## math.hs.probability.hypergeometric

**人工审查问题**：无放回均匀抽样及合法整数支撑集是否满足？有放回不得复用。

候选SHA：32e19775af8d600e9ed132c6154a1fbc871fd014fa229fbff8a3ab43415347f6；当前稿SHA：8b241b93c47cef3f88d5e601c6e5481b1168c57cd5cebadb915f8f1d4b81a69a。
两版均未裁决，不选择其中之一作为学生端权威事实源。

**受控案例 1**：{"K": 2, "N": 5, "equal_likelihood_without_replacement": true, "k": 1, "n": 2}
状态：FINITE_EXACT_CASE_ONLY；有限输出：{"conflict_decision": "OPEN_REQUIRES_HUMAN_MATHEMATICAL_REVIEW", "probability": "3/5", "status": "FINITE_EXACT_CASE_ONLY", "student_solution_verified": false, "support": [0, 2], "teacher_approved": false, "universal_proof_certified": false}

**受控案例 2**：{"K": 2, "N": 5, "equal_likelihood_without_replacement": false, "k": 1, "n": 2}
状态：CONDITIONS_NOT_ESTABLISHED；有限输出：{"reason": "Uniform subset sampling without replacement required", "status": "CONDITIONS_NOT_ESTABLISHED"}

## math.hs.statistics.correlation-regression

**人工审查问题**：常量自变量令回归斜率未定义；零相关不能排除非线性或证明独立。

候选SHA：acc74aacbf1fa0c20eff89a29f73bd94d745214cc614545b9c75df78e42ce1da；当前稿SHA：9b1444a77b709f2e8fc4cb7cbe23cba08d1580ab920a31d3bb6d6b52d9e22e09。
两版均未裁决，不选择其中之一作为学生端权威事实源。

**受控案例 1**：{"xs": [-1, 0, 1], "ys": [1, 0, 1]}
状态：FINITE_EXACT_CASE_ONLY；有限输出：{"causality": "NOT_ESTABLISHED", "conflict_decision": "OPEN_REQUIRES_HUMAN_MATHEMATICAL_REVIEW", "correlation_defined": true, "correlation_squared": "0/1", "nonlinear_relationship_excluded": false, "slope": "0/1", "status": "FINITE_EXACT_CASE_ONLY", "student_solution_verified": false, "teacher_approved": false, "universal_proof_certified": false}

**受控案例 2**：{"xs": [1, 1, 1], "ys": [1, 2, 3]}
状态：CONDITIONS_NOT_ESTABLISHED；有限输出：{"reason": "Constant x makes OLS slope undefined", "status": "CONDITIONS_NOT_ESTABLISHED"}

## math.hs.triangle.area-sine

**人工审查问题**：输入角须是两边夹角且三角形不退化。

候选SHA：65f0f943e5c9568894a150f757a9065920564f6e019e60f84112394c77633007；当前稿SHA：feca569a56b1d149b0e6bb391b9dfd6af6e6d96b32cb64bac55da5b2256fc360。
两版均未裁决，不选择其中之一作为学生端权威事实源。

**受控案例 1**：{"a": 3, "b": 4, "cos_included_angle": 0, "is_included_angle": true}
状态：FINITE_EXACT_CASE_ONLY；有限输出：{"area_squared": "36/1", "conflict_decision": "OPEN_REQUIRES_HUMAN_MATHEMATICAL_REVIEW", "expression": "1/2*a*b*sin(included angle), square verified exactly", "nondegenerate": true, "status": "FINITE_EXACT_CASE_ONLY", "student_solution_verified": false, "teacher_approved": false, "universal_proof_certified": false}

**受控案例 2**：{"a": 3, "b": 4, "cos_included_angle": 1, "is_included_angle": true}
状态：CONDITIONS_NOT_ESTABLISHED；有限输出：{"reason": "Nondegenerate triangle, positive sides, included angle required", "status": "CONDITIONS_NOT_ESTABLISHED"}

## math.hs.vector.linear-operations

**人工审查问题**：向量同维同坐标；坐标相加正确不等于模长可相加。

候选SHA：a8977ba555d84ed6fd84d7ce38b0e8834d8386b13cc42a93d17b940d4d397fc1；当前稿SHA：ce4d8f75e4ccb20a695f299c041b2ec84157a885466fbc70b5dbe90e253923e6。
两版均未裁决，不选择其中之一作为学生端权威事实源。

**受控案例 1**：{"u": [1, 0], "v": [0, 1]}
状态：FINITE_EXACT_CASE_ONLY；有限输出：{"conflict_decision": "OPEN_REQUIRES_HUMAN_MATHEMATICAL_REVIEW", "norm_additivity": "NOT_ASSUMED", "norm_sum_squared": "2/1", "norm_u_squared": "1/1", "norm_v_squared": "1/1", "status": "FINITE_EXACT_CASE_ONLY", "student_solution_verified": false, "sum_components": ["1/1", "1/1"], "teacher_approved": false, "universal_proof_certified": false}

**受控案例 2**：{"u": [1, 0], "v": [0, 1, 1]}
状态：CONDITIONS_NOT_ESTABLISHED；有限输出：{"reason": "Same vector dimension required", "status": "CONDITIONS_NOT_ESTABLISHED"}

## 后续审核门槛

逐项复核两版完整原文、全部数学假设、量词、证明链及反例；保存真实教师身份、时间与版本记录。
发现失败案例只要求修改，不自动裁决。有限实例不得升级为形式证明、课标通过或学生可发布。
