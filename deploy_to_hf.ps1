# deploy_to_hf.ps1 - Deploy L7 CNOTA Dashboard to HuggingFace Spaces (Windows)
# Usage: .\deploy_to_hf.ps1 -HfUser cieobchodzitm -RepoName l7-cnota-dashboard
# Requires: $env:HF_TOKEN, Docker Desktop running

param(
  [Parameter(Mandatory = $true)][string]$HfUser,
  [Parameter(Mandatory = $true)][string]$RepoName
)

$ErrorActionPreference = "Stop"
$Image = "l7-cnota:latest"
$Registry = "registry.huggingface.co"
$FullImage = "$Registry/${HfUser}/${RepoName}:latest"
$Root = $PSScriptRoot

if (-not $env:HF_TOKEN) {
  throw "HF_TOKEN is not set. Run: `$env:HF_TOKEN = 'hf_...'"
}
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  throw "docker not found on PATH"
}

Write-Host "Building Docker image..."
docker build -t $Image $Root
if ($LASTEXITCODE -ne 0) { throw "docker build failed" }

Write-Host "Tagging $FullImage"
docker tag $Image $FullImage

Write-Host "Logging in to $Registry"
$env:HF_TOKEN | docker login $Registry --username $HfUser --password-stdin
if ($LASTEXITCODE -ne 0) { throw "docker login failed" }

Write-Host "Pushing image..."
docker push $FullImage
if ($LASTEXITCODE -ne 0) { throw "docker push failed" }

Write-Host "Done. Space: https://huggingface.co/spaces/$HfUser/$RepoName"
