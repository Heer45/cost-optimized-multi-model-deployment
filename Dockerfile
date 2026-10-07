# ============================================================
# Dockerfile for Cost-Optimized Multi-Model Deployment App
# ============================================================

# --- Base Image ---
FROM python:3.13-slim

# --- Metadata ---
LABEL maintainer="ps4-project"
LABEL description="Streamlit dashboard for cost-optimized multi-model ML deployment"

# --- Prevent Python from buffering stdout/stderr ---
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# --- Set working directory ---
WORKDIR /app

# --- Install dependencies first (layer caching) ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy application source files ---
COPY app.py .
COPY router.py .
COPY model_manager.py .
COPY cost_simulator.py .
COPY patients.py .

# --- Copy data files required at runtime ---
COPY patients.json .
COPY latency_profile.json .

# --- Copy trained ML models ---
COPY models/ models/

# --- Copy Streamlit configuration ---
COPY .streamlit/ .streamlit/

# --- Expose Streamlit default port ---
EXPOSE 8501

# --- Health check ---
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

# --- Start the Streamlit application ---
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]

