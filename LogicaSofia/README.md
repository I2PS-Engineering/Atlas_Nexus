# LogicaSofia

A standalone, **Linux-first AI application** within the I2PS Engineering Atlas Nexus repository. The official name and directory are **LogicaSofia** (one word; capital L and S; no accent).

## Implementation status — v0.2.0

- Read-only Linux hardware inventory (`logicasofia inventory`).
- Local HTTP API bound **only to 127.0.0.1** (`logicasofia serve`).
- Truthful `GET /health` inference readiness and `GET /v1/models` listing.
- `POST /v1/chat/completions` proxy to a **separately installed and running**, OpenAI-compatible LOCAL inference server (non-streaming requests).
- No model, inference runtime or hardware selected or installed automatically. No hardcoded weights or fabricated responses.
- Standard-library Python runtime; automated tests include a stub model backend.

**Not production-ready:** no user authentication, streaming, remote clients, distributed scheduling, model download, data retention or hardened multitenancy. Do not expose this API publicly.

## Quick start (Linux, Python >=3.10)

~~~bash
cd LogicaSofia
PYTHONPATH=src python3 -m unittest discover -s tests -v
bash scripts/bootstrap.sh
source .venv/bin/activate
logicasofia inventory
logicasofia serve
~~~

In another shell:

~~~bash
curl -s http://127.0.0.1:8765/health
curl -s http://127.0.0.1:8765/v1/models
~~~

Without a model backend, the chat API returns HTTP 503 rather than pretending inference works.

To use an **already running** local OpenAI-compatible model server on port 8080:

~~~bash
logicasofia serve --backend-url http://127.0.0.1:8080
~~~

Request a real response (replace `<model-id>` with one returned by the local model listing):

~~~bash
curl -s http://127.0.0.1:8765/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"<model-id>","messages":[{"role":"user","content":"Hello"}],"stream":false}'
~~~

**Backend boundary:** The upstream URL must be `http://127.0.0.1:PORT` or `http://[::1]:PORT`. No DNS hostnames, remote endpoints, or redirects are accepted. Only model listing and non-streaming chat requests are forwarded.

## Architecture

LogicaSofia owns AI-specific inference APIs, model adapters and future evaluation/knowledge layers. **Orion Core, Data Core, Phoenix Core and Horizon Core remain distinct architectural subsystems**, not active dependencies. Older Atlas Nexus model and Kubernetes decisions are **not automatically approvals for LogicaSofia**.

See `docs/ARCHITECTURE.md` and `docs/DECISIONS.md`. Do not commit credentials, weights, private data or datasets.

**License:** Not yet selected. No public reuse rights are granted by this bootstrap.
