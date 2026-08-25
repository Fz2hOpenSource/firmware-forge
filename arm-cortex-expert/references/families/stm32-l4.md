# STM32 L4

## Family Notes

- Good fit for fixed-point DSP, DMA-driven peripherals, and low-power designs.
- Typically no D-cache complexity like M7-class parts.
- Keep power and latency tradeoffs explicit.

## Practical Guidance

- Use DMA for continuous peripheral traffic.
- Keep FreeRTOS tasks lean if the project uses RTOS.
- Prefer reusable driver layers when the same peripheral may move across boards.
