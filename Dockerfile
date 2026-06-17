# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install .

EXPOSE 8085
RUN useradd --create-home --uid 10001 appuser
USER appuser

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8085/healthz').status==200 else 1)"

CMD ["uvicorn", "aigovkit.api.main:app", "--host", "0.0.0.0", "--port", "8085"]
