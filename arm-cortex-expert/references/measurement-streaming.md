# Continuous Measurement Streaming

Read this reference for continuous acquisition, long-running upload, mixed ADC/FPGA/timer sources, configuration transitions, or failures that appear as a stopped or "stuck" stream.

## State Model and Liveness

- Represent at least these concepts separately: configured, producer running, source valid, processed output ready, stream enabled, and transport connected. Do not collapse them into one boolean.
- A first-output timeout applies only before the first valid publication of a run. After publication begins, use a separate sustained no-progress rule with its own reason and recovery.
- Temporary no-signal, saturation, invalid status, or profile warm-up should normally keep the service alive, publish explicit invalidity or withhold values according to the product contract, and recover automatically when valid input returns.
- A single malformed, missing, or skewed sample group must not permanently poison synchronization. Drop/count it and re-establish alignment within a bounded number of events or time.
- Define stop and disconnect independently: which producers stop, which configuration remains, which queues drain, and whether reconnect restarts upload automatically.

## Transaction and Generation Rules

- Validate an entire requested configuration before changing hardware or application state.
- Quiesce affected producers, drain or invalidate queued work, apply hardware and algorithms, increment generation/epoch, and accept only matching-generation results.
- Tag processed values with the measurement profile, source generation, context/calibration revision, and timestamp needed to prove they still match the active interpretation.
- On failure, restore the last known-good configuration or enter a reported safe stopped state. Do not expose a partially committed configuration.

## Rates and Capacity

- Record raw event rate, algorithm/output rate, publication rate, upload rate, values per sample, batch size, and every producer that can feed a shared queue.
- For each ring or queue, calculate `buffer_time = usable_items / worst_case_arrival_rate` and compare it with the longest measured or bounded consumer stall.
- Include ISR work, copying, cache maintenance, filtering, serialization, network calls, diagnostics, transition bursts, and coincident producers in CPU and service-rate budgets.
- Report utilization and headroom. A passing average rate does not explain burst stalls, repeated recovery cycles, or a ring that periodically reaches full.
- Network batching changes latency and overhead; it is not filtering or decimation.

## Mixed and Independent Sources

- Synchronize with source timestamps or explicit epochs. Nominally equal rates do not mean simultaneous samples.
- Choose association skew and history depth from measured source jitter, task latency, clock drift, and scheduling stalls—not simply one nominal output period.
- Define whether the consumer may use a new result, a marked held result, or only an exact-epoch match. Count these paths separately.
- Distinguish no history, expired history, out-of-window candidate, stale generation, invalid source, incomplete group, and queue overflow.
- A matching algorithm may search bounded history, but it must never borrow a future/adjacent epoch merely to make a group complete.

## Time and Counter Semantics

- For wrapping unsigned clocks, compute elapsed time with modular subtraction when the maximum legitimate interval is below half the counter range.
- Keep "not yet observed" in a validity flag. Never initialize a maximum interval to an invalid numeric sentinel that can appear as a real maximum.
- Define sequence wrap, duplicate, missing, and regression detection independently.
- Expose monotonic counters suitable for before/after deltas; document reset events and use wider counters when expected product lifetime can overflow them.

## Transport and Control Coexistence

- Packetize immutable completed snapshots, never live DMA or algorithm state.
- Bound partial-write and no-progress loops. Record backpressure without allowing network stalls to block acquisition indefinitely.
- When control and measurement share a connection, measure control-response latency under maximum upload load and ensure data batching does not starve control frames.
- Define backlog behavior on disconnect: discard, bounded retain, or resume from storage. Never let an unbounded backlog accumulate silently.

## Verification

- Test every supported rate and channel/value combination, including repeated stop/start and rate/profile changes.
- Inject missing input, invalid status, source recovery, timestamp wrap, queue pressure, transport disconnect, and bounded consumer stalls.
- Run long enough to expose counter wrap assumptions, clock drift, periodic storage/network stalls, and rare recovery paths.
- Treat unexplained drops, repeated resynchronization, or queue growth as a failed capacity/liveness proof even if final average throughput is close to nominal.
