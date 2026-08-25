# DSH Embedded Workbench

A [DSH](https://github.com/deepseek-ai) agent preset for **Cortex-M / STM32 firmware development**. It bundles a firmware design/review skill, chip-database and map-file analysis tools, and Keil MDK build/flash commands into one workbench that you enable with a single click — covering the full loop of *design → code → build → flash → debug* inside a DSH session.

## Why This Exists

AI writes firmware code fast but without a senior engineer's guardrails: DMA cache coherency, interrupt-priority ordering, RTOS task boundaries — the traps nobody names go unguarded. Sizing up an unfamiliar STM32 means paging through hundred-page manuals, when the AI could query the CubeMX database directly; a HardFault arrives as a single PC value, and parsing the `.map` file beats guessing. This workbench turns those three pains into ready-to-use skills and tools, wires in build & flash, and keeps the whole loop inside one session.

## What You Can Do With It

Organized by your task, not by what the repo contains:

| Your task | How it helps |
|---|---|
| 🧠 Get designs reviewed to a senior embedded standard | `arm-cortex-expert` checks SPI+DMA cache coherency, interrupt-priority ordering, RTOS task-boundary violations, driver layering — loading references matched to your chip |
| 🧪 Put a verification strategy under the firmware | `embedded-test-engineer` plans test layering, seams and test doubles, measurement-data replay regression, tolerance policy, HIL coverage |
| 📡 Design a device protocol and govern its evolution | `embedded-protocol-designer` defines frame formats, command space, state gating, timeout/retry — with version-freeze governance (RS-485/UART/CAN etc.) |
| 🔍 Scope out an unfamiliar STM32 | `stm32cli` queries the CubeMX database: chip capabilities, peripheral instances, DMA request mapping, pin muxing, clock tree, interrupt vectors |
| 🗺️ Locate a HardFault, see who eats the RAM | `map-parser` parses Keil `.map` files: symbol lookup, memory-region analysis, PC-value diagnosis, size ranking, MPU alignment checks |
| ⚙️ Build and flash without leaving the session | `/build` runs UV4 builds and flashing (backends: keil/stlink/dap/jlink); see the [build/flash SOP](docs/mdk-build-flash.md) |

## The Complexity Ladder

The methodology underneath this workbench: **six stop-points** — ask yourself one question per level; if the answer is "yes", stay there:

1. Can a bare-metal super-loop meet latency, jitter, and maintainability needs? If yes, skip the RTOS.
2. Can blocking, polling, or interrupt-driven I/O meet CPU-load and jitter needs? If yes, skip DMA.
3. Can a single buffer with clear ownership absorb worst-case consumer latency? If yes, skip double buffers / rings.
4. Can a non-cacheable DMA region solve coherency on this core? If yes, skip per-transfer clean/invalidate.
5. Is integer/fixed-point error below the measured noise budget? Then skip float/CMSIS-DSP (and never force fixed-point on an FPU part with a measured-safe float path).
6. Can a direct driver API preserve ownership and backpressure? If yes, skip frameworks, queues, and transport layers.

Stop-points are ceilings, not steps: escalate only on project evidence or stated requirements, and write down the trigger. Hard safety boundaries (critical sections, cache maintenance, DMA accessibility) do not participate in simplification. Full definition: [arm-cortex-expert/references/common.md](arm-cortex-expert/references/common.md).

## Quick Start

### 1. Install (once)

Simplest way: **double-click `install.bat` in File Explorer** and wait for it to finish.

Or from a terminal:

```powershell
git clone <this-repo>
cd <repo>
.\install.ps1          # syncs to $DSH_HOME\.agent-presets\embedded\
.\install.ps1 -Symlink # dev mode: repo edits take effect immediately
```

Normally **zero configuration** is needed: `UV4.exe` is auto-detected from the registry, and project `.uvprojx` files are found by searching downward from the session workspace. Only if auto-detection fails, edit `$DSH_HOME\.agent-presets\embedded\scripts\mdk\mdk.config.ps1` (field reference in the [SOP](docs/mdk-build-flash.md)).

### 2. Enable

Create a new session in DSH and pick 「嵌入式开发工作台」 (Embedded Workbench) from the preset menu — chosen once, remembered as default.

### 3. First Commands

Just state your intent to the AI:

- "Review this SPI+DMA RX path for cache coherency" (loads the M7/H7 reference automatically)
- "Which DMA does SPI1 RX map to on STM32H723?" → calls `stm32cli`
- "HardFault with PC=0x0800b455 — locate it" → calls `map-parser fault`

Build/flash via the slash command (suffix semantics in the [SOP](docs/mdk-build-flash.md)):

```text
/build        # incremental build (default)
/build -r     # full rebuild
/build -f     # flash download
/build -rf    # rebuild then flash (skipped if the build has errors)
```

## Requirements

| Component | Needed for | Notes |
|---|---|---|
| DSH | required | preset host |
| Python 3.8+ | tools | stm32cli / map-parser |
| CubeMX database | stm32cli only | pass via `--db-path` or `STM32CUBEMX_DB_PATH` |
| Keil MDK (UV4) | build/flash | auto-detected; build features degrade gracefully without it |
| Flash tool | matching backend | ST-LINK(CubeProgrammer) / CMSIS-DAP(pyocd) / J-Link |

## Repository Layout

```text
firmware-forge/
├── arm-cortex-expert/            # Skill (SKILL.md + layered references + Python tools)
│   ├── references/               #   cores/ families/ lwip — loaded on demand per CPU
│   └── tools/
│       ├── stm32cli/             #   CubeMX database query CLI
│       └── map-parser/           #   Keil .map file analysis CLI
├── embedded-test-engineer/       # Skill (firmware verification: pyramid/doubles/replay/HIL)
├── embedded-protocol-designer/   # Skill (device protocol design: frames/command space/versioning)
├── preset/                       # DSH agent preset metadata + composition
├── plugins/mdk/                  # /build slash-command plugin (mdk-commands.mjs)
├── scripts/mdk/                  # mdk.ps1 wrapper + flash-backends.ps1 + config template
├── docs/                         # Docs for humans: usage manual + build/flash SOP
├── install.bat                   # Windows double-click installer (wraps install.ps1)
├── install.ps1                   # One-shot install/update into DSH
└── LICENSE                       # MIT
```

## Documentation Map

| If you want to... | Go to |
|---|---|
| Get running in 5 minutes | this file · Quick Start |
| Handle daily life after install: presets, placing skills, update/uninstall | [docs/workbench-usage.md](docs/workbench-usage.md) (Chinese) |
| Everything build/flash: detection priority, multi-project, four backends, known pitfalls | [docs/mdk-build-flash.md](docs/mdk-build-flash.md) (Chinese) — authoritative `/build` reference |
| Read a skill's full contract | each skill's `SKILL.md`, details in `references/` |
| 中文说明 | [README.md](README.md) |

> The two docs under `docs/` are currently written in Chinese; all commands, paths, and identifiers are language-neutral. See also [arm-cortex-expert/SKILL.md](arm-cortex-expert/SKILL.md) (English) for the full skill contract.

## Design Principles

- **Thin entry, load on demand**: `SKILL.md` routes; heavy content lives in `references/` keyed by CPU class so context stays small.
- **Evidence priority**: project code / `.ioc` / linker script > vendor manuals > skill references > general heuristics; inference must be stated.
- **Middleware is read-only by default**: configure HAL/RTOS/LwIP through supported surfaces, hooks, callbacks, and weak overrides.
- **Tools accelerate, never overrule**: stm32cli/map-parser output yields to project evidence on any conflict.

## License

Released under the [MIT License](LICENSE).
