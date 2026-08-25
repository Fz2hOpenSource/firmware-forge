# STM32 L0

## Family Notes

- Treat this as a low-power, low-resource target.
- Prefer simple driver state machines and compact buffers.
- Avoid assuming DSP acceleration, cache, or high-throughput DMA use cases.

## Practical Guidance

- Keep init code short.
- Use the smallest viable data path.
- Favor clarity over layering if the project is tiny, but keep board glue separate from driver logic.
