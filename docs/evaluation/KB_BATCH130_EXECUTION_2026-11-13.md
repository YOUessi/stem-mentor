# KB Batch130 | Mac-only execution, mathematical audit, delivery evidence

Date: 2026-11-13 (Asia/Singapore); host: YOUTangdeMacBook-Air.local (MacBook Air). No Tang development, no force push, no main merge.
Mathematical-audit source commit: d5cdc1eb2e539aab7dd13cc66d79a43f01b2877b; source code tree: 655b2dabbc1c98fd4f158644706ee3b37001689a.

## Honest curriculum scope

- 53 new manual original-PDF-context dossiers; 157/239 historical semantic candidates context-reviewed; 82 remaining.
- These are editorial source contexts, not official atoms or official curriculum denominators. All seven official denominators remain UNKNOWN.
- Licensed original PDF text remains on Mac. GitHub CI checks published hash fingerprints but cannot attest that it rehashed the unshipped PDF.

## Seven-track historical editorial-candidate audit (NOT official atom coverage)

| Track | Historical project candidates | Source-context reviewed | Still unreviewed | Official atom denominator |
|---|---:|---:|---:|---|
| COMPULSORY | 75 | 63 | 12 | UNKNOWN |
| SELECTIVE_COMPULSORY | 51 | 32 | 19 | UNKNOWN |
| ELECTIVE_A | 30 | 12 | 18 | UNKNOWN |
| ELECTIVE_B | 30 | 12 | 18 | UNKNOWN |
| ELECTIVE_C | 24 | 14 | 10 | UNKNOWN |
| ELECTIVE_D | 17 | 12 | 5 | UNKNOWN |
| ELECTIVE_E | 12 | 12 | 0 | UNKNOWN |

This table is a draft-editorial review ledger, not proof of national coverage, not a frozen official syllabus denominator.

## Original deep curriculum material and math review

- 8 original teacher-review lessons: 集合的元素属于关系与对象判定、充要条件的双向蕴含核验、连续函数异号端点的零点存在性、对数换底公式的底数合法性核验、有限等可能样本空间上的古典概率计数、平均变化率到瞬时变化率的极限过渡、直线倾斜角与斜率的定义域、椭圆作为两焦点距离和为定长的点集.
- 16 exact finite teacher examples and 8 explicit mathematical condition negatives. Finite checks do not prove general theorems.
- Math audit fixed a probability-assumption gap: individually fair dice or coins need not have equiprobable joint outcomes; independence or an explicit joint distribution is required. Added mathematically exact correlated coin/dice negatives and automated regression tests.
- Ellipse proof now derives focal distances from sum and squared difference, then proves both directions of the standard equation with signs checked. Added an exact non-axis test.
- Initial focused test 152 passed / 1 failed from nondeterministic track order; repaired before published draft. No false teacher approvals or student releases.
- Every manuscript remains REVIEW_PENDING / TEACHER_ONLY, general theorems uncertified, unverified student free-text steps not auto-approved.

## Real Mac execution and SHA-256-locked raw logs

| Check | Exit | Output summary | Raw .log SHA-256 |
|---|---:|---|---|
| KB_BATCH130_FOCUS_INITIAL | 1 | 151 passed in 2.13s | 3a2a97609f0c3091363186c0ba365a3fdb0ec1ae21591b66ff67f4a38fbcdedb |
| KB_BATCH130_FOCUS_FINAL | 0 | 153 passed in 2.75s | fcac9a164fa238a762c066a9c9e402e8b9ab358c16453d6518d006178accba02 |
| KB_BATCH130_FOCUS_MATH_AUDIT_FINAL | 0 | 156 passed in 2.28s | 8e287bc564f0088a003b3ee22eb1ece03566ee0624c5014783e714d32608f370 |
| KB_BATCH130_CI_SIMULATION_FINAL | 0 | 100 passed, 53 skipped in 2.31s | d80a29ea07395b176c07fe120f951dcf4c5413f7700a72562b0302d580a0185a |
| KB_BATCH130_CI_SIMULATION_MATH_AUDIT_FINAL | 0 | 103 passed, 53 skipped in 1.88s | 94fcab2f23554d202bd434cb443476147430e2de519c11d61fcab2a9ac438068 |
| KB_BATCH130_MAC_BROWSER_FINAL | 0 | 2 passed in 13.00s | 65490a6ff5ba4c222b87fe379a8f232ef2d5b240a638e8c43a55df0bc8106c8b |
| KB_BATCH130_MAC_BROWSER_MATH_AUDIT_FINAL | 0 | 2 passed in 11.94s | 8e7dff4258dd9386c5e5551ed503d0eb55216902f09cedc10ed65e5c4f689588 |
| KB_BATCH130_MAC_CHECK_FINAL | 0 | 66293 passed, 5 skipped, 1 warning in 1075.52s (0:17:55) | fc17f84aecc3dd0d3183b2242f3842725bcaab55f51b42eaeea05842f49cb665 |
| KB_BATCH130_MAC_CHECK_MATH_AUDIT_FINAL | 0 | 66293 passed, 5 skipped, 1 warning in 1148.14s (0:19:08) | 46a74592c531e81fba7ab2be84b3aafff33cb4a8adb8c68b8aaecf52690ee474 |

## Known failures, outstanding acceptance and next batch

- Software test success is not teacher verification, proof certification, course coverage or learner effectiveness. Original PDF source replay and offline fingerprints are separate controls.
- Still unresolved: 538 uncertified proof steps, 172 unreviewed prerequisite edges, 10 mathematical conflicts, official seven-track denominator UNKNOWN, 0 teacher-approved records, 0 student-authoritative releases.
- Next batch: adjudicate the remaining 82 weak-context candidates against the original on Mac, de-duplicate and separate non-atoms, triage P0 proofs and prerequisite edges, add cross-topic complete original lessons, assess RAG abstention and teacher-solution leakage under realistic prompts.
- Delivery: Draft PR #156 stacked over #155; verify remote SHA and tree on GitHub after evidence submission and record results in Issues #17-#27.
