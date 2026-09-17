# Continuous Measurement Streaming

Read this reference for continuous acquisition, long-running upload, mixed ADC/FPGA/timer sources, configuration transitions, or failures that appear as a stopped or "stuck" stream.

## State Model and Liveness

- Distinguish configured, producer running, source validity, output readiness, stream enable and transport connection only where they can change independently under the product contract. These are questions to resolve, not six required stored flags or state machines. Derive values from authoritative state where possible.
- A first-output timeout applies only before the first valid publication of a run. After publication begins, use a separate sustained no-progress rule with its own reason and recovery.
- Temporary no-signal, saturation, invalid status, or profile warm-up should normally keep the service alive, publish explicit invalidity or withhold values according to the product contract, and recover automatically when valid input returns.
- A single malformed, missing, or skewed sample group must not permanently poison synchronization. Drop/count it and re-establish alignment within a bounded number of events or time.
- Define stop and disconnect independently: which producers stop, which configuration remains, which queues drain, and whether reconnect restarts upload automatically.

## Configuration Boundaries and Generations

- Validate an entire requested configuration before changing hardware or application state.
- For changes affecting active hardware or data interpretation, choose a verified application boundary: quiesce/drain when necessary, or use supported atomic/shadow configuration. Reject stale work by generation or another demonstrated isolation mechanism. An unrelated atomic parameter needs no stop/restart or new epoch.
- Where processed values can outlive their configuration, retain enough identity/freshness information to associate them with the active interpretation. Use the profile, generation, calibration revision or timestamp actually needed; proven invalidation/ownership can avoid extra metadata.
- Report operation failure without requiring recovery to succeed first. Claim restoration or a stopped state only when verified. If hardware effects cannot be confirmed within the allowed budget, report failure with hardware uncertainty and follow containment/supervision policy; assigning SAFE or rolling back a software struct is insufficient. Preserve partial-effect evidence and reject unsafe new work.

## Rates and Capacity

- Record raw event rate, algorithm/output rate, publication rate, upload rate, values per sample, batch size, and every producer that can feed a shared queue.
- For each queue, record usable capacity C, worst occupancy Q before the stall, coincident burst B and bounded subsequent arrival rate r. A no-service stall T must satisfy `Q + B + ceil(r*T) <= C` with explicit margin; define B/r to avoid double-counting. `(C-Q-B)/r` is only the remaining stall allowance for r > 0, not an end-to-end latency bound. For variable service, bound cumulative arrivals minus guaranteed service over the relevant windows. Include descriptors and batch-fill delay, not just payload bytes.
- Show consumer service headroom above sustained simultaneous arrivals and bound recovery from backlog. Account for interrupt masking, flash waits, locks, logging and scheduling in the stall bound; reserve control/deadline service under peak data traffic. Measure sustainable application link rate with framing and retransmission overhead instead of using PHY bitrate as capacity.
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

- Select tests by boundaries and interactions: maximum aggregate load, distinct clocks/DMA/resource regimes, independent vs shared channel lifecycles, repeated stop/start and rate/profile transitions. Exhaust small finite option sets when practical; do not demand a Cartesian product of all parameters without a risk-based reason.
- Inject missing input, invalid status, source recovery, timestamp wrap, queue pressure, transport disconnect, and bounded consumer stalls.
- Run long enough to expose counter wrap assumptions, clock drift, periodic storage/network stalls, and rare recovery paths.
- Treat unexplained drops, repeated resynchronization, or queue growth as an unresolved capacity/liveness failure even if final average throughput is close to nominal.
