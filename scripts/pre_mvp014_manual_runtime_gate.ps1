# PRE-MVP014 MANUAL RUNTIME GATE
# Run in VS Code Terminal / standalone PowerShell, NOT Codex.

$ErrorActionPreference = "Stop"

$worktreePath = "C:\Users\jbc89\OneDrive\문서\Asperitas AI agent\.work\_clean_worktrees\pre_mvp014_runtime_20260621_152238"
Set-Location $worktreePath

Write-Output "=== 1. CLEAN WORKTREE CHECK ==="
git status --short --branch
git rev-parse --short HEAD
git rev-parse HEAD
git rev-list --left-right --count origin/main...HEAD

Write-Output "=== 2. PROCESS CHECK ==="
$procs = @(Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like "*scripts/run_retrieval_eval.py*" })
$procs | Select-Object ProcessId,ParentProcessId,CommandLine | Format-List

if ($procs.Count -gt 0) {
  Write-Output "HOLD_EXISTING_RETRIEVAL_PROCESS"
  Write-Output "Close/stop the Codex task that is spawning these processes, then rerun this script."
  exit 1
}

Write-Output "=== 3. ARTIFACT VERIFY ==="
python scripts/verify_artifacts.py
if ($LASTEXITCODE -ne 0) { throw "HOLD_ARTIFACT_VERIFY_FAILED" }

Write-Output "=== 4. MVP003 RUN 1 ==="
$env:PYTHONUNBUFFERED="1"
$env:PYTHONFAULTHANDLER="1"
$env:PYTHONIOENCODING="utf-8"

Measure-Command { python -X faulthandler -u scripts/run_retrieval_eval.py --retriever mvp003 --limit 5 }
if ($LASTEXITCODE -ne 0) { throw "HOLD_MVP003_RUN1_FAILED" }

Write-Output "=== 5. MVP003 RUN 2 ==="
Measure-Command { python -X faulthandler -u scripts/run_retrieval_eval.py --retriever mvp003 --limit 5 }
if ($LASTEXITCODE -ne 0) { throw "HOLD_MVP003_RUN2_FAILED" }

Write-Output "=== 6. CMD REDIRECTION CHECK ==="
$logDir = Join-Path (Get-Location).Path ".runtime_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$cmdOut = Join-Path $logDir "cmd_mvp003.stdout.log"
$cmdErr = Join-Path $logDir "cmd_mvp003.stderr.log"
$cmd = "python -X faulthandler -u scripts/run_retrieval_eval.py --retriever mvp003 --limit 5 > `"$cmdOut`" 2> `"$cmdErr`""

Measure-Command { cmd.exe /c $cmd }
if ($LASTEXITCODE -ne 0) { throw "HOLD_CMD_REDIRECTION_FAILED" }

Select-String -Path $cmdOut -Pattern "Overall pass rate"

Write-Output "=== 7. FAST SANITY ==="
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
if ($LASTEXITCODE -ne 0) { throw "HOLD_BASELINE_FAILED" }

python scripts/run_retrieval_eval.py --retriever vector --limit 5
if ($LASTEXITCODE -ne 0) { throw "HOLD_VECTOR_FAILED" }

python scripts/verify_artifacts.py
if ($LASTEXITCODE -ne 0) { throw "HOLD_FINAL_ARTIFACT_VERIFY_FAILED" }

Write-Output "=== 8. FINAL CHECK ==="
git status --short --branch
git rev-list --left-right --count origin/main...HEAD

$finalProcs = @(Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like "*scripts/run_retrieval_eval.py*" })
Write-Output "FINAL_RETRIEVAL_PROCESS_COUNT=$($finalProcs.Count)"
$finalProcs | Select-Object ProcessId,ParentProcessId,CommandLine | Format-List

if ($finalProcs.Count -gt 0) { throw "HOLD_FINAL_RETRIEVAL_PROCESS_LEFT" }

Write-Output "=== FINAL REPORT ==="
Write-Output "CLEAN_WORKTREE_RUNTIME_GO_MVP014_PREFLIGHT"
Write-Output "NEXT_STEP=PROCEED_TO_MVP014_PREFLIGHT"
