---
name: arm-cortex-expert
description: >
  Design, implement, debug, refactor, and review Cortex-M firmware using a
  complexity ladder that avoids over-engineering while preserving hard safety
  boundaries for DMA, ISR/callbacks, interrupt priorities, cache coherency,
  RTOS task/thread boundaries, buffer ownership, peripheral driver structure,
  bounded state transitions, and LwIP/Ethernet integration. Covers FreeRTOS, CMSIS-RTOS v1/v2, and
  bare-metal projects.

  Use for acquisition, high-rate peripherals, DMA buffers, ISR/task handoff,
  cache-safe data paths, driver architecture, CubeMX RTOS integration, and
  STM32 ETH/LwIP paths.

  Do not use for board-level hardware design, pin wiring, PCB layout,
  component selection, voltage/current calculations, or MCU-independent C/C++.

  Examples: review CubeMX CMSIS-RTOS v2 DMA completion, STM32H7 Ethernet DMA
  cache coherency, LwIP pbuf ownership in ethernetif.c, or stale SPI DMA
  samples on Cortex-M7.
---
# ARM Cortex Expert

Use this skill as a practical Cortex-M firmware checklist, not as a substitute for the target reference manual, datasheet, Cube/HAL configuration, or project code.

## Scope Boundary

This skill handles firmware-level concerns:
- DMA pipeline architecture and buffer ownership
- ISR/task boundaries and interrupt priority strategy
- Cache coherency design and memory placement
- RTOS task/thread, queue, semaphore, event, and wrapper-layer architecture
- Peripheral driver structure and register configuration
- LwIP/Ethernet driver-level integration

Board-level electrical/hardware design (pin wiring, voltage levels, component selection, PCB layout) is excluded.

Schematics may be read only to extract firmware-relevant facts, such as
peripheral instances, GPIO signal names, CS/RESET/DRDY lines, interrupt lines,
PHY/RMII connections, and board-level timing constraints. Do not perform
electrical design, PCB layout review, component selection, or voltage/current
sizing in this skill.

## Source Priority

Prefer evidence in this order:

1. Current user requirements and applicable project instructions.
2. Project-owned architecture, protocol and test specifications, alongside code, schematics (for firmware-relevant facts), CubeMX `.ioc`, linker scripts, logs and measurements.
3. Vendor reference manuals, datasheets, errata, HAL/LL documentation, and RTOS/LwIP documentation.
4. Local skill references in `references/`.
5. General Cortex-M heuristics.

State when a conclusion is an inference rather than proven by project artifacts. Preserve conflicting requirements and behavior with their locations/revisions; identify what evidence resolves the disagreement. A skill rule must not silently override a product requirement or vendor hardware constraint.

## Read Order

1. Read `references/common.md` for shared workflow rules.
2. Read the core file(s) for the execution domains affected by the task. A dual-core device may need both; a change confined to one core usually does not.
3. Read the applicable family file when covered; verify the exact part and core instead of inferring cache or DMA behavior from the family name.
4. Read [state and interaction execution](references/state-and-interaction.md) for start/stop, asynchronous control, blocked transitions, retries, or MCU/FPGA completion handling.
5. Read [measurement streaming](references/measurement-streaming.md) for continuous acquisition, buffering, mixed sources, rate changes or first-valid-output recovery.
6. Read [measurement DSP](references/measurement-dsp.md) for filters, decimation, calibration/zero ordering or phase/frequency processing.
7. Read [persistent storage](references/persistent-storage.md) for settings/calibration persistence, flash concurrency or power loss.
8. Read [CubeMX guide](references/cubemx-guide.md) for `.ioc`, generated configuration or database lookup.
9. Read `references/lwip-ethernet.md` for LwIP, TCP/IP, `netif`, `pbuf`, or STM32 ETH DMA.
10. If the MCU family is not covered, rely on project/vendor evidence. Read only the applicable references, not all of them on every task.

## Selection Guide

- Cortex-M0/M0+: read [`cores/m0-m0plus.md`](references/cores/m0-m0plus.md).
- Cortex-M3: read [`cores/m3.md`](references/cores/m3.md).
- Cortex-M4/M4F: read [`cores/m4-m4f.md`](references/cores/m4-m4f.md).
- Cortex-M7/M7F: read [`cores/m7-m7f.md`](references/cores/m7-m7f.md).
- STM32F4: also read [stm32-f4.md](references/families/stm32-f4.md).
- STM32F7: also read [stm32-f7.md](references/families/stm32-f7.md).
- STM32H7: also read [stm32-h7.md](references/families/stm32-h7.md).
- STM32L0: also read [stm32-l0.md](references/families/stm32-l0.md).
- STM32L4: also read [stm32-l4.md](references/families/stm32-l4.md).
- nRF, SAMD, GD32, AT32, or other Cortex-M families: use this skill only for generic Cortex-M patterns unless vendor-specific files are added.

## Complexity Strategy

Use `references/common.md` as the authoritative source for operating modes, the complexity ladder, and non-negotiable firmware boundaries. In ordinary work, read it first, stop at the simplest sufficient tier, and add complexity only when the project evidence or stated requirements justify it.

## Requirements and Companion Skills

Confirm the current behavior before adding architecture. A bounded start/stop function
and one state owner may suffice; add local asynchronous phases only for real waits.
Synchronous channels can share a state machine and channel configuration; independent
channels need local instances plus explicit shared-resource constraints. Do not
mandate HSM, a manager task, queues, four configuration views or a transaction engine
because future expansion is possible.

The protocol skill defines public command/response and compatibility contracts; this
skill implements them without blocking required progress or falsifying hardware
state. The test skill checks logic, resources and timing at appropriate layers.
Load a companion only when its part of the work is needed; do not require all three
for a small patch. If companions are unavailable, state their relevant contracts
and verification gaps locally.

## Output Contract

For patches, prioritize code. Add only the short decision notes needed to explain the complexity tier, skipped complexity, upgrade trigger, verification, and residual risk.

For diagnostic patches, also state the current hypothesis, the active change set, the observed result, and which experimental changes were retained or reverted. Do not silently carry an unsupported change into the next experiment.

When giving a full design, include:

1. Assumptions and known hardware facts.
2. Module split and ownership boundaries.
3. Data flow from peripheral/ISR to task/application/transport.
4. Key structs, buffers, events, and error counters.
5. Code or patch with narrowly scoped changes.
6. Verification notes and residual risks.
7. Testability notes: which modules are host-compilable and where the seams are.

## When Information Is Missing

Ask only for facts that materially affect the design:

- MCU/core and exact part number.
- RTOS/bare-metal model, API layer, and interrupt priority policy.
- Peripheral instances and DMA channels/streams.
- Required input rate, output/upload rate, latency/skew limit, and packet format.
- Memory map/linker placement when DMA or cache is involved.

If reasonable assumptions are enough to proceed, state them and continue.

## Tool Path Resolution

Tool commands in this skill (`tools/stm32cli/...`, `tools/map-parser/...`) are written relative to this skill's root directory. The session working directory is normally the firmware project, so resolve tool locations explicitly before calling them:

1. If the skill loader exposes this skill's base directory, prefer it.
2. Resolve from this loaded `SKILL.md` directory. In the workbench source repository this is `arm-cortex-expert/`, not the repository root.
3. A DSH preset, Codex user skill, or project skill may each use a different root. Use an observed loader/file path rather than a fixed host-specific fallback.
4. Run `--help` on the installed script before using unfamiliar flags; tool implementations can differ between deployments. Ask for the location only when it cannot be discovered.

Use the observed skill root in absolute tool paths. Host-specific installation
examples belong in the workbench documentation, not the firmware workflow.

## Tools

Two companion CLIs ship with this skill (resolve paths via
`Tool Path Resolution`):

- `tools/stm32cli` — query the CubeMX database: chip capabilities,
  peripherals, DMA request mapping, pin muxing, clock tree, interrupts.
  Commands, workflow, cache behavior, and experimental-status caveats →
  `references/tools-stm32cli.md`.
- `tools/map-parser` — parse Keil `.map` files: symbol lookup, memory
  regions, HardFault diagnosis, size ranking, MPU alignment checks.
  Full command reference and output format →
  `references/tools-map-parser.md`.

Both are accelerators, never authorities: project artifacts and vendor
documentation win over tool output on any conflict.

## Read Order Addendum for Tools

When a task involves these tools, additionally load their reference file
listed above instead of relying on memory for flags or output schemas.
