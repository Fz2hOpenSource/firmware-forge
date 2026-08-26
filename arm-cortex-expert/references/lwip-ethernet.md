# LwIP and Ethernet Rules

Use this reference only for LwIP, Ethernet, TCP/IP upload, `netif`, `pbuf`, or STM32 ETH DMA work.

## Source Priority

- Prefer target project files first: `lwipopts.h`, `ethernetif.c`, `sys_arch.c`, CubeMX `.ioc`, linker script, MPU/cache setup, ETH DMA descriptor placement, and RTOS settings.
- Use local official reference indexes when the user provides them (for example local LwIP, STM32, or CMSIS-FreeRTOS checkouts containing an `AI_INDEX.md`); ask for their paths rather than assuming machine-specific locations.
- Treat upstream LwIP as the standard behavior reference. Treat STM32Cube's bundled LwIP and `ethernetif.c` as the integration reference for the actual generated project.
- Do not replace a Cube project's bundled LwIP or CMSIS files just because a newer official reference exists.

## API and Threading

- Identify the API layer before changing code: raw API, netconn API, socket API, or project-local wrapper.
- Do not call LwIP core, socket, netconn, `pbuf_free`, packet formatting, or blocking network operations from ISR or DMA callbacks.
- For `NO_SYS=0`, hand work to the TCP/IP thread with project-approved mechanisms such as `tcpip_callback`, mailbox, queue, or a network task.
- For `NO_SYS=1`, keep LwIP calls in the main/super-loop context and service timers as required by the project.
- Keep acquisition timing separate from network throughput; Ethernet bandwidth does not prove deterministic sampling.

## TX Progress and Retry Semantics

- Treat application acceptance, stack enqueue, driver submission, DMA completion, descriptor reclaim, wire transmission, and TCP acknowledgment as different events. A successful `send`, `netconn_write`, `tcp_write`, or `linkoutput` enqueue does not prove final delivery.
- Handle partial stream writes by advancing only by the returned byte count and retaining the unsent suffix.
- Track no-progress age as elapsed time since forward progress, not just retry count. Repeated `ERR_MEM`, would-block, zero-byte writes, or unchanged descriptor state must wait/yield and terminate or recover at a documented deadline.
- Keep linkoutput and driver retry loops bounded. Link-down, DMA-stall, and descriptor-exhaustion recovery must not indefinitely block acquisition, control traffic, or the TCP/IP thread.
- For zero-copy TX, retain the backing storage until the actual driver/DMA ownership release point.
- Expose distinct counters for application enqueue, short/rejected writes, driver submit, DMA completion/reclaim, no-progress timeout, link-down discard, and acknowledgment where observable.

## Pbuf Ownership

- Make `pbuf` ownership explicit: who allocates, who references, who may mutate payload, and who frees.
- Do not read live DMA RX buffers directly from application or network code unless ownership has transferred and cache maintenance is complete.
- For zero-copy RX, tie DMA descriptor buffer lifetime to `pbuf` lifetime and release the descriptor only after the final `pbuf_free`.
- For TX, do not let DMA read from stack memory, temporary packet buffers, or mutable application buffers after `linkoutput` returns unless the driver copies or owns the data.
- Count allocation failures, dropped packets, descriptor starvation, link-down drops, and TX/RX DMA errors.

## STM32H7 ETH DMA and Cache

- Place ETH DMA descriptors and RX/TX buffers in DMA-accessible memory, not DTCM when the ETH DMA cannot access it.
- Align descriptors and buffers to cache-line boundaries when D-cache is enabled.
- Use non-cacheable MPU regions for descriptors/buffers when practical; otherwise clean TX buffers before DMA and invalidate RX buffers after DMA completes and before CPU reads.
- Do not share a cache line between DMA-owned packet buffers and unrelated CPU-owned data.
- Verify `lwipopts.h` memory sizing (`MEM_SIZE`, `PBUF_POOL_SIZE`, `PBUF_POOL_BUFSIZE`, mailbox sizes) against worst-case burst and consumer latency.

## Review Checklist

- Confirm `ethernetif.c` does not call LwIP from ISR context.
- Confirm `linkoutput` and RX input paths preserve `pbuf` lifetime rules.
- Confirm link status, DHCP/static IP, and reconnection paths have bounded behavior.
- Confirm network backpressure cannot block high-priority acquisition or control paths indefinitely.
- Confirm partial writes preserve the unsent suffix and every retry/no-progress loop has a wait condition, deadline, and observable recovery result.
- Confirm diagnostics distinguish application/stack acceptance from driver or DMA progress.
- Confirm project diagnostics expose packet drops, pbuf allocation failures, descriptor exhaustion, and link state changes.
