# LwIP and Ethernet Rules

Use this reference only for LwIP, Ethernet, TCP/IP upload, `netif`, `pbuf`, or STM32 ETH DMA work.

## Source Priority

- Prefer target project files first: `lwipopts.h`, `ethernetif.c`, `sys_arch.c`, CubeMX `.ioc`, linker script, MPU/cache setup, ETH DMA descriptor placement, and RTOS settings.
- Use local official references when available (LwIP docs, STM32H7 reference manual, CMSIS-FreeRTOS docs). If the user has a local documentation repository, ask for the path; do not assume a fixed location.
- Treat upstream LwIP as the standard behavior reference. Treat STM32Cube's bundled LwIP and `ethernetif.c` as the integration reference for the actual generated project.
- Do not replace a Cube project's bundled LwIP or CMSIS files just because a newer official reference exists.

## API and Threading

- Identify the API layer before changing code: raw API, netconn API, socket API, or project-local wrapper.
- Do not call LwIP core, socket, netconn, `pbuf_free`, packet formatting, or blocking network operations from ISR or DMA callbacks.
- For `NO_SYS=0`, raw/core API work needs TCP/IP-thread execution or the port's supported core-locking contract. A separate network task alone does not make raw calls legal. Netconn/socket APIs have their own thread and per-connection serialization rules; follow the bundled port. See the [upstream threading rules](https://www.nongnu.org/lwip/2_1_x/multithreading.html).
- For `NO_SYS=1`, keep LwIP calls in the main/super-loop context and service timers as required by the project.
- Keep acquisition timing separate from network throughput; Ethernet bandwidth does not prove deterministic sampling.

## TX Progress and Retry Semantics

- Treat API acceptance, stack enqueue, driver submission, DMA completion, descriptor reclaim, wire transmission, and TCP acknowledgment as different events. `tcp_write`, `netconn_write`, a successful socket `send`, or `linkoutput` enqueue does not by itself prove that bytes reached the wire.
- Handle partial socket or stream writes by advancing only by the returned byte count. Preserve the unsent suffix, use a bounded deadline, and record short-write, would-block, zero-progress, timeout, reconnect, and discarded-backlog counters.
- Track no-progress age as elapsed time since the last forward progress, not only retry count. A loop that repeatedly returns `ERR_MEM`, `ERR_WOULDBLOCK`, zero bytes, or an unchanged descriptor index must yield or wait on an event and must terminate or recover at a documented deadline.
- Inspect `linkoutput` and lower-driver retry loops for busy polling, unbounded descriptor waits, and retries from the TCP/IP thread. Keep retries bounded and make link-down, DMA-stall, and descriptor-exhaustion recovery explicit; never let them indefinitely block acquisition or the LwIP core.
- When zero-copy TX is used, retain the backing buffer until the actual driver/DMA ownership release point. Do not free or reuse it merely because enqueue succeeded.
- Expose separate counters or timestamps for application enqueue, stack rejection/partial write, driver submit, DMA complete/reclaim, retry/no-progress age, link-down drop, and TCP acknowledgment when the API makes acknowledgment observable.

## Pbuf Ownership

- Make `pbuf` ownership explicit: who allocates, who references, who may mutate payload, and who frees.
- Do not read live DMA RX buffers directly from application or network code unless ownership has transferred and cache maintenance is complete.
- For zero-copy RX, tie DMA descriptor buffer lifetime to `pbuf` lifetime and release the descriptor only after the final `pbuf_free`.
- For TX, do not let DMA read from stack memory, temporary packet buffers, or mutable application buffers after `linkoutput` returns unless the driver copies or owns the data.
- Count allocation failures, dropped packets, descriptor starvation, link-down drops, and TX/RX DMA errors.

## STM32H7 ETH DMA and Cache

- Place ETH DMA descriptors and RX/TX buffers in DMA-accessible memory, not DTCM when the ETH DMA cannot access it.
- Align descriptors and buffers to cache-line boundaries when D-cache is enabled.
- Use verified non-cacheable regions when practical. For cacheable TX, clean before handoff; for RX, ensure dedicated target lines cannot write back stale dirty data over DMA writes before arming, then invalidate completed data before CPU reads. Descriptor ownership/status needs its own ordering and cache handling; payload maintenance alone is insufficient.
- Do not share a cache line between DMA-owned packet buffers and unrelated CPU-owned data.
- Verify `lwipopts.h` memory sizing (`MEM_SIZE`, `PBUF_POOL_SIZE`, `PBUF_POOL_BUFSIZE`, mailbox sizes) against worst-case burst and consumer latency.

## Review Checklist

- Confirm `ethernetif.c` does not call LwIP from ISR context.
- Confirm `linkoutput` and RX input paths preserve `pbuf` lifetime rules.
- Confirm link status, DHCP/static IP, and reconnection paths have bounded behavior.
- Confirm network backpressure cannot block high-priority acquisition or control paths indefinitely.
- Confirm partial writes preserve the unsent suffix and every retry/no-progress loop has a wait condition, deadline, and observable recovery result.
- Confirm diagnostics distinguish enqueue success from driver/DMA completion or other evidence of actual transmission.
- Confirm project diagnostics expose packet drops, pbuf allocation failures, descriptor exhaustion, and link state changes.
