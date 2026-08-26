# Common Cortex-M Rules

## Source Discipline

- Prefer project artifacts over generic advice: code, `.ioc`, linker script, schematic, map file, build log, and measured timing.
- Treat this reference as a checklist. Verify family-specific register, DMA, cache, and clock details against vendor documentation.
- Call out assumptions when the exact MCU, DMA engine, memory region, or RTOS priority policy is unknown.

## Middleware and Generated Code Preservation

- Treat third-party middleware, RTOS kernels, vendor HAL/LL/CMSIS sources, protocol-stack internals, and generated code outside protected user sections as read-only by default.
- Prefer supported configuration and extension surfaces, such as `.ioc`, `FreeRTOSConfig.h`, `lwipopts.h`, vendor configuration headers, build options, official hooks and callbacks, weak-function overrides, generated `USER CODE` sections, and project-owned wrapper or adapter modules.
- Do not patch middleware merely to test a downstream hypothesis, bypass a documented integration contract, or hide an application, configuration, ownership, priority, memory-placement, or cache-coherency defect.
- Before proposing a direct middleware edit, establish from project and vendor evidence that the defect is inside the exact bundled version, confirm that no supported configuration or extension point is sufficient, and reduce the change to the smallest maintainable patch.
- Do not directly edit middleware internals without explicit user approval. Record the component and version, affected files, reason, upstream issue or documentation when available, validation plan, and the burden when regenerating or upgrading the package.
- For generated code, change the persistent source configuration or protected user section whenever possible. Warn when regeneration could overwrite a necessary exception.

## Diagnostic Experiment Discipline

- Reproduce and record the baseline before changing behavior. Inspect the existing diff so user-authored and unrelated changes are not mistaken for part of the experiment.
- Associate every diagnostic edit with one explicit hypothesis and keep its patch minimal, observable, and reversible. Change one independent variable at a time when practical.
- After testing hypothesis A, record whether the evidence supports, rejects, or is inconclusive for A. A build, simulation, or hardware run that fails for an unrelated reason is inconclusive, not proof.
- Before testing hypothesis B, determine whether B depends on A:
  - If B is independent, revert A first when A was rejected or inconclusive.
  - If B requires A, retain A and state that the active experiment is the combined hypothesis `A+B`.
  - If retaining an inconclusive A is temporarily necessary, isolate and label it; do not silently treat it as established.
- Revert only assistant-authored experimental hunks. Never discard user changes or unrelated work with broad reset, checkout, clean, or stash operations.
- Before each requested test, summarize the active behavioral changes and dependencies. After the result, report which changes are kept, reverted, or still unverified.

## Operating Modes

- `lite`: make the smallest correct change, then name obvious risks and simpler alternatives.
- `full`: default mode; apply the complexity ladder and hard safety boundaries before adding RTOS, DMA, buffering, cache, or DSP complexity.
- `ultra`: challenge the requirement itself when rate, latency, channel count, precision, storage, or upload bandwidth appears over-specified.

## Complexity Ladder

Use these as stop-points, not mandatory steps. Stop at the simplest tier that satisfies stated or measured requirements, and document the upgrade trigger when it matters.

1. Can a bare-metal super-loop meet latency, jitter, and maintainability needs? If yes, skip RTOS.
2. Can blocking, polling, or interrupt-driven I/O meet CPU load and jitter needs? If yes, skip DMA.
3. Can a single buffer with clear ownership meet worst-case consumer latency? If yes, skip double buffers or rings.
4. Can a non-cacheable DMA region be used on cacheable cores? If yes, skip per-transfer clean/invalidate, but still verify DMA access, alignment, MPU attributes, and cache-line isolation.
5. Is integer or fixed-point accuracy below the measured noise/error budget? If yes, skip float/CMSIS-DSP. If the MCU has an FPU and float is measured safe, do not force fixed-point.
6. Can a direct driver API preserve ownership and backpressure? If yes, skip framework, queue, network, or transport layers.

## Shared Workflow

1. Identify the peripheral path: source, trigger, bus, I/O mode, buffer, processing, and consumer.
2. Identify rates separately: raw/input sample rate, processed output rate, upload rate, and publication divider.
3. Apply the Complexity Ladder section above and select the simplest sufficient tier.
4. Define ownership: ISR owns event capture, driver owns hardware state, processing owns filtering/decimation, transport owns packetization.
5. Define failure behavior: timeout, overflow, missed sample, skew violation, DMA error, and transport backpressure.
6. Add observability: counters, min/max interval, dropped frames, last error, and optional timestamps.

## Reconfiguration and State Continuity

- Model profile, excitation, peripheral mode, filter, calibration, and rate changes as explicit transactions: validate first; quiesce affected producers; drain or invalidate old work; apply hardware and algorithm state; advance a generation/epoch; then publish the first valid result.
- Tag queued samples, processed results, and application-visible snapshots with enough revision information to reject stale data after a transition.
- Define separately which state survives stream stop/start, transport disconnect, source recovery, profile change, algorithm reset, software reset, and power cycle. Do not let incidental globals decide product behavior.
- Preserve filter state only when sample timing, coefficients, units, calibration, and signal meaning remain compatible. Otherwise reset or transform it explicitly and expose warm-up/settle state.
- A failed transition must leave the previous known-good state or a clearly reported safe stopped state; never continue with a partially applied configuration.

## Streaming and Mixed Sources

- Keep source validity, processing readiness, stream running state, and transport connectivity separate. A temporary invalid source should not silently kill the service or require manual restart unless the product contract explicitly says so.
- Separate startup first-output timeout from sustained no-progress detection. Recovery after a source returns must be bounded and observable.
- For independently clocked sources, use timestamp/epoch association with a measured skew and history budget. A single incomplete group must be dropped or resynchronized without poisoning later groups.
- Use wrap-safe unsigned time differences and an explicit "observed" flag. Do not use `UINT32_MAX` or another interval value as both data and invalid sentinel.
- For detailed capacity, recovery, association, and counter rules, read `measurement-streaming.md`.

## ISR and Task Boundaries

- Keep ISR/DMA callbacks non-blocking.
- Do not run filters, printf, packet formatting, flash writes, or LwIP socket calls inside ISR.
- Use ring buffers, queues, task notifications, or event groups to hand work to tasks.
- Protect shared state with the smallest suitable critical section. Avoid long global interrupt masks.
- Make callback ownership explicit: who allocates a buffer, who fills it, who may read it, and who releases it.

## DMA and Buffering

- Start with the simplest buffer ownership model that can meet worst-case latency; add double buffers or rings only when single-buffer ownership cannot keep up.
- Choose buffer depth from worst-case consumer latency, not only average throughput.
- Count and expose overflows; do not silently drop data.
- For DMA-to-memory RX DMA on cacheable memory, ensure target cache lines are not dirty before starting DMA. Use non-cacheable MPU regions, dedicated aligned RX buffers, or explicit cache maintenance before arming DMA. After DMA completes, invalidate before CPU reads. Do not share a cache line between DMA-owned data and unrelated CPU-owned data.
- For memory-to-DMA, clean cache before starting DMA on cacheable cores.
- Align DMA buffers to the target cache line size when cache is present.

## RTOS Guidance

- Identify the RTOS API surface before changing synchronization code: native FreeRTOS, CMSIS-RTOS v1, CMSIS-RTOS v2, or bare metal.
- For CubeMX projects, inspect the `.ioc`, generated `freertos.c`, and included CMSIS headers to determine whether CMSIS-RTOS v1 or v2 is used.
- When the user provides local official sources (for example a CMSIS_6 or CMSIS-FreeRTOS checkout), use them for CMSIS-Core/RTOS2 API definitions and the RTOS2-on-FreeRTOS adapter implementation; the target project's bundled `Drivers/CMSIS`, generated code, and `FreeRTOSConfig.h` still win.
- When migrating CMSIS-RTOS v1 to v2, verify message queue semantics: v1 `osMessagePut/Get` commonly passes a `uint32_t` value or pointer, while v2 `osMessageQueuePut/Get` copies fixed-size messages from/to `msg_ptr`; for DMA buffers, queue a pointer or descriptor intentionally instead of copying large buffers.
- Keep driver APIs usable from tasks/threads; provide separate ISR-safe notification functions when needed.
- Verify the ISR-callable API subset, timeout rules, and object types for the selected RTOS layer.
- Do not assume native FreeRTOS `FromISR` APIs are available when the project uses CMSIS-RTOS wrappers.
- Keep RTOS wrapper usage consistent inside a module; avoid mixing CMSIS-RTOS and native RTOS calls unless the project already has a clear boundary.
- For FreeRTOS-backed CMSIS-RTOS projects, NVIC priority rules and `configMAX_SYSCALL_INTERRUPT_PRIORITY` still matter for ISR-to-thread signaling.
- Avoid priority inversion: high-rate acquisition tasks should not block behind slow logging, UI, or network tasks.
- Define backpressure policy between producer and consumer: block, drop oldest, drop newest, or degrade rate.

## Non-Negotiable Boundaries

Do not simplify away these checks or mechanisms:

- ISR priority and RTOS syscall priority compliance, including `configMAX_SYSCALL_INTERRUPT_PRIORITY` for FreeRTOS-backed paths.
- Cortex-M7/H7 DMA cache coherency, DMA-accessible memory placement, buffer alignment, and cache-line isolation.
- Explicit ownership for DMA buffers, descriptors, callbacks, queues, and application-visible data.
- Overflow, timeout, DMA error, bus error, and dropped-frame counters or equivalent visibility.
- DMA error callbacks and recovery behavior for acquisition paths.
- Stack and heap failure visibility for RTOS paths.
- Bounds checks for packet lengths, decoded protocol fields, ring indexes, and DMA transfer sizes.

## Networking and Upload

- For LwIP, Ethernet, TCP/IP upload, `netif`, `pbuf`, or STM32 ETH DMA work, also read `lwip-ethernet.md`.
- Keep LwIP/Ethernet code out of low-level drivers.
- Batch small measurement frames before sending when latency allows.
- Packetize from stable completed frames; never read live DMA buffers directly in the network task.
- Define packet sequence numbers and timestamps so the host can detect drops, reordering, and skew.
- Treat network throughput and acquisition determinism separately: a fast Ethernet link does not guarantee sample timing.

## Signal Processing

- Choose numeric representation from evidence:
  - Use integer/fixed-point for small MCUs, no FPU, strict determinism, or wire formats.
  - Use float/CMSIS-DSP when the target has an FPU and measured CPU load is acceptable.
  - Avoid `double` on MCUs without double-precision hardware unless explicitly required.
- Document filter reset behavior when sample/output rates change.
- Distinguish raw ADC sample rate from filtered output/upload rate.
- State filter group delay, transient/warm-up behavior, saturation/invalid-input policy, and whether runtime state is inherited across compatible configurations.
- Before changing a filter to hide outliers, separate random noise, periodic interference, isolated impulses, true steps, slow drift, and calibration bias.
- For detailed multirate, notch, circular phase, anomaly, and calibration-chain rules, read `measurement-dsp.md`.

## Intentional Simplification Comments

When code intentionally stays at a simpler tier, leave a short upgrade trigger near the decision point if it will prevent future over-design or accidental misuse.

Use the generic `intentional simplification:` prefix by default. Use `ponytail:` only when the user or project explicitly asks for that local convention.

Preferred forms:

```c
/* intentional simplification: IRQ path is enough below 1 kHz; switch to DMA if overflow_count > 0 */
/* intentional simplification: single buffer is safe while max_task_latency < buffer_fill_time */
```

Optional project-local tag when the user wants it:

```c
/* ponytail: Q15 filter stays below measured noise floor; switch to float/CMSIS-DSP if error budget changes */
/* ponytail: non-cacheable DMA region avoids per-transfer cache maintenance; keep buffer cache-line aligned */
```

Keep these comments sparse. Use them for deliberate simplifications and upgrade triggers, not for restating obvious code.

## Validation Checklist

- Measure ISR interval min/max and processing task latency.
- Exercise highest configured rate with logging disabled.
- Force consumer stalls and confirm overflow counters behave as intended.
- For cacheable systems, test stale-data failure modes by enabling D-cache.
- Verify stack use for ISR, acquisition task, processing task, and network task.
- Confirm generated packets include enough metadata for host-side diagnosis.

## Coding Principles

- Keep board glue, reusable drivers, protocol parsing, signal processing, and transport code in separate modules.
- Keep driver state private to the driver module; expose narrow APIs for init, start, stop, status, and error inspection.
- Make ownership explicit for buffers, DMA descriptors, callbacks, queues, and application-visible data.
- Prefer fixed-size buffers for real-time paths; add rings or double buffers only when latency or ownership requires them. Avoid heap allocation in ISR, callbacks, and high-rate tasks.
- Do not place large buffers on task stacks unless stack usage has been measured.
- Return explicit status values from driver APIs; count timeouts, overflows, DMA errors, bus errors, and dropped frames.
- Do not silently discard samples, packets, or hardware errors unless a documented drop policy requires it.
- Keep ISR and DMA callbacks short; defer filtering, packet formatting, logging, and network operations to tasks.
- Use the smallest suitable critical section for shared ISR/task state; do not rely on `volatile` for atomicity.
- Name rates, units, buffer sizes, and timeouts clearly; avoid unexplained magic numbers in peripheral code.
- Keep debug output out of timing-critical paths; prefer counters, timestamps, trace pins, or rate-limited logs.
- Add bounds checks for array indexes, packet lengths, ring positions, and decoded protocol fields.
- Define recovery behavior for invalid states, peripheral stalls, DMA errors, and task backpressure.
- Keep generated Cube/HAL code separated from reusable driver and application logic where practical.
- Follow existing project naming, error-code, and module conventions unless they conflict with real-time safety or correctness.

## Testability and Host Builds

Design modules so verification is possible without rework:

- Keep business logic (algorithms, protocol parsing, state machines,
  calibration math) free of vendor headers and direct register access so
  it compiles unchanged in host test builds.
- Route hardware access and time sources (tick, delay, IRQ-derived flags)
  through callable interfaces instead of calling HAL macros inline from
  logic modules.
- Introduce test seams (link-time wrap, function pointer, weak symbol)
  where verification value justifies them; do not add speculative
  abstraction layers without a verification or portability purpose.
- The embedded-test-engineer skill consumes these seams; if a design
  cannot be host-verified where it reasonably should be, state that gap
  explicitly in the output.
