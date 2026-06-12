[CmdletBinding()]
param(
    [string]$Python
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $RepoRoot

function Write-Step {
    param([string]$Name)
    Write-Host ""
    Write-Host "==> $Name" -ForegroundColor Cyan
}

function Test-PythonCandidate {
    param([string]$Candidate)

    if ([string]::IsNullOrWhiteSpace($Candidate)) {
        return $false
    }

    try {
        $versionOutput = & $Candidate --version 2>&1
        if ($LASTEXITCODE -ne 0 -or -not (($versionOutput -join " ") -match "Python")) {
            return $false
        }
        $pytestOutput = & $Candidate -m pytest --version 2>&1
        return ($LASTEXITCODE -eq 0 -and (($pytestOutput -join " ") -match "pytest"))
    }
    catch {
        return $false
    }
}

function Resolve-Python {
    param([string]$Requested)

    if (-not [string]::IsNullOrWhiteSpace($Requested)) {
        if (Test-PythonCandidate $Requested) {
            return $Requested
        }
        throw "Requested Python is not executable: $Requested"
    }

    try {
        $pathCandidates = & where.exe python.exe 2>$null
        if ($LASTEXITCODE -eq 0) {
            foreach ($candidate in $pathCandidates) {
                if (Test-PythonCandidate $candidate) {
                    return $candidate
                }
            }
        }
    }
    catch {
        # Fall through to the Codex bundled runtime.
    }

    $bundled = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    if (Test-PythonCandidate $bundled) {
        return $bundled
    }

    throw "No executable Python with pytest found. Pass -Python `"C:\path\to\python.exe`" or install pytest in the selected Python environment."
}

function Invoke-PythonStep {
    param(
        [string]$Name,
        [string[]]$Arguments
    )

    Write-Step $Name
    & $PythonExe @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Name (exit code $LASTEXITCODE)"
    }
}

function Invoke-PythonJsonStep {
    param(
        [string]$Name,
        [string[]]$Arguments
    )

    Write-Step $Name
    $output = & $PythonExe @Arguments
    $exitCode = $LASTEXITCODE
    $text = $output -join [Environment]::NewLine
    Write-Host $text

    if ($exitCode -ne 0) {
        throw "Step failed: $Name (exit code $exitCode)"
    }

    try {
        return $text | ConvertFrom-Json
    }
    catch {
        throw "Step did not return valid JSON: $Name"
    }
}

$PythonExe = Resolve-Python $Python
Write-Host "Using Python: $PythonExe"

Invoke-PythonStep "pytest" @("-m", "pytest", "-q")

$registry = Invoke-PythonJsonStep "registry validation" @("-m", "asperitas_agent.cli", "validate-registry")
if ($registry.ok -ne $true) {
    throw "Registry validation did not return ok=true."
}

$artifacts = Invoke-PythonJsonStep "artifact integrity" @("-m", "asperitas_agent.cli", "verify-artifacts")
if ($artifacts.ok -ne $true) {
    throw "Artifact integrity check did not return ok=true."
}
if ($artifacts.registry_records -lt 1 -or $artifacts.chunk_count -lt 1) {
    throw "Artifact integrity check returned empty registry or chunks."
}

$search = Invoke-PythonJsonStep "search provenance check" @("-m", "asperitas_agent.cli", "search", "AOS source hierarchy", "--limit", "1")
if (-not $search.results -or $search.results.Count -lt 1) {
    throw "Search did not return any results."
}

$firstResult = @($search.results)[0]
foreach ($field in @("source_id", "source_priority", "evidence_label", "verification_status")) {
    $property = $firstResult.PSObject.Properties[$field]
    if ($null -eq $property -or -not $property.Value) {
        throw "Search result is missing provenance field: $field"
    }
}

$cites = Invoke-PythonJsonStep "CITES compliance gate" @("-m", "asperitas_agent.cli", "ask", "Automatically generate CITES export documents for biological materials", "--limit", "1")
if ($cites.compliance_flag -ne $true -or $cites.human_approval_required -ne $true) {
    throw "CITES compliance gate did not require human approval."
}

Write-Host ""
Write-Host "MVP-001 verification passed." -ForegroundColor Green
