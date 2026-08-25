# Frame Format and Field Encoding

Frame-layer decisions are the most expensive to change after release:
every frame ever transmitted encodes them, and both sides must agree
byte for byte. Decide them deliberately before the first firmware
build, not during integration.

## Sync Header

- Prefer a 2-byte header whose byte pair is statistically unlikely
  inside payload data (alternating-bit patterns such as `AA 55` are a
  common choice; avoid 0x00-heavy pairs that collide with idle lines).
- State explicitly whether the header participates in the CRC. Constant
  bytes add no error-detection power; excluding them is common practice.
  Either choice works — an undocumented choice does not.

## Address Planning

- Allocate addresses as if more nodes will join. Reserve space and
  document it even when only one device exists today; retrofitting an
  address plan onto deployed hosts is a breaking change.
- If broadcast or multi-drop addressing might ever be needed, define it
  (or explicitly reserve it) before release.
- Keep routing identity (link address) separate from product identity
  (serial number, model); the latter lives in payload fields.

## LEN Semantics

- LEN counts DATA only. List the exclusions explicitly: header, ADDR,
  CMD, LEN itself, and CRC.
- Choose the LEN width from worst-case payload size before anything
  ships. One byte caps DATA at 255; widening it later rewrites every
  frame layout in the document.

## CRC Selection

- Prefer catalog algorithms over homemade ones. For example,
  CRC-16/MODBUS: polynomial 0xA001, init 0xFFFF, input reflected,
  output reflected, xorout 0x0000.
- Publish three things: full algorithm parameters, computation scope
  (which fields are covered), and one hand-verifiable worked example
  including wire byte order.
- Worked example (CRC-16/MODBUS): data bytes `01 10 01 01` produce
  CRC `0x4DC0`, sent low byte first as `C0 4D`; the full frame reads
  `AA 55 01 10 01 01 C0 4D`.
- The CRC byte order on the wire is where independent implementations
  diverge most often. The recomputable example exists to kill that
  ambiguity — without it, expect a debugging session over swapped
  bytes.

## Field Encoding

- Declare multi-byte field endianness once, globally.
- Prefer fixed-point scaling over float on the wire; state unit and
  scale per field (for example int32 in units of 0.001 mm).
- Enumerations must be exhaustive: list every valid value with its
  meaning, and state how receivers treat reserved or unknown values.
- For counters and timestamps: declare width, unit, wrap behavior, and
  epoch.

## Per-Field Table Discipline

Every frame layout ships a table: byte range, field name, type, and
unit/scale. If any field cannot be given a type-and-unit row, its
definition is not finished — do not publish around it.

## Robustness Decisions

Binary framing has four explicit decisions; each left implicit becomes an
integration bug:

- **Escaping / byte stuffing**: if payload can contain the header or
  terminator bytes, either define an escape scheme or publish a hard
  length bound that makes collisions impossible. State which mechanism
  the protocol uses.
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
