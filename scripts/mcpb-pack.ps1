# Fresh-stage src/ -> mcpb/src/ then pack. Never pack a stale twin.
# See mcp-central-docs/standards/MCPB_PACKAGING_STANDARDS.md § Fresh copy before pack.

param([string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path)
Set-Location $RepoRoot
$ErrorActionPreference = "Stop"

$pkg = "mastodon_mcp"
$srcPkg = Join-Path $RepoRoot "src\$pkg"
$mcpbRoot = Join-Path $RepoRoot "mcpb"
$stageRoot = Join-Path $mcpbRoot "src"
$stagePkg = Join-Path $stageRoot $pkg

if (-not (Test-Path $srcPkg)) {
    Write-Host "ERROR: live source missing: $srcPkg" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path (Join-Path $RepoRoot "manifest.json"))) {
    Write-Host "ERROR: manifest.json missing at repo root" -ForegroundColor Red
    exit 1
}

New-Item -ItemType Directory -Force -Path dist | Out-Null
New-Item -ItemType Directory -Force -Path $mcpbRoot | Out-Null

# HARD: wipe staging so old crap cannot ship
if (Test-Path $stageRoot) {
    Remove-Item -Recurse -Force $stageRoot
    Write-Host "Wiped stale mcpb\src" -ForegroundColor Yellow
}
New-Item -ItemType Directory -Force -Path $stageRoot | Out-Null
Copy-Item -Recurse -Force $srcPkg $stagePkg
Write-Host "Fresh copy: src\$pkg -> mcpb\src\$pkg" -ForegroundColor Green

# Manifest for pack-from-mcpb layouts; keep root manifest as source of truth
Copy-Item -Force (Join-Path $RepoRoot "manifest.json") (Join-Path $mcpbRoot "manifest.json")

$proj = Get-Content (Join-Path $RepoRoot "pyproject.toml") -Raw
$name = if ($proj -match '(?m)^name = "(.*)"') { $Matches[1] } else { Split-Path -Leaf $RepoRoot }
$ver = if ($proj -match '(?m)^version = "(.*)"') { $Matches[1] } else { "0.1.0" }
$out = Join-Path $RepoRoot "dist\$name-v$ver.mcpb"

# Pack repo root (live src/ + assets); mcpb/src is gitignored and listed in .mcpbignore
# but we still refreshed it so any mcpb/-relative tooling sees current code.
npx --yes @anthropic-ai/mcpb pack $RepoRoot $out
Write-Host "Bundle: $out" -ForegroundColor Green
