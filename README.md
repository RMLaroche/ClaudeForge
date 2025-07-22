# Claude Development Container

A simple, ready-to-use Docker container for development with Claude Code, GitHub CLI, and Python.

## What You Get

- **Python 3.11** + common dev packages (pytest, black, jupyter, etc.)
- **Claude Code CLI** (authenticated)
- **GitHub CLI** (authenticated)
- **Zsh + Oh My Zsh** for a nice terminal experience
- **Development tools** (vim, nano, git)

## One-Time Setup

```bash
./setup.sh
```

This creates two images:
- `claudeforge-setup` (base image, no auth)
- `claudeforge` (ready-to-dev with authentication)

## Daily Usage

```bash
docker run -it --rm -v $(pwd):/home/dev/workspace claudeforge
```

Or with docker-compose:
```bash
docker-compose run --rm claudeforge
```

## Example Workflow

```bash
# Start authenticated container
docker run -it --rm -v $(pwd):/home/dev/workspace claudeforge

# Create a project (no auth needed - already logged in!)
mkdir my-api && cd my-api
python -m venv venv && source venv/bin/activate

# Use Claude Code for development
claude-code "Create a FastAPI application with user authentication"

# Push to GitHub
git init
gh repo create my-api --public
git add . && git commit -m "Initial commit"
git push -u origin main
```

## Images

- **`claudeforge-setup`**: Base image with tools installed
- **`claudeforge`**: Ready-to-dev image with authentication baked in

Just use `claudeforge` for development - everything is already authenticated!