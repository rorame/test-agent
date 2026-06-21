import uuid

import uvicorn
from google.protobuf.json_format import ParseDict
from starlette.applications import Starlette

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types.a2a_pb2 import AgentCard, Message
from a2a.utils.constants import DEFAULT_RPC_URL

from test_agent.agent import agent
from test_agent.configs.agent import LANGFUSE_HANDLER
from test_agent.configs.settings import settings

HOST = settings.a2a_host
PORT = settings.a2a_port

EXAMPLE_QUESTION = (
    "Сколько понадобится времени гепарду, чтобы пересечь "
    "Москву-реку по Большому Каменному мосту?"
)


def build_agent_card(public_url: str) -> AgentCard:
    """Public Agent Card describing this agent's single skill."""
    return ParseDict(
        {
            "name": "Crossing-Time Agent",
            "description": (
                "Estimates how long a moving animal needs to cross a structure "
                "(e.g. a cheetah across the Bolshoy Kamenny Bridge). Reasons "
                "step by step over web search and code execution, and verifies "
                "its own result before answering."
            ),
            "version": "0.1.0",
            "supported_interfaces": [
                {
                    "url": public_url,
                    "protocol_binding": "JSONRPC",
                    "protocol_version": "1.0",
                }
            ],
            "capabilities": {"streaming": False},
            "default_input_modes": ["text/plain"],
            "default_output_modes": ["text/plain"],
            "skills": [
                {
                    "id": "crossing-time",
                    "name": "Crossing-time estimation",
                    "description": (
                        "Compute how long an animal takes to traverse a bridge "
                        "or similar span, with explicit assumptions and a "
                        "self-verification step."
                    ),
                    "tags": ["reasoning", "estimation", "physics", "search"],
                    "examples": [EXAMPLE_QUESTION],
                }
            ],
        },
        AgentCard(),
    )


class CrossingTimeExecutor(AgentExecutor):
    """Bridges A2A requests to the deep agent's ``ainvoke`` call."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        question = context.get_user_input() or EXAMPLE_QUESTION
        thread_id = context.context_id or str(uuid.uuid4())

        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": question}]},
            config={
                "configurable": {"thread_id": thread_id},
                "callbacks": [LANGFUSE_HANDLER],
            },
        )
        answer = result["messages"][-1].content

        reply = ParseDict(
            {
                "message_id": str(uuid.uuid4()),
                "context_id": context.context_id or thread_id,
                "role": "ROLE_AGENT",
                "parts": [{"text": answer}],
            },
            Message(),
        )
        await event_queue.enqueue_event(reply)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("Cancellation is not supported.")


def build_app() -> Starlette:
    public_url = f"http://{HOST}:{PORT}{DEFAULT_RPC_URL}"
    card = build_agent_card(public_url)
    handler = DefaultRequestHandler(
        agent_executor=CrossingTimeExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=card,
    )
    routes = create_agent_card_routes(card) + create_jsonrpc_routes(
        handler, DEFAULT_RPC_URL
    )
    return Starlette(routes=routes)


app = build_app()


if __name__ == "__main__":
    print(f"A2A server on http://{HOST}:{PORT}  "
          f"(card: http://{HOST}:{PORT}/.well-known/agent-card.json)")
    uvicorn.run(app, host=HOST, port=PORT)
