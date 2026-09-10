# Firmware Forge · Embedded Skills, Commands and Tools

[中文](README.md) · [Usage guide (Chinese)](docs/workbench-usage.md) · [Design philosophy](docs/design-philosophy.md) · [Contributing](CONTRIBUTING.md)

Firmware Forge is a collection of **AI skills, commands and tools for embedded development**. Current coverage focuses on **STM32 / Cortex-M firmware, FreeRTOS, device interaction and verification**, with chip queries, build-artifact analysis and Keil MDK build/flash commands.

Current host integrations are **Codex skills** and the **DSH workbench**. Other hosts are deferred until needed. The current scope is firmware software engineering; it does not imply coverage of every MCU, embedded Linux or board-level hardware design.

## Capability map (the AI selects the entry)

**You do not need to pick a skill first.** After installation, describe the task in your firmware project; the AI loads the matching skill, command, or tool from the request. Naming a skill with `$skill-name` is optional — useful to confirm routing or force one entry, not a usage prerequisite.

The table shows what the AI may use and what each entry delivers. **It is not a manual selection checklist:**

| Task | Entry | Main output |
|---|---|---|
| Drivers, DMA/RTOS, acquisition/DSP, storage, networking or performance diagnosis | [arm-cortex-expert](arm-cortex-expert/SKILL.md) | Focused implementation or diagnosis, ownership and platform checks |
| Unit tests, driver isolation, measurement replay, accuracy regression or timing | [embedded-test-engineer](embedded-test-engineer/SKILL.md) | Tests, replay results, tolerance rationale and hardware gaps |
| Device-to-host/FPGA contracts, protocol design or compatible evolution | [embedded-protocol-designer](embedded-protocol-designer/SKILL.md) | Frames, commands, duplicate/failure semantics and compatibility |
| Build, rebuild or flash an existing project | DSH `/build`, `/build -r`, `/flash` | Selected-project results and logs; [MDK guide](docs/mdk-build-flash.md) |
| Query chip resources, analyze map files or lint explicit state graphs | Python helper tools | Scoped query and analysis results |

Skills guide engineering decisions, commands provide execution entry points, and tools process specific inputs. Use them independently or together as needed. Protocol design is not a prerequisite for firmware implementation, testing or builds. If the AI picks the wrong entry, restate the task or name the intended skill.

## Design philosophy

**Clear tasks, proportionate designs, traceable evidence and verifiable results.**

Establish the current task and acceptance criteria, preserve useful project infrastructure, and select the relevant implementation, diagnosis, test or command workflow. Requirements-first does not mean rewriting specifications for each patch. State models and bounded recovery apply where the actual path needs them.

See the [design rationale and examples](docs/design-philosophy.md) (Chinese, with an English overview).

## Quick start

```sh
git clone https://github.com/Fz2hOpenSource/firmware-forge.git
cd firmware-forge
```

### Codex

Copy the complete skill directories you need into `~/.agents/skills/` for personal use, or your firmware repository's `.agents/skills/` for project use. Keep `SKILL.md`, references and tools together. Inspect and back up an existing same-name skill before updating it. Local discovery and reload behavior follow the [official skill documentation](https://learn.chatgpt.com/docs/build-skills).

For a first installation on Windows, run this from the cloned repository; it stops before copying if any selected destination already exists:

```powershell
$skillNames = @('arm-cortex-expert', 'embedded-protocol-designer', 'embedded-test-engineer')
$skillDestination = Join-Path $env:USERPROFILE '.agents\skills'
foreach ($name in $skillNames) {
  if (Test-Path -LiteralPath (Join-Path $skillDestination $name)) {
    throw "Skill already exists; compare and back up before updating: $name"
  }
}
New-Item -ItemType Directory -Force -Path $skillDestination | Out-Null
foreach ($name in $skillNames) {
  Copy-Item -LiteralPath (Join-Path (Get-Location).Path $name) -Destination $skillDestination -Recurse -ErrorAction Stop
}
```

After installation, describe the task in natural language; the AI selects an installed skill automatically when possible. You can still force one with `$skill-name`. If it does not appear, check the directory layout and restart Codex. An existing deployment may use another loader-reported location; avoid installing duplicate copies blindly. DSH and Keil are not required for skill use.

For example, request firmware diagnosis directly:

```text
Use $arm-cortex-expert.
This existing STM32 + FreeRTOS acquisition project occasionally reads stale data
after DMA completion. Inspect the actual MCU, memory regions, cache maintenance
and buffer handoff. Establish the cause, then make the smallest supported fix.
Keep the existing sampling and communication contracts; report checks and gaps.
```

Or start directly with verification:

```text
Use $embedded-test-engineer to build replay regression for the existing filter
and calibration chain. Inspect data formats, references and allowed errors first,
then choose minimal test seams. Distinguish regression fidelity from measurement accuracy.
```

See [independent task and protocol examples](docs/workbench-usage.md#example).

### DSH (optional)

The [DSH guide](docs/workbench-usage.md#dsh) documents the installer. `./install.ps1` installs the preset under `$DSH_HOME/.agent-presets/embedded` (default `~/.dsh/.agent-presets/embedded`). It replaces managed plugin/script/skill trees and removes skill directories outside its distribution list; back up customizations first. This is not a Codex installer.

On Windows, `install.bat` is a double-click entry to the same installer. Choose the embedded preset in DSH. The current Windows MDK plugin offers `/build`, `/build -r`, `/build <alias>`, `/flash` and `/flash <alias>`. Build first, check its result, then invoke `/flash` separately when needed. Build/flash requires UV4, project configuration and the selected programmer; it is not supplied by copying skills. See [MDK usage (Chinese)](docs/mdk-build-flash.md).

### Tool entry points without hardware

Run from the repository root with Python 3.10+:

```sh
python arm-cortex-expert/tools/stm32cli/stm32cli.py --help
python arm-cortex-expert/tools/map-parser/map-parser.py --help
python embedded-test-engineer/scripts/check_state_model.py --help
```

Actual queries need a CubeMX database; map analysis needs a build artifact. State-graph lint is an optional specialist tool requiring an explicit model. See the [runnable positive and negative examples](docs/workbench-usage.md#tools).

## Tools and dependencies

| Tool | Requirements and reference |
|---|---|
| CubeMX query CLI | Python and a local CubeMX database; [reference](arm-cortex-expert/references/tools-stm32cli.md) |
| Keil map parser | Python and an armlink map file; [reference](arm-cortex-expert/references/tools-map-parser.md) |
| MDK wrapper/plugin | Windows, Keil UV4 and the selected flash backend; [guide](docs/mdk-build-flash.md) |
| Optional state-graph linter | Python 3.10+ standard library; [format and limits](embedded-test-engineer/references/state-model-format.md) |

Python 3.10+ is a common starting point for these tools. The recorded test environment is Python 3.14.2, not a full version/platform certification. Third-party compilers, databases and programmers are separately installed and licensed.

## Contributing and evidence

See [CONTRIBUTING.md](CONTRIBUTING.md) for a lightweight workflow and [AGENTS.md](AGENTS.md) for AI collaboration rules. [Behavior scenarios](docs/skill-behavior-cases.md) are evaluation criteria, not evidence of completed device tests. The [audit record](docs/skills-audit-2026-09-08.md) describes checks actually performed.

See also the [architecture](docs/architecture.md), [DSH integration](docs/dsh-integration.md) and [current integration checks](docs/integration-2026-09-10.md) (Chinese).

The [pre-release check record](docs/release-check-2026-09-10.md) lists the completed offline checks and remaining host/hardware validation (Chinese).

A graph pass does not prove scheduler, DMA/cache, FPGA CDC or physical safety behavior. Query/map tools also need cross-checking against the actual project and vendor evidence.

## License

[MIT](LICENSE). Report problems or propose improvements through [GitHub Issues](https://github.com/Fz2hOpenSource/firmware-forge/issues).
