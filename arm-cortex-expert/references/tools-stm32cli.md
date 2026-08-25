# stm32cli — CubeMX Database Query Tool

Companion CLI shipped in `tools/stm32cli/`. Resolve its absolute path via
the skill's `Tool Path Resolution` rules. It is an experimental accelerator,
not an authority: project artifacts and vendor documentation win on any
conflict, and stale or implausible output must be cross-checked against the
underlying XML (`db/mcu/families.xml`, `<MCU>.xml`, `IP/*.xml`).

Use `stm32cli` to query STM32 chip-specific information from CubeMX database. Resolve the script path as described in `Tool Path Resolution` above.

### Experimental Status and Source Fallback

`stm32cli` is an experimental lookup accelerator, not an authoritative source. Its output may be incomplete, stale, or incorrect because of parser limitations, cache state, unsupported CubeMX database revisions, or ambiguous MCU/peripheral naming.

- Treat the target project's `.ioc`, bundled generated code, linker and build configuration, CubeMX database XML, and vendor reference manual, datasheet, and errata as stronger evidence than `stm32cli` output.
- If a command fails, omits expected data, returns an implausible value, or conflicts with project or vendor evidence, stop relying on that result. Clear the CLI cache when stale data is plausible, then inspect the underlying CubeMX source files directly instead of repeatedly querying the tool.
- Resolve the database root from `--db-path` or `tools/stm32cli/config.py`, select the applicable database version, and inspect the relevant XML under `db/mcu/`: `families.xml`, `<MCU-name>.xml`, and `IP/*.xml`.
- Do not modify firmware, middleware, or generated code merely to match an unverified CLI result. State the discrepancy and base the conclusion on the source files and official documentation.
- Debug or patch `stm32cli` itself only when the task explicitly includes improving the experimental tool; keep tool fixes separate from firmware diagnostic changes.

### CLI Commands

```bash
# Query chip info
python tools/stm32cli/stm32cli.py chip STM32H723ZGTx

# List MCUs by family/core
python tools/stm32cli/stm32cli.py chip --list --family STM32H7 --core Cortex-M7

# Query peripheral info
python tools/stm32cli/stm32cli.py spi STM32H723ZGTx SPI1
python tools/stm32cli/stm32cli.py adc STM32H723ZGTx ADC1

# List all peripherals
python tools/stm32cli/stm32cli.py peripheral STM32H723ZGTx --list

# Query DMA mapping
python tools/stm32cli/stm32cli.py dma STM32H723ZGTx SPI1_RX

# List all DMA channels
python tools/stm32cli/stm32cli.py dma STM32H723ZGTx --list

# Query pin mux
python tools/stm32cli/stm32cli.py pin STM32H723ZGTx SPI1

# List all pins
python tools/stm32cli/stm32cli.py pin STM32H723ZGTx --list

# Query clock info
python tools/stm32cli/stm32cli.py clock STM32H723ZGTx

# Query interrupt info
python tools/stm32cli/stm32cli.py irq STM32H723ZGTx SPI1

# List all interrupts
python tools/stm32cli/stm32cli.py irq STM32H723ZGTx --list
```

### Integration Workflow

1. Use `chip` to get MCU capabilities (core, frequency, RAM, peripherals)
2. Use `peripheral` to get peripheral configuration (DMA, pins, features)
3. Use `dma` to verify DMA channel availability
4. Use `pin` to check pin assignments
5. Use `irq` to get interrupt information
6. Generate configuration based on actual hardware capabilities

### Cache

The tool caches results in `~/.stm32cli_cache/`. To clear cache:

```bash
python tools/stm32cli/stm32cli.py --clear-cache
```


## Family Quick Notes (configuration)

| Family | Watch points |
|---|---|
| STM32H7 | DMA memory-domain restrictions (DTCM vs AXI-SRAM vs SRAM1-4 not interchangeable); explicit cache coherency; Ethernet DMA |
| STM32F4 | simpler memory model; DMA1/DMA2 only; no D-cache concerns |
| STM32L0/L4 | low-power constraints; fewer DMA channels; peripheral clock gating |

Before finalizing any configuration: verify DMA channel availability, pin
conflicts, interrupt priorities vs RTOS syscall limits, DMA buffer memory
placement, and clock-tree limits.
