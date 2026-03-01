from mcp.server.fastmcp import FastMCP
from learningos_mcp.gdrive_client import GDriveManager
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__ + "learningOS MCP")

mcp = FastMCP("learningOS")

class UpdateLearningMapPayload(BaseModel):
    topic_id: str
    content: str
    mastery_delta: int # Track the mastery level of the topic

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

mcp.run(transport="sse")

def main():
    """Entry point – starts the MCP server with SSE transport."""
    try:
        GDriveManager.get_instance()
        logger.info("GDriveManager initialised")
        mcp.run(transport="sse")
        logger.info("MCP server started")
    except Exception as e:
        logger.error(f"Critical MCP system error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
