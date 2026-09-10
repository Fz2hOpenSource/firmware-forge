# Device States and Link Timing

## Minimum State Model

Read `requirements-and-growth.md` for simple development and channel expansion.
Create a state when future behavior must remember a distinct operating condition
or a real asynchronous wait. Keep rate/channel selection as configuration and retry
count as bounded operation context where their behavior permits it. These still
have state space; changing an enum to flags does not remove complexity.

Define one writer per authoritative field/domain. Derive busy/ready flags where
possible instead of maintaining independent writable copies. Separate device mode,
link reachability, data validity, operation phase and hardware observations only
where the requirements distinguish them; they need not become separate managers.

An IDLE/RUNNING design can suffice when start/stop are bounded and failures leave a
confirmed state. Add STARTING/STOPPING only when the operation spans processing
turns. Unknown physical outcome cannot be concealed by assigning IDLE.

## State × Input Behavior

For the affected states and commands, specify accept, reject, merge, defer or ignore.
Deferral needs capacity and expiry. Repeated STOP may share the active stopping
operation; START while stopping may return BUSY. Choose and document behavior.

Valid addressed unicast commands denied by current state return a defined error.
Broadcasts, malformed frames and protocols that forbid replies need their own
silence/discard rules; replying indiscriminately can cause bus collisions.

Classify each parameter change: permitted immediately, applied at a verified
boundary, or forbidden while running. Rate/filter changes may need a controlled
transition; an unrelated display preference may not. Calibration/factory operations
follow product requirements rather than a universal measurement-time ban.

Document which filters, buffers, counters and configuration survive start, stop,
disconnect and reset. Publish only confirmed effects; continuity choices must match
measurement meaning, not accidental variable initialization.

## Delivery and Initiation

- **Polled/master initiated:** define legal requesters, bus access and turnaround.
- **Periodic/current value:** define update period, maximum age and missing-data
  behavior. If old values can be superseded, avoid per-update transaction retries.
- **Event/transaction:** if every occurrence or effect matters, define identity,
  delivery/retention and duplicate semantics; the next update cannot replace it.
- **Hybrid:** classify traffic and bound interference. Waveform upload cannot
  indefinitely delay STOP, status or error reporting.

Multi-transmitter shared links require a defined access mechanism. Use the chosen
transport's arbitration where applicable; do not impose UART/RS-485 assumptions
on CAN or full-duplex links. Event-driven does not imply unregulated bus access.

## Timing and Failure

Derive exchange deadlines from serialization, turnaround, worst device work, bus
load, task scheduling and margin. Example constants are not defaults. Distinguish
receipt/acceptance deadline from long-operation completion and stream freshness.
Specify the clock/unit and budget source; do not compare PC wall time directly to
MCU ticks. Counter wrap and reboot invalidate naive time comparisons.

At an exchange timeout, the host has not obtained the promised response in time.
That does not establish whether the command took effect. Classify command semantics
before retrying: repeated requests may be harmless, deduplicated, queryable, or
unsafe to repeat. Define which layer owns retries, maximum attempts and a total
deadline that is not refreshed by partial responses or nested recovery.

Reachability/offline status is a separate assessment based on expected contact and
freshness. One failed command may coexist with valid telemetry; stopped streaming
may be intentional. When heartbeat is necessary it may share a status frame; a
periodic polled exchange may already provide the needed evidence. Heartbeat does
not by itself prove acquisition progress or hardware safety.

For every temporary wait declare the completion evidence, timeout result, and
applicable cancel/disconnect/restart behavior. A timeout clause is a requirement,
not proof that firmware can process it: the implementation review must check
blocked drivers, queue saturation, timer delivery and scheduling. Recovery has a
bounded endpoint; when safety cannot be confirmed, report that fact explicitly.

## Line Discipline

For half-duplex links specify direction switching, legal initiators, inter-frame
gaps, reply/broadcast rules and processing latency. For mixed streaming/control,
specify bounded bursts or arbitration and measure control latency at maximum load.

For asynchronous outcomes, restart and lost completion use `operation-lifecycle.md`.
