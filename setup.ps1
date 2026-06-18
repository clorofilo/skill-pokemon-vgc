# VGC App — Setup script for Windows
# Run once after cloning: .\setup.ps1
# Installs dependencies, builds MCP server, and registers the skill globally.

$ErrorActionPreference = "Stop"
$REPO = $PSScriptRoot

Write-Host "`n=== vgc-app setup ===" -ForegroundColor Cyan
Write-Host "Repo: $REPO"

# 1. MCP server
Write-Host "`n[1/4] Building MCP server..." -ForegroundColor Yellow
Push-Location "$REPO\mcp-server"
npm install
npm run build
Pop-Location

# 2. calc-tools
Write-Host "`n[2/4] Installing Python dependencies..." -ForegroundColor Yellow
Push-Location "$REPO\calc-tools"
pip install -r requirements.txt
Pop-Location

# 3. Install skill globally
Write-Host "`n[3/4] Installing skill globally..." -ForegroundColor Yellow
$skillsDir = "$env:USERPROFILE\.claude\skills"
if (-not (Test-Path $skillsDir)) { New-Item -ItemType Directory -Force $skillsDir | Out-Null }
Copy-Item "$REPO\skill\pokemon-vgc.md" "$skillsDir\pokemon-vgc.md" -Force
Write-Host "  Skill installed to $skillsDir\pokemon-vgc.md"

# 4. Global CLAUDE.md
$claudeDir = "$env:USERPROFILE\.claude"
$claudeMd  = "$claudeDir\CLAUDE.md"
$routing = @"

# VGC Skill (Pokemon Champions)
For any competitive Pokemon question (teambuilding, team analysis, damage calc, EVs, leads, matchups), invoke the ``pokemon-vgc`` skill automatically via the Skill tool before responding.
"@
if (Test-Path $claudeMd) {
    if (-not (Select-String -Path $claudeMd -Pattern "pokemon-vgc" -Quiet)) {
        Add-Content $claudeMd $routing
        Write-Host "  Added routing to existing $claudeMd"
    } else {
        Write-Host "  $claudeMd already has pokemon-vgc routing — skipped"
    }
} else {
    Set-Content $claudeMd "# Global Instructions$routing"
    Write-Host "  Created $claudeMd"
}

# 5. Write .claude/settings.json with correct absolute path
Write-Host "`n[4/4] Writing .claude/settings.json..." -ForegroundColor Yellow
$distPath = "$REPO\mcp-server\dist\index.js" -replace '\\', '\\'
$settingsDir = "$REPO\.claude"
if (-not (Test-Path $settingsDir)) { New-Item -ItemType Directory -Force $settingsDir | Out-Null }
@"
{
  "mcpServers": {
    "vgc-assistant": {
      "command": "node",
      "args": ["$distPath"]
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
"@ | Set-Content "$settingsDir\settings.json"
Write-Host "  Written to $settingsDir\settings.json"

Write-Host "`n=== Setup complete ===" -ForegroundColor Green
Write-Host "To use the skill in another directory, copy:"
Write-Host "  $settingsDir\settings.json  ->  <target-dir>\.claude\settings.json"
