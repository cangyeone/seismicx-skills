---
name: seismicx-skills
description: Unified SeismicX orchestrator for seismology work. Use when a request spans, ambiguously belongs to, or needs routing among scientific-paper revision, earthquake detection and catalog production, seismic dataset construction, and SeismicXM/PNSN fine-tuning. Also use for end-to-end seismic AI projects involving raw waveforms, phase picks, event catalogs, station metadata, velocity models, standardized HDF5, model training or evaluation, and manuscript or reviewer-response writing. Trigger for Chinese or English requests about 地震波形、震相拾取、地震目录、地震数据集、模型微调、地震学论文, or coordination of the seismicx-paper-skill, seismicx-catalog, seismicx-dataset, and seismicx-fine-tuning skills.
---

# SeismicX Skills Orchestrator

Coordinate the four SeismicX skills as one seismology workflow. Route each stage
to the narrowest capable child skill, preserve explicit artifacts between stages,
and apply cross-stage scientific quality gates.

## Agent compatibility

Use this `SKILL.md` as the canonical portable entrypoint in Codex, OpenCode,
Claude Code, or another Agent Skills client. Treat `$skill-name`,
`/skill-name`, and a host-native skill-tool call as client-specific syntax for
the same canonical frontmatter `name`. If the host does not expose a native
skill tool, locate and read the selected child's `SKILL.md` directly.

`AGENTS.md` and `CLAUDE.md` are compatibility entrypoints only.
`agents/openai.yaml` adds Codex/ChatGPT UI metadata but is not required for the
workflow.

## Dispatch map

| Route | Child skill | Owns |
|---|---|---|
| paper | `$seismicx-paper-skill` | Manuscript editing, scientific argument, claim calibration, abstracts, discussions, cover letters, and reviewer responses |
| catalog | `$seismicx-catalog` | Continuous-waveform inference, phase picking, association, location, magnitude, focal mechanisms, activity analysis, and final earthquake catalogs |
| dataset | `$seismicx-dataset` | Waveform conversion, miniSEED indexing, label normalization, standard event or continuous HDF5, dataset indexes, and dataloaders |
| fine-tuning | `$seismicx-fine-tuning` | SeismicXM/PNSN data adapters, manifests, group-safe splits, training, validation, comparison, and reproducible evaluation |

Read [references/routing.md](references/routing.md) when ownership is ambiguous.
Read [references/pipelines.md](references/pipelines.md) whenever two or more
routes are required.

## Required dispatch procedure

1. Identify the user's actual deliverable, available inputs, constraints, and
   acceptance criterion. Distinguish a requested result from a request to merely
   explain a method.
2. Select the minimum route set from the dispatch map. Do not invoke all four
   skills for a single-route task.
3. Resolve every selected child skill before acting:
   - Prefer a child skill already exposed by the agent environment.
   - Otherwise run
     `python <this-skill>/scripts/resolve_skills.py locate --skill <route>`.
   - If it is missing, report the exact repository. Install it only with user
     authorization by running
     `python <this-skill>/scripts/resolve_skills.py install --skill <route> --target <skill-directory>`.
   - Do not claim to have used a child skill when its `SKILL.md` was not loaded.
4. Read the selected child's complete `SKILL.md`, then read only the child
   references needed for the current stage. Treat its domain-specific operating
   rules as authoritative unless they conflict with system or user instructions.
5. For a multi-route task, write a stage plan with an input, output, and validation
   gate for each transition. Execute one stage at a time and validate its output
   before handing it to the next child.
6. Return the requested result first. Then report routes used, material artifacts,
   validation performed, unresolved assumptions, and whether each run was a smoke
   test or a completed scientific workflow.

## Resolve common overlaps

- Use **catalog** for inference on waveform archives; use **fine-tuning** for
  changing model weights, thresholds under an experiment protocol, or comparing
  trained models.
- Use **dataset** for durable waveform/label standardization and HDF5/index
  production; use **fine-tuning** for experiment-local manifests and adapters.
- Use **catalog** to create or refine earthquake events and picks; use **dataset**
  only after those products need conversion into reusable training labels or
  standardized datasets.
- Use **paper** to express supplied or produced evidence. Never let the paper
  stage invent results, citations, model performance, catalog quality, mechanisms,
  or novelty.
- Skip an upstream stage when the user already provides a validated artifact
  satisfying the next child's input contract. Record why it was accepted.

## Cross-stage contracts

At each handoff, preserve:

- source paths and immutable input identifiers;
- time standard and precision, waveform units, sample rate, component order, and
  channel naming;
- network, station, location, channel, event, and pick identifiers;
- coordinate reference, depth sign and units, velocity-model identity, and
  magnitude convention;
- label ontology and order, split grouping key, preprocessing, thresholds, seed,
  checkpoint identity, and source revision;
- commands, versions, checksums where practical, intermediate artifacts, QC
  results, and known limitations.

Never silently reinterpret a sample index, phase name, coordinate, depth, label,
or model output at a route boundary. Convert explicitly and retain the original
field when information does not map cleanly.

## Scientific quality gates

- **Dataset gate:** validate schema, readable waveform keys, finite samples,
  metadata consistency, and dataloader access.
- **Training gate:** reject group leakage; dry-run the real checkpoint and input
  shape; keep model selection separate from held-out testing.
- **Catalog gate:** inspect station coverage, duplicate or unmatched picks,
  association residuals, location depth boundaries, azimuthal gaps, magnitude
  outliers, first-motion quality, and map sanity.
- **Paper gate:** trace central claims to produced or supplied evidence and keep
  claim strength within that evidence boundary.

Do not pass a failed artifact downstream as if it were valid. Stop at the failed
gate, preserve diagnostic outputs, and propose the smallest corrective action.

## Operating rules

- Prefer explicit intermediate files and reproducible commands over a hidden
  monolithic run.
- Inspect local data before downloading models or datasets. Never fetch a broad
  or multi-terabyte collection by default.
- Do not overwrite raw data, source catalogs, checkpoints, or user manuscripts.
- Do not publish, upload, or commit raw waveforms, generated catalogs, model
  weights, experiment outputs, or manuscripts unless the user explicitly asks.
- Keep regional assumptions explicit, including phase ontology, travel-time or
  velocity model, magnitude relation, response source, and sampling rate.
- Separate a smoke test from a production result in both execution and reporting.
