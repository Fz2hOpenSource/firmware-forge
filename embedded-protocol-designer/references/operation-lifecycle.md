# Asynchronous Operations and Uncertain Outcomes

Use this reference only when an interaction outlives the immediate exchange,
supports retries/reconnect, or can lose an irreversible result. A synchronous
bounded command need not acquire a general request ledger or transaction engine.

## Acceptance and Result

Define what ACCEPTED promises: validation, execution slot and result record, and
whether acceptance survives reset. Resource-full rejection precedes side effects.
Revalidate state-dependent conditions at execution or reserve them at admission.

Choose the smallest useful result vocabulary. One option is ACCEPTED/RUNNING then
SUCCEEDED/FAILED/CANCELLED/INDETERMINATE. Indeterminate means automatic operation
processing ended without sufficient effect evidence; attach effect certainty,
hardware safety confirmation and next action. It is not a successful recovery.

A host timeout creates local uncertainty, not a device-authored failure. Stop an
unbounded UI spinner with an explicit unknown outcome and a bounded query/reconnect
path. Notifications may accelerate progress; retained result/status queries provide
recovery after notification loss. Queries need service capacity even while busy.

## Correlation and Duplicates

Select identities to distinguish requests that can coexist or arrive late: target,
boot/session epoch, client request, suboperation phase and, if needed, attempt.
Do not require every field on every protocol. Show why reused IDs cannot make a
stale response advance a new operation; single-flight alone does not establish it.

Same key and equivalent payload returns existing progress/result. Same key with
different payload is a conflict. Bound the dedup/result table and retention window;
do not evict active entries to accept more work. Expired/not-found results do not
prove non-execution. Identity/digest/CRC are not a substitute for authentication.

Define handling of old-attempt responses for the same operation: an old completion
may remain valid under an idempotent effect contract, whereas an old failure must
not abort a later successful attempt. Reject obsolete phases/epochs and never
reverse a recorded request terminal; publish later observations separately.

## Restart and Reconciliation

After reconnect check device identity, boot epoch, capabilities and a consistent
snapshot before replaying pending work. MCU reset does not imply FPGA reset.
Define what request records, configuration and data generations survive each reset.

RAM dedup does not protect across reboot. Durable operation logs also have crash
windows around external effects. Claim exactly-once only with a justified end-to-end
commit/idempotency mechanism; otherwise reconcile or report uncertainty and do not
automatically repeat a non-idempotent action. A current register value may not prove
whether a past pulse/calibration/erase happened.

Epoch uniqueness and sequence comparison need a defined lifetime/window and wrap
policy. Cross-epoch values are not ordered by ordinary integer comparison.

## Cancellation and Recovery

CANCEL of an operation and STOP of a producer are different possible contracts.
Define irreversible points, cancel-vs-completion ordering, and resource cleanup.
Cancelling a host wait does not prove cancellation of a device effect.

Each retry/recovery consumes a finite count or a non-renewed total deadline.
An expired operation may use a separately declared bounded containment interval.
BUSY or heartbeat is not effective progress and cannot silently renew budgets.
Compensation can fail; never assume arbitrary hardware work is rollbackable.

Publish hardware-safe only from valid observation or a verified independent
protection guarantee. If that evidence is unavailable, preserve the unknown fact,
inhibit unsafe new work and invoke the product's supervision/containment policy.
Do not invent reset/disable commands or assume a reset makes outputs safe.

## Evidence

For new protocol mechanisms retain examples for lost completion, duplicate same/different
payload, reboot with a late ACK, expired results, cancellation races and failed
recovery. Test only mechanisms present in the design. The test skill turns these
contracts into event-sequence tests; byte-level parser fixtures alone are insufficient.
