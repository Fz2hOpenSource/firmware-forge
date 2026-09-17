# Frame Format and Field Encoding

Frame-layer decisions are the most expensive to change after release:
every frame ever transmitted encodes them, and both sides must agree
byte for byte. Decide them deliberately before the first firmware
build, not during integration.

## Sync Header

- Choose framing appropriate to the transport. A byte-stream protocol may use
  a fixed marker such as `AA 55`; do not assume any marker is absent from arbitrary
  binary payload. Frame-oriented transports may already supply boundaries.
- State whether the header participates in the CRC and how header corruption is
  detected/rejected. Do not infer integrity properties merely from a constant value.

## Address Planning

- Decide addressing from current topology and agreed expansion requirements.
  Multi-drop needs a defined address plan. A point-to-point protocol may omit an
  address; document that future multi-drop may require a versioned migration.
- Reserve addressing/broadcast space for required expansion, not every imaginable
  topology. Keep reserved values distinguishable from currently supported behavior.
- Keep routing identity (link address) separate from product identity
  (serial number, model); the latter lives in payload fields.

## LEN Semantics

- Choose one LEN definition: DATA-only, remaining-frame or total-frame. State
  exactly which fields it includes/excludes and verify it in an example. Preserve
  existing published semantics rather than imposing DATA-only on every protocol.
- Choose the LEN width from worst-case payload size before anything
  ships. One byte represents at most 255 in the chosen LEN scope (DATA-only
  can carry 255 data bytes; a total-length scope allows fewer); widening it rewrites the
  frame layout in the document.

## CRC Selection

- Prefer catalog algorithms over homemade ones. For example,
  CRC-16/MODBUS: canonical polynomial 0x8005 (reflected implementation
  polynomial 0xA001), init 0xFFFF, input reflected,
  output reflected, xorout 0x0000.
- Publish three things: full algorithm parameters, computation scope
  (which fields are covered), and one hand-verifiable worked example
  including wire byte order.
- Worked example (CRC-16/MODBUS): data bytes `01 10 01 01` produce
  CRC `0x4DC0`, sent low byte first as `C0 4D`; the full frame reads
  `AA 55 01 10 01 01 C0 4D`. This illustrative layout is header `AA 55`
  (excluded from CRC), address `01`, command `10`, one-byte DATA length `01`,
  DATA `01`, CRC `C0 4D`. CRC covers address through DATA; this is not a
  mandated product layout.
- Parameter naming follows the [CRC catalogue](https://reveng.sourceforge.io/crc-catalogue/16.htm#crc.cat.crc-16-modbus);
  distinguish a canonical polynomial from its reflected implementation constant.
- The CRC byte order on the wire is where independent implementations
  diverge most often. The recomputable example exists to kill that
  ambiguity — without it, expect a debugging session over swapped
  bytes.

## Field Encoding

- Declare multi-byte field endianness once, globally.
- Choose integer/scaled fixed-point or a precisely specified floating format
  from range, precision and compatibility needs. State units and scale (for
  example int32 in 0.001 mm), or IEEE 754 width, byte order and NaN/Inf policy.
  Preserve an existing adequate encoding instead of converting it by default.
- Enumerations must be exhaustive: list every valid value with its
  meaning, and state how receivers treat reserved or unknown values.
- For counters and timestamps: declare width, unit, wrap behavior, and
  epoch.

## Per-Field Table Discipline

For structured configuration updates, also use the update contract below; a type
table alone does not define omission, clearing or merge behavior.

Every frame layout ships a table: byte range, field name, type, and
unit/scale. If any field cannot be given a type-and-unit row, its
definition is not finished — do not publish around it.

## Structured Configuration Updates

When commands accept optional fields or partial objects, first recover the existing
published semantics and compare all relevant save/update entry points. Do not
impose "omitted means retain" on a replacement command or silently change released
behavior. Define only input forms the encoding supports:

| Input | Required decision |
|---|---|
| Field absent | Retain, default, or reject as required |
| Valid value present | Which fields change and when the value becomes effective |
| Empty array/string or null | Clear, special value, or reject; do not conflate them with absence |
| Wrong type or out-of-range value | Reject whole request, or explicitly report defined partial handling |
| Part of a nested object | Merge members or replace object; treatment of absent members |

Specify revision behavior for a change, a no-op and a rejected request. Equivalent
entry points must honor the same declared update semantics; intentional differences
must be visible in their contracts. Validate response plus changed-field readback,
preservation of untouched fields, and revision behavior, not ACK alone.

## Robustness Decisions

Binary framing has four explicit decisions; each left implicit becomes an
integration bug:

- **Boundary recognition**: choose escaping, a validated length-delimited parser,
  or transport-provided framing. A maximum length bounds memory and waiting but
  does not prevent marker bytes inside payload. State how partial/corrupt frames
  time out and how resynchronization distinguishes candidate from valid frames.
- **Maximum frame length**: publish a hard upper bound (header + addr +
  cmd + len + data + crc). Receivers use it to size buffers and reject
  oversized frames deterministically instead of hanging.
- **Desync recovery**: after garbage or a corrupted frame, define how the
  receiver resynchronizes — typically scan forward for the next valid
  header and re-validate via LEN and CRC before trusting any frame.
- **CRC-error frames**: decide whether the receiver responds. Common
  practice is silent drop plus an error counter — replying to a corrupt
  address may hit the wrong node on multi-drop buses. Count CRC errors
  in diagnostics either way.
