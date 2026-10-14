# Apply GitHub branch protection for main and develop.
# Requires: gh CLI, admin on minhhung2556/cv_tailor, and a public repo (or GitHub Pro for private).
$ErrorActionPreference = "Stop"
$Repo = "minhhung2556/cv_tailor"
$Payload = Join-Path $PSScriptRoot "apply_branch_protection.json"

foreach ($Branch in @("main", "develop")) {
    Write-Host "Protecting $Branch ..."
    gh api --method PUT "repos/$Repo/branches/$Branch/protection" --input $Payload
}

Write-Host "Done."
