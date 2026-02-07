#!/bin/bash
# Initialize Vehicle-Telemetry as a Git repository for GitHub
# Run: bash INIT_GIT.sh

set -e

echo "🚀 Initializing Vehicle-Telemetry Git repository..."
echo

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git not installed. Install with: sudo apt-get install -y git"
    exit 1
fi

cd "$(dirname "$0")"

# Initialize git
if [ -d ".git" ]; then
    echo "⚠️  Git repo already exists. Skipping init."
else
    echo "✓ Initializing git repository..."
    git init
    
    # Configure git
    echo "📝 Configure git user (optional):"
    git config user.name "Your Name" 2>/dev/null || true
    git config user.email "your.email@example.com" 2>/dev/null || true
fi

# Add all files
echo "✓ Adding files to git..."
git add .

# Create initial commit
echo "✓ Creating initial commit..."
git commit -m "Initial commit: Vehicle-Telemetry v1.0.0

- Real-time Pygame dashboard UI
- Multi-sensor support (MPU6050, FC-33, DS3231)
- CSV data logging
- Autostart on boot
- Complete documentation suite" || true

echo
echo "==============================================="
echo "✓ Git repository initialized!"
echo "==============================================="
echo
echo "Next steps:"
echo
echo "1. Create GitHub repository at:"
echo "   https://github.com/vishnuskandha/Vehicle-Telemetry"
echo
echo "2. Add remote and push:"
echo "   git remote add origin https://github.com/vishnuskandha/Vehicle-Telemetry.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo
echo "Or use SSH:"
echo "   git remote add origin git@github.com:vishnuskandha/Vehicle-Telemetry.git"
echo "   git push -u origin main"
echo
