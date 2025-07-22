# ClaudeForge

An autonomous development tool that uses Claude Code CLI to automatically work on GitHub issues and create pull requests.

## Features

- **No API Key Required**: Uses your existing Claude subscription via Claude Code CLI
- Automated Claude Code sessions from GitHub issues
- Support for Python projects (extensible to other languages)  
- Notification system (Discord, Email)
- Docker deployment for VPS hosting
- Pull request automation

## How It Works

ClaudeForge bridges GitHub issues with Claude Code:

1. **Input**: GitHub issue URL + your instruction
2. **Context Building**: Combines your instruction with issue details and repo context
3. **Autonomous Development**: Claude Code works independently in the repository
4. **Result**: Commits changes and creates a pull request automatically

## Quick Start

### Local Installation
```bash
pip install -e .
claudeforge run --issue-url "https://github.com/user/repo/issues/123" --instruction "Fix the authentication bug"
```

### Docker (Recommended for VPS)
```bash
git clone https://github.com/RMLaroche/ClaudeForge.git
cd ClaudeForge
cp .env.example .env
# Edit .env with your GitHub token
docker-compose up -d
```

## Configuration

- **No API Key**: Uses Claude Code CLI with your subscription
- **GitHub Token**: Required for repository access
- **Notifications**: Optional Discord/Email alerts

See `DOCKER_GUIDE.md` for detailed Docker setup and `config.example.yml` for all options.