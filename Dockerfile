FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y \
    gcc g++ curl git libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# HuggingFace Spaces: non-root user
RUN useradd -m -u 1000 user && chown -R user:user /app
USER user

# Environment defaults (override via HF Space Secrets)
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=7860
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE=none

# These MUST be set as HF Space Secrets:
# API_BASE_URL, MODEL_NAME, HF_TOKEN, OPENAI_API_KEY

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=15s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:7860/_stcore/health || exit 1

# Run Streamlit app (OpenEnv validation hits the Streamlit port)
CMD ["streamlit", "run", "app/main.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.fileWatcherType=none", \
     "--browser.gatherUsageStats=false"]