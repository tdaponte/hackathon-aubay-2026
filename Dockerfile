FROM python:3.12-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ateliers ./ateliers
RUN mkdir -p /app/data

FROM runtime AS tests
COPY requirements-dev.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements-dev.txt
RUN python -m playwright install --with-deps chromium
COPY tests ./tests
COPY scripts ./scripts
CMD ["python", "-m", "pytest", "-q"]

FROM runtime AS site
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "ateliers.app:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
