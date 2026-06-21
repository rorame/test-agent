import asyncio

from test_agent.agent import agent
from test_agent.configs.agent import LANGFUSE_HANDLER

DEFAULT_QUESTION = (
    "Сколько понадобится времени гепарду, чтобы пересечь "
    "Москву-реку по Большому Каменному мосту?"
)


async def main() -> None:
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": DEFAULT_QUESTION}]},
        config={
            "configurable": {"thread_id": "cli"},
            "callbacks": [LANGFUSE_HANDLER],
        },
    )
    print(f"Q: {DEFAULT_QUESTION}\n")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
