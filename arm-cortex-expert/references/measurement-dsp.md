# Measurement DSP and Calibration Chains

Read this reference for filtering, decimation, selectable output rates, anomaly handling, phase/frequency processing, zeroing, or device/sensor calibration.

## Rate and Chain Definition

- Name the actual input sample rate, internal processing rate, decimated output rate, and upload rate. Design coefficients from the rate at the stage where they execute.
- Write the conversion order explicitly with units and revisions at every boundary, for example: raw code → signal filter → nominal physical input → device calibration → optional input adapter → zero → sensor mapping.
- Keep raw/diagnostic values separate from normal calibrated values instead of overloading one field whose meaning depends on hidden mode.
- Apply anti-alias filtering before decimation. Averaging network packets after aliasing cannot restore lost information.

## Filter Design and State

- Record filter type/order, coefficient precision, design sample rate, cutoff/notch center and Q, expected attenuation, group delay, warm-up, and saturation behavior.
- Validate fixed coefficients against the implementation sign convention and numeric precision; preserve a host-side frequency/step response test when coefficients are product-critical.
- A narrow notch is appropriate only when interference frequency is stable. Use measured frequency drift to choose center and bandwidth, and report attenuation of nearby wanted signals.
- Preserve runtime state only when timing, coefficients, units, calibration, and signal meaning are compatible. Define reset, transform, or inherited behavior for each transition.
- Do not hide startup transients as random invalid data. Expose settle/readiness so callers can distinguish warm-up from hardware failure.

## Noise, Drift, Outliers, and Steps

- Separate random noise, periodic interference, impulses, true load steps, slow drift, clipping, and calibration bias before choosing an algorithm.
- An outlier repair must be observable and bounded. Count detected, repaired, held, and relocked events; do not manufacture long runs of plausible data without indicating it.
- Step detection thresholds and confirmation length should scale with measured noise and output rate. Verify both rejection of interference and response to real steps.
- Slow-drift compensation must be explicitly enabled by product policy and gated by stable/near-zero evidence. Preserve an uncorrected mode for fidelity comparison.

## Phase and Frequency

- Treat phase as circular data. Use wrap-aware difference, circular mean/median, and boundary tests around ±180° or the selected canonical interval.
- Perform absolute-value and accumulator checks in a wider signed type so the most-negative integer cannot overflow.
- Distinguish source frequency, calibrated frequency, electrical phase, delay-corrected phase, sensor mechanical zero, and engineering conversion.
- When phase correction depends on frequency, define whether the frequency is nominal or device-calibrated and use that convention consistently at calibration and runtime.

## Calibration and Zero

- Keep device calibration, optional front-end/adapter correction, user zero, and sensor engineering calibration as distinct layers with independent revisions.
- Validate piecewise tables for finite values, allowed point count, strict axis ordering, direction/branch semantics, and duplicate or ambiguous zero points.
- Zeroing should capture the value at the layer specified by the protocol and remain correct when earlier calibration/adapter coefficients change.
- Updating a layer must invalidate or reprocess snapshots that were produced under an older revision; never reinterpret an old processed value using a new context.

## Verification

- Use deterministic host replay for coefficient and conversion regression, then verify the built target and hardware timing.
- Test DC gain, passband, stopband/notch drift, step response, warm-up, saturation recovery, rate switching, state inheritance, and circular boundaries.
- Compare RMS/standard deviation, robust noise, peak-to-peak, percentiles, spectral bands, drift, and segmented stability. Do not optimize only one metric.
- State which conclusions come from simulation, recorded replay, bench input, or the final sensor chain.
