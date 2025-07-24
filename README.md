# Claude Development Container

A simple, ready-to-use Docker container for development with Claude Code, GitHub CLI, and Python.

## What You Get

- **Python 3.11** + common dev packages (pytest, black, jupyter, etc.)
- **Claude Code CLI** (authenticated)
- **GitHub CLI** (authenticated)
- **Zsh + Oh My Zsh** for a nice terminal experience
- **Development tools** (vim, nano, git)
- **Autonomous Claude alias**: `claudef` (shorthand for `claude --dangerously-skip-permissions`)

## One-Time Setup

```bash
./setup.sh
```

This creates two images:
- `claudeforge-setup` (base image, no auth)
- `claudeforge` (ready-to-dev with authentication)

### Authentication Process

During setup, you'll need to:

1. **Authenticate Claude**:
   ```bash
   claude --dangerously-skip-permissions
   # Follow the configuration wizard
   # Exit with: /exit
   ```

2. **Authenticate GitHub**:
   ```bash
   gh auth login
   # Follow the prompts
   ```

3. **Exit container**: `exit`

## Daily Usage

```bash
docker run -it --rm -v $(pwd):/home/dev/workspace claudeforge
```

## Example Workflow

```bash
# Start authenticated container
docker run -it --rm -v $(pwd):/home/dev/workspace claudeforge

# Create a project (no auth needed - already logged in!)
mkdir my-api && cd my-api
python -m venv venv && source venv/bin/activate

# Use Claude for development (autonomous mode)
claudef "Create a FastAPI application with user authentication"

# Push to GitHub
git init
gh repo create my-api --public
git add . && git commit -m "Initial commit"
git push -u origin main
```

## Scheduling Claude Tasks

Two ways to schedule Claude tasks:

### Method 1: Schedule Container Start (Recommended)
Schedule from your host machine - starts fresh container, runs task, stops automatically:

```bash
# Run at 20:05 today
echo "5 20 * * * docker run --rm -v $(pwd):/home/dev/workspace claudeforge claude 'do something'" | crontab -

# Daily at 9:00 AM  
echo "0 9 * * * docker run --rm -v $(pwd):/home/dev/workspace claudeforge claude 'run tests and generate report'" | crontab -

# Every Monday at 10:00 AM
echo "0 10 * * 1 docker run --rm -v $(pwd):/home/dev/workspace claudeforge claude 'plan weekly development tasks'" | crontab -
```

**Benefits**: Clean state, resource efficient, reliable host scheduling

### Method 2: Schedule Inside Container
Keep container running and schedule tasks internally:

```bash
# Start persistent container
docker run -d --name claudeforge-scheduler -v $(pwd):/home/dev/workspace claudeforge sleep infinity

# Add scheduled tasks inside container
docker exec claudeforge-scheduler bash -c "echo '5 20 * * * cd /home/dev/workspace && claude \"do something\"' | crontab -"
docker exec claudeforge-scheduler bash -c "echo '0 9 * * * cd /home/dev/workspace && claude \"run tests\"' | crontab -"

# Start cron daemon
docker exec claudeforge-scheduler service cron start
```

**Drawbacks**: Persistent container, resource usage, state accumulation

### One-time Tasks with `at`
```bash
# Method 1: Container start
echo "docker run --rm -v $(pwd):/home/dev/workspace claudeforge claude 'do something'" | at 20:05

# Method 2: Inside running container  
docker exec claudeforge-scheduler bash -c "echo 'cd /home/dev/workspace && claude \"do something\"' | at 20:05"
```

### Task Management
```bash
# View host cron jobs
crontab -l

# View container cron jobs
docker exec claudeforge-scheduler crontab -l

# Remove all host cron jobs
crontab -r

# Stop persistent container
docker stop claudeforge-scheduler && docker rm claudeforge-scheduler
```

**Cron Time Format**: `minute hour day month dayofweek`
- `5 20 * * *` = 20:05 every day
- `30 14 * * 1` = 14:30 every Monday  
- `0 */2 * * *` = Every 2 hours

**Recommendation**: Use Method 1 (container start) for better resource management and reliability.

## Images

- **`claudeforge-setup`**: Base image with tools installed
- **`claudeforge`**: Ready-to-dev image with authentication baked in

Just use `claudeforge` for development - everything is already authenticated!