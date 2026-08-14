# SeismicX routing reference

Use this reference only when a request could reasonably belong to more than one
child skill.

## Canonical dependencies

| Route | Skill name | Repository |
|---|---|---|
| paper | `seismicx-paper-skill` | `https://github.com/cangyeone/seismicx-paper-skill.git` |
| catalog | `seismicx-catalog` | `https://github.com/cangyeone/seismicx-catalog-skill.git` |
| fine-tuning | `seismicx-fine-tuning` | `https://github.com/cangyeone/seismicx-fine-tuning-skill.git` |
| dataset | `seismicx-dataset` | `https://github.com/cangyeone/seismicx-dataset-skill.git` |

Repository names and frontmatter skill names differ for the catalog,
fine-tuning, and dataset repositories; the paper repository already matches.
Resolve and install by frontmatter `name`, not repository name alone.

## Decision rules

### Choose paper

Choose the paper route when the requested deliverable is prose or argument:

- edit, translate, shorten, or strengthen a manuscript;
- rewrite a title, abstract, introduction, results, discussion, or conclusion;
- calibrate claims against supplied evidence;
- draft a cover letter or response to reviewers;
- review LaTeX, Markdown, DOCX, or plain-text scientific writing.

Do not route ordinary run notes or a technical command explanation to paper.
When the user asks to write a manuscript from new analysis, complete and validate
the analytical route first, then hand its evidence bundle to paper.

### Choose catalog

Choose the catalog route when waveform data must become detected events or a
scientifically reviewed earthquake catalog:

- scan continuous MSEED, SAC, SEED, or other ObsPy-readable waveforms;
- detect or pick Pg, Sg, Pn, Sn or user-selected phases;
- estimate first motion;
- associate picks with REAL or GaMMA;
- locate with grid, bayes_location, NonLinLoc, or SeismicX-Location;
- calculate ML, focal mechanisms, rates, or event maps.

Picking with fixed pretrained weights is catalog work. Training or adapting the
picker is fine-tuning work.

### Choose dataset

Choose the dataset route when the deliverable is a durable, reusable data product:

- convert arbitrary waveform formats to miniSEED;
- create or query an EarthScope mseedindex SQLite database;
- infer and normalize heterogeneous catalogs or phase labels;
- build standard event or continuous SeismicX HDF5;
- index HDF5 or verify it with a dataloader.

A CSV manifest used only by one experiment can remain fine-tuning work. Route to
dataset when the user requests standardization, archival reuse, indexing, or
conversion across tools.

### Choose fine-tuning

Choose the fine-tuning route when model parameters or experiment conclusions are
the deliverable:

- adapt user-defined waveform layouts and label ontologies;
- build group-safe train, validation, and test partitions;
- fine-tune SeismicXM for classification or picking;
- fine-tune PNSN for Pg/Sg/Pn/Sn picking;
- compare frozen-head, partially unfrozen, or full-model training;
- evaluate checkpoints reproducibly.

Do not use PNSN for event classification. Do not interpret window-level accuracy
as operational continuous-detection performance.

## Ambiguous examples

| Request | Route decision |
|---|---|
| “从连续波形生成地震目录” | catalog |
| “把 SAC 和旧目录整理成标准 HDF5” | dataset |
| “用自己的区域数据微调 PNSN，再跑连续检测” | fine-tuning → catalog |
| “把现有事件目录做成训练集并训练 SeismicXM” | dataset → fine-tuning |
| “从原始波形完成数据集、训练、目录验证和论文” | dataset → fine-tuning → catalog → paper |
| “润色基于现有实验结果的讨论部分” | paper |
| “重新定位目录并改写论文结果部分” | catalog → paper |

## Tie breakers

1. Route by the requested output, not merely the input file type.
2. Prefer one child when it can safely produce the complete deliverable.
3. Add a second child only when a durable handoff artifact is required.
4. Reuse a validated user artifact instead of rebuilding it.
5. If ambiguity changes scientific meaning or compute cost, state the assumption
   before execution.
