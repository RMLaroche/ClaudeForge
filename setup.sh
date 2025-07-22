#!/bin/bash

set -e

echo "🐳 Claude Development Container Setup"
echo "======================================"

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "1️⃣ Building base container..."
docker build -t claudeforge-setup .

echo "2️⃣ Starting container for authentication..."
docker run -it --name claudeforge-auth-temp \
    -v $(pwd):/home/dev/workspace \
    claudeforge-setup /bin/zsh -c "
echo '🔐 Please authenticate Claude Code and GitHub CLI:'
echo ''
echo '1. claude-code auth login'
echo '2. gh auth login'
echo ''
echo '💡 After authentication, type \"exit\" to continue setup'
echo ''
exec /bin/zsh
"

echo "3️⃣ Creating ready-to-dev image..."
docker commit claudeforge-auth-temp claudeforge

echo "4️⃣ Cleaning up..."
docker rm claudeforge-auth-temp

echo "✅ Setup complete!"
echo ""
echo "🚀 To start developing:"
echo "   docker run -it --rm -v \$(pwd):/home/dev/workspace claudeforge"