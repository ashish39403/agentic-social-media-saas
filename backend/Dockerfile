FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --create-home app

COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
RUN uv sync --frozen --no-dev
RUN chown -R app:app /app

USER app

EXPOSE 8000
CMD ["uvicorn", "social_saas.main:app", "--host", "0.0.0.0", "--port", "8000"]
