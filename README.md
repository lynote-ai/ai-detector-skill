# AI Detector Skill

![AI Detector Skill hero](assets/hero.svg)

![Python](https://img.shields.io/badge/python-3.9%2B-3776ab)
![License](https://img.shields.io/badge/license-MIT-16a34a)
[![CI](https://github.com/lynote-ai/ai-detector-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/lynote-ai/ai-detector-skill/actions/workflows/ci.yml)
![No Network](https://img.shields.io/badge/network-none-f59e0b)

An explainable, cautious **AI-generated text risk analyzer** for Codex, Claude Code, Cursor, Aider, Continue, and other repo-aware agents.

一个可解释、偏保守的 **AI 文本风险分析器**，适合 Codex、Claude Code、Cursor、Aider、Continue 等代码代理或仓库内智能助手使用。

The project is deliberately modest: it estimates **AI-like signals**, not proof of authorship.

这个项目刻意保持克制：它输出的是 **AI 风格信号风险**，不是作者身份的证据。

## Highlights / 项目亮点

- Explainable weighted signals instead of a black-box accusation machine.
- Local CLI and Python API with zero runtime network calls for detection itself.
- Short-text guardrail: samples under about 80 words return `insufficient_text`.
- Skill-ready structure with `SKILL.md`, `scripts/`, `references/`, and `assets/`.
- Reproducible dataset evaluation and synthetic benchmark reports.

- 使用可解释的加权信号，而不是黑盒式“定罪器”。
- 检测本体支持本地 CLI 和 Python API，运行时不依赖网络。
- 对短文本有保护机制：低于约 80 词会返回 `insufficient_text`。
- 采用适合开源 Skill 的结构：`SKILL.md`、`scripts/`、`references/`、`assets/`。
- 提供可复现的数据集测试和合成基准报告。

## Project Structure / 项目结构

```text
ai-detector-skill/
├── SKILL.md
├── scripts/
│   ├── detect.py
│   ├── setup.sh
│   ├── benchmark.py
│   └── evaluate_hc3.py
├── references/
│   └── api-reference.md
├── assets/
│   ├── hero.svg
│   ├── score-bands.svg
│   ├── workflow.svg
│   └── templates/
│       └── report.md
├── src/aidetect/
├── tests/
├── AGENTS.md
└── README.md
```

- `SKILL.md`: portable skill contract for Codex-style workflows.
- `scripts/detect.py`: repository-local wrapper around the CLI.
- `scripts/setup.sh`: bootstrap script for local installation.
- `scripts/evaluate_hc3.py`: reproducible dataset evaluation.
- `references/api-reference.md`: public output contract.

- `SKILL.md`：可移植的 Skill 说明书。
- `scripts/detect.py`：仓库内的检测入口包装脚本。
- `scripts/setup.sh`：本地环境初始化脚本。
- `scripts/evaluate_hc3.py`：可复现的数据集评测脚本。
- `references/api-reference.md`：公开输出契约说明。

## Install / 安装

### Python Package / 作为 Python 包安装

```bash
pip install -e .
```

### Bootstrap Script / 使用初始化脚本

```bash
bash scripts/setup.sh
```

### Install as a Local Skill / 作为本地 Skill 安装

Clone this repository and copy it into your local skills directory, or keep it as a normal repo that your agent can inspect.

克隆仓库后，可以把整个目录复制到本地 skills 目录中，或者直接把它当作普通仓库让代理读取。

```bash
cp -R ai-detector-skill "$CODEX_HOME/skills/"
```

## CLI Usage / 命令行使用

```bash
ai-detect examples/sample_ai_like.txt
cat essay.txt | ai-detect --json
python scripts/detect.py examples/sample_human_like.txt --json
```

Example output:

```text
Conclusion: AI-like signals are present, but this medium-confidence score is a risk estimate rather than proof.
Score: 84/100
Confidence: medium
Verdict: high_ai_likelihood
Words analyzed: 256
```

示例输出会包含结论、分数、置信度、判定、证据信号、注意事项和必要时的后续建议。

## Python API / Python 调用

```python
from aidetect import analyze_text

result = analyze_text(open("essay.txt", encoding="utf-8").read())
print(result.score, result.confidence, result.verdict)
for signal in result.strongest_signals():
    print(signal.name, signal.note)
```

## Dataset Evaluation / 数据集测试

We ran one reproducible evaluation round on the public [HC3 dataset](https://huggingface.co/datasets/Hello-SimpleAI/HC3), using the English `finance`, `medicine`, and `open_qa` subsets, with the first 100 rows from each subset.

我们基于公开的 [HC3 数据集](https://huggingface.co/datasets/Hello-SimpleAI/HC3) 做了一轮可复现测试，使用英文 `finance`、`medicine`、`open_qa` 三个子集，每个子集取前 100 条问答对。

Summary of the current detector on that slice:

当前版本在这组样本上的摘要表现：

- Human mean score: `5.4`
- AI mean score: `18.4`
- Mean separation: `13.0` points
- Human coverage: `0.427`
- AI coverage: `0.920`
- Covered accuracy at `score >= 45`: `0.317`
- Covered accuracy at `score >= 70`: `0.317`

Interpretation:

解读：

- The detector does separate human and AI answers on average, but only weakly on this HC3 slice.
- The short-text guardrail is active and prevents many short human answers from being over-classified.
- With current score bands, the detector is conservative and has low recall on HC3.
- This supports using the project for **triage and explanation**, not as a stand-alone classifier.

- 这个检测器在均值上能区分人类与 AI 文本，但在这组 HC3 样本上的分离度仍然偏弱。
- 短文本保护机制确实在工作，避免了很多人类短答案被硬判。
- 以当前分数带来看，检测器明显偏保守，因此在 HC3 上召回较低。
- 这说明它更适合作为 **初筛和解释工具**，而不是独立裁决器。

Full report:

完整报告：

- [`docs/HC3_EVALUATION.md`](docs/HC3_EVALUATION.md)

Reproduce:

复现命令：

```bash
make eval-hc3
```

## Typical User Cases / 典型使用案例

### 1. Teacher Triage / 教师初筛

Use case:

场景：

A teacher receives a 400-word reflection that feels unusually polished and wants a cautious signal before doing manual review.

老师收到一篇 400 词左右、语言异常工整的课程反思，希望在人工复核前先做一轮谨慎初筛。

Suggested workflow:

建议流程：

1. Run `ai-detect submission.txt --json`.
2. Review the strongest signals and caveats.
3. Compare the passage with the student's known writing before making any judgment.

1. 运行 `ai-detect submission.txt --json`。
2. 查看最强信号和注意事项。
3. 和学生已知写作样本对比，再决定是否需要进一步沟通。

### 2. Editorial Review / 编辑审核

Use case:

场景：

An editor wants to spot obviously formulaic product reviews or guest posts before spending time on manual edits.

编辑希望先筛掉明显模板化的产品评论或投稿文章，再决定是否投入人工修改时间。

Why it fits:

适配原因：

- Medium-length prose works better than short snippets.
- Explainable signals help editors justify why a draft feels templated.

- 中等篇幅的散文式文本更适合当前检测器。
- 可解释信号能帮助编辑理解“为什么这段文字显得模板化”。

### 3. Trust and Safety Queueing / 内容安全队列分流

Use case:

场景：

A moderation team wants to sort suspicious long-form posts into a manual review queue, not auto-remove them.

内容审核团队希望把可疑长文本分流到人工复核队列，而不是直接自动删除。

Why it fits:

适配原因：

- The tool is conservative.
- It is better for prioritization than enforcement.

- 这个工具本身就偏保守。
- 更适合优先级排序，不适合直接执法或处罚。

### 4. Internal Prompt or Content QA / 内部提示词或内容质检

Use case:

场景：

A team compares human-written drafts and AI-assisted drafts to understand where generated language starts sounding too generic.

团队对比人工草稿和 AI 辅助草稿，想知道哪些段落开始显得过于泛化、过于工整。

Why it fits:

适配原因：

- The score is useful as a relative signal across versions.
- Strongest signals can guide rewriting.

- 分数适合做版本间的相对比较。
- 最强信号可以反过来指导改写。

### Cases to Avoid / 不建议使用的场景

- Making disciplinary decisions about a named student or employee.
- Treating a single score as proof of cheating or fraud.
- Very short text such as a one-paragraph message under about 80 words.
- High-stakes authorship disputes without known-sample comparison.

- 直接对具名学生或员工做纪律处分。
- 把单次分数当作作弊或造假的证据。
- 对低于约 80 词的短文本强行下结论。
- 在没有已知写作样本对比的情况下处理高风险作者归属争议。

## Use as an Agent Skill / 作为 Agent Skill 使用

### Claude Code

Copy `.claude/skills/ai-detector/` into your Claude Code skills location, or keep it in this repo and ask Claude Code to use the `ai-detector` skill.

把 `.claude/skills/ai-detector/` 复制到 Claude Code 的 skills 目录，或者直接让 Claude Code 读取当前仓库中的 `ai-detector` skill。

### Codex and Other Repo-Aware Agents

Use the root [`SKILL.md`](SKILL.md) as the main portable skill definition, and keep [`AGENTS.md`](AGENTS.md) at the repository root for repo-aware agents.

对 Codex 或其他可读取仓库说明的代理，优先使用根目录 [`SKILL.md`](SKILL.md)，并保留仓库根部的 [`AGENTS.md`](AGENTS.md)。

### Generic Prompt Block

Use [`docs/AGENT_PROMPT.md`](docs/AGENT_PROMPT.md) as a portable instruction block.

如果你要给别的代理复用提示块，可以直接使用 [`docs/AGENT_PROMPT.md`](docs/AGENT_PROMPT.md)。

## Output Contract / 输出契约

The analyzer returns:

分析器返回以下字段：

- `score`: 0-100 AI-like writing risk estimate
- `verdict`: `insufficient_text`, `low_ai_likelihood`, `mixed_or_uncertain`, or `high_ai_likelihood`
- `confidence`: `low` or `medium`
- `word_count`: analyzed token count
- `conclusion`: one-sentence uncertain summary
- `signals`: weighted evidence, not accusations
- `caveats`: safety notes for responsible use
- `next_steps`: useful follow-up actions

![Score bands](assets/score-bands.svg)

## Responsible Workflow / 负责的使用流程

![Responsible detection workflow](assets/workflow.svg)

1. Run the analyzer on a sufficiently long sample.
2. Read the strongest evidence signals in context.
3. Keep caveats attached to the score.
4. For high-stakes contexts, require human review and comparison with known writing samples.

1. 对足够长的文本样本运行分析器。
2. 结合上下文阅读最强证据信号。
3. 不要把 caveats 和分数拆开看。
4. 高风险场景必须加入人工复核和已知样本比对。

Preferred wording:

推荐表达：

- "AI-like signals are present."
- "The result is uncertain because the sample is short."
- "This should be reviewed against known writing samples."

- “存在 AI 风格信号。”
- “由于样本较短，结果存在较大不确定性。”
- “建议与已知写作样本对比后再做人工判断。”

Avoid:

避免：

- "This was written by AI."
- "The detector proves misconduct."
- Accusations against a named person.

- “这就是 AI 写的。”
- “检测器证明了存在违规。”
- 对具名个人作出指控。

## Development / 开发

```bash
make test
make demo
make benchmark
make eval-hc3
```

## CI / 持续集成

GitHub Actions now runs:

GitHub Actions 现在会自动运行：

- `make test` on Python `3.9`, `3.11`, and `3.13`
- `make benchmark` to regenerate the synthetic benchmark report
- `make eval-hc3` to regenerate the HC3 evaluation report
- uploads `docs/BENCHMARK.md` and `docs/HC3_EVALUATION.md` as workflow artifacts

- 在 Python `3.9`、`3.11`、`3.13` 上执行 `make test`
- 执行 `make benchmark` 重新生成合成基准报告
- 执行 `make eval-hc3` 重新生成 HC3 数据集评测报告
- 将 `docs/BENCHMARK.md` 和 `docs/HC3_EVALUATION.md` 作为 workflow artifact 上传

## Contributing / 贡献

- See [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution guidelines.
- Keep `SKILL.md`, CLI behavior, and output contract in sync.
- Prefer lightweight, explainable improvements over hidden complexity.

- 贡献前请先阅读 [`CONTRIBUTING.md`](CONTRIBUTING.md)。
- 修改公开行为时，请同步更新 `SKILL.md`、CLI 行为和输出契约。
- 优先做轻量、可解释的改进，而不是引入隐藏复杂度。

## License / 许可证

MIT
