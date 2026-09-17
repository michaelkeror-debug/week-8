"""Route a: MCP health is a client handshake, not an HTTP port.

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
        contents = getattr(version, "contents", version)

        # normalize to a list
        if not isinstance(contents, list):
            contents = [contents]

       
        version_text = None
        for item in contents:
            text = getattr(item, "text", None)
            if text is not None:
                version_text = text.strip()
                break

        if version_text is None:
            print("invalid version", contents)
            return 1

        print("tools", sorted(tools), "version", version_text)

        if not version_text.startswith(EXPECTED_VERSION_PREFIX):
            print("invalid version", version_text)
            return 1

        if not EXPECTED_TOOLS.issubset(tools):
            print("missing tools", EXPECTED_TOOLS - tools)
            return 1

        return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(handshake()))