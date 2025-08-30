# Cross-platform MCP configuration setup script
# This script detects the OS and creates the appropriate symlink/copy

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
$kilocodeDir = Join-Path $projectRoot ".kilocode"
$mcpConfigPath = Join-Path $kilocodeDir "mcp.json"

Write-Host "Setting up MCP configuration for current OS..." -ForegroundColor Green

# Detect OS
if ($IsWindows -or $env:OS -eq "Windows_NT") {
    Write-Host "Detected Windows OS" -ForegroundColor Cyan
    $sourceConfig = Join-Path $kilocodeDir "mcp-windows.json"
    
    # Remove existing config if it exists
    if (Test-Path $mcpConfigPath) {
        Remove-Item $mcpConfigPath -Force
    }
    
    # Copy Windows config
    Copy-Item $sourceConfig $mcpConfigPath -Force
    Write-Host "Windows MCP configuration applied successfully!" -ForegroundColor Green
    
} elseif ($IsLinux -or $IsMacOS) {
    Write-Host "Detected Unix-based OS (Linux/macOS)" -ForegroundColor Cyan
    $sourceConfig = Join-Path $kilocodeDir "mcp-linux.json"
    
    # Remove existing config if it exists
    if (Test-Path $mcpConfigPath) {
        Remove-Item $mcpConfigPath -Force
    }
    
    # Create symlink on Unix systems
    New-Item -ItemType SymbolicLink -Path $mcpConfigPath -Target $sourceConfig -Force
    Write-Host "Linux/macOS MCP configuration applied successfully!" -ForegroundColor Green
    
} else {
    Write-Host "Unable to detect OS. Please manually copy the appropriate config:" -ForegroundColor Yellow
    Write-Host "  - For Windows: copy .kilocode/mcp-windows.json to .kilocode/mcp.json"
    Write-Host "  - For Linux/macOS: copy .kilocode/mcp-linux.json to .kilocode/mcp.json"
}

Write-Host "`nConfiguration complete! Restart VS Code to apply changes." -ForegroundColor Green