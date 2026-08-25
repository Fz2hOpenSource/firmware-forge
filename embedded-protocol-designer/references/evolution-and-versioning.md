# Evolution and Version Governance

Protocols break during upgrades more often than in initial design. The
failure pattern is consistent: an unstated convention (LEN scope, CRC
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

After freeze:

- Never redefine an existing CMD's meaning, a field's layout, a scale
  factor, or an enumeration value.
- Additive changes only: new features take new CMD/SubCMD values from
  reserved ranges.
- Deprecate instead of reuse: mark the old value obsolete, keep parsing
  it, and return a deprecation-aware error where possible.
- Version increments follow declared rules, for example:
  - parameter tweaks within the existing model → minor;
  - new capability via new commands → minor;
  - frame layout, measurement model, or semantic changes → major.

## Changelog Discipline

Every revision begins with an explicit delta statement against the
previous version: corrected items, added items, kept items. The kept
list matters as much as the changes — it tells implementers what is
safe to build against without re-reading the whole document.

## Recurring Wounds and Their Rules

| Wound | Rule it produces |
|---|---|
| Single-device assumption broken when a second node appears | Plan address space on day one |
| Polled stream later switched to active upload | Declare transport model early; note migration cost |
| ok/fail-only statuses | Cause-coded error taxonomy |
| No state gating | State × command permission matrix |
| Command documented only by its response | Request AND response frames mandatory |
| Missing timeout contract | Deadline / retry cap / offline verdict |
| Ambiguous CRC byte order | Recomputable worked-example obligation |
| Informal edits between revisions | Freeze contract + changelog discipline |
| Standalone device died silently, nobody noticed | Liveness/heartbeat obligation for unpolled devices |
| Flat command space outgrew into a pseudo-dictionary | Declare command-space architecture (flat vs object dictionary) by expected parameter count |

Each rule is cheap on day one; each wound is a fielded-device recall
risk if discovered after release.

## Document Audit Checklist

Review any protocol document against these questions. Each "no" is a
gap; rank gaps by integration risk (a missing response mapping breaks
every host; a missing example breaks one CRC):

1. System architecture and address allocation with reserved space?
2. Frame format with LEN exclusions and full CRC parameters?
3. At least one recomputable full-frame byte example?
4. Command-space architecture declared (flat / object dictionary / mixed)?
5. Command table with number, name, direction?
6. Response mapping rule plus explicit exceptions?
7. Every command carries request AND response frames with typed fields?
8. Device state machine with per-state permission matrix?
9. Initiation model stated, with heartbeat/liveness rules for unpolled
   operation?
10. Timeout / retry / offline contract with stream exemption?
11. Complete cause-coded error table?
12. Version and freeze clauses?

## Interface With Verification

Each frozen version ships golden frame fixtures — encode/decode vector
pairs captured in the document or alongside it. The embedded-test-
engineer skill turns these into host-level parser regression tests, so
an implementation change that breaks wire compatibility fails a test
instead of failing a customer. Version the fixtures together with the
protocol document.
