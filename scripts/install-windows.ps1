param(
  [ValidateSet("claude-desktop", "cursor", "vscode", "generic")]
  [string]$Client = "claude-desktop",
  [switch]$Project,
  [switch]$DryRun,
  [switch]$NoBackup,
  [string]$Instance,
  [string]$Token
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$configScript = Join-Path $scriptDir "liongard-mcp-config.js"

$argsList = @("--client", $Client)

if ($Instance) {
  $argsList += @("--instance", $Instance)
}
if ($Token) {
  $argsList += @("--token", $Token)
}
if ($Project) {
  $argsList += "--project"
}
if ($DryRun) {
  $argsList += "--dry-run"
} else {
  $argsList += "--write"
}
if (-not $NoBackup) {
  $argsList += "--backup"
}

node $configScript @argsList

Write-Host ""
Write-Host "Restart or reconnect the MCP server in $Client after updating config."
