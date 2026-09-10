---
name: embedded-protocol-designer
description: >
  Define interaction requirements, design and evolve embedded device-to-host or MCU-to-FPGA
  interaction contracts, from simple start/stop upload to multichannel acquisition.
  Covers UART/RS-485/CAN/USB framing, command semantics, minimum state models,
  duplicate requests, bounded waits, reconnect outcomes, and version compatibility.
  Use for protocol documents, new interactions, state explosion during reliability
  improvements, or backward-compatible command changes. Not electrical design,
  low-level driver implementation, or standalone parser test implementation.
---

# Embedded Protocol Designer

Start from agreed requirements and implement the smallest complete interaction.
Support later changes through explicit responsibilities and compatible interfaces,
not by prebuilding every possible state or feature. Use the user's language.

Use this skill for interaction contracts. Ordinary driver implementation, numeric
optimization, build commands or replay tests under unchanged interfaces do not
need a protocol-design pass. A hardware interface alone is not a reason to redesign
its externally observable behavior.

## Working Mode

- **New design:** read [requirements and growth](references/requirements-and-growth.md).
  Confirm the behavior, then choose a minimum command/state model. An unresolved
  design-changing requirement must remain explicit; do not silently decide it.
- **Local extension:** inspect the existing contract and affected host/device paths.
  Identify changed behavior and compatibility impact, then make a focused delta.
  Do not regenerate the entire protocol or add an object dictionary merely because
  another parameter was added.
- **Failure review:** reconstruct a short failing exchange and identify which side
  waited, retried, committed, or lost evidence. Separate transport reachability,
  operation outcome, and hardware condition before prescribing more states.

Ask only for missing facts that change the current design, after inspecting project
evidence. For a full wire design these usually include topology/node count,
who initiates communication, throughput/payload bounds, and what start/stop means.
For a local change, do not reopen already established requirements. Draft independent
parts while a required answer is pending; label permitted assumptions clearly.

## Ownership and Composition

This skill owns externally observable behavior: frames, commands, permissions,
completion meaning, retries, and compatibility. The firmware owner chooses how
to realize that contract; implementation constraints must be raised rather than
silently changing the protocol.

When implementation work requires it, `arm-cortex-expert` handles ISR/DMA, task
ownership, actual timeouts and resource release. When verification work requires
it, `embedded-test-engineer` handles byte fixtures, event sequences and hardware
gaps. Do not load all three for every small change. Skills remain usable without
the companions: report the relevant implementation or verification boundary.

Follow user and project instructions. Compare project protocol requirements with
host/device code and captured behavior; preserve disagreements as evidence, rather
than treating either the document or the code as automatically correct. Vendor
specifications govern platform facts; skill examples are not product requirements.

## Essential Decisions

- Distinguish a command, a current-value update, and a historical event. Select
  request/response, periodic updates, notifications or a combination by delivery
  requirements; do not make every waveform packet a reliable transaction.
- Choose flat commands or a dictionary by actual needs for parameter discovery,
  tooling and maintenance. State count and parameter count alone are not thresholds.
- Define framing, length scope, units, byte order and integrity checks where the
  chosen transport needs them; provide recomputable vectors. Use an existing
  protocol's encoding when applicable rather than inventing another wire format.
- A setting's effective value must be observable where needed; a shared config/status
  query can cover many settings. A distinct read opcode for every write is optional.
- Define repeated START/STOP and busy-time inputs. Parameters, retry counters and
  channel masks need ownership and bounds, but do not automatically need new modes.
- Immediate bounded operations can return their actual result directly. Add
  acceptance/progress/result tracking only for genuine asynchronous needs.
- Sending, accepting, completing and observing completion are different facts.
  Host timeout does not prove non-execution; non-idempotent retry needs a defensible
  deduplication or reconciliation contract. Do not turn a failed exchange directly
  into a claim that the hardware stopped or the device is offline.
- Define a bounded exit for each temporary wait, including recovery. Repeated BUSY,
  duplicate ACKs and heartbeats must not silently renew an operation's total budget.
- Decide which changes are permitted while measuring from product requirements:
  immediate, deferred to a controlled boundary, or rejected. Do not universally
  forbid or universally allow all parameter changes.
- Separate ordinary public status from internal transition detail. Expose internal
  phases for diagnostics when useful, without requiring the host to mirror them.
- Preserve released semantics. Plan required compatibility, but do not add unused
  runtime machinery solely for hypothetical future expansion.

## Read Only Relevant References

- Requirements, minimal start/stop, channel growth, state vs parameters →
  [requirements-and-growth.md](references/requirements-and-growth.md).
- Frame layout, LEN, CRC, field encoding and scaling →
  [frame-and-fields.md](references/frame-and-fields.md).
- Command organization, response mapping and error taxonomy →
  [command-space.md](references/command-space.md).
- State permissions, delivery semantics, retries, deadlines and disconnect →
  [state-and-timing.md](references/state-and-timing.md).
- Long operations, lost results, restart, deduplication and cancellation →
  [operation-lifecycle.md](references/operation-lifecycle.md).
- Version evolution, freezing and full-document review →
  [evolution-and-versioning.md](references/evolution-and-versioning.md).

## Output Scales With the Task

A simple design can be a short requirements statement, command/state table,
ownership, repeat/failure behavior, and focused verification examples. Mark
unresolved facts and implementation assumptions. Do not fill unrelated templates.

A full wire specification also defines topology, addressing if applicable, frame
layout and example bytes, per-command inputs and outputs, errors, timing, delivery
rules and compatibility. Use the full-document checklist in the versioning reference.

For a revision, lead with changed observable behavior and its impact. For a review,
give evidence locations, trigger sequence, risk, minimum correction and validation.
Separate declared behavior from implemented and tested behavior. Never claim that
a well-formed state diagram proves runtime liveness or hardware safety.
