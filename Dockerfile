FROM python:3.11-slim

# System dependencies (ffmpeg for encoding; X libs for OpenCV headless drawing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Keep using the project's existing requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

EXPOSE 8000

# Keep the same entrypoint to avoid front-end changes
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
