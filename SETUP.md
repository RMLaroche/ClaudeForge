# Claude Development Container Setup

A ready-to-use development container with Claude Code, GitHub CLI, and Python pre-installed.

## What's Included

- **Python 3.11** with common development packages
- **Claude Code CLI** for AI-powered development
- **GitHub CLI (gh)** for GitHub operations
- **Development tools**: vim, nano, zsh, Oh My Zsh
- **Python packages**: black, pytest, jupyter, requests, pydantic, etc.

## Quick Setup

### 1. Build the Container

```bash
cd dev-container
docker build -t claude-dev .
```

### 2. First Run & Authentication

Start the container with interactive session:

```bash
docker run -it --name claude-dev-setup \
  -v $(pwd):/home/dev/workspace \
  claude-dev
```

### 3. Authenticate Claude Code

Inside the container:
```bash
claude-code auth login
# Follow the prompts to authenticate with your Claude subscription
```

### 4. Authenticate GitHub CLI

Still inside the container:
```bash
gh auth login
# Choose:
# - GitHub.com
# - HTTPS
# - Authenticate with browser or token
```

### 5. Save the Authenticated Container

Exit the container (`exit`) then commit it:
```bash
docker commit claude-dev-setup claude-dev:authenticated
docker rm claude-dev-setup
```

## Daily Usage

### Start Development Session

```bash
docker run -it --rm \
  --name claude-dev \
  -v $(pwd):/home/dev/workspace \
  claude-dev:authenticated
```

### With Docker Compose (Recommended)

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  claude-dev:
    image: claude-dev:authenticated
    container_name: claude-dev
    volumes:
      - .:/home/dev/workspace
    stdin_open: true
    tty: true
    working_dir: /home/dev/workspace
```

Then run:
```bash
docker-compose run --rm claude-dev
```

## Usage Examples

### Start a new Python project
```bash
# Inside container
mkdir my-project && cd my-project
python -m venv venv
source venv/bin/activate
pip install requests pydantic
```

### Use Claude Code for development
```bash
claude-code "Help me create a FastAPI application with user authentication"
```

### GitHub operations
```bash
gh repo create my-project --public
gh issue list
gh pr create --title "Feature: Add authentication"
```

## Persistent Data

Mount volumes to persist:
- **Code**: `-v $(pwd):/home/dev/workspace`
- **Git config**: `-v ~/.gitconfig:/home/dev/.gitconfig:ro`
- **SSH keys**: `-v ~/.ssh:/home/dev/.ssh:ro`

## Advanced Setup

### With SSH Keys
```bash
docker run -it --rm \
  --name claude-dev \
  -v $(pwd):/home/dev/workspace \
  -v ~/.ssh:/home/dev/.ssh:ro \
  -v ~/.gitconfig:/home/dev/.gitconfig:ro \
  claude-dev:authenticated
```

### Background Development Server
```bash
docker run -d \
  --name claude-dev-server \
  -v $(pwd):/home/dev/workspace \
  -p 8000:8000 \
  claude-dev:authenticated \
  sleep infinity

# Attach when needed
docker exec -it claude-dev-server zsh
```

## Troubleshooting

### Claude Code not authenticated
```bash
claude-code auth status
claude-code auth login
```

### GitHub CLI not authenticated
```bash
gh auth status
gh auth login
```

### Container can't access files
Check volume mounting and file permissions:
```bash
ls -la /home/dev/workspace
sudo chown -R dev:dev /home/dev/workspace
```