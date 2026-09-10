# Evolution and Version Governance

Protocol upgrades can fail because an unstated convention (LEN scope, CRC
byte order, response mapping, state gating, timing) was never written
down, so a later revision or a second implementation quietly assumes
something different.

## Draft Phase

- Mark tunable values (sampling rates, timeouts, thresholds, filter
  parameters) as pending-validation rather than silently changing them
  between drafts.
- Freeze only after validation evidence exists (measurement runs,
  interop tests). A draft that reaches firmware without a freeze clause
  will drift, and the drift will be discovered by a device that no
  longer matches its host.

## Freeze Contract

Within a supported compatibility line, preserve command meanings, layouts, units,
defaults, enum values, timing promises and repeated/failure behavior. New features
may use reserved commands or a declared extension mechanism; adding a field or enum
is compatible only when old receivers are specified and tested to handle it.

Deprecation is documentation/capability metadata while old behavior remains supported.
Replacing a working command with an error is a breaking change, not deprecation.
Do not reuse its identifier for another meaning.

Classify versions by observable compatibility, not edit size. A parameter/default
or timeout tweak can break a host; a new command may be additive if old peers can
avoid it. Incompatible changes need a separate negotiated version or an explicit
migration boundary. Check supported old-host/new-device and new-host/old-device
pairs, including unknown commands/fields/enums and asynchronous result semantics.
Add capability discovery only when peers need it; fixed paired releases may use a
documented version pairing instead.

## Changelog Discipline

Describe the changed observable behavior, compatibility impact and relevant
verification against the previous version. A small additive change needs a small
delta, not a repeated inventory of all unchanged protocol content.

## Recurring Wounds and Their Rules

| Wound | Rule it produces |
|---|---|
| Single-device assumption broken when a second node appears | Confirm topology first; reserve addresses for required expansion or explicitly document migration cost |
| Polled stream later switched to active upload | Declare transport model early; note migration cost |
| ok/fail-only statuses | Cause-coded error taxonomy |
| No state gating | State × command permission matrix |
| Command documented only by its response | Request AND response frames mandatory |
| Missing timeout contract | Deadline, semantic retry policy and separate reachability/outcome verdicts |
| Ambiguous CRC byte order | Recomputable worked-example obligation |
| Informal edits between revisions | Freeze contract + changelog discipline |
| Standalone device died silently, nobody noticed | Define expected-contact/freshness rules; add heartbeat only when existing traffic is insufficient |
| Flat command space outgrew into a pseudo-dictionary | Choose flat/dictionary by actual discovery and maintenance needs |

Assess each convention against actual product requirements; do not prebuild
unneeded features merely to avoid every hypothetical migration.

## Document Audit Checklist

Use these questions for a full wire-protocol review, marking genuinely inapplicable
items with a reason. For a local extension review only changed and dependent contracts.
Rank applicable gaps by integration risk (a missing response mapping breaks
every host; a missing example breaks one CRC):

1. System architecture and addressing/expansion decision appropriate to topology?
2. Frame format with LEN exclusions and full CRC parameters?
3. At least one recomputable full-frame byte example?
4. Command-space architecture declared (flat / object dictionary / mixed)?
5. Command table with number, name, direction?
6. Response mapping rule plus explicit exceptions?
7. Request/response commands have both frames, with explicit exceptions for streams and no-reply operations?
8. Device state machine with per-state permission matrix?
9. Initiation model stated, with heartbeat/liveness rules for unpolled
   operation?
10. Timeout / semantic retry / uncertain outcome / reachability contract, with separate stream freshness?
11. Complete cause-coded error table?
12. Version and freeze clauses?

## Interface With Verification

Each frozen version ships golden frame fixtures — encode/decode vector
pairs captured in the document or alongside it. The embedded-test-
engineer skill turns these into host-level parser regression tests, so
an implementation change that breaks wire compatibility fails a test
instead of failing a customer. Version the fixtures together with the
protocol document.
