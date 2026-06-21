from langchain_core.tools import tool
from pydantic import BaseModel, Field
from tavily import TavilyClient

from test_agent.configs.settings import settings

_client = TavilyClient(api_key=settings.tavily_api_key)


class WebSearchInput(BaseModel):
    """Search the web for factual information (lengths, speeds, distances, etc.).

    Returns a short summary answer followed by a list of sources with URLs.
    Always cite the sources you rely on.
    """

    query: str = Field(description="The search query")
    max_results: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of results to return."
    )


@tool(args_schema=WebSearchInput)
def web_search(query: str, max_results: int = 5) -> str:
    resp = _client.search(
        query=query,
        max_results=max_results,
        include_answer=True
    )

    lines = []
    if resp.get("answer"):
        lines.append(f"Summary answer: {resp['answer']}\n")
    lines.append("Sources:")
    for i, r in enumerate(resp.get("results", []), 1):
        content = (r.get("content", "") or "").strip()
        lines.append(f"[{i}] {r.get('title', '')} — {r.get('url', '')}\n    {content}")
    return "\n".join(lines)
