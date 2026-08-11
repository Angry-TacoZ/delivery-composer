[CmdletBinding()]
param(
    [string]$ProjectId = "composermvp-4d5c0",
    [string]$Region = "us-east1",
    [string]$ServiceName = "delivery-composer-api",
    [string]$CustomDomain = "composer.jamesai.space",
    [switch]$BudgetAlertConfirmed
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$runtimeServiceAccount = "delivery-composer-runtime@$ProjectId.iam.gserviceaccount.com"

function Assert-LastExitCode([string]$Action) {
    if ($LASTEXITCODE -ne 0) {
        throw "$Action failed with exit code $LASTEXITCODE."
    }
}

function Invoke-Firebase([string[]]$FirebaseArguments) {
    if (Get-Command firebase.cmd -ErrorAction SilentlyContinue) {
        & firebase.cmd @FirebaseArguments
    }
    else {
        & npx.cmd --yes firebase-tools@latest @FirebaseArguments
    }
    Assert-LastExitCode "Firebase CLI"
}

function Resolve-GcloudCommand {
    $command = Get-Command gcloud.cmd -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $localInstall = Join-Path $env:LOCALAPPDATA "Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
    if (Test-Path $localInstall) {
        return $localInstall
    }

    $machineInstall = Join-Path $env:ProgramFiles "Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
    if (Test-Path $machineInstall) {
        return $machineInstall
    }

    throw "Google Cloud CLI is required. Install and authenticate gcloud before deployment."
}

if (-not $BudgetAlertConfirmed) {
    throw "Create and verify a Cloud Billing budget alert, then rerun with -BudgetAlertConfirmed."
}

$gcloudCommand = Resolve-GcloudCommand

Push-Location $repoRoot
try {
    & git fetch origin
    Assert-LastExitCode "git fetch"
    $branch = (& git branch --show-current).Trim()
    Assert-LastExitCode "git branch inspection"
    if ($branch -ne "main") {
        throw "Deployments must run from main; current branch is '$branch'."
    }
    if (& git status --porcelain) {
        throw "The worktree must be clean before deployment."
    }
    $localHead = (& git rev-parse HEAD).Trim()
    $remoteHead = (& git rev-parse origin/main).Trim()
    if ($localHead -ne $remoteHead) {
        throw "Local main must exactly match origin/main before deployment."
    }

    $env:PYTHONUTF8 = "1"
    & (Join-Path $repoRoot "scripts\verify.ps1")
    Assert-LastExitCode "Repository verification"

    & $gcloudCommand config set project $ProjectId --quiet
    Assert-LastExitCode "Google Cloud project selection"
    & $gcloudCommand services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com iam.googleapis.com --quiet
    Assert-LastExitCode "Google Cloud API enablement"

    $projectNumber = (& $gcloudCommand projects describe $ProjectId --format "value(projectNumber)").Trim()
    Assert-LastExitCode "Google Cloud project number lookup"
    if (-not $projectNumber) {
        throw "Google Cloud did not return a project number for '$ProjectId'."
    }
    $buildServiceAccount = "$projectNumber-compute@developer.gserviceaccount.com"
    $builderRole = & $gcloudCommand projects get-iam-policy $ProjectId `
        --flatten "bindings[].members" `
        --filter "bindings.role=roles/run.builder AND bindings.members=serviceAccount:$buildServiceAccount" `
        --format "value(bindings.role)"
    Assert-LastExitCode "Cloud Run builder role lookup"
    if (-not $builderRole) {
        & $gcloudCommand projects add-iam-policy-binding $ProjectId `
            --member "serviceAccount:$buildServiceAccount" `
            --role "roles/run.builder" `
            --condition None `
            --quiet
        Assert-LastExitCode "Cloud Run builder role assignment"
    }

    $existingRuntimeAccount = & $gcloudCommand iam service-accounts list `
        --project $ProjectId `
        --filter "email=$runtimeServiceAccount" `
        --format "value(email)"
    Assert-LastExitCode "Runtime service account lookup"
    if (-not $existingRuntimeAccount) {
        & $gcloudCommand iam service-accounts create delivery-composer-runtime `
            --project $ProjectId `
            --display-name "Delivery Composer runtime" `
            --quiet
        Assert-LastExitCode "Runtime service account creation"
    }

    & $gcloudCommand run deploy $ServiceName `
        --project $ProjectId `
        --region $Region `
        --source (Join-Path $repoRoot "api") `
        --service-account $runtimeServiceAccount `
        --allow-unauthenticated `
        --ingress all `
        --execution-environment gen2 `
        --cpu 1 `
        --cpu-throttling `
        --memory 512Mi `
        --concurrency 20 `
        --timeout 60 `
        --min 0 `
        --max 1 `
        --no-session-affinity `
        --clear-cloudsql-instances `
        --clear-secrets `
        --liveness-probe "httpGet.path=/api/health,httpGet.port=8080,initialDelaySeconds=5,timeoutSeconds=5,periodSeconds=30,failureThreshold=3" `
        --labels "application=delivery-composer,environment=demo,data=synthetic" `
        --set-env-vars "DEMO_MODE=true,ALLOWED_ORIGINS=https://$CustomDomain,RATE_LIMIT_REQUESTS=10,RATE_LIMIT_WINDOW_SECONDS=900" `
        --quiet
    Assert-LastExitCode "Cloud Run deployment"

    $serviceUrl = (& $gcloudCommand run services describe $ServiceName `
        --project $ProjectId `
        --region $Region `
        --format "value(status.url)").Trim()
    Assert-LastExitCode "Cloud Run URL lookup"
    if (-not $serviceUrl) {
        throw "Cloud Run did not return a service URL."
    }

    $directHealth = Invoke-RestMethod -Uri "$serviceUrl/api/health" -TimeoutSec 30
    if (
        $directHealth.status -ne "ok" -or
        $directHealth.execution_mode -ne "deterministic_demo" -or
        -not $directHealth.demo_mode -or
        $directHealth.database_configured -or
        $directHealth.gemini_configured
    ) {
        throw "Cloud Run health response does not match the deterministic, credential-free contract."
    }

    Invoke-Firebase @("deploy", "--only", "hosting", "--project", $ProjectId)

    $hostingUrl = "https://$ProjectId.web.app"
    $hostingVerified = $false
    for ($attempt = 1; $attempt -le 6; $attempt++) {
        try {
            $hostingResponse = Invoke-WebRequest -Uri $hostingUrl -TimeoutSec 30
            if ($hostingResponse.StatusCode -ne 200 -or $hostingResponse.Content -notmatch "Delivery Composer") {
                throw "Firebase Hosting did not return the expected application shell."
            }
            $hostingHealth = Invoke-RestMethod -Uri "$hostingUrl/api/health" -TimeoutSec 30
            if ($hostingHealth.execution_mode -ne "deterministic_demo") {
                throw "Firebase Hosting is not routing API requests to the deterministic Cloud Run service."
            }
            $hostingVerified = $true
            break
        }
        catch {
            if ($attempt -eq 6) {
                throw "Firebase Hosting did not pass its smoke tests after a bounded propagation wait: $($_.Exception.Message)"
            }
            Start-Sleep -Seconds 5
        }
    }
    if (-not $hostingVerified) {
        throw "Firebase Hosting verification ended without a passing result."
    }

    Write-Host "Deployment verified."
    Write-Host "Hosting: $hostingUrl"
    Write-Host "Cloud Run: $serviceUrl"
    Write-Host "Next: connect $CustomDomain in Firebase Hosting and verify DNS plus HTTPS."
}
finally {
    Pop-Location
}
