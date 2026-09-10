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

Plan the remaining HIL work when equipment or evidence is unavailable. Do not mark
unexecuted tests as passed; use connected equipment only within the user's actual
scope and authorization. Electrical measurement methodology is outside this skill.
