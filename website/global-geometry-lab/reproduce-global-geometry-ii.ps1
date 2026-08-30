[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateNotNullOrEmpty()]
    [string]$Certificate
)

$ErrorActionPreference = "Stop"
$Verifier = Join-Path $PSScriptRoot "reproduce-global-geometry-ii.js"

if (-not (Test-Path -LiteralPath $Verifier -PathType Leaf)) {
    throw "Global Geometry II verifier not found beside this wrapper: $Verifier"
}

$NodeCommand = Get-Command node -ErrorAction Stop
$Arguments = @($Verifier, "--verify")
if ($PSBoundParameters.ContainsKey("Certificate")) {
    # The Node entrypoint resolves relative certificate paths from the repository
    # root, so invocation behavior is independent of the PowerShell working dir.
    $Arguments += @("--certificate", $Certificate)
}

& $NodeCommand.Source @Arguments
exit $LASTEXITCODE
