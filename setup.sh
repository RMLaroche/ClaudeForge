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

# Create a script to show persistent instructions
cat > /tmp/auth-instructions.sh << 'SCRIPT'
#!/bin/zsh

# Function to show instructions
show_instructions() {
    echo "============================================"
    echo "🔐 CLAUDE & GITHUB AUTHENTICATION SETUP"
    echo "============================================"
    echo ""
    echo "STEP 1: Authenticate Claude"
    echo "  → Run: claude"
    echo "  → Follow the configuration wizard"
    echo "  → Exit Claude with: /exit"
    echo ""
    echo "STEP 2: Authenticate GitHub"
    echo "  → Run: gh auth login"
    echo "  → Follow the prompts"
    echo ""
    echo "STEP 3: Exit container"
    echo "  → Run: exit"
    echo ""
    echo "💡 TIP: If Claude clears the screen, run 'help' to see these instructions again"
    echo "============================================"
}

# Add help alias
alias help='show_instructions'

# Show instructions immediately
show_instructions

# Keep instructions available in prompt
export PS1="[claudeforge-setup] $ "

exec /bin/zsh
SCRIPT

chmod +x /tmp/auth-instructions.sh

docker run -it --name claudeforge-auth-temp \
    -v $(pwd):/home/dev/workspace \
    -v /tmp/auth-instructions.sh:/home/dev/auth-instructions.sh \
    claudeforge-setup /home/dev/auth-instructions.sh

echo "3️⃣ Creating ready-to-dev image..."
docker commit claudeforge-auth-temp claudeforge

echo "4️⃣ Cleaning up..."
docker rm claudeforge-auth-temp

echo "✅ Setup complete!"
echo ""
echo "🚀 To start developing:"
echo "   docker run -it --rm -v \$(pwd):/home/dev/workspace claudeforge"