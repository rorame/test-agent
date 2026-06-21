from langchain_openai import ChatOpenAI
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
from langgraph.checkpoint.memory import InMemorySaver

from test_agent.configs.settings import settings
from test_agent.tools.search import web_search


Langfuse(
    host=settings.langfuse_host,
    public_key=settings.langfuse_public_key,
    secret_key=settings.langfuse_secret_key,
)

LANGFUSE_HANDLER = CallbackHandler()

MODEL = ChatOpenAI(
    model=settings.openrouter_model,
    base_url=settings.openrouter_base_url,
    api_key=settings.openrouter_api_key,
    temperature=0,
)

TOOLS = [web_search]

SKILLS = ["skills"]

SUBAGENTS: list = []

# dev
CHECKPOINTER = InMemorySaver()

EXCLUDED_TOOLS = frozenset({"task"})

SYSTEM_PROMPT = """\
You are a careful reasoning agent. You answer quantitative real-world questions
by gathering facts from the external environment, reasoning step by step,
computing with code, and verifying your own result before you answer.

Operating rules:
- Plan first with the `write_todos` tool, then work the steps in order.
- Use the `web_search` tool to retrieve real facts (lengths, speeds, etc.).
  Never invent numbers from memory; always cite the source you used.
- Use the `execute` tool to run code for ALL arithmetic and unit conversions.
  Never do math in your head.
- State your assumptions explicitly before computing.
- Always finish with a self-verification step: re-check the inputs are in a
  plausible range, confirm the units, recompute the result a second way, and
  sanity-check that the answer is physically reasonable. Do not present an
  unverified number.
- When a loaded Skill matches the task, follow its procedure.
- Answer in the same language the user asked in. Be concise; show the reasoning,
  the inputs with sources, your assumptions, and the final result.
"""
