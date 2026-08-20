# course-paper-grading

面向高校教师的课程论文评分 Skill，用于批量处理课程论文、案例分析、营销策划案、评分表、课程总评和个性化评语。

## 能做什么

- 阅读 Word、PDF 论文并建立学生或小组对应关系
- 按最新版评分表给出各分项小分和论文总分
- 结合出勤、展示成绩计算课程总评
- 按教师长期话术写出包含论文具体内容的评语
- 回填 Excel 或 Word 副本并保留公式和格式
- 根据教师自然语言修改长期评分偏好和评语措辞
- 自动检查加总、公式、漏项、同分人数和评语完整性

## 工作原理

Skill 先通过 `SKILL.md` 判断任务并选择需要读取的参考文件。当前任务中老师的最新说明和最新版表格始终优先；仓库规则只作为长期默认值。

```text
教师本次要求和最新版表格
        ↓
教师长期偏好
        ↓
论文类型评分标准
        ↓
通用规则与黄金样例
        ↓
分项评分 → 总分校验 → 总评计算 → 评语 → 文件副本
```

## 目录

```text
course-paper-grading/
├── SKILL.md
├── README.md
├── PROMPTS.md
├── agents/openai.yaml
├── references/
│   ├── teacher-preferences.md
│   ├── configuration.md
│   ├── scoring-rules.md
│   ├── comment-style.md
│   ├── output-specifications.md
│   └── rubrics/
│       ├── research-paper.md
│       ├── case-analysis.md
│       └── marketing-plan.md
├── examples/
│   ├── gold-standard.md
│   └── complete-workflow/
├── scripts/validate_scores.py
└── tests/validation-cases.md
```

## 安装与调用

在支持 Agent Skills 的 Codex 中，可以直接发送：

```text
$skill-installer 请从 https://github.com/SullivanWYM/master17 安装根目录的 Skill，安装名称使用 course-paper-grading。
```

私有仓库需要当前环境已经登录 GitHub或配置访问凭据。安装后可以显式调用：

```text
$course-paper-grading 请读取本次论文和最新版评分表，先给出各分项小分、总分和理由，不要修改原文件。
```

也可以直接使用自然语言，例如“按最新评分表重新打分并写评语”。更多可复制指令见 [PROMPTS.md](PROMPTS.md)。

仅把仓库链接发给不支持 Skills 的通用 AI，不能保证其自动读取全部文件。此时应明确要求它先读 `SKILL.md`，再按其中路由读取参考文件。

## 修改入口

- 改长期评分习惯：`references/teacher-preferences.md`
- 改默认权重和计算方式：`references/configuration.md`
- 改某类论文评分尺度：`references/rubrics/`
- 改评语措辞：`references/comment-style.md`
- 改 Excel、Word 输出格式：`references/output-specifications.md`
- 增加教师确认范例：`examples/gold-standard.md`

修改长期规则时，建议同时增加或调整一个匿名验证案例，防止后续版本偏离。

## 隐私

公开仓库不得包含真实学生论文、姓名、学号、成绩、教师签名、课程名单、本地绝对路径或未匿名化截图。仓库中的示例均应使用虚构身份和虚构案例。

## 验证

运行匿名示例：

```powershell
python scripts/validate_scores.py examples/complete-workflow/sample-grades.json
```

Skill 结构可使用 Codex 内置 `skill-creator` 的 `quick_validate.py` 检查。

## 许可

MIT License。评分结果仍需任课教师审核确认，本 Skill 不替代教师的最终学术判断。
