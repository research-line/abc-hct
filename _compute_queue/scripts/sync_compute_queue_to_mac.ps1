param(
    [string]$MacHost = "lukas@100.119.69.90",
    [string]$KeyPath = "$env:USERPROFILE\.ssh\id_ed25519_mcmc",
    [string]$RemoteRoot = "/Users/lukas/compute/abc_hct"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")

ssh -i $KeyPath -o BatchMode=yes -o ConnectTimeout=20 $MacHost "mkdir -p '$RemoteRoot/_compute_queue' '$RemoteRoot/_scripts' '$RemoteRoot/_results'"

scp -i $KeyPath -r `
    (Join-Path $ProjectRoot "_compute_queue") `
    "${MacHost}:$RemoteRoot/"

$scripts = @(
    "_scripts/mstar_h3a_qb3_wiedemann_production.sage",
    "_scripts/qb3_wiedemann_certificate_verify.py",
    "_scripts/qb3_wiedemann_production_runbook.py"
)

foreach ($rel in $scripts) {
    $src = Join-Path $ProjectRoot $rel
    if (Test-Path $src) {
        scp -i $KeyPath $src "${MacHost}:$RemoteRoot/$rel"
    }
}

$guards = @(
    "_results/mstar_h3a_qb3_wiedemann_smoke_80224_raw_guard_2026-05-23.json",
    "_results/mstar_h3a_qb3_wiedemann_smoke_80224_anc_guard_2026-05-23.json",
    "_results/mstar_h3a_restline_kernel_quotient_80224_raw_2026-05-17.json",
    "_results/mstar_h3a_restline_kernel_quotient_80224_anc_2026-05-17.json"
)

foreach ($rel in $guards) {
    $src = Join-Path $ProjectRoot $rel
    if (Test-Path $src) {
        scp -i $KeyPath $src "${MacHost}:$RemoteRoot/$rel"
    }
}

Write-Output "Synced compute queue to ${MacHost}:$RemoteRoot"
