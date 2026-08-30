param(
    [string]$ReplicationRoot = "C:\Users\Public\ggii-u2-replication",
    [int]$Repetitions = 5,
    [int]$ConcurrentWorkers = 2,
    [Parameter(Mandatory = $true)]
    [string]$ExpectedWrapperSha256
)

$ErrorActionPreference = "Stop"

if ($Repetitions -lt 3) {
    throw "Repetitions must be at least 3"
}
if ($ConcurrentWorkers -lt 2) {
    throw "ConcurrentWorkers must be at least 2"
}

$expectedBenchmarkSha256 = "68c839dabace59d67274f8c1df48eff59ada23f128f2705042c92b0697dc187a"
$node = Join-Path $ReplicationRoot "runtime\node-v22.22.2-win-x64\node.exe"
$benchmark = Join-Path $ReplicationRoot "readiness\benchmark-global-geometry-ii-u2-full-evaluation.js"
$readiness = Join-Path $ReplicationRoot "readiness"
$reportPath = Join-Path $readiness "windows-readiness-wrapper-run-v2.json"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Get-LowerSha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}

function Assert-NewOutput([string]$Path) {
    if (Test-Path -LiteralPath $Path) {
        throw "Refusing to overwrite existing readiness output: $Path"
    }
}

function Write-CrlfJsonLines([string]$Path, [string[]]$Lines) {
    $text = ($Lines -join "`r`n") + "`r`n"
    [System.IO.File]::WriteAllText($Path, $text, $utf8NoBom)
}

function Invoke-SequentialBenchmark([string]$OutputPath) {
    Assert-NewOutput $OutputPath
    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    $lines = & $node $benchmark
    $exitCode = $LASTEXITCODE
    $timer.Stop()
    if ($exitCode -ne 0) {
        throw "Benchmark exited with code $exitCode"
    }
    Write-CrlfJsonLines $OutputPath $lines
    return [PSCustomObject]@{
        path = $OutputPath
        bytes = (Get-Item -LiteralPath $OutputPath).Length
        sha256 = Get-LowerSha256 $OutputPath
        processWallSeconds = [Math]::Round($timer.Elapsed.TotalSeconds, 6)
    }
}

if (-not (Test-Path -LiteralPath $node -PathType Leaf)) {
    throw "Portable Node executable is missing"
}
if (-not (Test-Path -LiteralPath $benchmark -PathType Leaf)) {
    throw "Outcome-blind benchmark is missing"
}

$wrapperSha256 = Get-LowerSha256 $PSCommandPath
if ($wrapperSha256 -ne $ExpectedWrapperSha256.ToLowerInvariant()) {
    throw "Wrapper SHA-256 mismatch"
}
if ((Get-LowerSha256 $benchmark) -ne $expectedBenchmarkSha256) {
    throw "Benchmark SHA-256 mismatch"
}
Assert-NewOutput $reportPath

$sequential = @()
for ($index = 1; $index -le $Repetitions; $index += 1) {
    $name = "u2-feasibility-benchmark-windows-default-v2-r{0:d2}.json" -f $index
    $sequential += Invoke-SequentialBenchmark (Join-Path $readiness $name)
}

$concurrentPaths = @()
for ($index = 1; $index -le $ConcurrentWorkers; $index += 1) {
    $name = "u2-feasibility-benchmark-windows-concurrent-v2-c{0:d2}.json" -f $index
    $path = Join-Path $readiness $name
    Assert-NewOutput $path
    $concurrentPaths += $path
}

$jobScript = {
    param($NodePath, $BenchmarkPath, $OutputPath)
    $ErrorActionPreference = "Stop"
    $encoding = New-Object System.Text.UTF8Encoding($false)
    $startedAtUtc = [DateTime]::UtcNow.ToString("o")
    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    $lines = & $NodePath $BenchmarkPath
    $exitCode = $LASTEXITCODE
    $timer.Stop()
    if ($exitCode -ne 0) {
        throw "Benchmark exited with code $exitCode"
    }
    [System.IO.File]::WriteAllText($OutputPath, (($lines -join "`r`n") + "`r`n"), $encoding)
    [PSCustomObject]@{
        path = $OutputPath
        bytes = (Get-Item -LiteralPath $OutputPath).Length
        sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $OutputPath).Hash.ToLowerInvariant()
        startedAtUtc = $startedAtUtc
        endedAtUtc = [DateTime]::UtcNow.ToString("o")
        processWallSeconds = [Math]::Round($timer.Elapsed.TotalSeconds, 6)
    }
}

$groupStartedAtUtc = [DateTime]::UtcNow.ToString("o")
$groupTimer = [System.Diagnostics.Stopwatch]::StartNew()
$jobs = @()
foreach ($path in $concurrentPaths) {
    $jobs += Start-Job -ScriptBlock $jobScript -ArgumentList $node, $benchmark, $path
}
try {
    $jobs | Wait-Job | Out-Null
    $received = @($jobs | Receive-Job)
    $concurrent = @($received | ForEach-Object {
        [PSCustomObject]@{
            path = $_.path
            bytes = $_.bytes
            sha256 = $_.sha256
            startedAtUtc = $_.startedAtUtc
            endedAtUtc = $_.endedAtUtc
            processWallSeconds = $_.processWallSeconds
        }
    })
    foreach ($job in $jobs) {
        if ($job.State -ne "Completed") {
            throw "Concurrent benchmark job did not complete: $($job.State)"
        }
    }
}
finally {
    $jobs | Remove-Job -Force -ErrorAction SilentlyContinue
}
$groupTimer.Stop()

$record = [ordered]@{
    schema = "ggii.u2.windows-readiness-wrapper-run/2"
    scientificOutcome = $false
    purpose = "Repeated and concurrent synthetic numerical-kernel throughput only"
    generatedAtUtc = [DateTime]::UtcNow.ToString("o")
    wrapperSha256 = $wrapperSha256
    benchmarkSha256 = $expectedBenchmarkSha256
    benchmarkSourceCommit = "e240c1bdc2037ecd597bbfc535e233109194c4f8"
    nodeVersion = (& $node --version)
    exactBenchmarkArgs = @()
    repetitions = $Repetitions
    sequential = $sequential
    concurrent = [ordered]@{
        workers = $ConcurrentWorkers
        groupStartedAtUtc = $groupStartedAtUtc
        groupEndedAtUtc = [DateTime]::UtcNow.ToString("o")
        groupWallSeconds = [Math]::Round($groupTimer.Elapsed.TotalSeconds, 6)
        items = $concurrent
    }
    rawEncoding = [ordered]@{
        characterEncoding = "UTF-8"
        byteOrderMark = $false
        lineEnding = "CRLF"
        trailingLineEndingCount = 1
    }
    outcomeBlindBenchmarkTransferred = $true
    u2ScientificSourceTransferred = $false
    scientificOutcomesRun = $false
}

$reportLines = ($record | ConvertTo-Json -Depth 8) -split "`r?`n"
Write-CrlfJsonLines $reportPath $reportLines
[PSCustomObject]@{
    reportPath = $reportPath
    reportBytes = (Get-Item -LiteralPath $reportPath).Length
    reportSha256 = Get-LowerSha256 $reportPath
    wrapperSha256 = $wrapperSha256
    benchmarkSha256 = $expectedBenchmarkSha256
    repetitions = $Repetitions
    concurrentWorkers = $ConcurrentWorkers
} | ConvertTo-Json -Compress
