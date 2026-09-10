# Firmware Forge · Embedded Skills, Commands and Tools

[中文](README.md) · [Usage guide (Chinese)](docs/workbench-usage.md) · [Design philosophy](docs/design-philosophy.md) · [Contributing](CONTRIBUTING.md)

AI is often good at writing firmware code, yet less sure which manual to trust, which boundaries to keep, or when to stop adding machinery. Firmware Forge fills that gap: a set of AI skills for STM32 / Cortex-M and FreeRTOS work, together with chip queries, map analysis, and Keil MDK build/flash commands.

Skills carry engineering judgment. Commands perform the action. Tools inspect concrete data. They compose when needed, but each can stand alone. Protocol design is one specialty in the set — not a prerequisite for every task.

The currently supported hosts are **Codex** and **DSH**. Other hosts are deferred until there is a real need. Coverage is firmware software engineering; it does not claim every MCU, embedded Linux, or board-level hardware design.

## Capability map

After installation, describe the task. The AI loads the matching skill, command, or tool from the request. You can also prefix a message with `$skill-name` to name an entry explicitly.

| Your task | Entry | Main output |
|---|---|---|
| Drivers, DMA/RTOS, acquisition/DSP, storage, networking, or performance diagnosis | [arm-cortex-expert](arm-cortex-expert/SKILL.md) | Focused implementation or diagnosis, ownership, and remaining platform checks |
| Unit tests, driver isolation, replay, accuracy regression, or timing | [embedded-test-engineer](embedded-test-engineer/SKILL.md) | Tests, replay results, tolerance rationale, and hardware gaps |
| Device-to-host/FPGA contracts, protocol design, or compatible evolution | [embedded-protocol-designer](embedded-protocol-designer/SKILL.md) | Frames and commands, duplicate/failure semantics, compatibility |
| Build, rebuild, or flash an existing project | DSH `/build`, `/build -r`, `/flash` | Results and logs for the selected project; see the [MDK guide](docs/mdk-build-flash.md) |
| Query chip resources, analyze a map, or lint an explicit state graph | Python helper tools | Scoped query and analysis results |

## Design philosophy

Good reliability work makes failure more controllable without making ordinary development heavier. Firmware Forge follows four plain rules: state the task, keep the design proportionate, ground claims in inspectable evidence, and verify what you assert.

“Requirements-first” does not mean rewriting a product specification for every patch. State models and bounded recovery belong only on paths that actually carry those risks. See the full [design notes](docs/design-philosophy.md) (Chinese, with an English overview).

## Quick start

### 1. Get the project

```sh
git clone https://github.com/Fz2hOpenSource/firmware-forge.git
cd firmware-forge
```

### 2. Install into your environment

| How you work | Next step | What you need |
|---|---|---|
| Use skills in Codex | Follow [Codex install](docs/workbench-usage.md#codex) and copy the full skill directories; then describe tasks naturally | Codex; DSH, Keil, and a board are not required |
| Use the workbench in DSH | Read the [DSH install notes](docs/workbench-usage.md#dsh), then run `./install.ps1` (or double-click `install.bat` on Windows) | A DSH that can load this preset; the current MDK plugin uses Windows PowerShell |
| Try the offline tools first | Run the help commands below | Python 3.10+; no AI host or hardware |

### 3. Start from the current task

```text
This existing STM32 + FreeRTOS acquisition project occasionally reads stale data
after DMA completion. Inspect the actual MCU, memory regions, cache maintenance
and buffer handoff. Establish the cause, then make the smallest supported fix.
Keep the existing sampling and communication contracts; report checks and gaps.
```

Verification can be requested the same way:

```text
Build a replay regression for the existing filter and calibration chain.
Inspect data formats, references and allowed errors first, then choose
minimal test seams. Distinguish regression fidelity from measurement accuracy.
```

More examples live in the [usage guide](docs/workbench-usage.md#example).

### Tools without hardware

From the repository root:

```sh
python arm-cortex-expert/tools/stm32cli/stm32cli.py --help
python arm-cortex-expert/tools/map-parser/map-parser.py --help
python embedded-test-engineer/scripts/check_state_model.py --help
```

Chip queries need a local CubeMX database; map analysis needs an existing build artifact. State-graph lint targets explicitly modeled waits and recovery — it is a specialist tool, not a substitute for runtime verification. Runnable positive and negative examples are in [tool trial](docs/workbench-usage.md#tools).

## Tools and dependencies

| Capability | Path | Requirements |
|---|---|---|
| CubeMX query | `arm-cortex-expert/tools/stm32cli/stm32cli.py` | Python; local CubeMX database; [reference](arm-cortex-expert/references/tools-stm32cli.md) |
| Keil map analysis | `arm-cortex-expert/tools/map-parser/map-parser.py` | Python; armlink map file; [reference](arm-cortex-expert/references/tools-map-parser.md) |
| MDK build/flash | `scripts/mdk/` and `plugins/mdk/` | Windows, Keil UV4, chosen flash backend and target; [guide](docs/mdk-build-flash.md) |
| Optional state-graph lint | `embedded-test-engineer/scripts/check_state_model.py` | Python 3.10+ stdlib; [format and limits](embedded-test-engineer/references/state-model-format.md) |

Python 3.10+ is a practical baseline. The recorded tool test environment is Python 3.14.2; that is not a full version/platform certification. Third-party compilers, databases, and programmers are installed and licensed separately.

## Documentation and evidence

- [Install, use, update, and troubleshoot](docs/workbench-usage.md) (Chinese)
- [Skill ownership and maintenance](docs/skills-integration.md) (Chinese)
- [Architecture](docs/architecture.md) and [DSH integration](docs/dsh-integration.md) (Chinese)
- [Integration record](docs/integration-2026-09-10.md) and [pre-release checks](docs/release-check-2026-09-10.md) (Chinese)
- [Contributing](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md) for AI collaborators
- [Behavior scenarios](docs/skill-behavior-cases.md) and the [2026-09-08 audit](docs/skills-audit-2026-09-08.md)

A graph pass does not prove scheduler behavior, DMA/cache correctness, FPGA CDC, or physical safety. Query and map tools must still be checked against the real project and vendor evidence. Claims about hardware need the matching tests.

## License

[MIT](LICENSE). Report problems or propose improvements through [GitHub Issues](https://github.com/Fz2hOpenSource/firmware-forge/issues).
