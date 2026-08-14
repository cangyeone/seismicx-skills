# SeismicX Skills

A unified Agent Skill orchestrator for seismology. It selects and coordinates
four SeismicX child skills according to the requested deliverable, while keeping
data, model, catalog, and manuscript handoffs explicit and traceable.

This repository follows the open
[Agent Skills specification](https://agentskills.io/specification) and is
designed for Codex, OpenCode, Claude Code, and other agents that can read a
`SKILL.md` file and its relative resources.

## Capabilities and Upstream Skills

| Task | Child skill | Upstream repository |
|---|---|---|
| Scientific manuscript revision, abstracts, discussions, reviewer responses, and claim calibration | `seismicx-paper-skill` | [seismicx-paper-skill](https://github.com/cangyeone/seismicx-paper-skill) |
| Continuous-waveform detection, picking, association, location, magnitude, focal mechanisms, and earthquake catalogs | `seismicx-catalog` | [seismicx-catalog-skill](https://github.com/cangyeone/seismicx-catalog-skill) |
| Waveform conversion, miniSEED indexing, label normalization, standard HDF5, and dataloaders | `seismicx-dataset` | [seismicx-dataset-skill](https://github.com/cangyeone/seismicx-dataset-skill) |
| SeismicXM/PNSN data adaptation, fine-tuning, validation, and model comparison | `seismicx-fine-tuning` | [seismicx-fine-tuning-skill](https://github.com/cangyeone/seismicx-fine-tuning-skill) |

The orchestrator does not vendor the four repositories. It first uses child
skills already discovered by the active agent. It can also locate or explicitly
install missing child skills through `scripts/resolve_skills.py`.

## Routing

A single-purpose request loads only the necessary child skill:

- “Build an earthquake catalog and event map from continuous miniSEED” → `catalog`
- “Convert SAC and a legacy bulletin into standard HDF5” → `dataset`
- “Fine-tune PNSN with regional data” → `fine-tuning`
- “Revise the Discussion and calibrate its scientific claims” → `paper`

Multi-stage requests use explicit intermediate artifacts and validation gates:

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

When the user already provides a validated intermediate artifact, the
orchestrator skips the corresponding upstream stage.

## Agent Compatibility

`SKILL.md` is the canonical workflow. The other entrypoints only help
different agents discover and load it.

| Agent | User-level directory | Project-level directory | Explicit invocation |
|---|---|---|---|
| Codex | `~/.agents/skills/seismicx-skills/` | `.agents/skills/seismicx-skills/` | `$seismicx-skills` |
| OpenCode | `~/.config/opencode/skills/seismicx-skills/` or `~/.agents/skills/seismicx-skills/` | `.opencode/skills/seismicx-skills/` or `.agents/skills/seismicx-skills/` | Use `seismicx-skills`; OpenCode V2 also supports `/seismicx-skills` |
| Claude Code | `~/.claude/skills/seismicx-skills/` | `.claude/skills/seismicx-skills/` | `/seismicx-skills` |
| Other Agent Skills clients | The client-configured skills directory | Usually `.agents/skills/` | Use the skill name `seismicx-skills` |

Compatibility entrypoints:

- `SKILL.md`: portable Agent Skills entrypoint and complete orchestration rules.
- `AGENTS.md`: repository instructions for OpenCode, Codex, and agents that
  support the AGENTS convention.
- `CLAUDE.md`: Claude Code repository entrypoint and compatibility guidance.
- `agents/openai.yaml`: Codex/ChatGPT UI metadata and implicit-invocation
  settings; other agents can safely ignore it.

Official documentation:

- [Codex skills](https://developers.openai.com/codex/skills)
- [OpenCode Agent Skills](https://opencode.ai/docs/skills)
- [Claude Code skills](https://code.claude.com/docs/en/skills)

## Installation

Git and Python 3.10 or later are required. Keep the complete repository
directory intact so that `SKILL.md`, `scripts/`, and `references/` remain
available through relative paths.

### Shared Codex and OpenCode Installation

`~/.agents/skills` is discovered by both Codex and OpenCode:

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/cangyeone/seismicx-skills.git ~/.agents/skills/seismicx-skills
python ~/.agents/skills/seismicx-skills/scripts/resolve_skills.py install --skill all --target ~/.agents/skills
```

### OpenCode-Specific Installation

```bash
mkdir -p ~/.config/opencode/skills
git clone https://github.com/cangyeone/seismicx-skills.git ~/.config/opencode/skills/seismicx-skills
python ~/.config/opencode/skills/seismicx-skills/scripts/resolve_skills.py install --skill all --target ~/.config/opencode/skills
```

Make sure the active OpenCode agent's `skill` permission is not set to
`deny`.

### Claude Code Installation

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/cangyeone/seismicx-skills.git ~/.claude/skills/seismicx-skills
python ~/.claude/skills/seismicx-skills/scripts/resolve_skills.py install --skill all --target ~/.claude/skills
```

Restart the agent to refresh its skill catalog if the top-level skills
directory was created after the current session started.

### Project-Level Installation

For a shared Codex and OpenCode project installation:

```bash
mkdir -p .agents/skills
git clone https://github.com/cangyeone/seismicx-skills.git .agents/skills/seismicx-skills
python .agents/skills/seismicx-skills/scripts/resolve_skills.py install --skill all --target .agents/skills
```

For Claude Code, replace `.agents/skills` with `.claude/skills`. OpenCode
can also use `.opencode/skills`.

The resolver installs every child repository under its frontmatter `name`,
such as `seismicx-catalog/`, so Agent Skills discovery and invocation remain
consistent even when the upstream repository name differs. Existing
directories are never overwritten.

## Usage

Codex:

```text
Use $seismicx-skills to inspect the waveform and catalog files in this project,
build a standard training dataset, fine-tune PNSN, validate it on continuous
data, and produce a reviewed earthquake catalog.
```

Claude Code:

```text
/seismicx-skills Use the continuous waveforms, station metadata, and velocity
model in the current directory to produce a reviewed earthquake catalog.
```

OpenCode or another Agent Skills client:

```text
Use the seismicx-skills skill to route this seismology task and validate every
artifact before passing it to the next stage.
```

Natural-language activation also works:

```text
I have SAC waveforms, a legacy phase bulletin, and StationXML. Build a standard
dataset, fine-tune PNSN, produce a candidate catalog from one month of
continuous data, and revise the manuscript using the validated results.
```

## Dependency Management

Inspect installed child skills without changing files:

```bash
python scripts/resolve_skills.py status
python scripts/resolve_skills.py locate --skill catalog
```

Install one or all child skills:

```bash
python scripts/resolve_skills.py install --skill dataset --target ~/.agents/skills
python scripts/resolve_skills.py install --skill all --target ~/.agents/skills
```

Available route names are `paper`, `catalog`, `dataset`,
`fine-tuning`, and `all`. Use `--search-root` to add a custom skill
directory configured by another agent.

The resolver searches:

- `.agents/skills`, `.opencode/skills`, and `.claude/skills` from the
  current directory up to the Git repository root;
- `~/.agents/skills`, `~/.config/opencode/skills`,
  `~/.claude/skills`, and the compatible legacy Codex directory;
- directories beside the orchestrator and explicit `--search-root` values.

## Scientific and Data Safety

- Keep source waveforms, catalogs, model checkpoints, and manuscripts unchanged.
- Do not automatically download large or multi-terabyte datasets.
- Never describe a smoke test as a production result.
- Never present window-level model accuracy as continuous-monitoring performance.
- Do not treat events that fail location, magnitude, or station-coverage QC as
  a final earthquake catalog.
- Use only supplied or validated evidence during manuscript work; do not invent
  missing results or citations.
- Do not upload or commit data, catalogs, weights, experiment outputs, or
  manuscripts unless the user explicitly requests it.

## Repository Structure

```text
seismicx-skills/
├── SKILL.md
├── README.md
├── LICENSE
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

- [Routing boundaries](references/routing.md) resolve ambiguous task ownership.
- [Multi-skill pipelines](references/pipelines.md) define stage artifacts,
  handoff fields, validation gates, and failure handling.
- [Dependency resolver](scripts/resolve_skills.py) locates or explicitly
  installs the four upstream skills.

## License

Unless otherwise noted, the contents of this repository are licensed under the
[Creative Commons Attribution-NonCommercial 4.0 International License](LICENSE),
SPDX identifier `CC-BY-NC-4.0`. The material may be copied, shared, and
adapted with attribution and an indication of changes, but it may not be used
for commercial purposes.

This license applies only to the contents of the `seismicx-skills`
repository. The four upstream child-skill repositories, third-party code,
datasets, model weights, and other external materials remain under their own
licenses and are not relicensed by this orchestrator.

## Maintainers

- Xin Liu（刘鑫）: [xinliu_geo@outlook.com](mailto:xinliu_geo@outlook.com)
- Yuqi Cai（蔡育埼）: [caiyuqiming@foxmail.com](mailto:caiyuqiming@foxmail.com)
- Ziye Yu（于子叶）: [yuziye@hotmail.com](mailto:yuziye@hotmail.com)

## Validation

```bash
python -m py_compile scripts/resolve_skills.py
python scripts/resolve_skills.py status
python /path/to/skill-creator/scripts/quick_validate.py .
```
