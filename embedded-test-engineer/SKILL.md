---
name: embedded-test-engineer
description: >
  Design and implement firmware verification strategies: host-based unit
  testing, seams and test doubles, measurement data replay regression,
  driver isolation, integration test design, timing validation strategy,
  protocol event-sequence and bounded-recovery tests, and hardware-in-loop coverage
  planning for Cortex-M / STM32 projects.

  Use for: deciding what to test and at which pyramid layer, isolating
  logic from HAL for host builds, choosing stub/fake/mock, building
  golden-data replay for measurement pipelines (ADC/filter/calibration),
  defining numeric tolerance rules, assessing numeric regressions and
  accuracy evidence, planning HIL coverage.

  Do not use for: PCB electrical testing, oscilloscope methodology, EMC,
  mechanical testing, or feature code unrelated to verification.

  Examples: "为标定算法建回放回归测试", "这个协议状态机能不能在 PC 上测",
  "FFF 还是 CMock", "改了滤波器如何证明精度没退化", "plan HIL coverage".
---

# Embedded Test Engineer

Verify the behavior the current requirements promise, at the lowest useful cost.
Use `arm-cortex-expert` when platform implementation questions need it, and
`embedded-protocol-designer` when interaction semantics need defining. Do not load
all companions or build a full test framework for every small change. This skill
remains usable alone with explicit architecture assumptions and hardware gaps.

## Scope Boundary

This skill handles:

- Verification strategy across the test pyramid (unit / driver / integration / hardware)
- Host-based unit testing design and seams isolation
- Test double selection (stub / fake / mock) and anti-overmocking discipline
- Measurement data replay regression with tolerance policy
- Timing validation strategy and HIL coverage planning

It may plan WHEN hardware verification is required and what it must show;
it does not perform electrical measurement methodology itself. Board-level
electrical testing, oscilloscope procedures, EMC, and mechanical testing
are out of scope.

## Composability

- If the repository has an `AGENTS.md`, follow it first.
- Division of responsibility with `arm-cortex-expert`: that skill owns
  architecture facts (DMA buffer ownership, ISR rules, error counters,
  memory placement); this skill turns them into verification (overflow
  must trigger, buffer handoff must be asserted, drop counters must
  increment). If a verification target conflicts with an architecture
  rule, preserve the conflicting evidence and resolve it against user/project
  requirements and applicable hardware specifications. Neither skill wording nor
  a passing test may silently override those sources.
- Keep outputs compatible with other active skills.

## Source Priority

Prefer evidence in this order:

1. Current user requirements and applicable project instructions.
2. Product, algorithm, driver or protocol acceptance criteria relevant to the task, and applicable hardware specifications.
3. Implementation evidence: sources, build/link options, measurements and existing tests.
4. Skill references and general testing practice.

Requirements define expected behavior; code and tests reveal current behavior.
Preserve and resolve discrepancies rather than treating a passing old test as the
specification. Reuse the existing test infrastructure where suitable.

State when a conclusion is general practice rather than grounded in the
project's artifacts.

## Test Pyramid

Use the lowest-cost validation layer first; escalate only with a stated
trigger:

1. **L1 Host Unit Test** — algorithms, state machines, protocol parsing,
   calibration math. Runs on PC in milliseconds.
2. **L2 Driver Test** — HAL wrappers, SPI/I2C/UART behavior through seams,
   error handling paths.
3. **L3 Integration & Simulation** — RTOS task interaction, DMA pipeline,
   communication stacks; deterministic simulators where available.
4. **L4 Hardware Test (HIL)** — real timing, electrical behavior,
   peripheral correctness, precision against standard sources.

## Coverage Philosophy

Confirm the test objective from the request, existing requirements and observed
regression. A test or replay task does not require restarting product or protocol
design. For local changes, test affected behavior and dependencies: numeric
accuracy and alignment for algorithms, error paths and resource handling for
drivers, or event sequences for asynchronous operations. Use protocol references
and graph tooling only for relevant interaction/state risks. Add test machinery
only when it protects a concrete risk.

Prioritize failure-risk coverage over code-coverage percentage:

1. Failure risk coverage (what can regress and hurt)
2. Boundary condition coverage (range edges, saturation, timeouts, empty/full)
3. Requirement coverage (what the spec promises)

Do not chase 100% line coverage. A fully covered ADC driver with a wrong
sampling sequence still fails on hardware.

## Test Double Rules

- **Stub**: only input values or state triggers are needed.
- **Fake**: a simplified working model is enough (RAM-backed Flash).
- **Mock**: interaction order and argument details matter.

Hard rules:

- Do not mock everything. Prefer real implementations when behavior is
  simple or integration is cheap.
- Delete mocks whose maintenance cost exceeds their protective value.
- A test that only validates mocks is invalid.

## Measurement Data Replay

For measurement pipelines verify the whole chain:
`raw → filter → calibration → compensation → result`.

- Record from the earliest stable boundary available — raw codes plus
  metadata headers, preferred over pre-computed engineering values. When
  earlier stages cannot be captured, replay from the first stable
  boundary and document the uncovered upstream stages explicitly.
- Golden sets cover the operating envelope, not just happy-path data.
- Tolerance policy is defined before test code is written.
- Golden updates need a justified expected-behavior change and old/new comparison,
  with approval under the project's policy (including existing authorization).
  A matching baseline shows regression fidelity; accuracy needs a traceable reference.
  Never rewrite expectations solely to turn a failure green.

See `references/data-replay.md`.

## Timing vs Functional

A passing unit test does not prove interrupt latency, DMA jitter, cache
behavior, or peripheral timing. Those belong to L3 simulation or L4 HIL,
and any timing claim must state its measurement means (DWT cycle counter,
timer capture, trace).

## Protocol State Verification

Byte-level golden frames verify encoding, not interaction recovery. When commands
span events, test real state logic with virtual time and reproducible event sequences:
lost completion, duplicate requests, old epochs, cancellation races, full queues and
recovery that also fails. Select only scenarios supported by current mechanisms.
Read [protocol-state-testing.md](references/protocol-state-testing.md).

For an explicit finite transition model, the optional standard-library Python 3.10+
tool checks missing timeout exits, terminal reversal and timeout recovery cycles:

```text
python <this-skill>/scripts/check_state_model.py <model.json> --json
```

Read [state-model-format.md](references/state-model-format.md) before extracting a
model from source. Resolve paths from this loaded skill directory. A graph pass is
not a firmware, guard, scheduler or safety proof; never add fictional edges to pass.
Use optional `--strict` when a gate must also stop on unresolved warnings; read the
exit code or `gate_status`, since `status` retains the structural-error verdict.
The tool's own tests live in `tests/test_state_model.py`; they do not test the device.

## Directory Convention

```text
project/
├── ...firmware sources...
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── fixtures/
│   └── data/            # recorded replay streams + golden sets
└── hardware_tests/
```

Precondition: business logic contains no direct register access — that
layering is owned by `arm-cortex-expert`. Legacy modules that violate it
are still verifiable: start with characterization tests at their current
boundary and introduce seams incrementally instead of blocking all
verification.

## Tool Selection

Stay tool-neutral. Choose by: existing build system > team language >
dependency weight. See `references/frameworks.md` for the comparison
matrix and the MDK + CMake dual-build approach.

## Output Contract

Scale the proposal to the change; a small case can express the following in a few
sentences rather than a full document:

1. Test objective
2. Risk being protected (what regression this prevents)
3. Test boundary (what is inside/outside the test)
4. Test implementation (files, framework, doubles used)
5. Expected result (with numeric tolerances when applicable)
6. Remaining hardware gap (what still needs L4)

Replay-type proposals additionally output the tolerance table and the
baseline version they compare against.

## When Information Is Missing

Ask only for facts that change the design:

- Can the current build system produce host binaries?
- Is there an existing preferred framework?
- Are measurement-chain metadata (gain, rate, temperature) actually recorded?

If reasonable assumptions suffice, state them and continue.

## Read Order

Read only what the task needs; do not bulk-load references:

- What should be tested for this change? → `references/test-strategy.md`
- Choosing/using seams and doubles → `references/test-doubles.md`
- Framework selection or host build setup → `references/frameworks.md`, `references/host-setup.md`
- Measurement replay or tolerance definition → `references/data-replay.md`
- Timing claims, simulation, HIL planning → `references/timing-and-hil.md`
- Protocol liveness, repeated/late events, unknown outcomes → `references/protocol-state-testing.md`
- Optional finite state graph lint and model limitations → `references/state-model-format.md`
