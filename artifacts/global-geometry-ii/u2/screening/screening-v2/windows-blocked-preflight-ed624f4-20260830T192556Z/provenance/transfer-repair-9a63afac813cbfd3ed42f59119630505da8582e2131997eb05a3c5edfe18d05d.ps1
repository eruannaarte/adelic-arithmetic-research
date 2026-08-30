$ErrorActionPreference = 'Stop'
$runRoot = 'C:\Users\Public\ggii-u2-replication\runs\screening-v2-ed624f4-20260830T192556Z'
$archive = Join-Path $runRoot 'incoming\source-1c3373267057b8a018ad5039e0f3b2b4e8eb2b1d.zip'
$boundaryIncoming = Join-Path $runRoot 'incoming\source-boundary-v2.json'
$sourceRoot = Join-Path $runRoot 'source'
$provenancePath = Join-Path $runRoot 'provenance\transfer-verification.json'
$archiveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash.ToLowerInvariant()
$boundaryHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $boundaryIncoming).Hash.ToLowerInvariant()
if ($archiveHash -ne 'a28677772f4a372bc720b2eee7e4f62c011a276cc8d234e8b7684b74d0287984') { throw "archive transfer hash mismatch: $archiveHash" }
if ($boundaryHash -ne 'c60331209247fccee700d10d38b9ae03da3f81e9013f19281a1f5918fb9e6c73') { throw "boundary transfer hash mismatch: $boundaryHash" }
if (Test-Path -LiteralPath $provenancePath) { throw 'refusing to overwrite transfer provenance' }

$boundary = Get-Content -Raw -LiteralPath $boundaryIncoming | ConvertFrom-Json
$beforeCopy = @(Get-ChildItem -LiteralPath $sourceRoot -File -Recurse | ForEach-Object { $_.FullName.Substring($sourceRoot.Length + 1).Replace('\', '/') } | Sort-Object)
$expectedBeforeCopy = @($boundary.files | ForEach-Object { $_.path } | Sort-Object)
if (($beforeCopy -join "`n") -ne ($expectedBeforeCopy -join "`n")) { throw "extracted C1 path-set mismatch before repair: actual=$($beforeCopy.Count), expected=$($expectedBeforeCopy.Count)" }

$verifiedFiles = @()
foreach ($entry in $boundary.files) {
  $full = Join-Path $sourceRoot ($entry.path.Replace('/', '\'))
  $item = Get-Item -LiteralPath $full
  $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $full).Hash.ToLowerInvariant()
  if ($item.Length -ne $entry.bytes -or $hash -ne $entry.sha256) { throw "extracted file mismatch: $($entry.path)" }
  $verifiedFiles += [ordered]@{ path = $entry.path; bytes = [long]$item.Length; sha256 = $hash }
}

$boundaryRelative = 'artifacts/global-geometry-ii/u2/screening/screening-v2/source-boundary-v2.json'
$boundaryTarget = Join-Path $sourceRoot ($boundaryRelative.Replace('/', '\'))
if (Test-Path -LiteralPath $boundaryTarget) { throw 'boundary target already exists; refusing overwrite' }
New-Item -ItemType Directory -Path (Split-Path -Parent $boundaryTarget) -Force | Out-Null
Copy-Item -LiteralPath $boundaryIncoming -Destination $boundaryTarget
$targetBoundaryHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $boundaryTarget).Hash.ToLowerInvariant()
if ($targetBoundaryHash -ne $boundaryHash) { throw 'extracted boundary hash mismatch' }

$expectedAfterCopy = @($expectedBeforeCopy) + @($boundaryRelative) | Sort-Object
$afterCopy = @(Get-ChildItem -LiteralPath $sourceRoot -File -Recurse | ForEach-Object { $_.FullName.Substring($sourceRoot.Length + 1).Replace('\', '/') } | Sort-Object)
if (($afterCopy -join "`n") -ne ($expectedAfterCopy -join "`n")) { throw "source path-set mismatch after boundary copy: actual=$($afterCopy.Count), expected=$($expectedAfterCopy.Count)" }

$gitAvailable = [bool](Get-Command git -ErrorAction SilentlyContinue)
if ($gitAvailable) { throw 'portable policy violation: Git is available on default PATH' }
$nodePath = 'C:\Users\Public\ggii-u2-replication\runtime\node-v22.22.2-win-x64\node.exe'
if (-not (Test-Path -LiteralPath $nodePath -PathType Leaf)) { throw 'portable Node executable missing' }

$payload = [ordered]@{
  schema = 'gg.u2.screening.windows-transfer-verification/1'
  semanticRole = 'outcome-blind transfer and extraction provenance; no decision authority'
  runId = 'screening-v2-ed624f4-20260830T192556Z'
  sourceCommit = '1c3373267057b8a018ad5039e0f3b2b4e8eb2b1d'
  boundaryCommit = 'ed624f4ff42b4e5488a1889c3d55ba1195e5a952'
  archive = [ordered]@{ bytes = [long](Get-Item -LiteralPath $archive).Length; sha256 = $archiveHash; fileEntryCount = 15 }
  boundary = [ordered]@{ bytes = [long](Get-Item -LiteralPath $boundaryIncoming).Length; sha256 = $boundaryHash; semanticDigest = 'a1b1b9bb525ba9c172be48af60b9881a13ce58ebed9862a60fec18a25f07fae0' }
  extraction = [ordered]@{ exactPathSetVerified = $true; requiredFileCount = 15; totalFileCountIncludingBoundary = $afterCopy.Count; files = $verifiedFiles }
  setupRepair = [ordered]@{ initialVerifierSha256 = '61c74d64bc82587af79a05319338574372e18722e09554c2eb361f913a4ce342'; initialFailure = 'boundary parent directory absent after valid extraction; runner was not invoked'; action = 'created only the missing boundary parent and copied the separately pinned boundary' }
  executionPreflight = [ordered]@{ portableNodeExists = $true; gitAvailableOnDefaultPath = $false; sourceMode = 'portable' }
  outcome = [ordered]@{ u2Status = 'UNRESOLVED'; decisionAuthority = 'NONE' }
}
$payloadCompact = $payload | ConvertTo-Json -Depth 8 -Compress
$sha = [Security.Cryptography.SHA256]::Create()
try {
  $payloadDigest = ([BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($payloadCompact)))).Replace('-', '').ToLowerInvariant()
} finally {
  $sha.Dispose()
}
$artifact = [ordered]@{}
foreach ($key in $payload.Keys) { $artifact[$key] = $payload[$key] }
$artifact['contentAddress'] = [ordered]@{ algorithm = 'sha256'; serialization = 'PowerShell ConvertTo-Json -Compress over ordered payload'; digest = $payloadDigest; bytes = [Text.Encoding]::UTF8.GetByteCount($payloadCompact) }
$artifactJson = $artifact | ConvertTo-Json -Depth 8
[IO.File]::WriteAllText($provenancePath, $artifactJson + "`n", [Text.UTF8Encoding]::new($false))
$provenanceFileHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $provenancePath).Hash.ToLowerInvariant()

[ordered]@{
  verified = $true
  archiveSha256 = $archiveHash
  boundarySha256 = $boundaryHash
  requiredFiles = $verifiedFiles.Count
  exactSourceFileCount = $afterCopy.Count
  gitOnDefaultPath = $gitAvailable
  provenancePayloadDigest = $payloadDigest
  provenanceFileSha256 = $provenanceFileHash
} | ConvertTo-Json -Compress
