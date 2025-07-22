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
echo '============================================'
echo '🔐 CLAUDE & GITHUB AUTHENTICATION SETUP'
echo '============================================'
echo ''
echo 'STEP 1: Authenticate Claude'
echo '  → Run: claude --dangerously-skip-permissions'
echo '  → Follow the configuration wizard'
echo '  → Exit Claude with: /exit'
echo ''
echo 'STEP 2: Authenticate GitHub'
echo '  → Run: gh auth login'
echo '  → Follow the prompts'
echo ''
echo 'STEP 3: Exit container'
echo '  → Run: exit'
echo '============================================'
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