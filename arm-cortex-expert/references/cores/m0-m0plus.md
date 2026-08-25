# M0 and M0+

## Key Constraints

- No cache maintenance.
- Limited interrupt and exception features compared with M3/M4/M7.
- Keep RAM usage low and avoid large buffers unless required.
- Prefer simple critical sections and minimal ISR work.
- Avoid assuming DSP or FPU acceleration.

## Recommended Patterns

- Use small fixed-size buffers.
- Prefer blocking or simple interrupt-driven drivers when throughput is modest.
- Use integer arithmetic and lightweight state machines.
- Keep memory barriers and priority rules simple unless the target platform requires more.

## Common Risks

- Stack overflow from oversized buffers.
- Hidden latency from long interrupt handlers.
- Overengineering with abstractions that cost too much RAM or flash.
