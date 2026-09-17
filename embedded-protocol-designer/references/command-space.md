# Command Space Organization

## Partitioning

- Group commands into functional blocks with numeric stride for growth
  (for example 0x10 measurement control, 0x20 calibration, 0x30
  parameters) and leave gaps between blocks; renumbering commands after
  release is a breaking change.
- Make effective settings observable where integration needs readback. Separate
  read/write opcodes, a common config query, or dictionary access are possible;
  do not require one extra command per setting. Specify whether a returned value
  is requested, applied or observed, and its validity when those differ.

## Configuration Completion

If saving, applying and obtaining a new result can finish separately, define which
stage the response acknowledges and how the remaining outcome is observed. A
successful save does not imply that hardware is using it or that new valid data
exists. Specify the visible result when persistence succeeds but application fails,
and when application succeeds but output is still warming up. Existing queries and
validity/revision fields may suffice; do not require three new commands or an
asynchronous operation ledger for a synchronous setting.

Readback must identify whether it reports stored settings, applied settings or
measured output. A configuration revision attached to a result denotes what produced it,
not merely the newest saved revision. Partial-update field rules belong in
[frame-and-fields.md](frame-and-fields.md#structured-configuration-updates).

## Response Mapping

- Define the response mapping as one rule plus explicit exceptions,
  published as a table. A common rule: response CMD = request CMD +
  0x80, only if the request range, width and reserved values prevent overflow
  and collisions with responses, errors and unsolicited streams.
- Exceptions are listed, not implied: the dedicated error-response
  command, active-upload stream frames. A rule-plus-exceptions model
  scales; per-command improvisation does not.

## Command Space Architectures

Choose one of two architectures — or mix them per function class — and
state the choice in the protocol document:

**Flat Command Model (CMD + SubCMD)** — best for simple devices.
Grouped functions can use `DATA = SubCMD + parameters` with a declared SubCMD
width. A valid addressed unicast request with unknown CMD/SubCMD returns the
defined error when replies are legal. Broadcasts, streams and corrupt frames
follow explicit no-reply/discard rules rather than this request/response rule.

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

**Choosing.** Keep flat commands while they remain clear. Consider a dictionary
when generic tools must discover parameters or measured maintenance needs justify
it; parameter count alone is not an upgrade threshold. Mixing is allowed
— control verbs often stay flat while tunable parameters live in the
dictionary — but every command declares which space it belongs to.

## Request/Response Pairing Rule

Every request/response command documents BOTH its request frame and its response frame.
Explicit no-reply operations, broadcasts and stream events document their own
delivery and observation rules instead of inventing unsafe replies.
A command described only by its response cannot be implemented by a
host author without reverse engineering, and the gap surfaces late —
usually during integration of an independent implementation.

## Error Taxonomy

Define only errors the product can emit, with actionable meanings. The following
codes are illustrative, not a mandatory minimum or a reason to add storage/CRC
replies. State-not-allowed does not authorize automatic retries:

| Code | Meaning | Who fixes it |
|---|---|---|
| 0x00 | Success | — |
| 0x01 | Unknown command | Host |
| 0x02 | Parameter error | Host |
| 0x03 | State not allowed | Host (inspect current state and operation policy) |
| 0x04 | Operation failed | Device / process |
| 0x05 | Storage (flash) failure | Device |
| 0x06 | CRC / frame error | Link or host |

The point of the third column: binary ok/fail hides which side must
act. Parameter-error versus state-not-allowed versus storage-failure
lead to completely different user actions.

An error response describes this request's outcome. Do not substitute a stale
global last-error value; historical diagnostics and current rejection reasons have
different lifetimes even if they use the same error codes.

## Production and Identity Commands

- Put factory operations in their own command block (device serial,
  hardware version).
- Declare identity mutability, access policy and persistence from manufacturing
  requirements; serial/hardware identity may be immutable or provisionable.
  Factory calibration can affect measurements: specify its allowed operating
  conditions, application boundary and invalidation of old data. Do not infer
  either write permission or absence of measurement effects from the command block.

## Streaming Data

- Streams get their own command number and a fixed layout, separate
  from request/response traffic.
- Include sequence numbers and/or timestamps so hosts can detect drops,
  reordering, and skew.
- Declare the transport model early (poll versus active upload):
  switching models later changes host architecture, not just a command.
