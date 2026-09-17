# Test Strategy: What to Test, When

Answer "what verification does this change need?" before writing any test.

## Change-Type → Verification Mapping

| Change | Primary layer | Typical verification |
|---|---|---|
| Filter coefficients / calibration constants | L1 replay | Data replay regression against golden set with tolerance table |
| Algorithm structure (filter topology, state machine) | L1 unit + replay | Host unit tests for branches, replay for numeric behavior |
| Protocol parser | L1 unit | Frame-level host tests: valid, truncated, malformed, fuzzed inputs |
| Protocol operation/state behavior | L1 sequences + relevant L3/L4 | Repeated commands, lost results, late completion, timeout/recovery budgets and resource ownership |
| DMA configuration (channel, burst, buffer) | L2 + relevant L3/L4 | Seams check intended setup; target stress verifies actual DMA access, cache and handoff timing |
| HAL / peripheral init code | L2 driver | Register write order via mock; error paths via stubs |
| RTOS task / priority / queue changes | L3 integration | Deadlock, starvation, backpressure policy checks |
| Linker script / memory placement | Static analysis + relevant L4 | Map/MPU layout checks, then target DMA/cache smoke when placement affects hardware |
| Compiler / toolchain version bump | full L1 + L3/L4 smoke | Existing suite green before anything else ships |
| PCB revision / component swap | L4 HIL subset | Re-run hardware acceptance checklist |
| Lifecycle loop changes (repeated init/cleanup, long-period tasks) | L2/L3 | Heap baseline regression: snapshot after cleanup must return to the recorded baseline |

## Standing Practices

- **New feature**: write L1 tests for pure logic first; identify the HIL gap
  early and record it instead of discovering it at release time.
  First establish expected behavior from current requirements. Skip mechanisms
  the feature does not contain; do not invent concurrency or asynchronous state
  merely to fit a test template.
- **Bug fix**: when feasible, reproduce the failure on the old implementation
  and confirm the correction passes the same test. A test written later can be
  checked against the old version in isolation. For nondeterministic hardware
  failures, retain captured diagnostic/HIL evidence and state the reproduction gap;
  absence of a red test must not become a claim that the bug was proven fixed.
- **Risk ranking**: when time is short, rank candidates by
  `regression probability × blast radius × detection difficulty` and cover
  the top first.

## Check That a Regression Test Can Discriminate

For a critical regression, establish the state in which the promised behavior is
observable before triggering the change. For example, "reapplying unchanged
configuration preserves filter output" needs a warmed, valid output first; two
successful apply calls immediately after initialization do not test continuity.
Assert the visible validity, continuity or value contract, not just a success code.

Confirm fault injection reaches the intended path and that the observation window
includes its consequence. When feasible, make one targeted countercheck in an
isolated test copy: restore the old defect (such as an unnecessary reset) and verify
that this test fails for the intended reason. Initialization failure, an unrelated
crash or a build failure is not that evidence. Record the gap when this check cannot
be run; full mutation testing is not required for every small patch.

## Changes With Multiple Consumers

For public availability or validity changes, select affected status, one-shot read,
single/mixed stream and recovery paths, including different value kinds. Test each
against its contract: raw input may be allowed while engineering values are not.
Include binding/configuration changes that leave numeric parameters unchanged,
stale cached results and current-request error reasons where those paths exist.

For partial updates, select absent, valid, empty/null, wrong-type, out-of-range and
nested-partial inputs supported by the protocol. Assert response, changed-field
readback, contracted treatment of omitted fields and revision behavior across relevant update
entry points. Derive expected values from the declared merge/replacement contract,
independently of each implementation. An observed divergence should fail the test
unless a specification or approved change permits it; characterization of current
behavior is not acceptance of that behavior. Do not impose retain-on-omission on
an explicitly specified replacement command. Where persistence and live application
differ, exercise save success/apply failure and apply success/no fresh result yet;
do not let one successful stage stand for all three.

## Keep Verification Proportional

Skip dedicated tests for reversible low-impact edits with no meaningful regression
risk. File type is not the criterion: a timeout constant, DMA flag or generator
can change safety or timing behavior and need targeted validation. Check generated
output and the failure-prone generator logic when applicable. Combine recorded
replay with synthetic numeric boundaries; neither covers all risks alone.

## Interface With arm-cortex-expert

That skill's non-negotiable boundaries map directly to concrete tests:

| Architecture boundary (arm-cortex-expert) | Verification (this skill) |
|---|---|
| Overflow/drop counters must exist | L2/L3: force overflow, assert counter increments and data policy holds |
| Explicit DMA buffer ownership | L2: assert handoff order; no consumer reads during fill window |
| DMA error callbacks required | L2: inject error, assert callback fires once and recovery runs |
| ISR stays short | L4: measure ISR duration; not provable on host |
| Bounds checks on packet/ring indexes | L1: boundary-value cases at exactly 0, 1, n-1, n |

If a boundary cannot be verified at the intended layer, escalate the gap to
the architecture skill rather than silently dropping it.
