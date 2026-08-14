# Multi-skill pipeline contracts

Use this reference when two or more child skills are selected.

## Stage template

For every stage, record:

1. route and child skill;
2. accepted inputs and why they are valid;
3. exact command or editorial operation;
4. output paths and schemas;
5. validation gate and result;
6. assumptions and provenance required by the next stage.

Use separate work directories such as `01-dataset`, `02-training`,
`03-catalog`, and `04-paper` when the user has not supplied a layout.
Never move or rewrite the immutable source data merely to fit this structure.

## Dataset to fine-tuning

### Handoff

- standard HDF5 or a documented native-data adapter;
- canonical labels and explicit class or phase order;
- event/source grouping key;
- sample rate, component order, window definition, and waveform units;
- dataset index, validation report, and source hashes where practical.

### Gate

Open representative waveform records with the intended loader. Reject missing
labels, unreadable keys, non-finite samples, wrong shapes, or cross-split group
leakage. Resampling must be explicit; sample indices from one rate must not be
reinterpreted at another rate.

## Fine-tuning to catalog

### Handoff

- trusted checkpoint and checksum;
- exact architecture, source revision, preprocessing, component order, and
  sampling rate;
- phase or class ordering and inference thresholds;
- validation and held-out metrics;
- limits of the training distribution.

### Gate

Run a small continuous-waveform inference test before production scanning.
Confirm output tensor semantics, time alignment, false alarms over time, station
diversity, and timing residuals. A window-level metric alone does not satisfy
this gate.

If the catalog child does not directly support the new checkpoint, create an
experiment-local adapter instead of silently substituting a bundled model.
Document the adapter and verify it on known windows.

## Catalog to dataset

### Handoff

- located event table and associated-pick table;
- stable event, station, and pick identifiers;
- UTC origin and arrival times with precision;
- latitude, longitude, depth convention, magnitude type, and uncertainties;
- catalog QC results and selected velocity or travel-time model.

### Gate

Normalize the catalog without discarding unmapped source fields. Verify that
event windows use origin times unless the user explicitly requests pick-relative
windows. Confirm that station identifiers join waveform metadata unambiguously.

## Analysis to paper

“Analysis” may be a catalog, dataset, or fine-tuning stage.

### Evidence bundle

- user question and analysis scope;
- final tables, figures, metrics, and uncertainty;
- data selection and exclusions;
- methods, versions, parameters, and regional assumptions;
- failed checks and known limitations;
- a clear distinction between direct result, supported interpretation, and
  hypothesis.

### Gate

Trace every central numerical or scientific claim to the evidence bundle. The
paper child may improve explanation and calibrate wording, but it must not create
missing analyses, citations, metrics, mechanisms, or novelty.

## Common pipelines

### Raw archive to model

`dataset → fine-tuning`

Use dataset to standardize and validate reusable data. Use fine-tuning to build
group-safe partitions, dry-run the real checkpoint, train, and evaluate.

### Adapted model to operational candidate catalog

`fine-tuning → catalog`

Train and validate first. Then test continuous inference, associate and locate
picks, and perform catalog-level QC. Keep model metrics separate from catalog
quality metrics.

### Existing catalog to trained model

`dataset → fine-tuning`

Normalize catalog and phase labels, construct event windows or a documented
adapter, validate identifiers and waveform access, then train.

### Full seismic AI study

`dataset → fine-tuning → catalog → paper`

Build the data contract, train without leakage, test on continuous data through
catalog production, and write only from the validated evidence bundle. Skip any
stage already satisfied by a user-provided validated artifact.

### Catalog study and manuscript revision

`catalog → paper`

Produce or revise the catalog, complete location/magnitude/mechanism and spatial
sanity checks as applicable, then hand tables, figures, uncertainty, methods,
and limitations to paper.

## Failure handling

- Stop at the first failed gate that makes downstream interpretation invalid.
- Preserve partial artifacts and diagnostics in the current stage directory.
- Do not weaken a paper claim to hide a failed analysis; repair the analysis or
  clearly state that the evidence is unavailable.
- Do not retrain a model to compensate for a catalog schema or time-alignment
  error.
- Do not rebuild a dataset when a small explicit adapter can safely satisfy the
  next stage.
