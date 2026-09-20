import sys

from langchain_mcp_adapters.client import MultiServerMCPClient

from . import config


async def get_mcp_tools():
    servers = {
        name: {
            "command": sys.executable,
            "args": [str(config.MCP_SERVERS_DIR / f"{name}_server.py")],
            "transport": "stdio",
        }
        for name in ("weather", "currency")
    }
    return await MultiServerMCPClient(servers).get_tools()
