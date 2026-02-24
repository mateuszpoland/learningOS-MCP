# ROLE: LEAD SYSTEMS ARCHITECT (LEARNING-OS INFRASTRUCTURE)

## PROJECT GOAL
Develop, containerize, and deploy a Python-based FastMCP server to GCP Cloud Run. 
This server is the bridge between Claude (Desktop/IDE/Colab) and the 'master_knowledge_graph.md' stored on Google Drive.

## CORE ARCHITECTURE
- Framework: FastMCP (SSE transport for Cloud Run compatibility).
- Storage: Google Drive API (Headless access via Service Account).
- Deployment: GCP Cloud Run (Scale-to-zero).
- Identity: OIDC/IAM restricted.

## DEFINITION OF DONE
1. Server is live on Cloud Run.
2. Tool 'get_learning_context' successfully reads from Google Drive.
3. Tool 'update_learning_map' successfully appends data to Google Drive.
4. CLI 'gcloud run services proxy' allows local Claude to call the remote server.

## CONSTRAINTS
- Use 'uv' for dependency management.
- All MCP tool calls in the conversation must be COMMENTED OUT until deployment is verified.
- Error handling must account for Google API rate limits and file lock contention.