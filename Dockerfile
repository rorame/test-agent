FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

ENV A2A_HOST=0.0.0.0 \
    A2A_PORT=9000
EXPOSE 9000

CMD ["uv", "run", "python", "a2a_server.py"]
