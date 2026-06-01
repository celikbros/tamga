param(
    [string]$Patterns = "artifacts\private\v1_7_full_eval_leakage_patterns.regex",
    [string]$Corpus = "data\train\private\celik_ai\celik_gold_corpus.clean.jsonl",
    [string]$Out = "artifacts\private\v1_7_full_eval_leakage_rg_hits.txt",
    [int]$PollSeconds = 30
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PatternPath = Join-Path $RepoRoot $Patterns
$CorpusPath = Join-Path $RepoRoot $Corpus
$OutPath = Join-Path $RepoRoot $Out

if (-not (Get-Command rg -ErrorAction SilentlyContinue)) {
    throw "ripgrep (rg) is not available on PATH."
}
if (-not (Test-Path -LiteralPath $PatternPath)) {
    throw "Pattern file not found: $PatternPath"
}
if (-not (Test-Path -LiteralPath $CorpusPath)) {
    throw "Corpus file not found: $CorpusPath"
}

$OutDir = Split-Path -Parent $OutPath
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
Remove-Item -LiteralPath $OutPath -ErrorAction SilentlyContinue

Write-Host "Starting full eval leakage rg scan"
Write-Host "repo:     $RepoRoot"
Write-Host "patterns: $PatternPath"
Write-Host "corpus:   $CorpusPath"
Write-Host "out:      $OutPath"
Write-Host "poll:     every $PollSeconds seconds"

$argsList = @(
    "--pcre2",
    "-n",
    "-i",
    "-f",
    $PatternPath,
    $CorpusPath
)

$process = Start-Process -FilePath "rg" `
    -ArgumentList $argsList `
    -RedirectStandardOutput $OutPath `
    -RedirectStandardError "$OutPath.stderr" `
    -NoNewWindow `
    -PassThru

$start = Get-Date
while (-not $process.HasExited) {
    $elapsed = [int]((Get-Date) - $start).TotalSeconds
    $size = if (Test-Path -LiteralPath $OutPath) { (Get-Item -LiteralPath $OutPath).Length } else { 0 }
    Write-Host ("still running... elapsed={0}s output_size={1:n0} bytes" -f $elapsed, $size)
    Start-Sleep -Seconds $PollSeconds
    $process.Refresh()
}

$process.WaitForExit()
$process.Refresh()
$elapsedTotal = [int]((Get-Date) - $start).TotalSeconds
$exitCode = $process.ExitCode
$lineCount = if (Test-Path -LiteralPath $OutPath) {
    (Get-Content -LiteralPath $OutPath).Count
} else {
    0
}

Write-Host "DONE"
Write-Host "rg_exit_code=$exitCode"
Write-Host "elapsed_seconds=$elapsedTotal"
Write-Host "hit_line_count=$lineCount"
Write-Host "first 20 lines:"
if (Test-Path -LiteralPath $OutPath) {
    Get-Content -LiteralPath $OutPath -TotalCount 20
}

if (Test-Path -LiteralPath "$OutPath.stderr") {
    $stderrSize = (Get-Item -LiteralPath "$OutPath.stderr").Length
    if ($stderrSize -gt 0) {
        Write-Host "stderr:"
        Get-Content -LiteralPath "$OutPath.stderr" -TotalCount 20
    }
}
