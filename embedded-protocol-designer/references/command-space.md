# Command Space Organization

## Partitioning

- Group commands into functional blocks with numeric stride for growth
  (for example 0x10 measurement control, 0x20 calibration, 0x30
  parameters) and leave gaps between blocks; renumbering commands after
  release is a breaking change.
- Separate write and read commands (a `0x30 set` / `0x31 read` pattern).
  Every mutable setting gets a read counterpart from day one — a
  setting that can only be written forces blind configuration and
  hides what the device actually stored.

## Response Mapping

- Define the response mapping as one rule plus explicit exceptions,
  published as a table. A common rule: response CMD = request CMD +
  0x80.
- Exceptions are listed, not implied: the dedicated error-response
  command, active-upload stream frames. A rule-plus-exceptions model
  scales; per-command improvisation does not.

## Command Space Architectures

Choose one of two architectures — or mix them per function class — and
state the choice in the protocol document:

**Flat Command Model (CMD + SubCMD)** — best for simple devices.
Grouped functions use `DATA = SubCMD (1 byte) + parameters`. An unknown
CMD or unknown SubCMD must return the unknown-command error code,
never silence; silence turns every host-side typo into a timeout retry
loop.

**Object Dictionary Model (Index + Sub-Index)** — best for scalable or
complex devices (CANopen / IO-Link style). The protocol keeps a small
set of basic verbs (Read / Write) aimed at a 16-bit Index identifying
a logical block and an 8-bit Sub-Index identifying one parameter
within it. This model obliges the document to publish the complete
Object Dictionary table; an entry is not defined until it carries:

- Index and Sub-Index;
- name, type, unit/scale;
- access mode (ro / rw / wo);
- valid range and default value;
- persistence behavior (volatile, flash-backed, factory-only).

Out-of-range or access-violating requests return a defined error code;
reserved index ranges are documented like any other value.

**Choosing.** Flat stays manageable up to roughly a couple dozen
parameters. Move to a dictionary when the parameter set outgrows a
flat listing, when generic configuration tools must browse parameters,
or when firmware updates migrate parameter layouts. Mixing is allowed
— control verbs often stay flat while tunable parameters live in the
dictionary — but every command declares which space it belongs to.

## Request/Response Pairing Rule

Every command documents BOTH its request frame and its response frame.
A command described only by its response cannot be implemented by a
host author without reverse engineering, and the gap surfaces late —
usually during integration of an independent implementation.

## Error Taxonomy

Define a cause-coded taxonomy at least this fine:

| Code | Meaning | Who fixes it |
|---|---|---|
| 0x00 | Success | — |
| 0x01 | Unknown command | Host |
| 0x02 | Parameter error | Host |
| 0x03 | State not allowed | Host (retry after state change) |
| 0x04 | Operation failed | Device / process |
| 0x05 | Storage (flash) failure | Device |
| 0x06 | CRC / frame error | Link or host |

The point of the third column: binary ok/fail hides which side must
act. Parameter-error versus state-not-allowed versus storage-failure
lead to completely different user actions.

## Production and Identity Commands

- Put factory operations in their own command block (device serial,
  hardware version).
- Declare field mutability explicitly: firmware version is decided by
  firmware and read-only; serial numbers and hardware revisions are
  factory-writable; nothing in production commands may touch
  measurement behavior.

## Streaming Data

- Streams get their own command number and a fixed layout, separate
  from request/response traffic.
- Include sequence numbers and/or timestamps so hosts can detect drops,
  reordering, and skew.
- Declare the transport model early (poll versus active upload):
  switching models later changes host architecture, not just a command.
