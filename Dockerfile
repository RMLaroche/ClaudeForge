FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create user first (Claude Code CLI needs to be installed per-user)
RUN useradd -m -u 1000 -s /bin/bash claudeforge && \
    echo "claudeforge ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/claudeforge

# Switch to user for Claude Code installation
USER claudeforge
WORKDIR /home/claudeforge

# Install Claude Code CLI as the user
RUN curl -fsSL https://claude.ai/install.sh | bash && \
    echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc

# Make sure Claude Code is in PATH for this session
ENV PATH="/home/claudeforge/.local/bin:$PATH"

# Set working directory and copy application
WORKDIR /app
COPY --chown=claudeforge:claudeforge . .

# Install Python dependencies
RUN pip install --user -e .

# Create directories for repos and logs
RUN mkdir -p /tmp/claudeforge-repos /app/logs

# Set environment variables
ENV PYTHONPATH=/app/src
ENV CLAUDEFORGE_CONFIG=/app/config.yml

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import claudeforge; print('OK')" || exit 1

# Default command
CMD ["python", "-m", "claudeforge.cli", "--help"]