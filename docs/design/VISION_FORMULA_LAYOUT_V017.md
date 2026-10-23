# STEM Mentor v0.17 — Mac 原生公式区域定位与识别风险校对

## 本版性质和设备职责

全部代码开发、Swift 编译、Python 后端与 Web UI 开发、评测图像生成、测试及 Git 管理均在 MacBook Air 的独立工作区完成（~/Documents/文件/stem-mentor-vision-v017）。Tang 只作为可选的独立 GPU 公式模型推理服务器，不存储工程版本，也不在 Tang 上修改 STEM Mentor 的源码。原来的 v0.14 iPad 手写功能和 v0.15/16 分支不被覆盖。本阶段没有接入云端 VLM，没有真实学生数据或未获许可的中高考试卷图片。

Apple Vision 仍运行在 Mac 的原生 Swift OCR helper 中；iPad Web 页面拍照后将图片发送到 Mac FastAPI，因此目前不是纯 iPad 本地设备 OCR。

## 主要实现

1. 原生 Mac Apple Vision：不仅定位一整行，还把 OCR 候选字串中较明确的数学片段交给 VNRecognizedText.boundingBox(for:) 查找来源图像的真实区域。对中文叙述、英文冒号标签、独立公式和一行多条公式分别生成多个可追溯 normalized bbox。
2. 极保守字符分组：汉字/句读符号分隔通常的算式区段，英文常见动作词（Given/Solve/Find 等）做有限前缀过滤。区间括号中的英文逗号不当作句读分隔。同一行最多 8 个区域、全图最多 12 个候选，限制推理成本。
3. 字母与乘号混淆：普通 OCR 有时把单个 x 识别为 ×；当出现 ×=1 这类符号组合时仍保留候选供专用数学 OCR 和用户确认，而不是自行推断变量。
4. FastAPI：每个原生字串区域单独按需裁剪和路由，结果保留 bbox、raw_text、bbox_source、模型状态及 quality。原题干原样保留。无同意时绝不请求远端服务；模型第一次失败后同一请求后续候选停止调用。
5. 识别风险检查：formula_quality.py 只对机器可辨别的问题做检测：花括号未配对、^ 与 prime/wedge 混淆、小写 x 和大写 X 冲突、凭空出现因为/所以符号、题干英文混入公式、array/aligned 包装。检测为零仅表示这些有限规则未报警，绝不声明数学等价或正确。
6. 绿色 Review 页面显示每个公式的来源裁剪图、原 OCR 文本、专用模型输出、风险提示与 LaTeX 实时预览。用户必须显式确认题干后才能创建合成演示练习。原有视觉模型、手写笔迹、学生正确性标识均不受影响。

API 版本兼容：仍保留 v0.16 稳定字段 pipeline=HYBRID_VISION_V016，新增 routing.layout_detector=native_substring_multiregion_v017 和 expression.quality；不因这次功能升级修改既有学生学习数据结构。数学验证与识别置信度不混为一谈。

## 冻结合成评测：开发集和独立测试集分开

评测对象仅是图像中公式 **区域定位**，不是公式内容解析，更不是数学推理。使用 Mac 真实 Apple Vision helper 处理自己绘制的单行合成图：给定组成片段的文字和其预定义公式区域，由 PIL+系统字体画出图片和真实 bbox，评测时只看图片，不把片段真值传给 OCR。预测框与真值框通过一对一分配匹配；IoU 至少 0.4 且宽度不超过真值的 1.5 倍。精确率 TP/(TP+FP)，召回率 TP/(TP+FN)；无预测时的精确率记为 null。所有图片、详细输出仅保留在 Mac gitignored 的 artifacts/vision；JSON manifest、生成器与本报告可以安全提交 Git。

### 开发用 12 张合成图（11 个公式区域）

Manifest：evaluations/vision_v017/frozen_layout_manifest.json
SHA256：5027f260ad42326c853f009d7739ddfcb73d423a4509b1c1eff39aaebdc0203c

- v0.16 原始冒号式区域定位：TP=1、FP=0、FN=10，召回率 9.09%。
- v0.17 在测试时修复 ×=1 兼容：TP=11、FP=0、FN=0，精确率 100%，召回率 100%。

注意：此开发集合参与了规则迭代，不可以把这个 100% 报作独立泛化表现。最初改进版本先得到 10/11，再因已观察到 x 被普通文字 OCR 识别为 ×，才做了上述补充。

### 另行冻结的独立合成测试 20 张图（20 个公式区域）

Manifest：evaluations/vision_v017/frozen_holdout_manifest.json
SHA256：61755c84f206d5e47cfc0c6eb5cd5b556d228c95b79268186a4383c48cf64a2a

独立测试前冻结，包含中英文自然语言混排、两段等式、Songti/STHeiti/Arial 字体、低对比和轻微高斯模糊、无公式文本等。没有拿该组测试样本去修改已冻结的 v0.17 定位规则。

| 模型 | TP | FP | FN | Precision | Recall |
|---|---:|---:|---:|---:|---:|
| v0.16 | 2 | 0 | 18 | 100% | 10% |
| v0.17 | 18 | 1 | 2 | 94.74% | 90.00% |

错误分析（不据此事后修改已测新版本）：
- H005：视觉上 AB⊥CD，Apple Vision 把特殊数学符号 ⊥ 误成字母 L，输出 ABLCD，因此未触发数学候选；不能自行把 L 还原成垂直。需要新研究的图形/符号检测方案。
- H009：英文文本 Find all solutions of x^2-5x+6=0。v0.17 虽发现了数学候选，但 bbox 将说明文字 all solutions of 与公式连在一起，宽度偏大；按已冻结的匹配阈值计为 1 FP + 1 FN。应在下一版另用开发数据优化英文数学短语分离，不能篡改此轮 holdout 分数。
- 其余 18 个区域在当前阈值下被定位，仍不代表专用公式 OCR 的 LaTeX 识别无错。

由于独立集只含 20 个公式区域，误差区间很大，更无法覆盖复杂版面、真实试卷扫描、手写、彩色透视照片、阴影、图表、课堂板书或 Apple Pencil 笔迹。不能把它作为产品准确率、教师质量或学生成效证明。

## 实际复现（仅 Mac）

在独立 worktree：
    cd ~/Documents/文件/stem-mentor-vision-v017
    bash scripts/build_vision_ocr.sh
    .venv/bin/python evaluations/vision_v017/layout_benchmark.py
    .venv/bin/python evaluations/vision_v017/layout_benchmark.py --manifest evaluations/vision_v017/frozen_holdout_manifest.json --output artifacts/vision/v017_holdout_eval.json --image-dir artifacts/vision/v017_holdout_cases
    cd backend && PYTHONPATH=. ../.venv/bin/python -m pytest -q

Mac 浏览器用独立 synthetic demo 服务（无需真实学生数据）：
    cd ~/Documents/文件/stem-mentor-vision-v017/backend
    PYTHONPATH=. ../.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 18917

访问 http://127.0.0.1:18917/vision。Browser 测试可运行 tests/browser/test_vision_risk_v017.py，使用确定性的 mock OCR 输出验证警告渲染、编辑和确认流程。源图片仍未自动上传 Tang；如果已配置网络服务，用户勾选同意后才发送候选的局部图片。VLM 仍是按需且必须独立许可。

## 后续能力边界

- 准确识别数学字符、排版与数学等价分别属于不同任务；OCR 风险标记不是数学验证。不能把文字 OCR 的 x/× 当成同一个字符硬编码纠错。
- 下一轮重点研究视觉原生符号识别（⊥、∥ 等）、英文自然语言中公式边界、二维分式和矩阵的真正区域候选、现实照片扰动与真实人工标注的授权数据集。
- 长期要在 iPad 真正设备端运行 Apple Vision 需原生 Swift/iOS 包装；当前浏览器→Mac Web 服务是 Mac 端 OCR，而不是 iPad 原生 OCR。
