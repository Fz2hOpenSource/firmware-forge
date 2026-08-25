# Test Strategy: What to Test, When

Answer "what verification does this change need?" before writing any test.

## Change-Type → Verification Mapping

| Change | Primary layer | Typical verification |
|---|---|---|
| Filter coefficients / calibration constants | L1 replay | Data replay regression against golden set with tolerance table |
| Algorithm structure (filter topology, state machine) | L1 unit + replay | Host unit tests for branches, replay for numeric behavior |
| Protocol parser | L1 unit | Frame-level host tests: valid, truncated, malformed, fuzzed inputs |
| DMA configuration (channel, burst, buffer) | L2 + L3 | Driver seam tests for setup sequence; integration for overflow/handoff |
| HAL / peripheral init code | L2 driver | Register write order via mock; error paths via stubs |
| RTOS task / priority / queue changes | L3 integration | Deadlock, starvation, backpressure policy checks |
| Linker script / memory placement | L1 logic + analysis | Map/mpu-check style static analysis plus L3 smoke |
| Compiler / toolchain version bump | full L1 + L3/L4 smoke | Existing suite green before anything else ships |
| PCB revision / component swap | L4 HIL subset | Re-run hardware acceptance checklist |
| Lifecycle loop changes (repeated init/cleanup, long-period tasks) | L2/L3 | Heap baseline regression: snapshot after cleanup must return to the recorded baseline |

## Standing Practices

- **New feature**: write L1 tests for pure logic first; identify the HIL gap
  early and record it instead of discovering it at release time.
- **Bug fix**: the regression test that reproduces the bug is written first
  and must fail (red), then the fix turns it green. No red — no proof the
  test bites. For hardware-nondeterministic failures where no deterministic
  repro exists, a recorded diagnostic run or captured HIL evidence may
  substitute; note the substitution explicitly in the test.
- **Risk ranking**: when time is short, rank candidates by
  `regression probability × blast radius × detection difficulty` and cover
  the top first.

## When NOT to Write a Test

- Trivial configuration constants with no logic.
- Generator internals get no fine-grained unit tests — but generated output
  still receives compile checks, configuration smoke tests, and integration
  coverage.
- One-shot diagnostic scripts.
- Numeric pipelines: prefer one data replay set over dozens of hand-picked
  input assertions — real recordings beat synthetic guesses.

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
