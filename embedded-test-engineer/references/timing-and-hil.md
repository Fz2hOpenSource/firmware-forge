# Timing Validation, Simulation, and HIL Planning

Functional correctness and timing correctness are different claims. A
green unit suite proves neither interrupt latency, nor DMA jitter, nor
cache effects, nor peripheral protocol timing.

## Which Layer Can Prove What

| Indicator | Provable at |
|---|---|
| Retry/backoff durations, debounce logic (logical ticks) | L1 with fake tick injection |
| Scheduling behavior, deadlock/starvation, timeout logic at scale | L3 simulation (virtual time) |
| Register-level integration defects, multi-node exchanges | L3 (Renode, unmodified ELF) |
| ISR latency, DMA jitter, cache misses' impact | L4 HIL only |
| Peripheral protocol timing (setup/hold, sample instant) | L4 HIL only |

## Simulation Positioning

- **Renode**: runs the production cross-compiled ELF unmodified; given
  identical platform models and inputs, execution is instruction-level
  deterministic and reproduces the same trace across runs — external
  inputs (timers, radios, real peripherals) break determinism, so pin
  them in the model; multi-node boards/links; GDB-attachable. Good for
  register-level integration defects without hardware.
- **Zephyr native_sim**: compiles kernel + app as a host program; virtual
  time decoupled from wall clock (hours of timeouts in seconds); drives
  ZTest suites over full RTOS stacks.

Both are L3 evidence. Neither substitutes L4 for analog/timing claims.

## Hardware-Assisted Tests (L4)

Typical patterns for measurement systems:

| Type | Example |
|---|---|
| Signal source | Calibrator/DAC feeds known waveform into ADC input |
| Time/frequency | Signal generator outputs known 10 kHz; MCU/FPGA counter measures it; verdict computed in ppm automatically |
| Communication | PC script acts as protocol host: scripted sequences, malformed frames, timing pressure |
| Precision | Standard source at zero/mid/full scale; engineering output must meet accuracy spec |
| Trigger/latency | GPIO loop-back or timer capture measuring ISR-to-output delay |

## HIL Report Requirements

Every timing/HIL claim states:

1. Measurement means (DWT CYCCNT, timer capture, ITM trace, instrument model)
2. Repeat count and statistics (min / max / mean), not a single lucky run
3. Pass thresholds traced back to requirement values
4. Firmware version and hardware revision under test

Scope note: this skill plans what HIL must show and how results are judged;
operating lab instruments is the engineer's job.
