# Create a clean deployable archive of the L7 CNOTA stack (no node_modules / .git)
param(
  [string]$OutDir = (Join-Path (Split-Path $PSScriptRoot -Parent) "dist-packages")
)

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$stage = Join-Path $env:TEMP "l7-cnota-deploy-$stamp"
$zip = Join-Path $OutDir "l7-cnota-deployment-$stamp.zip"

New-Item -ItemType Directory -Force -Path $stage, $OutDir | Out-Null

$include = @(
  "Dockerfile",
  "docker-compose.yml",
  "deploy_to_hf.sh",
  "deploy_to_hf.ps1",
  ".dockerignore",
  ".env.example",
  "README.md",
  "LICENSE",
  "backend",
  "frontend"
)

foreach ($item in $include) {
  $src = Join-Path $Root $item
  if (-not (Test-Path $src)) { Write-Warning "Missing $item"; continue }
  $dest = Join-Path $stage $item
  if (Test-Path $src -PathType Container) {
    Copy-Item -Recurse -Force $src $dest
  } else {
    $parent = Split-Path $dest -Parent
    if ($parent) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    Copy-Item -Force $src $dest
  }
}

# Strip build artifacts from package
@(
  "frontend\node_modules",
  "frontend\dist",
  "backend\__pycache__",
  "backend\routers\__pycache__"
) | ForEach-Object {
  $p = Join-Path $stage $_
  if (Test-Path $p) { Remove-Item -Recurse -Force $p }
}

if (Test-Path $zip) { Remove-Item -Force $zip }
Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $zip -Force
Remove-Item -Recurse -Force $stage

Write-Host "Deployment package: $zip"
Write-Output $zip
