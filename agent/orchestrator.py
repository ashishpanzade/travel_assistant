from langchain.agents import create_agent
from langchain_core.messages import AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from . import config
from .mcp_tools import get_mcp_tools
from .prompts import SYSTEM_PROMPT
from .rag import search_travel_knowledge_base


async def build_agent():
    config.require_api_key()
    llm = ChatGoogleGenerativeAI(model=config.GEMINI_MODEL, google_api_key=config.GOOGLE_API_KEY)
    tools = [search_travel_knowledge_base, *await get_mcp_tools()]
    return create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)


def tools_used(messages):
    calls = {}
    for m in messages:
        if isinstance(m, AIMessage):
            for call in m.tool_calls:
                calls[call["id"]] = call
    return [
        {"tool": calls[m.tool_call_id]["name"], "args": calls[m.tool_call_id]["args"]}
        for m in messages
        if isinstance(m, ToolMessage) and m.tool_call_id in calls
    ]
