FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .
COPY . .
CMD ["python", "scripts/run_pipeline.py", "--source", "mock"]
