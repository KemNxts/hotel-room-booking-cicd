# Records several tasks one after another (one window at a time) and keeps going if one fails.
#   powershell -ExecutionPolicy Bypass -File record-all.ps1 -Tasks '02,03,04'
param(
    [Parameter(Mandatory)][string]$Tasks,   # quoted, comma separated: '02,03'
    [string]$WorkRoot = $env:TEMP
)
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
foreach ($t in ($Tasks -split '[,\s]+' | Where-Object { $_ })) {
    $t = $t.PadLeft(2, '0')
    "=== task $t  $(Get-Date -Format HH:mm:ss)"
    try {
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $here 'record-demo.ps1') -TaskId $t -WorkRoot $WorkRoot
        if ($LASTEXITCODE -ne 0) { "!! task $t exited with code $LASTEXITCODE" }
    } catch {
        "!! task $t failed: $($_.Exception.Message)"
    }
    Start-Sleep -Seconds 3
}
"=== all done $(Get-Date -Format HH:mm:ss)"
