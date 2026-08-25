---
name: arm-cortex-expert
description: >
  Design, implement, debug, refactor, and review Cortex-M firmware using a
  complexity ladder that avoids over-engineering while preserving hard safety
  boundaries for DMA, ISR/callbacks, interrupt priorities, cache coherency,
  RTOS task/thread boundaries, buffer ownership, peripheral driver structure,
  and LwIP/Ethernet integration. Covers FreeRTOS, CMSIS-RTOS v1/v2, and
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

1. User-provided project code, schematics (for firmware-relevant facts), CubeMX `.ioc`, linker scripts, and build settings.
2. Vendor reference manuals, datasheets, errata, HAL/LL documentation, and RTOS/LwIP documentation.
3. Local skill references in `references/`.
4. General Cortex-M heuristics.

State when a conclusion is an inference from general rules rather than proven by project artifacts.

## Read Order

1. Read `references/common.md` for shared workflow rules.
2. Read exactly one core file from `references/cores/` when the CPU class is known.
3. Read exactly one family file from `references/families/` when the MCU family is covered.
4. Read `references/lwip-ethernet.md` when the task involves LwIP, Ethernet, TCP/IP upload, `netif`, `pbuf`, or STM32 ETH DMA.
5. If the MCU family is not covered, skip family references and rely on project/vendor evidence.
6. Do not load unrelated reference files during ordinary firmware work. When auditing this skill itself, reading all resources is acceptable.

## Selection Guide

- Cortex-M0/M0+: read `cores/m0-m0plus.md`.
- Cortex-M3: read `cores/m3.md`.
- Cortex-M4/M4F: read `cores/m4-m4f.md`.
- Cortex-M7/M7F: read `cores/m7-m7f.md`.
- STM32F4/F7/H7/L0/L4: also read the matching family file.
- nRF, SAMD, GD32, AT32, or other Cortex-M families: use this skill only for generic Cortex-M patterns unless vendor-specific files are added.

## Complexity Strategy

Use `references/common.md` as the authoritative source for operating modes, the complexity ladder, and non-negotiable firmware boundaries. In ordinary work, read it first, stop at the simplest sufficient tier, and add complexity only when the project evidence or stated requirements justify it.

## Judgment Rules

- Prefer the simplest design that meets evidence. Add complexity only when it solves a measured or credible failure mode.
- Treat third-party middleware, RTOS kernels, vendor libraries, and generated code outside supported user sections as read-only by default. Prefer documented configuration, hooks, callbacks, weak overrides, and project-owned adapters; require evidence and explicit user approval before patching middleware internals.
- Keep diagnostic experiments reversible and hypothesis-scoped. Revert a failed or inconclusive change before testing an independent hypothesis; retain it only when the next test explicitly depends on it, and identify the test as a combined hypothesis.
- Keep ISRs and DMA callbacks short: record status, swap/commit buffers, notify tasks, then return.
- Do not place network transport, filtering, and low-level driver logic in the same module unless the user explicitly asks for a prototype.
- Design for verifiability: business logic stays free of vendor headers and direct register access; hardware and time sources sit behind callable interfaces; add test seams only where verification value justifies them. The embedded-test-engineer skill builds on this structure.
- Prefer fixed-size buffers and explicit ownership over hidden globals.
- Use DMA when it reduces CPU load or jitter, but do not force DMA for low-rate paths where blocking or interrupt-driven I/O is simpler and safe.
- Choose integer/fixed-point, float, or CMSIS-DSP based on the MCU, FPU, rate, precision, and existing project code. Do not force fixed-point when the project has an FPU and measured float path is safe.
- Treat Cortex-M7 cache maintenance, memory placement, and DMA accessibility as mandatory design topics, not afterthoughts.
- For configurable sampling/upload rates, distinguish ADC/input sample rate from output/upload rate and document filter/decimation behavior.

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
2. If the session workspace is this skill repository itself, the relative `tools/...` paths work as-is.
3. When installed via the embedded workbench preset, the skill root is `%DSH_HOME%\.agent-presets\embedded\skills\arm-cortex-expert` (`DSH_HOME` defaults to `%USERPROFILE%\.dsh`).
4. Otherwise, ask the user where this skill is checked out.

PowerShell helper — run once per session to set `$SkillRoot`, then call tools with absolute paths:

```powershell
$dsh = if ($env:DSH_HOME) { $env:DSH_HOME } else { Join-Path $env:USERPROFILE '.dsh' }
$SkillRoot = Join-Path $dsh '.agent-presets\embedded\skills\arm-cortex-expert'
if (-not (Test-Path (Join-Path $SkillRoot 'SKILL.md'))) {
  Write-Warning "Installed skill root not found: $SkillRoot - ask the user for the checkout location."
}
# Example calls:
python (Join-Path $SkillRoot 'tools\map-parser\map-parser.py') info firmware.map
python (Join-Path $SkillRoot 'tools\stm32cli\stm32cli.py') chip STM32H723ZGTx
```
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
