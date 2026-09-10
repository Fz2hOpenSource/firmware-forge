# CubeMX Configuration Guide

## Overview

This guide provides configuration guidance for STM32 microcontrollers using CubeMX database.

Resolve `tools/stm32cli/stm32cli.py` relative to the installed
`arm-cortex-expert` skill directory, not the firmware project's current working
directory. The CLI accelerates lookup only; the project's `.ioc`, generated
code, selected CubeMX XML, reference manual, datasheet, and errata remain the
evidence of record.

## Configuration Workflow

Tool deployments may differ. Run the local CLI and subcommand `--help` first.
Use `--summary` and `ip-config` only when that installation supports them; otherwise
use available chip queries and inspect the exact MCU/IP XML directly. This guide
does not authorize replacing a working tool installation with another version.

### Step 1: MCU Selection

Use `stm32cli chip` to query MCU capabilities:

```bash
# Get chip info
python tools/stm32cli/stm32cli.py chip STM32H723ZGTx --summary

# List available MCUs
python tools/stm32cli/stm32cli.py chip --list --family STM32H7
```

Key parameters to consider:
- Core type (Cortex-M0+, M3, M4, M7)
- Frequency
- Flash/RAM size
- Package
- Peripheral availability

If the summary reports conflicting values from different CubeMX database
sources, retain the conflict in the diagnosis and verify it externally. Do not
silently choose whichever value is larger or more convenient.

### Step 2: Peripheral Configuration

Use `stm32cli peripheral` to query peripheral details:

```bash
# Get peripheral info
python tools/stm32cli/stm32cli.py spi STM32H723ZGTx SPI1

# List all peripherals
python tools/stm32cli/stm32cli.py peripheral STM32H723ZGTx --list
```

For each peripheral, check:
- DMA channels available
- Pin assignments
- Interrupt lines
- Features supported

### Step 3: DMA Configuration

Use `stm32cli dma` to query DMA mapping:

```bash
# Get DMA for specific request
python tools/stm32cli/stm32cli.py dma STM32H723ZGTx SPI1_RX

# List all DMA channels
python tools/stm32cli/stm32cli.py dma STM32H723ZGTx --list
```

DMA considerations:
- Channel availability
- Stream/controller mapping
- Priority levels
- Memory domain accessibility

### Step 4: Pin Configuration

Use `stm32cli pin` to query pin assignments:

```bash
# Get pins for peripheral
python tools/stm32cli/stm32cli.py pin STM32H723ZGTx SPI1

# List all pins
python tools/stm32cli/stm32cli.py pin STM32H723ZGTx --list
```

Pin considerations:
- Alternate function mapping
- Pin conflicts
- Board layout constraints

### Step 5: Interrupt Configuration

Use `stm32cli irq` to query interrupt information:

```bash
# Get interrupts for peripheral
python tools/stm32cli/stm32cli.py irq STM32H723ZGTx SPI1

# List all interrupts
python tools/stm32cli/stm32cli.py irq STM32H723ZGTx --list
```

Interrupt considerations:
- Priority levels
- Preemption priorities
- RTOS integration

### Step 6: IP Configuration Discovery

Use the exact MCU part when resolving an IP configuration file:

```bash
python tools/stm32cli/stm32cli.py ip-config SPI --mcu STM32H723ZGTx --parameter BaudRate
```

Do not use a family-only filename match as proof that an IP XML applies to the
target device. Confirm the IP `Version` referenced by the exact MCU XML.

## STM32 Family-Specific Notes

### STM32H7

- Critical: DMA memory domain restrictions
- DTCM, AXI-SRAM, SRAM1-4 are not interchangeable for DMA
- Cache coherency must be handled explicitly
- Ethernet DMA requires special attention

### STM32F4

- Simpler memory model
- DMA1/DMA2 only
- No cache concerns (no D-cache)

### STM32L0/L4

- Low-power considerations
- Limited DMA channels
- Peripheral clock gating important

## Configuration Validation

Before finalizing configuration:

1. Verify DMA channel availability
2. Check pin conflicts
3. Validate interrupt priorities
4. Confirm memory placement for DMA buffers
5. Check clock tree constraints

## Common Pitfalls

1. **DMA Memory Domain**: H7 requires specific memory regions for DMA
2. **Pin Conflicts**: Multiple peripherals on same pin
3. **Interrupt Priority**: RTOS syscall priority compliance
4. **Cache Coherency**: H7 D-cache must be managed
5. **Clock Limits**: Peripheral clock frequency constraints
