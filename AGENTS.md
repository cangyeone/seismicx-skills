# SeismicX Skills Agent Instructions

This repository contains a portable, agent-agnostic orchestrator for seismology
work. Treat `SKILL.md` as the canonical workflow. Use this file as a short
entrypoint for OpenCode, Codex, and other tools that load `AGENTS.md`.

## Handle Seismology Requests

1. Read the complete root `SKILL.md`.
2. Select the minimum child route: `paper`, `catalog`, `dataset`, or
   `fine-tuning`.
3. Read `references/routing.md` only when ownership is ambiguous.
4. Read `references/pipelines.md` whenever more than one route is needed.
5. Load the selected child's complete `SKILL.md`. Prefer the host Agent's
   native skill tool; otherwise locate it with:

   ```bash
   python scripts/resolve_skills.py locate --skill <route>
   ```

6. Never claim to have used a child skill when its `SKILL.md` was not loaded.
7. Validate every handoff before starting the next stage.

Use `SKILL.md`, not this file, for the detailed scientific gates and safety
rules.

## Cross-Agent Compatibility

- Keep the root folder name `seismicx-skills`; it matches the skill
  frontmatter name required by portable Agent Skills clients.
- Keep all paths in `SKILL.md` relative to the repository root.
- Keep portable behavior in `SKILL.md`; do not move required workflow rules
  into `agents/openai.yaml`, `AGENTS.md`, or `CLAUDE.md`.
- Treat `agents/openai.yaml` as optional Codex/ChatGPT metadata.
- Install child repositories under their frontmatter skill names. The resolver
  handles upstream repository names that differ from skill names.

## Modify This Repository

- Preserve the four canonical upstream repositories and route names in
  `references/routing.md` and `scripts/resolve_skills.py`.
- Keep `README.md`, `AGENTS.md`, `CLAUDE.md`, and `SKILL.md`
  consistent when installation paths or invocation behavior changes.
- Do not vendor the child repositories or generated seismology artifacts.
- Use Python standard-library code in `scripts/resolve_skills.py`.
- Refuse to overwrite an existing skill directory during installation.

## Validate Changes

```bash
python -m py_compile scripts/resolve_skills.py
python scripts/resolve_skills.py locate --skill all --search-root <skills-parent>
python /path/to/skill-creator/scripts/quick_validate.py .
git diff --check
```
