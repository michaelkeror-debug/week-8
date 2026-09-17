"""Route A: MCP health is a client handshake, not an HTTP port.

Initialise, list_tools(), read version://current, assert check_stock and semver.
The stdio MCP from Monday has no port and no /health route.
"""

import asyncio
import sys

EXPECTED_TOOLS = {"check_stock"}
EXPECTED_VERSION_PREFIX = "1."


async def handshake() -> int:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command=sys.executable,
        args=["logistics_mcp_versioned.py"],
    )

    async with (
        stdio_client(params) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()

        tools = {tool.name for tool in (await session.list_tools()).tools}
        version = await session.read_resource("version://current")
        text = getattr(version, "contents", version)

        print("tools", sorted(tools), "version", text)


        if not str(text).startswith(EXPECTED_VERSION_PREFIX):
            print("invalid version", text)
            return 1

        if not EXPECTED_TOOLS.issubset(tools):
            print("missing tools", EXPECTED_TOOLS - tools)
            return 1

        return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(handshake()))