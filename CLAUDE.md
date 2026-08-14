# SeismicX Skills Claude Code Context

This is a portable Agent Skill, not a Claude-only workflow. Read the complete
root `SKILL.md` first and treat it as the source of truth. Invoke the installed
orchestrator as `/seismicx-skills`.

## Dispatch

- Use `seismicx-paper-skill` for manuscript and reviewer-response work.
- Use `seismicx-catalog` for waveform inference and earthquake catalogs.
- Use `seismicx-dataset` for durable waveform, label, index, and HDF5 products.
- Use `seismicx-fine-tuning` for SeismicXM/PNSN training and evaluation.
- Use the minimum route set. For multi-stage work, read
  `references/pipelines.md` and validate every artifact handoff.

Prefer Claude Code's native skill discovery under `.claude/skills` or
`~/.claude/skills`. If a child skill is not advertised, locate its canonical
`SKILL.md` without modifying files:

```bash
python scripts/resolve_skills.py locate --skill <route>
```

Read that child `SKILL.md` directly and load only the references needed for
the current stage. Do not replace child instructions with a generic workflow.

## Guardrails

- Keep original waveforms, catalogs, checkpoints, and manuscripts unchanged.
- Preserve time standards, units, sample rates, component order, identifiers,
  phase ontology, split grouping, preprocessing, and model provenance across
  stages.
- Do not pass a failed dataset, training run, or catalog QC result downstream.
- Do not invent scientific results, citations, mechanisms, or model performance
  in the paper stage.
- Do not publish, upload, or commit scientific artifacts unless the user
  explicitly requests it.

When editing this repository, follow `AGENTS.md` and run its validation
commands.
