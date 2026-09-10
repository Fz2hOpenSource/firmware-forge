# Executing Small and Growing Stateful Interactions

## Choose the Minimum Implementation

Begin with the agreed behavior and existing execution context. A small bounded
driver call can run directly in its owning command handler if it does not block
other timing obligations or wait for work dispatched by that same handler.
An owner is a responsibility, not necessarily a new RTOS task or framework.

For simple start/stop, define repeated inputs, failure effects and when hardware
is confirmed running/stopped. Introduce STARTING/STOPPING only if completion spans
events; do not hide asynchronous history in scattered flags or indefinite waits.
Configuration values and retry counts remain local data, with explicit bounds.

For channels that start together, use one acquisition state machine plus channel
selection. Independent channel lifecycles may reuse local instances. Shared clock,
bus, DMA and FPGA settings require their own ownership/coordination constraints;
a channel mask does not prove combinations are legal.

## Ownership and Snapshots

List authoritative fields, writer context, readers and lifetime. Derive busy or
mode flags instead of duplicating writable truth. Single-writer ownership alone
does not make a multi-field read consistent; publish a copied event, bounded locked
snapshot or versioned read suitable for the actual atomicity model.

Separate desired/applied/observed values only when their timing or meaning differs.
Attach freshness and epoch to observations where stale hardware reports are possible.
Do not assert steady-state invariants across partially completed transitions without
including phase and observation validity. Internal corruption needs diagnosis and
containment, not a default enum branch silently resetting to IDLE.

## Every Actual Wait Has an Executable Exit

For each asynchronous phase identify owner, expected evidence/identity, deadline,
failure/timeout branch and applicable cancellation/reset behavior. Draw waits through
tasks, queues, mutexes and buffers: A can deadlock waiting for B even without mutexes
if A holds the buffer/queue capacity that B needs to finish.

Do not hold a resource while waiting for another owner that needs that resource.
Do not synchronously wait inside the event loop that must dispatch completion.
Do not report ACCEPTED then silently lose the operation on queue-full; reserve or
serialize admission and check all effect/queue submission results.

Keep a monotonic deadline in the owner. Use the nearest deadline to bound receive
waits, check expiry between bounded dispatches, and define completion-vs-timeout
ordering at the boundary. A software timer posting to a full queue is not reliable
timeout execution. Timer callbacks must not block the timer service task.

Also inspect the worst driver block, interrupt masking and scheduling delay. If the
owner itself is stuck, local deadline checks cannot help; a separate supervisor or
verified independent protection must detect lack of meaningful progress. Idle and
running modes need different health criteria. Do not treat a heartbeat loop as proof
that acquisition, storage or a transition is advancing.

Use one retry owner and a non-renewed total operation deadline or decreasing budget.
Recovery must not create a fresh unlimited budget. Show bounded containment after
expiry if separately allowed. A persistent maintenance fault is a legitimate stable
boundary with explicit recovery conditions, not an automatic retry loop.

## Late Work and Resource Release

Tag asynchronous work with enough identity to reject old session/operation/phase
events. Decide old-attempt completion semantics from the effect contract. Already
recorded request results do not reverse when a late ACK arrives.

Queueing a descriptor copies the descriptor, not its pointed-to buffer. DMA must be
confirmed stopped before memory is reused. Epoch checks reject stale samples but
cannot prevent a still-active DMA engine from corrupting freed/reused memory.
Define owners on send failure, cancellation, timeout and delayed ISR callbacks.

For rate/profile changes affecting active data, quiesce affected producers, hand back
resources, apply and verify new interpretation, then publish matching-generation
data. Define filter continuity and first-valid-output behavior. If a change is atomic
and independent of active measurement, do not force this entire sequence.

## FPGA Boundary

Check the actual interface for payload publication/doorbell order, accepted vs done,
coherent multi-register snapshots, CDC handshake/FIFO, mailbox overwrite conditions,
and independent MCU/FPGA reset. Matching seq alone is insufficient if an epoch or
phase can be reused. CRC does not establish freshness or execution completion.

Do not guess register side effects, commands or reset behavior. Hardware-safe status
requires valid observation or a verified protection guarantee. If stopping cannot
be confirmed, report uncertainty and inhibit unsafe new work while following the
product's containment/supervision policy; setting SAFE in software is not evidence.

## Verify the Changed Path

Use existing host seams for state logic and virtual time where worthwhile; inject
missing/late completion, full queue, repeated stop and failed recovery. Retain
resource accounting. RTOS scheduling, DMA/cache and physical safety need appropriate
integration/target evidence. A finite graph exit is not proof that runtime can take it.
