import asyncio

import gradio as gr
from langchain_core.messages import AIMessage, HumanMessage

from agent.orchestrator import build_agent, tools_used

FOOTER = "\n\n---\nTools used: "

print("Starting up (connecting to the MCP servers)...")
agent = asyncio.run(build_agent())


def to_text(content):
    # gradio sometimes hands message content back as a list of parts
    if isinstance(content, list):
        return "".join(p["text"] if isinstance(p, dict) else p for p in content)
    return content


async def respond(message, history):
    messages = []
    for turn in history:
        text = to_text(turn["content"]).split(FOOTER)[0]
        messages.append(HumanMessage(text) if turn["role"] == "user" else AIMessage(text))
    messages.append(HumanMessage(message))

    result = await agent.ainvoke({"messages": messages})
    answer = result["messages"][-1].text

    used = tools_used(result["messages"])
    if used:
        answer += FOOTER + ", ".join(f"`{t['tool']}`" for t in used)
    return answer


demo = gr.ChatInterface(
    respond,
    title="Singapore Travel Assistant",
    description="Ask about attractions, transport, food and itineraries, or check the weather and convert currency.",
    examples=[
        "What are the must-visit attractions in Singapore?",
        "Which neighbourhoods are good for a cultural experience?",
        "What is the weather forecast for Singapore for the next 3 days?",
        "Convert INR 50000 to SGD",
        "Plan a three-day trip to Singapore and adjust the activities based on the weather forecast",
    ],
)

if __name__ == "__main__":
    demo.launch()
