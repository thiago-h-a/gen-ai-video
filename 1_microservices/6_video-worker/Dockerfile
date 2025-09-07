
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends         ffmpeg fonts-dejavu-core && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir fastapi uvicorn[standard] pydantic pillow numpy boto3
COPY src/ ./src/
VOLUME ["/data"]
EXPOSE 8091
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8091"]
