# Timing, Simulation and HIL Evidence

Choose the cheapest layer that can exercise the requirement. Passing examples
establish evidence within their inputs and model; they do not prove every possible
schedule or a physical worst-case bound.

| Claim | Useful evidence and boundary |
|---|---|
| Retry/debounce/deadline arithmetic | L1 virtual ticks, wrap and same-tick races; actual scheduling separate |
| Task interaction, deadlock/starvation scenarios | L3 controlled schedules/faults; model coverage and scheduling assumptions explicit |
| Register-level integration | L3 with applicable modeled peripherals; missing model behavior remains a hardware gap |
| ISR latency, DMA/cache interference | L4 under defined target load; measured max is not a universal WCET proof |
| Setup/hold, sample instant, analog accuracy | L4 with appropriate instruments/reference and uncertainty |

## Use Existing Simulation Where It Fits

Renode can execute target binaries with a suitable platform/peripheral model.
Verify support for the exact peripherals and version before claiming production
ELF compatibility; control external inputs and preserve the model/test setup for
repeatability. It does not supply every STM32/FPGA model automatically. See
[Renode platform descriptions](https://renode.readthedocs.io/en/latest/advanced/platform_description_format.html).

Zephyr native_sim builds a Zephyr application for host execution with simulated
time and hardware support. It does not run an arbitrary FreeRTOS firmware unchanged;
do not migrate the product merely to obtain tests. See
[Zephyr native_sim](https://docs.zephyrproject.org/latest/boards/native/native_sim/doc/index.html).

For MCU/FPGA interaction, retain relevant RTL simulation/CDC checks and tests of
independent reset, mailbox coherence and delayed completion. Host state tests
cannot establish physical CDC or bus timing correctness.

For MCU/FPGA evidence, name the actual DUT: algorithm/core, top-level bus interface,
MCU-side model or physical pair. Core simulation does not cover top-level SPI
transactions or on-wire status bits. List supported MCU/FPGA version pairs and
check each required direction separately: new MCU/old FPGA does not establish old
MCU/new FPGA compatibility. Do not require unsupported combinations. Associate
simulation, timing reports and flashed artifacts with their
source/configuration revisions. Missing RTL, CDC or physical timing evidence stays
an explicit gap, not a capability implied by this firmware testing skill.

## Preconditions and Scenario Verdicts

Before a target run, select preconditions from the mechanisms actually under test;
do not require every item in a measurement-oriented checklist. Record relevant
firmware/configuration versions and input conditions. If behavior depends on an
operating mode, verify the actual device mode rather than UI selection alone.
Device context, FPGA mode echo, sensor binding, stream/value kind and warm-up or
valid-output state are checks only where those mechanisms affect this test.
A prerequisite mismatch makes the intended acceptance test inapplicable until
resolved; it is not by itself proof of the target feature failing. Preserve the
observed mismatch as a separate finding.

For fault injection, use phase-specific criteria: healthy baseline, detected fault,
required behavior during the fault, recovery after the scenario's recovery trigger,
then a defined stable observation window. Loss of signal can be the expected
injected event, not an unconditional test failure. Confirm the injection actually occurred.

Disclose relevant resource ownership and side effects, such as an exclusive control
connection, starting/stopping streams or changing modes/bindings where applicable.
For state-changing tests, plan authorized cleanup, then verify and report its
outcome. Executing a finally block is not evidence that configuration was restored;
an unknown final device state remains an explicit result. Limit restoration checks
to state/resources the run could affect under its known behavior or stated risk;
do not add a persistent-configuration audit to a test known not to modify it.

## Observation Resolution

For polled observations, report polling interval, request duration and timestamp
basis, plus last normal / first abnormal and last abnormal / first recovered
observations when available. For other measurement methods, report their actual
time resolution and uncertainty instead of inventing polling parameters.
Before giving a physical-event interval, establish what each timestamp denotes
(device sampling, request start or response receipt) and relevant bounds on data age,
transport delay and clock offset. Coherent instantaneous samples can bracket a
transition; bounded delays may allow a wider interval. Without that mapping, report
only the observed status sequence, not a claimed event-time bound followed by a
disclaimer. Recovery latency additionally needs the recovery trigger's time.
Roughly one-second polling cannot establish a precise 2.000 s response. Keep
specified deadlines, observed intervals and the maximum in this run separate;
none alone establishes a universal bound.

## Target Scenarios

Select from current risks: reference signal at zero/mid/full scale, known frequency,
control traffic during maximum upload, bounded stop latency, storage stalls,
independent resets and recovery failure. No single scenario or a live heartbeat
establishes that all subsystems are progressing.

Each report states hardware/firmware revision, measurement means and clock basis,
load/fault conditions, sample count, min/max/distribution, threshold traced to a
requirement and instrumentation limitations. A cycle-counter result also needs
counter availability, wrap and clock/sleep behavior considered. State whether a
bound is analytic, model-derived or the maximum observed in the run.

Choose repetition count and observation duration from the acceptance criterion and
failure risk. Label exploratory counts as provisional; a round number is neither
a universal minimum nor evidence of a statistical guarantee.

Plan the remaining HIL work when equipment or evidence is unavailable. Do not mark
unexecuted tests as passed; use connected equipment only within the user's actual
scope and authorization. Electrical measurement methodology is outside this skill.
