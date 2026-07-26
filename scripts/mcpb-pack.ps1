param([string]$RepoRoot = $PSScriptRoot + "\..")
Set-Location $RepoRoot
New-Item -ItemType Directory -Force -Path dist | Out-Null
$proj = Get-Content pyproject.toml -Raw
$name = if ($proj -match '(?m)^name = "(.*)"') { $matches[1] } else { Split-Path -Leaf $PWD }
$ver = if ($proj -match '(?m)^version = "(.*)"') { $matches[1] } else { "0.1.0" }
if (-not (Test-Path manifest.json)) {
    Write-Host "ERROR: manifest.json missing at repo root" -ForegroundColor Red
    exit 1
}
npx --yes @anthropic-ai/mcpb pack $RepoRoot "$RepoRoot/dist/$name-v$ver.mcpb"
Write-Host "Bundle: $RepoRoot/dist/$name-v$ver.mcpb"
