# Measurement Replay: Regression and Accuracy Evidence

Replay recorded inputs through the real implementation to detect behavior changes.
Agreement with an approved baseline establishes regression fidelity, not absolute
measurement accuracy: both versions can share a bias. Accuracy claims require a
traceable reference input and its uncertainty, plus target/sensor-chain validation.

## Boundary and Recording

Use the earliest stable captured boundary, for example
`raw codes → filter → calibration → compensation → engineering value`.
List upstream stages that the capture cannot exercise. Run the actual C/C++ logic
through a host build or exported target output; a Python reimplementation alone
does not test the firmware. Python can analyze outputs independently.

Keep a versioned binary/text recording with the metadata needed to interpret it:
layout, channel mapping, units/gain/range, timestamps or sample timing, calibration
revision, baseline firmware, provenance and content hash. Include temperature when
it affects the claim. Mark unavailable metadata instead of guessing it. Record
initial filter state, gaps and validity as applicable; pin external artifact versions.

## Cases and Oracles

Select recorded normal and difficult segments plus synthetic boundary vectors:
zero, mid/full scale, clipping, steps, drift, missing input, reset and recovery as
relevant. Recordings expose real noise; synthetic cases expose rare precise faults.
For stateful pipelines test chunked vs continuous replay, warm-up, reconfiguration,
state inheritance and generation changes when supported.

Use requirement-derived oracles as well as the baseline. Mean/std/p2p alone can
miss channel swaps, timestamp shifts or a lost step; check sequence, metadata and
invalidity semantics before aggregate metrics.

## Tolerance Policy

- State tolerance and units before comparing. One possible rule is
  `abs(candidate-reference) <= atol + rtol*abs(reference)` with range-specific
  bounds where required. Define NaN/Inf, saturation and invalid-sample handling.
- Deterministic IIR replay with the same input, initial state and arithmetic can
  use sample-level comparisons (with justified numeric tolerance). Stateful does
  not imply statistics-only testing; compiler/FPU changes may need other tolerances.
- Check steady-window bias/noise and bounded settling/step response as required.
  Define window and alignment from the contract; do not shift results or discard
  transients after seeing failures to conceal latency or instability.
- Keep baseline deviation distinct from error against a calibrated reference.

## Report and Baseline Changes

For each relevant case report recording/version, metric, reference or baseline,
candidate, tolerance, verdict and uncovered hardware assumptions. A small change
needs only affected cases, not a mandatory full measurement report.

Keep old golden data and the comparison. Change expectations only when requirements
or evidence justify it; explain the expected change and follow project approval
policy, honoring authorization already given. Do not regenerate golden data from
candidate output merely to silence a failed assertion.
