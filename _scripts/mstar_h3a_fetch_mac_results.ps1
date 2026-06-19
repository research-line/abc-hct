param(
    [string]$MacHost = "lukas@100.119.69.90",
    [string]$KeyPath = "$env:USERPROFILE\.ssh\id_ed25519_mcmc",
    [string]$RemoteRoot = "/Users/lukas/compute/abc_hct",
    [string]$LocalRoot = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if (-not $LocalRoot) {
    $LocalRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Run-Checked {
    param([string[]]$Command)
    if ($DryRun) {
        Write-Host "[dry-run] $($Command -join ' ')"
        return
    }
    & $Command[0] @($Command[1..($Command.Length - 1)])
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $($Command -join ' ')"
    }
}

$items = @(
    "_results/mstar_h3a_120336_raw_standard_postprocess_2026-05-16_rank_verify.json",
    "_results/mstar_h3a_120336_raw_standard_postprocess_2026-05-16_rank_verify.md",
    "_results/mstar_h3a_240672_raw_rc3c_standard_2026-05-16.json",
    "_results/mstar_h3a_240672_raw_rc3c_standard_2026-05-16.md",
    "_results/mstar_h3a_240672_raw_standard_postprocess_2026-05-16.status.json",
    "_results/mstar_h3a_240672_raw_standard_postprocess_2026-05-16_order.json",
    "_results/mstar_h3a_240672_raw_standard_postprocess_2026-05-16_order.md",
    "_results/mstar_h3a_240672_raw_standard_postprocess_2026-05-16_rank_verify.json",
    "_results/mstar_h3a_240672_raw_standard_postprocess_2026-05-16_rank_verify.md",
    "_results/mstar_h3a_240672_raw_standard_auto_postprocess_2026-05-17.status.json",
    "_results/mstar_h3a_240672_raw_standard_auto_postprocess_2026-05-17_order.json",
    "_results/mstar_h3a_240672_raw_standard_auto_postprocess_2026-05-17_order.md",
    "_results/mstar_h3a_240672_raw_standard_auto_postprocess_2026-05-17_rank_verify.json",
    "_results/mstar_h3a_240672_raw_standard_auto_postprocess_2026-05-17_rank_verify.md",
    "_results/mstar_h3a_240672_raw_restline_t7_minikill_2026-05-17.status.json",
    "_results/mstar_h3a_240672_raw_restline_t7_minikill_2026-05-17.json",
    "_results/mstar_h3a_240672_raw_restline_t7_minikill_2026-05-17.md",
    "_results/h3a_residue_line_witness_240672_raw_standard_2026-05-16",
    "_results/h3a_residue_line_witness_240672_raw_standard_auto_2026-05-17",
    "_results/h3a_residue_line_witness_240672_raw_restline_t7_minikill_2026-05-17",
    "_results/mstar_h3a_240672_raw_restline_t7_minikill_2026-05-17_work",
    "_results/rc3c_standard_witness_240672_raw_q3863_2026-05-16",
    "_logs/mstar_h3a_240672_raw_rc3c_standard_2026-05-16.log",
    "_logs/mstar_h3a_240672_raw_standard_postprocess_2026-05-16.watcher.log",
    "_logs/mstar_h3a_240672_raw_standard_auto_postprocess_2026-05-17.watcher.log",
    "_logs/mstar_h3a_240672_raw_restline_t7_minikill_2026-05-17.log"
)

foreach ($item in $items) {
    $localPath = Join-Path $LocalRoot $item
    $localParent = Split-Path -Parent $localPath
    New-Item -ItemType Directory -Force -Path $localParent | Out-Null

    $remoteTest = "cd '$RemoteRoot' && if [ -e '$item' ]; then echo EXISTS; else echo MISSING; fi"
    $exists = & ssh -n -T -i $KeyPath -o BatchMode=yes -o ConnectTimeout=8 $MacHost $remoteTest
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[skip: ssh-failed] $item"
        continue
    }
    if (($exists | Select-Object -Last 1) -ne "EXISTS") {
        Write-Host "[skip] $item"
        continue
    }

    $remotePath = "${MacHost}:$RemoteRoot/$item"
    Write-Host "[fetch] $item"
    Run-Checked @("scp", "-i", $KeyPath, "-r", $remotePath, $localParent)
}

Write-Host "Fetch complete."
