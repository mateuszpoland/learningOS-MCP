from mcp.server.fastmcp import FastMCP

mcp = FastMCP("learningOS")


# --- MCP Tools (COMMENTED OUT until deployment is verified) ---

# @mcp.tool()
# async def get_learning_context() -> str:
#     """Reads the master_knowledge_graph.md from Google Drive."""
#     ...

# @mcp.tool()
# async def update_learning_map(content: str) -> str:
#     """Appends data to master_knowledge_graph.md on Google Drive."""
#     ...


def main():
    """Entry point – starts the MCP server with SSE transport."""
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
