<#
.SYNOPSIS
    Fill in any remaining placeholders and generate every local asset for the
    naitikk31 GitHub profile README.

.EXAMPLE
    .\setup.ps1 -Image .\me.jpg

.EXAMPLE
    # regenerate the portrait with different settings
    .\setup.ps1 -Image .\me.jpg -Cols 110 -Circle

.EXAMPLE
    # try the binary grid look instead of dots
    .\setup.ps1 -Image .\me.jpg -Mode binary -Cols 62
#>
[CmdletBinding()]
param(
    [string]$Image,
    [ValidateSet('dots', 'binary', 'ascii', 'braille')]
    [string]$Mode = 'dots',
    [int]$Cols = 100,
    [switch]$Circle,
    [switch]$Color,
    [switch]$Animate,
    [switch]$Invert,
    [switch]$Square,
    [string]$Focus = '0.5,0.5'
)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot

Write-Host "`n[1/3] drawing the skill radar" -ForegroundColor Cyan
python (Join-Path $root 'scripts\radar.py') --data (Join-Path $root 'assets\skills.json') -o (Join-Path $root 'assets\radar')

Write-Host "      drawing the language radar from the GitHub API" -ForegroundColor Cyan
try {
    python (Join-Path $root 'scripts\radar.py') --github naitikk31 -o (Join-Path $root 'assets\radar-langs') --values --limit 7 --curve 0.4 --exclude "shell,makefile,dockerfile,batchfile,procfile,html,css"
} catch {
    Write-Warning "language radar skipped (API error or no token): $_"
}

Write-Host "`n[2/3] generating stat and repo cards" -ForegroundColor Cyan
try {
    python (Join-Path $root 'scripts\cards.py') --user naitikk31 --projects (Join-Path $root 'assets\projects.json') --out (Join-Path $root 'assets')
} catch {
    Write-Warning "cards skipped: $_"
}

if ($Image) {
    Write-Host "`n[3/3] dot-matrixing $Image" -ForegroundColor Cyan
    $dotArgs = @(
        (Join-Path $root 'scripts\dotify.py'), $Image,
        '-o', (Join-Path $root 'assets\portrait'),
        '--mode', $Mode, '--cols', $Cols,
        '--equalize', '--detail', '0.5', '--reveal'
    )
    if ($Square)  { $dotArgs += @('--square', '--focus', $Focus) }
    if ($Circle)  { $dotArgs += '--circle' }
    if ($Color)   { $dotArgs += '--color' }
    if ($Animate) { $dotArgs += '--animate' }
    if ($Invert)  { $dotArgs += '--invert' }
    python @dotArgs
} else {
    Write-Host "`n[3/3] no -Image given, skipping the portrait" -ForegroundColor DarkGray
    Write-Host "      Once you have a photo, run:" -ForegroundColor DarkGray
    Write-Host "      .\setup.ps1 -Image .\me.jpg" -ForegroundColor Yellow
}

Write-Host "`ndone. Open preview.html to inspect results, then read SETUP.md.`n" -ForegroundColor Green
