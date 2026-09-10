# Firmware Forge · Embedded Skills and Workbench

[中文](README.md) · [Usage guide (Chinese)](docs/workbench-usage.md) · [Design philosophy](docs/design-philosophy.md) · [Contributing](CONTRIBUTING.md)

Three independent skills for AI-assisted **STM32 / Cortex-M firmware, FreeRTOS and MCU–FPGA interaction design**, with an optional DSH build/flash workbench.

Define requirements first, choose the smallest complete interaction, then implement and verify it. Start with simple upload control and add mechanisms only when multichannel acquisition, asynchronous work or recovery requirements need them.

## Choose a skill

| Task | Skill | Main output |
|---|---|---|
| Define or evolve device-to-host/FPGA interaction | [embedded-protocol-designer](embedded-protocol-designer/SKILL.md) | Behavior, commands/states, duplicate/failure semantics and compatibility |
| Implement or debug acquisition, DMA, tasks and transition exits | [arm-cortex-expert](arm-cortex-expert/SKILL.md) | Code, ownership, execution bounds and platform checks |
| Verify parsers, event sequences, replay and recovery | [embedded-test-engineer](embedded-test-engineer/SKILL.md) | Relevant tests, results and remaining hardware gaps |

Load only the skills needed for the task. These are engineering instructions and helper tools, not a runtime protocol stack or a universal state-machine engine.

## Design philosophy

**Reliability improvements should make failures more controllable without making ordinary development progressively harder.**

Agree on behavior and acceptance criteria; use the minimum sufficient design; give real state a clear owner and actual waits an endpoint. Extend affected parts as requirements grow. Evaluate maintainability and observable behavior rather than enum count. Separate design, implementation, test and hardware evidence.

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

Select an installed skill or mention it explicitly in your firmware project. If it does not appear, check the directory layout and restart Codex. An existing deployment may use another loader-reported location; avoid installing duplicate copies blindly. DSH and Keil are not required for skill use.

```text
Use $embedded-protocol-designer.
The device uses STM32 + FreeRTOS with one controlling host.
It needs START, STOP and STATUS. STOP ends both acquisition and upload.
No runtime parameter changes are needed; synchronized channels may be added later.
Inspect existing project contracts, then propose the minimum behavior table,
duplicate-command and failure handling. List missing facts and verification needs.
Design only at this stage; do not prebuild a framework for future requirements.
```

Expect a small requirements/behavior contract and explicit completion/failure semantics. Real asynchronous waits need local phases and deadlines; bounded driver behavior still needs project evidence. After agreeing on the design, request implementation with the firmware skill and relevant verification with the test skill.

### DSH (optional)

The [DSH guide](docs/workbench-usage.md#dsh) documents the installer. `./install.ps1` installs the preset under `$DSH_HOME/.agent-presets/embedded` (default `~/.dsh/.agent-presets/embedded`). It replaces managed plugin/script/skill trees and removes skill directories outside its distribution list; back up customizations first. This is not a Codex installer.

On Windows, `install.bat` is a double-click entry to the same installer. Choose the embedded preset in DSH. The current Windows MDK plugin offers `/build`, `/build -r` and `/flash`, with an optional project alias. Build/flash requires UV4, project configuration and the selected programmer; it is not supplied by copying skills. See [MDK usage (Chinese)](docs/mdk-build-flash.md).

### Try a tool without hardware

Use Python 3.10+ from the repository root; no AI host or board is needed:

```sh
python embedded-test-engineer/scripts/check_state_model.py embedded-test-engineer/assets/reconfigure-model.json --json --strict
python embedded-test-engineer/scripts/check_state_model.py embedded-test-engineer/assets/stuck-model.json --json --strict
```

The first example should emit `gate_status: pass` and exit `0`. The second intentionally contains a timeout recovery cycle: expect `TIMEOUT_CYCLE` and exit `1`. Run it as an expected failure, not a successful step in a fail-fast script.

## Tools and dependencies

| Tool | Requirements and reference |
|---|---|
| State-graph linter | Python 3.10+ standard library; [format and limits](embedded-test-engineer/references/state-model-format.md) |
| CubeMX query CLI | Python and a local CubeMX database; [reference](arm-cortex-expert/references/tools-stm32cli.md) |
| Keil map parser | Python and an armlink map file; [reference](arm-cortex-expert/references/tools-map-parser.md) |
| MDK wrapper/plugin | Windows, Keil UV4 and the selected flash backend; [guide](docs/mdk-build-flash.md) |

Python 3.10+ is a common starting point for these tools. The recorded test environment is Python 3.14.2, not a full version/platform certification. Third-party compilers, databases and programmers are separately installed and licensed.

## Contributing and evidence

See [CONTRIBUTING.md](CONTRIBUTING.md) for a lightweight workflow and [AGENTS.md](AGENTS.md) for AI collaboration rules. [Behavior scenarios](docs/skill-behavior-cases.md) are evaluation criteria, not evidence of completed device tests. The [audit record](docs/skills-audit-2026-09-08.md) describes checks actually performed.

See also the [architecture](docs/architecture.md), [DSH integration](docs/dsh-integration.md) and [current integration checks](docs/integration-2026-09-10.md) (Chinese).

A graph pass does not prove scheduler, DMA/cache, FPGA CDC or physical safety behavior. Query/map tools also need cross-checking against the actual project and vendor evidence.

## License

[MIT](LICENSE). Report problems or propose improvements through [GitHub Issues](https://github.com/Fz2hOpenSource/firmware-forge/issues).
