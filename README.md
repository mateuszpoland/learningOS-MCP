# learningOS-MCP

FastMCP server that bridges Claude (Desktop / IDE / Colab) with a `master_knowledge_graph.md` file stored on Google Drive. Deployed to GCP Cloud Run with scale-to-zero.

## Prerequisites

| Tool | Purpose |
|---|---|
| [uv](https://docs.astral.sh/uv/) | Python package & project manager |
| [gcloud CLI](https://cloud.google.com/sdk/docs/install) | Deploy to Cloud Run, proxy tunnelling, logs |
| [Docker](https://docs.docker.com/get-docker/) | Local container builds (optional — Cloud Run builds from source) |

## Setup

```bash
# 1. Install dependencies
uv sync

# 2. Copy env template and fill in your values
cp .env.example .env

# 3. Authenticate with GCP
gcloud auth login
gcloud auth application-default login
```

## Environment variables

See `.env.example`:

| Variable | Description |
|---|---|
| `GCLOUD_PROJECT_ID` | GCP project ID |
| `SERVICE_ACCOUNT` | Service-account email bound to the Cloud Run revision |
| `GDRIVE_FOLDER_ID` | Google Drive folder containing the knowledge graph |
| `GDRIVE_FILE_ID` | File ID of `master_knowledge_graph.md` |

## Deploy

```bash
make deploy
```

## Useful commands

```bash
make logs    # tail Cloud Run logs
make proxy   # tunnel Cloud Run service to localhost:8080
```
