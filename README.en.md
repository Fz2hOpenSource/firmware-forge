# DSH Embedded Workbench

A [DSH](https://github.com/deepseek-ai) agent preset for **Cortex-M / STM32 firmware development**. It bundles a firmware design/review skill, chip-database and map-file analysis tools, and Keil MDK build/flash commands into one workbench that you enable with a single click — covering the full loop of *design → code → build → flash → debug* inside a DSH session.

## What It Does

| Capability | Description |
|---|---|
| 🧠 Firmware skill | `arm-cortex-expert`: DMA pipelines, ISR/task boundaries, interrupt priorities, cache coherency, RTOS task architecture, driver layering, LwIP/Ethernet integration |
| 🧪 Verification skill | `embedded-test-engineer`: test pyramid strategy, seams and test doubles, measurement data replay regression, tolerance policy, HIL coverage planning |
| 📡 Protocol skill | `embedded-protocol-designer`: device protocol design/review for RS-485/UART/CAN — frame formats, command space, state gating, timeout/retry, version-freeze governance |
| 🔩 Complexity ladder | Six stop-points from bare-metal super-loop up to DMA double buffers — escalate only with evidence; hard safety boundaries are non-negotiable |
| 🔍 stm32cli | Query the CubeMX database: chip capabilities, peripherals, DMA request mapping, pin muxing, clock tree, interrupt vectors |
| 🗺️ map-parser | Parse Keil `.map` files: symbol lookup, memory-region analysis, HardFault diagnosis, size ranking, MPU alignment checks |
| ⚙️ `/build` command | One command for UV4 builds (`-r` rebuild) / flashing (`-f`, backends: keil/stlink/dap/jlink) / rebuild-then-flash (`-rf`) |

## Repository Layout

```text
├── arm-cortex-expert/            # Skill (SKILL.md + layered references + Python tools)
│   ├── references/               #   cores/ families/ lwip-ethernet — loaded on demand per CPU
│   └── tools/
│       ├── stm32cli/             #   CubeMX database query CLI
│       └── map-parser/           #   Keil .map file analysis CLI
├── embedded-test-engineer/       # Skill (firmware verification: pyramid/doubles/replay/HIL)
├── embedded-protocol-designer/   # Skill (device protocol design: frames/command space/versioning)
├── preset/                       # DSH agent preset metadata + composition
├── plugins/mdk/                  # /build slash-command plugin
├── scripts/mdk/                  # mdk.ps1 wrapper + four flash backends + config template
├── docs/                         # Usage guides and build/flash SOP (Chinese)
└── install.ps1                   # One-shot install/update into DSH
```

## Quick Start

### 1. Install (once)

```powershell
git clone <this-repo>
cd <repo>
.\install.ps1          # syncs to $DSH_HOME\.agent-presets\embedded\
.\install.ps1 -Symlink # dev mode: repo edits take effect immediately
```

Normally **zero configuration** is needed: `UV4.exe` is auto-detected from the registry, and project `.uvprojx` files are found automatically from the session workspace. Only if auto-detection fails, edit `$DSH_HOME\.agent-presets\embedded\scripts\mdk\mdk.config.ps1`.

### 2. Enable

Create a new session in DSH and pick「嵌入式开发工作台」(Embedded Workbench) from the preset menu.

### 3. Use

Just state your intent to the AI, for example:

- "Review this SPI+DMA RX path for cache coherency" (loads the M7/H7 reference automatically)
- "Which DMA does SPI1 RX map to on STM32H723?" → calls `stm32cli`
- "HardFault with PC=0x0800b455 — locate it" → calls `map-parser fault`

Build/flash via the slash command:

```text
/build        incremental build (default)
/build -r     full rebuild
/build -f     flash download
/build -rf    full rebuild then flash (skipped if the build fails)
```

## Requirements

| Component | Needed for | Notes |
|---|---|---|
| DSH | required | preset host |
| Keil MDK (UV4) | build/flash | auto-detected; build features degrade gracefully without it |
| Python 3.8+ | tools | stm32cli / map-parser |
| CubeMX database | stm32cli only | pass via `--db-path` or `STM32CUBEMX_DB_PATH` |
| Flash tool | matching backend | ST-LINK(CubeProgrammer) / CMSIS-DAP(pyocd) / J-Link |

## Design Principles

- **Thin entry, load on demand**: `SKILL.md` routes; heavy content lives in `references/` keyed by CPU class so context stays small.
- **Evidence priority**: project code / `.ioc` / linker script > vendor manuals > skill references > general heuristics; inference must be stated.
- **Middleware is read-only by default**: configure HAL/RTOS/LwIP through supported surfaces, hooks, callbacks, and weak overrides.
- **Tools accelerate, never overrule**: stm32cli/map-parser output yields to project evidence on any conflict.

See [arm-cortex-expert/SKILL.md](arm-cortex-expert/SKILL.md) for the full skill contract. Chinese documentation: [README.md](README.md)

## License

Released under the [MIT License](LICENSE).
