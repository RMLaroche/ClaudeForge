FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI
RUN curl -fsSL https://claude.ai/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml .
RUN pip install -e .

# Copy application code
COPY src/ ./src/
COPY config.example.yml ./config.example.yml

# Create directories for repos and logs
RUN mkdir -p /tmp/claudeforge-repos /app/logs

# Set environment variables
ENV PYTHONPATH=/app/src
ENV CLAUDEFORGE_CONFIG=/app/config.yml

# Create non-root user
RUN useradd -m -u 1000 claudeforge && \
    chown -R claudeforge:claudeforge /app /tmp/claudeforge-repos
USER claudeforge

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import claudeforge; print('OK')" || exit 1

# Default command
CMD ["python", "-m", "claudeforge.cli", "--help"]