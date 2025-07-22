# ClaudeForge Docker Guide

## How Docker Mode Works

ClaudeForge runs in Docker using your existing Claude subscription, not an API key. Here's how it works:

### Authentication
When the Docker container starts, it uses the **Claude Code CLI** which connects to your Claude subscription. You need to authenticate once by running:

```bash
docker run -it --rm claudeforge claude-code auth login
```

This will authenticate the Claude CLI inside the container using your existing subscription.

### How Instructions Are Passed

ClaudeForge receives instructions in several ways:

1. **CLI Command**: Direct instruction via command line
```bash
docker run claudeforge claudeforge run --issue-url "https://github.com/user/repo/issues/123" --instruction "Fix the bug in authentication"
```

2. **GitHub Webhooks**: Automatic processing when issues are created/updated (daemon mode)
```bash
docker run -p 8080:8080 claudeforge claudeforge daemon
```

3. **Configuration File**: Pre-configured instructions in `config.yml`

### Inside the Container

When ClaudeForge processes a GitHub issue:

1. **Repository Setup**: Clones the GitHub repo to `/tmp/claudeforge-repos/`
2. **Instruction Building**: Creates a comprehensive instruction combining:
   - Your custom instruction
   - GitHub issue details (title, description, comments)
   - Repository context (language, structure)
3. **Claude Code Execution**: Runs `claude-code -- "your instruction"` in the repository
4. **Result Processing**: Analyzes changes, commits them, and creates a pull request

## Docker Deployment

### 1. Simple Run
```bash
# One-time execution
docker run --rm \
  -e GITHUB_TOKEN=your_token \
  -v $(pwd)/logs:/app/logs \
  claudeforge \
  claudeforge run --issue-url "URL" --instruction "INSTRUCTION"
```

### 2. Docker Compose (Recommended)

Copy `.env.example` to `.env` and configure:
```env
GITHUB_TOKEN=your-github-token
CLAUDE_TIMEOUT=3600
DISCORD_WEBHOOK_URL=optional-discord-webhook
```

Run with:
```bash
docker-compose up -d
```

### 3. VPS Deployment

For continuous operation on a VPS:

```bash
# Clone and setup
git clone https://github.com/RMLaroche/ClaudeForge.git
cd ClaudeForge
cp .env.example .env
# Edit .env with your tokens

# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f
```

## Authentication Workflow

### First Time Setup
```bash
# 1. Start container with interactive session
docker run -it --name claudeforge-setup claudeforge bash

# 2. Inside container, authenticate Claude
claude-code auth login
# Follow prompts to authenticate with your Claude subscription

# 3. Commit the authenticated container
docker commit claudeforge-setup claudeforge:authenticated

# 4. Use the authenticated image
docker run --rm claudeforge:authenticated claudeforge --help
```

### Persistent Authentication
Mount the Claude config directory to persist authentication:
```bash
docker run -v ~/.config/claude:/home/claudeforge/.config/claude claudeforge
```

## How Instructions Work

### Basic Instruction Flow

1. **Input**: GitHub issue URL + custom instruction
2. **Context Building**: 
   ```
   You are an autonomous software development assistant working on a GitHub repository.
   
   Primary Instruction: [Your instruction]
   
   GitHub Issue Context:
   Title: [Issue title]
   Number: #123
   State: open
   
   Issue Description:
   [Full issue description]
   
   Repository Context:
   Name: user/repository
   Language: Python
   Default Branch: main
   ```

3. **Claude Code Execution**: The complete instruction is passed to Claude Code CLI
4. **Autonomous Work**: Claude works independently in the repository
5. **Result Processing**: Changes are committed and a PR is created

### Example Complete Workflow

```bash
# 1. ClaudeForge receives: 
claudeforge run \
  --issue-url "https://github.com/user/repo/issues/123" \
  --instruction "Add unit tests for the authentication module"

# 2. ClaudeForge builds full context and runs:
claude-code -- "You are an autonomous software development assistant...
Primary Instruction: Add unit tests for the authentication module
GitHub Issue Context: [issue details]
Repository Context: [repo details]
Your Task: [detailed steps]"

# 3. Claude Code works autonomously in the repo
# 4. ClaudeForge commits changes and creates PR
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub personal access token | Yes |
| `CLAUDE_TIMEOUT` | Session timeout in seconds | No (default: 3600) |
| `DISCORD_WEBHOOK_URL` | Discord webhook for notifications | No |
| `DISCORD_BOT_TOKEN` | Discord bot token | No |
| `SMTP_SERVER` | Email SMTP server | No |
| `SMTP_USERNAME` | Email username | No |

## Monitoring and Logs

View logs in real-time:
```bash
docker-compose logs -f claudeforge
```

Logs are also persisted in `./logs/` directory.

## Security Notes

- The container runs as non-root user `claudeforge`
- GitHub token should have minimal required permissions
- Claude authentication is handled through official Claude CLI
- Repository clones are isolated in temporary directories