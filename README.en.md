# DSH Embedded Workbench

A DSH firmware workbench for **STM32 / Keil MDK**. It helps you review firmware, query chip resources, inspect map-file issues, and run guarded MDK build or flash actions in one agent session.

It does not replace reference manuals or guess a board configuration. Project source, `.ioc` files, linker scripts, measurements, and vendor documentation always take priority.

## When to use it

| Your task | What the workbench provides |
| --- | --- |
| Review an SPI/ADC/UART + DMA path | Checks DMA-buffer ownership, ISR boundaries, cache coherency, and RTOS priority concerns. |
| Take over an unfamiliar STM32 | `stm32cli` queries chip, peripheral, DMA, pin, clock, and interrupt data from CubeMX databases. |
| Diagnose a HardFault or memory issue | `map-parser` uses a Keil `.map` file to locate PCs, symbols, memory regions, and MPU alignment issues. |
| Add confidence to a measurement chain | Plans host tests, seams, replay regression, tolerances, and HIL coverage. |
| Design a UART / RS-485 / CAN protocol | Defines frame, state-gating, timeout/retry, and compatibility rules. |
| Build or flash an MDK project | `/build` provides a single interface for builds and guarded flashing. |

## What it does not do

- It does not override project source, `.ioc` files, linker scripts, measurements, or vendor documentation; those are stronger evidence.
- It does not perform PCB, component-selection, electrical, or EMC design.
- It does not modify HAL, RTOS, or LwIP internals by default; use supported configuration, callbacks, hooks, weak overrides, and project-owned adapters first.
- It does not guess among multiple projects or images before flashing.

## Get started in five minutes

### Install

Double-click `install.bat`, or run:

```powershell
git clone <this-repo>
cd <repo>
.\install.ps1          # install/update $DSH_HOME\.agent-presets\embedded\
.\install.ps1 -Symlink # development mode: repository edits take effect immediately
```

The script discovers `UV4.exe` and searches downward from the session workspace for one `.uvprojx`. When that is not enough, edit `scripts\mdk\mdk.config.ps1`. Multi-project and backend rules are in the [MDK build/flash SOP](docs/mdk-build-flash.md) (Chinese).

### Enable and ask a concrete question

Create a DSH session and select 「嵌入式开发工作台」 (Embedded Workbench). Then describe the engineering task:

- “Review this SPI + DMA receive path for cache coherency.”
- “Which DMA can SPI1 RX use on STM32H723?”
- “Locate a HardFault with PC `0x0800b455` from this map file.”

```text
/build            # build (incremental by default; pass a project alias for multi-project repos)
/build -r         # full rebuild
/build sensor     # build the project aliased as 'sensor'
/flash            # flash
/flash main       # flash a specific project
```

## How it stays conservative

The workbench follows a **simplest sufficient design** rule: skip an RTOS when a super-loop is enough, skip DMA when IRQ I/O is enough, and skip rings when one clearly owned buffer is enough. Escalate complexity only for project evidence or an explicit requirement.

ISR/RTOS priority compliance, DMA ownership, M7/H7 cache coherency and DMA-accessible memory, bounds checks, and observable timeout/overflow/DMA-error paths are not optional simplifications. The complete rule set is in [the common Cortex-M guidance](arm-cortex-expert/references/common.md).

Read the [architecture guide](docs/architecture.md) (Chinese) for component integration, boundaries, and extension points.

## Requirements and support boundary

| Component | Required? | Used for |
| --- | --- | --- |
| DSH | yes | preset host |
| Python 3.8+ | tools only | `stm32cli` and `map-parser` |
| STM32CubeMX database | `stm32cli` only | pass `--db-path` or `STM32CUBEMX_DB_PATH` |
| Keil MDK / UV4 | build/flash only | build and flash actions |
| ST-Link / pyOCD / J-Link | backend-dependent | matching flash backend |

The current focus is Windows, DSH, Cortex-M / STM32, and Keil MDK. Other IDEs, chip families, and DSH versions are not verified support claims.

## Documentation

| Topic | Read |
| --- | --- |
| Presets, adding skills, update, and uninstall | [Daily use guide](docs/workbench-usage.md) (Chinese) |
| Projects, images, and four flash backends | [MDK build/flash SOP](docs/mdk-build-flash.md) (Chinese) |
| Layers, boundaries, and extension points | [Architecture guide](docs/architecture.md) (Chinese) |
| Host/isolate realms and preset maintenance | [DSH integration guide](docs/dsh-integration.md) (Chinese) |
| Complete contract of a skill | its `SKILL.md` and `references/` |
| 中文说明 | [README.md](README.md) |

## Repository layout

```text
firmware-forge/
├── arm-cortex-expert/            # firmware review skill + stm32cli, map-parser
├── embedded-test-engineer/       # verification strategy skill
├── embedded-protocol-designer/   # device protocol design skill
├── preset/                       # DSH metadata and agent composition
├── plugins/mdk/                  # /build plugin
├── scripts/mdk/                  # MDK and flash-backend scripts
├── docs/                         # user and maintainer documentation
├── install.bat / install.ps1     # Windows installation entry points
└── LICENSE                       # MIT
```

## License

Released under the [MIT License](LICENSE).
