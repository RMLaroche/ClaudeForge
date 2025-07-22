FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    vim \
    nano \
    zsh \
    sudo \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create developer user
RUN useradd -m -u 1000 -s /bin/zsh dev && \
    echo "dev ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/dev

# Switch to dev user
USER dev
WORKDIR /home/dev

# Install Oh My Zsh
RUN sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# Install Claude Code CLI
RUN curl -fsSL https://claude.ai/install.sh | bash && \
    echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.zshrc

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    sudo apt update && \
    sudo apt install gh -y

# Set up Python development environment
RUN pip install --user --upgrade pip && \
    pip install --user \
    black \
    isort \
    flake8 \
    mypy \
    pytest \
    ipython \
    jupyter \
    requests \
    pydantic \
    click \
    rich

# Create directories
RUN mkdir -p /home/dev/workspace /home/dev/.config

# Update PATH in both bashrc and zshrc
RUN echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc && \
    echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.zshrc

# Add claudef alias for autonomous Claude
RUN echo 'alias claudef="claude --dangerously-skip-permissions"' >> ~/.bashrc && \
    echo 'alias claudef="claude --dangerously-skip-permissions"' >> ~/.zshrc

# Set working directory
WORKDIR /home/dev/workspace

# Default command
CMD ["/bin/zsh"]