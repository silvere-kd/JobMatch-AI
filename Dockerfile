FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy project metadata first (keeps deps layer cached)
COPY pyproject.toml ./
# COPY README.md ./

# Copy sources BEFORE editable install so imports work even before volumes mount
COPY backend ./backend
COPY frontend ./frontend

# Install project in editable mode for dev (reflect code changes immediately)
RUN pip install --upgrade pip && pip install -e .

# Default command is overridden by docker compose services
CMD ["python", "-c", "print('Image built. Use docker compose to run services.')"]
