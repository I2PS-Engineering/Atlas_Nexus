# LogicaSofia — Engineering decisions

## LS-001 — Project identity (2026-10-28)

**Accepted:** LogicaSofia, one word, capital L and S, no accent. Python package `logicasofia`.

## LS-002 — Repository placement (2026-10-28)

**Accepted:** Develop under `LogicaSofia/` inside `I2PS-Engineering/Atlas_Nexus`. Preserve other directories. This supersedes the earlier request to create a standalone repository.

## LS-003 — Independent Linux AI software

**Accepted:** AI app operates standalone. Orion Core, Data Core, Phoenix Core and Horizon Core are separate and will be integrated later.

## LS-004 — Model-neutral bootstrap

**Accepted for bootstrap:** A pluggable localhost inference adapter. Do not silently inherit model, hardware or Kubernetes commitments from older Atlas documentation. Benchmark before committing to a first model.

## LS-005 — Truthful readiness

**Accepted:** Without an actual local model backend, the chat API must return 503. Never fabricate model responses or claim production readiness.

## LS-006 — Local networking

**Accepted:** Bind the unauthenticated API to localhost only and reject remote inference-backend URLs. No secrets or weights in Git.
