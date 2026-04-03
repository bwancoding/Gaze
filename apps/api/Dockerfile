FROM python:3.11-slim

# Install system dependencies for psycopg2, lxml, and Playwright chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    # Playwright Chromium dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libx11-xcb1 \
    fonts-noto-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium (without --with-deps, deps installed above)
RUN playwright install chromium

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

ENV PORT=8000
ENV PYTHONUNBUFFERED=1

EXPOSE ${PORT}

# Run with uvicorn - use shell form so $PORT is expanded
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
