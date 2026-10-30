# Runs INSIDE the recorded console window. It performs the real commands of a
# demo, paced so a viewer can read them. Nothing here is simulated: every
# "cmd" in the steps file is executed for real and its real output is shown.
param(
    [Parameter(Mandatory)][string]$StepsFile,
    [Parameter(Mandatory)][string]$TimingFile,
    [Parameter(Mandatory)][string]$GoFile,
    [Parameter(Mandatory)][string]$LogFile,
    [Parameter(Mandatory)][string]$Title,
    [Parameter(Mandatory)][string]$Repo,
    [int]$FontSize = 18,
    [int]$Cols = 130,
    [int]$Lines = 34
)

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class ConTool {
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    public struct CONSOLE_FONT_INFOEX {
        public uint cbSize; public uint nFont; public short X; public short Y;
        public int FontFamily; public int FontWeight;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)] public string FaceName;
    }
    [DllImport("kernel32.dll", SetLastError = true)] public static extern IntPtr GetStdHandle(int h);
    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool SetCurrentConsoleFontEx(IntPtr h, bool max, ref CONSOLE_FONT_INFOEX f);
    [DllImport("kernel32.dll")] public static extern IntPtr GetConsoleWindow();
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint flags);
}
"@

function Set-DemoFont([int]$size) {
    $f = New-Object ConTool+CONSOLE_FONT_INFOEX
    $f.cbSize = [System.Runtime.InteropServices.Marshal]::SizeOf($f)
    $f.FaceName = 'Consolas'; $f.FontFamily = 54; $f.FontWeight = 400; $f.X = 0; $f.Y = [int16]$size
    [void][ConTool]::SetCurrentConsoleFontEx([ConTool]::GetStdHandle(-11), $false, [ref]$f)
}

function Now-Ms { [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() }

function Write-Wrapped([string]$text, [string]$color, [int]$width) {
    foreach ($para in ($text -split "`n")) {
        $line = ''
        foreach ($w in ($para -split ' ')) {
            if (($line.Length + $w.Length + 1) -gt $width) { Write-Host $line -ForegroundColor $color; $line = $w }
            else { $line = if ($line) { "$line $w" } else { $w } }
        }
        if ($line) { Write-Host $line -ForegroundColor $color }
    }
}

# ---- window setup (must finish BEFORE the title is set; the recorder waits for the title)
Set-DemoFont $FontSize
cmd /c "mode con cols=$Cols lines=$Lines" | Out-Null
$Host.UI.RawUI.BackgroundColor = 'Black'
$Host.UI.RawUI.ForegroundColor = 'Gray'
Clear-Host
Set-Location $Repo
$env:PATH = (Join-Path $Repo '.venv\Scripts') + ';' + $env:PATH
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'
$env:PYTHONWARNINGS = 'ignore'
# move only (SWP_NOSIZE|SWP_NOZORDER) - never resize
[void][ConTool]::SetWindowPos([ConTool]::GetConsoleWindow(), [IntPtr]::Zero, 20, 20, 0, 0, 5)
$Host.UI.RawUI.WindowTitle = $Title

# NOTE: every variable below is prefixed with __ so that a demo command (run with Invoke-Expression
# in this same scope) can use names like $s, $i or $log without overwriting the player's own state.
trap { ("{0} TRAP: {1}`n{2}" -f (Get-Date -Format HH:mm:ss.fff), $_.Exception.Message, $_.ScriptStackTrace) | Add-Content "$LogFile.err"; Start-Sleep 3; break }
while (-not (Test-Path $GoFile)) { Start-Sleep -Milliseconds 100 }
$__goMs = Now-Ms

$__demo = Get-Content $StepsFile -Raw -Encoding UTF8 | ConvertFrom-Json
$__timing = Get-Content $TimingFile -Raw | ConvertFrom-Json
$__steps = @($__demo.steps)
$__log = @()

for ($__i = 0; $__i -lt $__steps.Count; $__i++) {
    $__s = $__steps[$__i]
    $__audioMs = [int]$__timing[$__i].audioMs
    Clear-Host
    $__stepStart = Now-Ms
    Add-Content "$LogFile.progress" ("{0} step {1} start" -f (Get-Date -Format HH:mm:ss.fff), ($__i + 1))
    Write-Host ("STEP {0} of {1}  -  {2}" -f ($__i + 1), $__steps.Count, $__s.title) -ForegroundColor Cyan
    Write-Host ('-' * ($Cols - 2)) -ForegroundColor DarkCyan
    if ($__s.say) { Write-Wrapped $__s.say 'Yellow' ($Cols - 4); Write-Host '' }
    Start-Sleep -Milliseconds 1200

    $__cmdStart = $__stepStart; $__cmdEnd = $__stepStart
    if ($__s.cmd) {
        $__cmdStart = Now-Ms
        Write-Host -NoNewline "PS hotel-booking> " -ForegroundColor Green
        foreach ($__ch in $__s.cmd.ToCharArray()) {
            Write-Host -NoNewline $__ch -ForegroundColor White
            Start-Sleep -Milliseconds 18
        }
        Write-Host ''
        try { Invoke-Expression $__s.cmd | Out-Host } catch { Write-Host $_.Exception.Message -ForegroundColor Red }
        $__cmdEnd = Now-Ms
        Add-Content "$LogFile.progress" ("{0} step {1} command finished" -f (Get-Date -Format HH:mm:ss.fff), ($__i + 1))
    }

    # let the voice-over finish, then give the viewer time to read the output
    $__pause = if ($null -ne $__s.pauseAfter) { [int]($__s.pauseAfter * 1000) } else { 2500 }
    $__elapsed = (Now-Ms) - $__stepStart
    $__wait = [Math]::Max(0, $__audioMs - $__elapsed) + $__pause
    Start-Sleep -Milliseconds $__wait
    $__log += [pscustomobject]@{
        index = $__i; title = $__s.title
        startMs = $__stepStart - $__goMs; cmdEndMs = $__cmdEnd - $__goMs; endMs = (Now-Ms) - $__goMs
        audioMs = $__audioMs
    }
}
$__total = (Now-Ms) - $__goMs
@{ goEpochMs = $__goMs; totalMs = $__total; steps = $__log } | ConvertTo-Json -Depth 5 | Set-Content $LogFile -Encoding UTF8
Start-Sleep -Milliseconds 2500   # keep the window open so the recorder can stop cleanly first
