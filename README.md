# SeismicX Skills

面向地震学工作的统一 Agent Skill 调度器。它根据任务目标选择并协调四个
SeismicX 子技能，在数据、模型、目录和论文之间建立可追溯的交接流程。

The repository follows the open
[Agent Skills specification](https://agentskills.io/specification) and is
designed for Codex, OpenCode, Claude Code, and other agents that can read a
`SKILL.md` file and its relative resources.

## 能力与上游技能

| 任务 | 调用的技能 | 上游仓库 |
|---|---|---|
| 科学论文修改、摘要、讨论、审稿回复和主张校准 | `seismicx-paper-skill` | [seismicx-paper-skill](https://github.com/cangyeone/seismicx-paper-skill) |
| 连续波形检测、拾取、关联、定位、震级、机制和地震目录 | `seismicx-catalog` | [seismicx-catalog-skill](https://github.com/cangyeone/seismicx-catalog-skill) |
| 波形转换、miniSEED 索引、标签归一化、标准 HDF5 和 dataloader | `seismicx-dataset` | [seismicx-dataset-skill](https://github.com/cangyeone/seismicx-dataset-skill) |
| SeismicXM/PNSN 数据适配、微调、验证和模型比较 | `seismicx-fine-tuning` | [seismicx-fine-tuning-skill](https://github.com/cangyeone/seismicx-fine-tuning-skill) |

统一技能不会把四个仓库复制到自身。它优先调用 Agent 已发现的子技能，
也可以通过 `scripts/resolve_skills.py` 定位或显式安装缺失的子技能。

## 调度方式

单一任务只加载必要的技能：

- “从连续 miniSEED 生成地震目录和分布图” → `catalog`
- “把 SAC 和旧目录做成标准 HDF5” → `dataset`
- “用区域数据微调 PNSN” → `fine-tuning`
- “修改论文讨论并校准科学主张” → `paper`

跨阶段任务使用明确的中间制品和质量门槛：

```text
raw waveforms/catalog
        │
        ▼
seismicx-dataset
        │ standardized HDF5 + canonical labels
        ▼
seismicx-fine-tuning
        │ checkpoint + preprocessing + evaluation
        ▼
seismicx-catalog
        │ picks + located events + catalog QC
        ▼
seismicx-paper-skill
        │ evidence-traceable manuscript
        ▼
final scientific deliverable
```

如果用户已经提供通过验证的中间制品，调度器会跳过相应上游阶段。

## Agent 兼容性

`SKILL.md` 是唯一的规范工作流。其他入口只负责让不同 Agent 找到并读取它。

| Agent | 用户级目录 | 项目级目录 | 显式调用 |
|---|---|---|---|
| Codex | `~/.agents/skills/seismicx-skills/` | `.agents/skills/seismicx-skills/` | `$seismicx-skills` |
| OpenCode | `~/.config/opencode/skills/seismicx-skills/` 或 `~/.agents/skills/seismicx-skills/` | `.opencode/skills/seismicx-skills/` 或 `.agents/skills/seismicx-skills/` | 使用 `seismicx-skills`，OpenCode V2 也可使用 `/seismicx-skills` |
| Claude Code | `~/.claude/skills/seismicx-skills/` | `.claude/skills/seismicx-skills/` | `/seismicx-skills` |
| 其他 Agent Skills 客户端 | 客户端配置的 skills 目录 | 通常为 `.agents/skills/` | 使用技能名 `seismicx-skills` |

兼容入口：

- `SKILL.md`：开放 Agent Skills 入口和完整调度规范。
- `AGENTS.md`：OpenCode、Codex 和支持 AGENTS 约定的仓库级 Agent 指令。
- `CLAUDE.md`：Claude Code 仓库入口和兼容说明。
- `agents/openai.yaml`：Codex/ChatGPT 的界面元数据和隐式调用设置；
  其他 Agent 可以安全忽略。

相关官方说明：

- [Codex skills](https://developers.openai.com/codex/skills)
- [OpenCode Agent Skills](https://opencode.ai/docs/skills)
- [Claude Code skills](https://code.claude.com/docs/en/skills)

## 安装

需要 Git 和 Python 3.10 或更高版本。保持整个仓库目录不变，
使 `SKILL.md`、`scripts/` 和 `references/` 能通过相对路径访问。

### Codex 与 OpenCode 共用安装

`~/.agents/skills` 同时被 Codex 和 OpenCode 发现：

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/cangyeone/seismicx-skills.git \
  ~/.agents/skills/seismicx-skills
python ~/.agents/skills/seismicx-skills/scripts/resolve_skills.py \
  install --skill all --target ~/.agents/skills
```

### OpenCode 专用安装

```bash
mkdir -p ~/.config/opencode/skills
git clone https://github.com/cangyeone/seismicx-skills.git \
  ~/.config/opencode/skills/seismicx-skills
python ~/.config/opencode/skills/seismicx-skills/scripts/resolve_skills.py \
  install --skill all --target ~/.config/opencode/skills
```

确保活动 Agent 的 `skill` 权限不是 `deny`。

### Claude Code 安装

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/cangyeone/seismicx-skills.git \
  ~/.claude/skills/seismicx-skills
python ~/.claude/skills/seismicx-skills/scripts/resolve_skills.py \
  install --skill all --target ~/.claude/skills
```

如果技能目录是在当前会话启动后首次创建，重新启动 Agent 以刷新技能列表。

### 项目级安装

Codex 与 OpenCode 共用：

```bash
mkdir -p .agents/skills
git clone https://github.com/cangyeone/seismicx-skills.git \
  .agents/skills/seismicx-skills
python .agents/skills/seismicx-skills/scripts/resolve_skills.py \
  install --skill all --target .agents/skills
```

Claude Code 将上面的 `.agents/skills` 替换为 `.claude/skills`。
OpenCode 也可以使用 `.opencode/skills`。

解析器把子仓库安装到与其 frontmatter `name` 一致的目录，例如
`seismicx-catalog/`，从而保持 Agent Skills 客户端的发现和调用一致。
它不会覆盖已有目录。

## 使用

Codex：

```text
Use $seismicx-skills to inspect the waveform and catalog files in this project,
build a standard training dataset, fine-tune PNSN, validate it on continuous
data, and produce a reviewed earthquake catalog.
```

Claude Code：

```text
/seismicx-skills 使用当前目录的连续波形、台站资料和速度模型生成地震目录。
```

OpenCode 或通用 Agent：

```text
Use the seismicx-skills skill to route this seismology task and validate every
artifact before passing it to the next stage.
```

自然语言触发同样有效，例如：

```text
我有 SAC 波形、旧震相目录和 StationXML。先建立标准数据集，微调 PNSN，
再在一个月连续波形上生成候选地震目录，最后根据验证结果修改论文。
```

## 依赖管理

只检查，不修改文件：

```bash
python scripts/resolve_skills.py status
python scripts/resolve_skills.py locate --skill catalog
```

安装一个或全部子技能：

```bash
python scripts/resolve_skills.py install --skill dataset --target ~/.agents/skills
python scripts/resolve_skills.py install --skill all --target ~/.agents/skills
```

可用路由为 `paper`、`catalog`、`dataset`、`fine-tuning` 和
`all`。也可以通过 `--search-root` 添加 Agent 的自定义技能目录。

解析器会搜索：

- 当前项目向上到 Git 根目录中的 `.agents/skills`、
  `.opencode/skills` 和 `.claude/skills`；
- `~/.agents/skills`、`~/.config/opencode/skills`、
  `~/.claude/skills` 和兼容的旧 Codex 目录；
- 调度器自身的同级目录及显式 `--search-root`。

## 科学与数据安全

- 原始波形、目录、模型权重和论文源文件保持只读。
- 不自动下载大规模或多 TB 数据集。
- 不把 smoke test 描述成生产结果。
- 不把窗口级模型精度描述成连续监测性能。
- 不把未通过定位、震级或台网覆盖 QC 的结果当作最终目录。
- 论文阶段只能使用已提供或已验证的证据，不能生成缺失结果或引用。
- 未经用户明确要求，不上传或提交数据、目录、权重、实验输出或论文。

## 仓库结构

```text
seismicx-skills/
├── SKILL.md
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── routing.md
│   └── pipelines.md
└── scripts/
    └── resolve_skills.py
```

- [路由边界](references/routing.md)处理容易混淆的任务归属。
- [多技能流水线](references/pipelines.md)定义阶段制品、交接字段和失败处理。
- [依赖解析器](scripts/resolve_skills.py)定位或显式安装四个上游技能。

## 验证

```bash
python -m py_compile scripts/resolve_skills.py
python scripts/resolve_skills.py status
python /path/to/skill-creator/scripts/quick_validate.py .
```
