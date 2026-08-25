# Measurement Data Replay and Accuracy Regression

The instrument-team method for proving "this change did not degrade
accuracy": feed recorded real-world data through the pipeline and compare
engineering outputs against an approved baseline.

## Pipeline Under Test

```text
recorded raw codes → filter → calibration → compensation → engineering value
```

Feed data from the earliest stable boundary available — raw codes rather
than pre-computed engineering values — so every stage of the chain is
re-verified, not just the last one. When earlier stages genuinely cannot
be captured, replay from the first stable boundary and document the
uncovered upstream stages explicitly in the test.

## Recording Spec

Binary stream of raw ADC codes plus a metadata header (JSON sidecar or
prefixed block). Required metadata:

- device/sensor model, gain and range configuration
- sample rate, channel map
- ambient temperature (and sensor temperature if available)
- recording timestamp, duration, sample count
- firmware baseline version that produced the recording
- data format version (layout can evolve; readers must detect it)

Store checksums with each recording. Large sets may live in LFS or an
artifact store; the test must reference an exact version.

## Golden Set Coverage Matrix

A golden set is never just "normal" data:

- zero input / static noise floor
- full scale and clipping/saturation behavior
- mid-range linear region
- temperature-drift segments (cold/soak/hot as available)
- optional: injected fault recordings (glitches, dropouts) for filter
  recovery checks

## Tolerance Policy (define before writing test code)

- Combine **absolute + relative** tolerance so near-zero outputs do not
  explode relative error.
- Segment tolerances by range where accuracy specs vary.
- For stateful filters (IIR), assert statistics on a steady-state window —
  mean error, standard deviation (e.g. 3σ bound), peak-to-peak — not
  sample-by-sample equality.
- Bound convergence time (samples/seconds to settle within band) when the
  pipeline is stateful.
- A regression metric set covers: **accuracy** (mean error),
  **repeatability** (std deviation), **noise** (peak-to-peak),
  **drift** (slow trend), **convergence time**.

## Regression Report

For each golden case, old vs new baseline on the same recording:

| Case | Metric | Baseline | Candidate | Tolerance | Verdict |
|---|---|---|---|---|---|
| mid-range 10 mV | mean error | 0.000008 | 0.000009 | ±0.000010 | PASS |
| full scale | p2p noise | 0.9 | 1.4 | ≤1.5 | PASS |

Output the full table plus a human-readable diff summary; a bare
pass/fail is not a reviewable regression report.

## Golden Update Procedure

Golden data is immutable without approval. An update requires:

1. Reason (why the old expectation is no longer correct)
2. Expected behavior change stated before comparing
3. Old/new comparison report attached
4. Explicit approval

Never update golden data to make a failing test pass. If the failure is a
real regression, fix the code; if the old golden was wrong, fix it through
this procedure.
