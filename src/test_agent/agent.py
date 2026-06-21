from deepagents import create_deep_agent
from deepagents.backends.local_shell import LocalShellBackend
from deepagents.middleware._tool_exclusion import _ToolExclusionMiddleware

from test_agent.configs.settings import ROOT_DIR
from test_agent.configs.agent import (
    CHECKPOINTER,
    EXCLUDED_TOOLS,
    MODEL,
    SKILLS,
    SUBAGENTS,
    SYSTEM_PROMPT,
    TOOLS,
)

agent = create_deep_agent(
    model=MODEL,
    tools=TOOLS,
    system_prompt=SYSTEM_PROMPT,
    backend=LocalShellBackend(
        root_dir=str(ROOT_DIR), virtual_mode=False, inherit_env=True
    ),
    skills=SKILLS,
    checkpointer=CHECKPOINTER,
    subagents=SUBAGENTS,
    middleware=[_ToolExclusionMiddleware(excluded=EXCLUDED_TOOLS)],
)
