import logging
import os

from dotenv import load_dotenv

load_dotenv()

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from learningos_mcp.gdrive_client import GDriveManager

logger = logging.getLogger("learningOS-MCP")

mcp = FastMCP("learningOS", host="0.0.0.0", port=int(os.getenv("PORT", "8080")))


class UpdateLearningMapPayload(BaseModel):
    topic_id: str
    content: str
    mastery_delta: int


@mcp.tool()
async def get_knowledge_graph(query: str) -> str:
    """Reads the master_knowledge_graph.md from Google Drive."""
    manager = GDriveManager.get_instance()
    return await manager.async_read_master_knowledge_graph()


@mcp.tool()
async def update_learning_map(topic_id: str, content: UpdateLearningMapPayload) -> str:
    """Appends data to master_knowledge_graph.md on Google Drive."""
    manager = GDriveManager.get_instance()
    current_content = await manager.async_read_master_knowledge_graph()
    new_entry = f"\n## **{topic_id}**:\n{content.content}\nMastery Level(progress update): {content.mastery_delta}"
    new_content = current_content + new_entry
    await manager.async_write_master_knowledge_graph(new_content)
    return f"Updated learning map for topic {topic_id} in the Master Knowledge Map"


def main():
    """Entry point – starts the MCP server with SSE transport."""
    try:
        GDriveManager.get_instance()
        logger.info("GDriveManager initialised – starting SSE server on 0.0.0.0:%s", os.getenv("PORT", "8080"))
        mcp.run(transport="sse")
    except Exception as e:
        logger.error("Critical MCP system error: %s", e)
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
