FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS runtime

ENV UV_PROJECT_ENVIRONMENT=/app/venv \
    PATH="/app/venv/bin:$PATH"

WORKDIR /app

FROM runtime AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --all-groups;

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --all-groups

FROM runtime

COPY --from=builder /app /app

EXPOSE 8000

RUN ["chmod", "+x", "./start.sh"]
ENTRYPOINT ["./start.sh"]