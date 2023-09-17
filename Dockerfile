# Use multi-stage builds to reduce the size of the final image
FROM python:3.10-slim as builder

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \ 
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.5.1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/* \
    && pip install "poetry==$POETRY_VERSION"

COPY poetry.lock pyproject.toml poetry.toml ./

RUN  poetry install --no-interaction --no-ansi --no-root --without dev,lint,extras


FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /app /app

COPY /knowledge_gpt ./knowledge_gpt 

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "knowledge_gpt/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
