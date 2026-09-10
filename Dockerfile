FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    python3-dev \
 && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY bot/ ./bot
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

FROM python:3.14-slim-bookworm

ENV TZ=Asia/Yekaterinburg

RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

COPY --from=builder --chown=nonroot:nonroot /app /app

ENV PATH="/app/.venv/bin:$PATH"

USER nonroot

WORKDIR /app

CMD ["python", "-u", "-m", "bot.main"]
