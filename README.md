# course-paper-grading

一个用于课程论文批量评分、总分汇总和评语撰写的 Codex skill。

这个仓库是公开发布版，核心目标是把你常用的评分流程整理成可复用、可修改、可迁移的结构。实际评分时，Codex 会优先读取 `SKILL.md`，再按需读取 `references/` 里的评分标准、话术模板和配置说明。

## 适用场景

- 课程论文、案例分析、小组论文的批量评分
- 按小分项汇总论文得分
- 结合出勤、展示等成绩计算课程总评
- 根据论文内容撰写带有具体亮点的评语
- 后续修改评分规则、总分比例和评语话术

## 目录说明

- `SKILL.md`：核心工作流
- `agents/openai.yaml`：Codex 界面显示信息
- `references/scoring-rules.md`：评分项和总分规则
- `references/comment-style.md`：评语结构和固定话术
- `references/configuration.md`：可调整入口，方便后续改分值和措辞
- `examples/`：匿名示例
- `tests/`：验证样例

## 使用方式

把整个文件夹放到你的技能目录下，例如：

`$CODEX_HOME/skills/course-paper-grading`

然后在 Codex 里直接说：

- 给这些论文打分并写评语
- 按这个新的评分表重新算总分
- 把评语里的某个固定说法改掉
- 以后都按这个模板来

## 修改入口

如果你想长期沿用这个 skill，建议优先改这三个文件：

1. `references/configuration.md`
2. `references/scoring-rules.md`
3. `references/comment-style.md`

这样可以把“评分规则”和“评语话术”分开维护，避免每次都改 `SKILL.md`。

## 发布前建议

- 不要把真实学生论文、学号、成绩表直接公开
- 示例尽量匿名化
- 如果要公开到 GitHub，先检查是否包含私人路径或本地文件名
- 如果你准备长期维护，可以把课程名、分值和总分比例都放进 `references/configuration.md`

