FROM python:3.10-slim

WORKDIR /app

# Install git for auto-update functionality and minimal system deps
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY turbo/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and THEIR system dependencies
RUN playwright install chromium && playwright install-deps chromium

# Copy project files
COPY . .

# Ensure output directory exists (though volume will likely override)
RUN mkdir -p /app/outputs

EXPOSE 8000

# Set PYTHONPATH to ensure 'turbo' module is found
ENV PYTHONPATH=/app

CMD ["python", "-m", "uvicorn", "turbo.server:app", "--host", "0.0.0.0", "--port", "8000"]
