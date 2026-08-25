# Device States and Link Timing

## State Machine

- Define named device states (for example IDLE / RUNNING / CALIBRATION
  / ERROR), the transitions between them, and which command triggers
  each transition.
- Document entry actions that reset pipeline state: filters cleared,
  counters zeroed, buffers released. Hosts reason about data validity
  through these boundaries.

## Permission Matrix

- Build a matrix of states × command classes with allow/deny per cell,
  published in the protocol document.
- Denials return the state-not-allowed error code. Silent ignore makes
  hosts poll blindly and blame the link.
- Typical invariant: while measuring, deny parameter changes, factory
  configuration, and calibration. Mid-run mutation corrupts filter
  continuity and invalidates calibration; the gate exists to make the
  failure impossible rather than detectable.
- Recovery commands (soft reset, clear error) document exactly what
  they preserve and what they wipe — ambiguity here turns a recovery
  attempt into data loss.

## Initiation Model

State the model in the protocol document; it decides who may transmit
and when:

- **Master-Slave Polled**: one master initiates every exchange; devices
  never transmit unsolicited frames except declared streams. The
  natural fit for shared half-duplex buses (RS-485 multi-drop).
- **Event-Driven / Standalone**: the device uploads without being
  polled. Define what triggers an upload (event thresholds, state
  changes) and/or fixed broadcast intervals. On a shared multi-drop
  bus this is safe only with time-slot allocation or arbitration;
  free-form pushing is safe only on point-to-point full-duplex links.
- **Hybrid**: polled request/response coexists with declared periodic
  or event-driven streams; declare which traffic belongs to which
  side.

## Timing Contract

- For polled exchanges, response deadline: after N milliseconds without a
  response, the host treats the exchange as failed. Derive N instead of
  guessing — longest-frame transmission time both ways at the configured
  baud rate, plus worst-case device processing time, plus scheduling
  margin (500 ms is a workable starting point for low-speed UART links).
- Retry cap: retransmit at most M times (3 is typical); after the cap,
  declare the device offline instead of retrying forever.
- Liveness (heartbeat): an event-driven device that nobody polls must
  still prove it is alive. Define the heartbeat interval, its content
  (a status word plus an uptime or sequence counter; it may share the
  status-data frame), and how many missed periods mark the device
  offline (three consecutive periods is typical). These constants
  belong in the document, not in each implementation.
- Active-upload streams are exempt from the request/response deadline —
  they are not responses — but get their own liveness rule (maximum
  inter-frame gap before the host declares the stream dead).
- Per-command overrides of the default deadline are allowed but must be
  stated per command in the document, never discovered on the bus.

## Line Discipline and Turnaround

- Under a master-slave model on half-duplex multi-drop links (RS-485),
  only the master initiates; state turnaround expectations (response
  latency bounds, inter-frame gaps) so driver authors can schedule
  line-direction switches and timeouts from the document alone.
- Under an event-driven model on a shared multi-drop bus, time-slot
  allocation or arbitration must be defined before multiple talkers
  are enabled.
- On point-to-point full-duplex links, either side may transmit within
  the declared model — say so explicitly rather than leaving it
  implied by the schematic.

## Why Timing Belongs in the Document

Without a deadline, a hung device hangs the host thread indefinitely;
without an offline verdict, every consumer invents its own; without a
liveness rule, a standalone device dies silently. A short timing
section prevents all three — and prevents each side from
"temporarily" picking different constants.
