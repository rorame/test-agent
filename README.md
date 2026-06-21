# Crossing-Time Agent

A reasoning agent that answers quantitative real-world questions by gathering
facts from the external environment, reasoning step by step, computing with
code, and **verifying its own result** before answering.

Reference task:

> «Сколько понадобится времени гепарду, чтобы пересечь Москву-реку по Большому
> Каменному мосту?»
> *(How long does a cheetah need to cross the Moskva River via the Bolshoy
> Kamenny Bridge?)*

## How it works

The agent is built on [`deepagents`](https://github.com/langchain-ai/deepagents)
(LangChain) and reasons with this loop, driven by a loadable
[Skill](src/test_agent/skills/cheetah-bridge-crossing/SKILL.md):

1. **Plan** — `write_todos` lays out the steps.
2. **Retrieve** — `web_search` (Tavily) fetches real facts (bridge length,
   cheetah speed) *with sources*. Numbers are never recalled from memory.
3. **Interpret** — states assumptions explicitly: distance = the **bridge
   length** (traversing the bridge), not the river width.
4. **Compute** — the `execute` tool runs Python for all arithmetic and unit
   conversions (no mental math).
5. **Self-verify** — re-checks input ranges, unit consistency, recomputes a
   second way, and sanity-checks plausibility before answering.

It also surfaces the physics caveat that a cheetah's top speed is only
sustainable for a few hundred metres.

### Architecture

```
main.py ───────┐
               ├──> test_agent.agent (deepagents agent)
a2a_server.py ─┘     ├─ model:   GLM-5.2 via OpenRouter (env-swappable)
                     ├─ backend: LocalShellBackend (execute tool, local)
                     ├─ skills:  src/test_agent/skills/cheetah-bridge-crossing/SKILL.md
                     ├─ tools:   web_search (Tavily, typed pydantic schema)
                     └─ tracing: Langfuse (LangChain callback)
```

The project is an installable package under `src/test_agent/` (src-layout, built
with `uv_build`); `main.py` (CLI) and `a2a_server.py` live at the root and each
call `agent.ainvoke(...)` directly.

- **Agent** (`test_agent.agent`): builds the deepagents `agent` object.
- **Search** (`test_agent.tools.search`): a single `web_search` tool over Tavily
  with a typed `pydantic` args schema. A Wikipedia backend is planned for a later
  feature branch.
- **Config** lives in `test_agent.configs` (`configs.settings` typed
  `pydantic-settings` for all creds plus `ROOT_DIR`, `configs.agent` for
  model/tools/skills/prompt/tracing).

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python ≥ 3.11.

```bash
make install            # uv sync
cp .env.example .env    # then fill in your keys
```

Keys (`.env`):
- `OPENROUTER_API_KEY` — model gateway. Model is `OPENROUTER_MODEL`
  (default `z-ai/glm-5.2`), swappable to any OpenRouter model.
- `TAVILY_API_KEY` — web search backend.
- `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_HOST` — tracing
  (defaults target a local Langfuse at `http://127.0.0.1:3000`).

## Run

### Make targets

```bash
make run                 # default cheetah/bridge question (CLI)
make serve               # A2A server on http://127.0.0.1:9000
make docker-build        # build the image
make docker-run          # run the A2A server in Docker
```

### CLI

```bash
uv run python main.py                      # the default cheetah/bridge question
```

### A2A server (Google Agent-to-Agent protocol)

```bash
uv run python a2a_server.py                # http://127.0.0.1:9000
```

- Agent Card: `GET http://127.0.0.1:9000/.well-known/agent-card.json`
- JSON-RPC endpoint: `POST http://127.0.0.1:9000/` (method `SendMessage`)

Example call:

```bash
curl -s -X POST http://127.0.0.1:9000/ \
  -H 'Content-Type: application/json' -H 'A2A-Version: 1.0' -d '{
  "jsonrpc":"2.0","id":"1","method":"SendMessage",
  "params":{"message":{"messageId":"u1","role":"ROLE_USER",
    "parts":[{"text":"Сколько понадобится времени гепарду, чтобы пересечь Москву-реку по Большому Каменному мосту?"}]}}
}'
```

### Docker

```bash
make docker-build
make docker-run                                  # serves A2A on :9000
docker run --rm --env-file .env crossing-time-agent uv run python main.py   # one-off CLI
```

Keys are passed at runtime via `--env-file .env` (never baked into the image).

## Tracing

Every run is traced to [Langfuse](https://langfuse.com) via a LangChain callback
handler (`test_agent.configs.agent`), passed in the `callbacks` of each
`agent.ainvoke(...)` call. Set
`LANGFUSE_HOST`/`LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY` in `.env` to point at
your instance; the defaults assume a local Langfuse on `http://127.0.0.1:3000`.

## Notes & limitations

- `LocalShellBackend` runs the `execute` tool **on the host** (no sandbox
  isolation). Fine for this controlled task; swap in a hosted deepagents sandbox
  backend (E2B/Modal/Daytona/…) if isolation is needed.
- The answer is non-deterministic (LLM); the deterministic parts are the search
  tool, the code-run math, and the self-verification checks.
