#!/usr/bin/env bash
# VGC App — Setup script for macOS / Linux
# Run once after cloning: bash setup.sh
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo ""
echo "=== vgc-app setup ==="
echo "Repo: $REPO"

# 1. MCP server
echo ""
echo "[1/4] Building MCP server..."
cd "$REPO/mcp-server"
npm install
npm run build
cd "$REPO"

# 2. calc-tools
echo ""
echo "[2/4] Installing Python dependencies..."
cd "$REPO/calc-tools"
pip install -r requirements.txt
cd "$REPO"

# 3. Install skill globally
echo ""
echo "[3/4] Installing skill globally..."
mkdir -p "$CLAUDE_DIR/skills"
cp "$REPO/skill/pokemon-vgc.md" "$CLAUDE_DIR/skills/pokemon-vgc.md"
echo "  Skill installed to $CLAUDE_DIR/skills/pokemon-vgc.md"

# 4. Global CLAUDE.md
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
ROUTING="
# VGC Skill (Pokemon Champions)
For any competitive Pokemon question (teambuilding, team analysis, damage calc, EVs, leads, matchups), invoke the \`pokemon-vgc\` skill automatically via the Skill tool before responding."

if [ -f "$CLAUDE_MD" ]; then
    if grep -q "pokemon-vgc" "$CLAUDE_MD"; then
        echo "  $CLAUDE_MD already has pokemon-vgc routing — skipped"
    else
        echo "$ROUTING" >> "$CLAUDE_MD"
        echo "  Added routing to existing $CLAUDE_MD"
    fi
else
    echo "# Global Instructions$ROUTING" > "$CLAUDE_MD"
    echo "  Created $CLAUDE_MD"
fi

# 5. Write .claude/settings.json with correct absolute path
echo ""
echo "[4/4] Writing .claude/settings.json..."
DIST_PATH="$REPO/mcp-server/dist/index.js"
mkdir -p "$REPO/.claude"
cat > "$REPO/.claude/settings.json" <<EOF
{
  "mcpServers": {
    "vgc-assistant": {
      "command": "node",
      "args": ["$DIST_PATH"]
    }
  },
  "permissions": {
    "allow": [
      "Bash(npm:*)",
      "Bash(node:*)",
      "Bash(python:*)",
      "Bash(pip:*)",
      "Bash(pytest:*)",
      "Bash(npx:*)",
      "Bash(git:*)"
    ]
  }
}
EOF
echo "  Written to $REPO/.claude/settings.json"

echo ""
echo "=== Setup complete ==="
echo "To use the skill in another directory, copy:"
echo "  $REPO/.claude/settings.json  ->  <target-dir>/.claude/settings.json"
