---
name: embedded-protocol-designer
description: >
  Design and review embedded device communication protocols for
  RS-485 / UART / CAN / USB-bridged device-to-host links: binary frame
  formats (header, address, LEN semantics, CRC with worked examples),
  command-space organization (flat CMD/SubCMD vs object dictionary),
  response mapping and cause-coded error taxonomy, device state machines
  with per-state command permissions, timeout/retry/offline contracts,
  and version-freeze compatibility governance.

  Use when authoring or auditing a protocol document, adding commands
  without breaking hosts, or planning a backward-compatible upgrade.
  Do not use for firmware implementation behind the link (use
  arm-cortex-expert), parser test design (use embedded-test-engineer),
  or the RS-485 electrical layer.

  Examples: "给采集盒定一版 RS485 协议", "评审这版协议文档缺什么",
  "RUNNING 状态该禁止哪些命令", "加一个新命令怎么不破坏旧上位机",
  "超时和重传怎么定", "这个协议怎么冻结版本", "参数用对象字典还是扁平命令",
  "独立设备主动上报怎么做心跳", "audit this protocol draft".
---

# Embedded Protocol Designer

A protocol document is an interface contract between a device and every
host that will ever talk to it — including hosts that do not exist yet.
This skill turns recurring protocol-evolution failures into upfront
design rules. Its core claim: most protocol rework comes not from wrong
commands but from unstated conventions (LEN scope, CRC byte order,
response mapping, state permissions, timing), which are cheap to fix on
day one and expensive to discover during integration.

## Scope Boundary

This skill handles:

- Frame format decisions: header, address, LEN semantics, CRC selection,
  field encoding, fixed-point scaling, byte order
- Command-space organization: write/read separation, SubCMD structure,
  response mapping rules, dedicated error channels
- Device state machines and per-state command permission matrices
- Link timing contracts: response deadline, retry policy, offline verdict
- Version governance: freeze rules, additive-change discipline,
  changelog requirements
- Completeness review of a protocol document

It does not handle firmware driver implementation behind the link, the
physical/electrical layer, or verification strategy for the resulting
parser code (that is embedded-test-engineer's L1 layer).

## Interaction Rule

Never produce a full protocol design before the physical and
architectural constraints are confirmed. Unless the prompt states them
explicitly, begin by asking the user to clarify, at minimum:

- bus topology (bus versus point-to-point, maximum node count);
- initiation model (master/slave polled, peer-to-peer, or event-driven
  standalone);
- data volume expectations (upload rates, payload sizes).

The checklist in `Required Facts Before Design` below is the full
question set. Design-altering unknowns (topology, initiation model,
data volume) must be resolved first — ask, don't guess. For remaining
low-risk gaps, proceed with an assumption-based draft immediately and
collect every assumption into a pending-confirmation block at the top
of the output, never silently baked in.

## Typical Triggers

- "给采集盒定一版 RS485 协议"
- "评审这版协议文档缺什么" / "audit this protocol draft"
- "RUNNING 状态该禁止哪些命令"
- "加一个新命令怎么不破坏旧上位机"
- "超时和重传怎么定" / "这个协议怎么冻结版本"

## Composability

- If the repository has an `AGENTS.md`, follow it first.
- Division of responsibility with `arm-cortex-expert`: that skill owns
  how firmware implements the link (UART/DMA paths, ISR callbacks,
  buffer ownership); this skill owns the wire contract those drivers
  serve. If an implementation constraint conflicts with a published
  protocol rule, raise the conflict — never silently reinterpret the
  document on one side.
- Division with `embedded-test-engineer`: every frozen protocol version
  should ship golden frame fixtures (encode/decode vectors). That skill
  turns them into host-level parser regression tests.
- Protocol documents are project evidence: under this skill's own
  Source Priority they rank above these references.

## Source Priority

Prefer evidence in this order:

1. Existing protocol documents in the project, bus captures / logic
   analyzer dumps, and the host/device code that implements them.
2. Link constraints from the project: bus topology, node count,
   half/full duplex, single/multi master, payload sizes, streaming
   requirements.
3. Local references in `references/`.
4. Industry conventions (Modbus RTU framing practice, catalog CRC
   algorithms).

State when a conclusion is convention rather than grounded in project
artifacts.

## Design Principles

Each rule requires a decision to be made AND recorded — most allow several
valid answers; what breaks integrations is an undocumented one:

- Address plan: decide whether the link needs node addresses. Multi-drop
  or expansion-likely links must reserve address space on day one
  (retrofitting is breaking); pure point-to-point links may omit the
  address field, but record that choice in the document.
- Frame shape: declare one primary frame layout and keep per-command
  deviations explicit and minimal. Undocumented per-command layouts are
  what break host implementations.
- LEN semantics: choose a definition (DATA-only / remaining-frame /
  total-frame), state exactly what it includes and excludes, and back it
  with one verifiable example frame. Any definition works if it is unique
  and testable.
- CRC: prefer standard catalog algorithms; publish full parameters,
  computation scope, and one hand-verifiable worked example including
  wire byte order. Byte order is where independent implementations
  diverge.
- Separate write and read commands. Every mutable setting gets a read
  counterpart from day one.
- Define the response mapping as a rule (for example response CMD =
  request CMD + 0x80) plus its explicit exceptions (error channel,
  active-upload streams).
- Give every command BOTH a request frame and a response frame. A
  command documented only by its response cannot be implemented by a
  host.
- Error codes must distinguish causes: unknown command, invalid
  parameter, state-not-allowed, operation failed, storage failure,
  CRC error. Binary ok/fail hides which side must act.
- Define the device state machine and gate commands per state. Denied
  commands return the state-not-allowed code, never silence.
  Typical invariant: no parameter, factory-config, or calibration
  mutation while measuring.
- Timing: derive deadlines from measurable quantities (baud rate, max
  frame length, device processing time, bus scheduling, margin) rather
  than picking constants; publish the derivation and the resulting
  numbers (a 500 ms deadline with a 3-retry cap is a common starting
  point for low-speed UART links). Streams are exempt from the
  request/response deadline but get their own liveness rule.
- Declare units, type, and fixed-point scale on every field
  (for example int32 in 0.001 mm). Never put float on the wire without
  an explicit endianness decision.
- Freeze before release: after freeze, never redefine an existing CMD's
  meaning or a field's layout. New features take new CMD/SubCMD values.

## Read Order

Read only what the task needs; do not bulk-load references:

- Frame layout, LEN/CRC/encoding/scaling decisions →
  `references/frame-and-fields.md`
- Command organization, response rules, error taxonomy →
  `references/command-space.md`
- State machine, permission matrix, timeout/retry/offline →
  `references/state-and-timing.md`
- Upgrading, freezing, changelog discipline, document audit checklist →
  `references/evolution-and-versioning.md`

## Output Contract

When authoring a protocol document, the deliverable must contain all of
the following; when reviewing, check against the same list and report
gaps ranked by integration risk, each with the concrete fix:

1. System architecture and address allocation (including reserved space).
2. Frame format with LEN boundary definition, CRC parameters and
   computation scope, plus at least one recomputable example frame.
3. Command-space architecture declaration: flat command model, object
   dictionary model, or mixed — with each command's ownership stated.
4. Command table with number, name, and direction (object dictionaries:
   the complete dictionary table instead).
5. Response mapping rule and dedicated error channel.
6. Per-command request AND response frames with field tables
   (name, type, unit/scale).
7. Device-side action semantics per command.
8. Device state machine and per-state allowed/denied command matrix.
9. Initiation model (master-slave polled / event-driven standalone /
   hybrid) and, for unpolled operation, the liveness/heartbeat rules.
10. Timeout, retry, and offline-detection rules, with stream exemption.
11. Complete error-code table.
12. Version and freeze clauses (what may change, what may not).

For patch-style revisions to an existing document, output an explicit
delta statement first: corrected items, added items, kept items.

## Required Facts Before Design

The Interaction Rule makes this checklist mandatory before any full
protocol design is produced. Ask only for facts that change the design:

- Physical link and topology: bus versus point-to-point; maximum node
  count.
- Initiation model: master/slave polled, peer-to-peer, or event-driven
  standalone upload.
- Data volume expectations: streamed versus polled data, upload rates,
  typical and worst-case payload size (the upper bound decides LEN
  width before anything ships).
- Identity assignment: who sets serial numbers and hardware versions.
- Which settings persist across power cycles.

If the user explicitly opts for an assumption-based draft, proceed —
but collect every assumption into the pending-confirmation block at
the top of the output instead of baking them in silently.
