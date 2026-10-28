# LogicaSofia — Architecture v0.2.0

## Software boundaries

- **LogicaSofia:** AI-facing local API, model adapters, future evaluation and knowledge retrieval.
- **Orion Core:** separate orchestration and scheduling subsystem; later integration.
- **Data Core:** separate data and persistent storage subsystem; later integration.
- **Phoenix Core:** separate failover and recovery subsystem; later integration.
- **Horizon Core:** separate resource-monitoring and optimization subsystem; later integration.

The latter four are **not implemented by this component**; the app does not depend on them or modify existing Atlas services.

## Implemented request flow

~~~text
Linux localhost client
   |
   | HTTP 127.0.0.1:8765
   v
LogicaSofia gateway
   |-- GET /health: gateway status + model readiness
   |-- GET /v1/models: configured model listing or empty
   |-- POST /v1/chat/completions: JSON validation, 1 MiB cap,
   |                              stream:false only
   v
Optional local OpenAI-compatible inference server
   |  explicit URL, 127.0.0.1 or ::1 only
   v
Real model (installed and operated separately)
~~~

## Not implemented

Model downloads, model selection, training, vector databases, user sessions, authentication, GPU scheduling, distributed inference, HA and production access controls. No generated AI answers are possible without a real backend.

## Integration and safety rules

No hardcoded model, public network binding, automatic model download, credentials or remote inference URL. Backend URLs are validated; backend HTTP calls do not follow redirects. Authentication, TLS and access policy are prerequisites for any future remote access.
