# ClaudeForge

An autonomous development tool that uses Claude Code to automatically work on GitHub issues and create pull requests.

## Features

- Automated Claude Code sessions from GitHub issues
- Support for Python projects (extensible to other languages)
- Notification system (Discord, Email)
- Docker deployment for VPS hosting
- Pull request automation

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run ClaudeForge
python -m claudeforge --issue-url <github-issue-url> --instruction "<your-instruction>"
```

## Configuration

See `config.example.yml` for configuration options.

## Docker Deployment

```bash
docker build -t claudeforge .
docker run -d --name claudeforge claudeforge
```