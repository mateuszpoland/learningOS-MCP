FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first (layer caching)
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY .env .env
# Install dependencies
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

# Cloud Run sets PORT env var (default 8080)
ENV PORT=8080
EXPOSE 8080

CMD ["python", "src/learningos_mcp/server.py"]
