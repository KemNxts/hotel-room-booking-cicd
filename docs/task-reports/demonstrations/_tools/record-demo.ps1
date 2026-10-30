# Records ONE task demo: opens a console window, runs the real commands in it
# (player.ps1), captures ONLY that window with ffmpeg/gdigrab, adds a synthetic
# (Windows SAPI text-to-speech) voice-over, writes an SRT and cuts screenshots
# out of the finished recording.
#
#   powershell -ExecutionPolicy Bypass -File record-demo.ps1 -TaskId 01
#
# Input : ..\task-NN\task-NN-steps.json   (title + steps: title/say/cmd/pauseAfter)
# Output: ..\task-NN\task-NN-demo.mp4, task-NN-demo.srt, screenshots\*.png
param(
    [Parameter(Mandatory)][string]$TaskId,
    [string]$Voice = 'Microsoft David Desktop',
    [int]$Fps = 15,
    [string]$Part = '',            # e.g. 'git' -> task-NN-git-steps.json / task-NN-git-demo.mp4
    [string]$WorkRoot = $env:TEMP,
    [switch]$KeepWork
)
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = (Resolve-Path (Join-Path $here '..\..\..\..')).Path
$taskDir = Join-Path $here "..\task-$TaskId"
$taskDir = (Resolve-Path $taskDir).Path
$sfx = if ($Part) { "-$Part" } else { "" }
$pfx = if ($Part) { "$Part-" } else { "" }
$stepsFile = Join-Path $taskDir "task-$TaskId$sfx-steps.json"
$outMp4 = Join-Path $taskDir "task-$TaskId$sfx-demo.mp4"
$outSrt = Join-Path $taskDir "task-$TaskId$sfx-demo.srt"
$shotDir = Join-Path $taskDir 'screenshots'
$work = Join-Path $WorkRoot "hotel-demo-$TaskId$sfx"
if (Test-Path $work) { Remove-Item $work -Recurse -Force }
New-Item -ItemType Directory -Path $work | Out-Null
$title = "HOTEL-DEMO-T$TaskId"
$ffmpeg = (Get-Command ffmpeg).Source
$ffprobe = (Get-Command ffprobe).Source

$demo = Get-Content $stepsFile -Raw -Encoding UTF8 | ConvertFrom-Json
$steps = @($demo.steps)

# ---- 1. voice-over per step (offline, Windows SAPI) ----------------------------------
Add-Type -AssemblyName System.Speech
$timing = @()
for ($i = 0; $i -lt $steps.Count; $i++) {
    $wav = Join-Path $work ("s{0:D2}.wav" -f $i)
    $ms = 0
    if ($steps[$i].say) {
        $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
        $synth.SelectVoice($Voice); $synth.Rate = 0
        $synth.SetOutputToWaveFile($wav)
        $synth.Speak([string]$steps[$i].say)
        $synth.Dispose()
        $d = & $ffprobe -v error -show_entries format=duration -of csv=p=0 $wav
        $ms = [int]([double]$d * 1000)
    }
    $timing += [pscustomobject]@{ audioMs = $ms }
}
$timingFile = Join-Path $work 'timing.json'
ConvertTo-Json -InputObject @($timing) | Set-Content $timingFile -Encoding UTF8

# ---- 2. open the demo window, then record only that window ---------------------------
$goFile = Join-Path $work 'go'
$logFile = Join-Path $work 'log.json'
$mode = if ($demo.mode) { [string]$demo.mode } else { 'console' }
if ($mode -eq 'browser') {
    # a visible Chrome driven by Selenium; its window title is "<title> - Google Chrome"
    $py = Join-Path $repo '.venv\Scripts\python.exe'
    $bp = Join-Path $here 'browser_player.py'
    $winTitle = "$title - Google Chrome"
    if ($demo.launcher -eq 'pytest') {
        # the project's REAL Selenium tests, run by pytest with the pytest_player plugin (visible, slowed down)
        $env:DEMO_STEPS = $stepsFile; $env:DEMO_TIMING = $timingFile; $env:DEMO_GO = $goFile
        $env:DEMO_LOG = $logFile; $env:DEMO_TITLE = $title
        $env:PYTHONPATH = $here; $env:HEADLESS = '0'
        if ($demo.e2eBaseUrl) { $env:E2E_BASE_URL = [string]$demo.e2eBaseUrl }
        $pargs = "-m pytest -p pytest_player $($demo.pytestArgs) -q --no-header -p no:cacheprovider"
        $win = Start-Process -FilePath $py -ArgumentList $pargs -WorkingDirectory $repo -PassThru -WindowStyle Hidden -RedirectStandardError (Join-Path $work 'player.err')
    } else {
        $win = Start-Process -FilePath $py -ArgumentList "`"$bp`" --steps `"$stepsFile`" --timing `"$timingFile`" --go `"$goFile`" --log `"$logFile`" --title $title --repo `"$repo`"" -PassThru -WindowStyle Hidden -RedirectStandardError (Join-Path $work 'player.err')
    }
} else {
    # a console window running player.ps1
    $winTitle = $title
    $player = Join-Path $here 'player.ps1'
    $arg = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$player`" -StepsFile `"$stepsFile`" -TimingFile `"$timingFile`" -GoFile `"$goFile`" -LogFile `"$logFile`" -Title $title -Repo `"$repo`""
    $win = Start-Process conhost.exe -ArgumentList $arg -PassThru
}

$found = $false
for ($t = 0; $t -lt 600; $t++) {
    if (Get-Process | Where-Object { $_.MainWindowTitle -eq $winTitle }) { $found = $true; break }
    Start-Sleep -Milliseconds 100
}
if (-not $found) { throw "demo window '$winTitle' did not appear" }
Start-Sleep -Milliseconds 500

$rawMp4 = Join-Path $work 'raw.mp4'
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $ffmpeg
$psi.Arguments = "-y -hide_banner -loglevel error -f gdigrab -framerate $Fps -draw_mouse 0 -i `"title=$winTitle`" -vf `"scale=trunc(iw/2)*2:trunc(ih/2)*2`" -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p `"$rawMp4`""
$psi.UseShellExecute = $false
$psi.RedirectStandardInput = $true
$psi.RedirectStandardError = $true
$ff = [System.Diagnostics.Process]::Start($psi)
$errTask = $ff.StandardError.ReadToEndAsync()
$ffStartMs = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
Start-Sleep -Milliseconds 1500
New-Item -ItemType File -Path $goFile | Out-Null

# wait for the player to finish (log file appears), max 40 minutes
$deadline = (Get-Date).AddMinutes(40)
while (-not (Test-Path $logFile) -and -not $win.HasExited -and (Get-Date) -lt $deadline) { Start-Sleep -Milliseconds 500 }
Start-Sleep -Milliseconds 300   # the player keeps its window open ~2.5 s after writing the log
$ff.StandardInput.Write('q'); $ff.StandardInput.Flush()
if (-not $ff.WaitForExit(20000)) { $ff.Kill() }
$ffErr = $errTask.Result
if ($ffErr) { Write-Host "ffmpeg: $ffErr" -ForegroundColor Yellow }
if (-not (Test-Path $logFile)) {
    $perr = Join-Path $work 'player.err'
    if (Test-Path $perr) { Write-Host "--- player error output ---" -ForegroundColor Red; Get-Content $perr -Tail 25 | Write-Host }
    foreach ($extra in "$logFile.err", "$logFile.progress") { if (Test-Path $extra) { Write-Host "--- $(Split-Path -Leaf $extra) ---" -ForegroundColor Red; Get-Content $extra -Tail 12 | Write-Host } }
    throw 'player did not finish - no log written'
}
$log = Get-Content $logFile -Raw | ConvertFrom-Json

# seconds from start of the video file to the player's "go"
$offset = ($log.goEpochMs - $ffStartMs) / 1000.0
$offset = [Math]::Max(0.0, $offset - 0.35)  # ffmpeg needs ~0.35 s to open the first frame

# ---- 3. mix the voice-over onto the video --------------------------------------------
$inputs = @('-i', $rawMp4); $filters = @(); $labels = @(); $n = 1
for ($i = 0; $i -lt $steps.Count; $i++) {
    if ($timing[$i].audioMs -gt 0) {
        $wav = Join-Path $work ("s{0:D2}.wav" -f $i)
        $delay = [int](($offset + $log.steps[$i].startMs / 1000.0) * 1000)
        $inputs += @('-i', $wav)
        $filters += "[$n]adelay=${delay}|${delay}[a$n]"
        $labels += "[a$n]"
        $n++
    }
}
if ($labels.Count -gt 0) {
    $fc = ($filters -join ';') + ';' + ($labels -join '') + "amix=inputs=$($labels.Count):normalize=0:dropout_transition=0,apad[aout]"
    & $ffmpeg -y -hide_banner -loglevel error @inputs -filter_complex $fc -map 0:v -map '[aout]' -c:v copy -c:a aac -b:a 128k -shortest $outMp4
} else {
    Copy-Item $rawMp4 $outMp4 -Force
}

# ---- 4. SRT (sentences share the step's narration time by length) ----------------------
function Fmt-Srt([double]$sec) {
    $ts = [TimeSpan]::FromSeconds([Math]::Max(0, $sec))
    '{0:D2}:{1:D2}:{2:D2},{3:D3}' -f [int][Math]::Floor($ts.TotalHours), $ts.Minutes, $ts.Seconds, $ts.Milliseconds
}
$srt = New-Object System.Text.StringBuilder
$cue = 1
for ($i = 0; $i -lt $steps.Count; $i++) {
    if (-not $steps[$i].say) { continue }
    $sentences = @([regex]::Split(([string]$steps[$i].say).Trim(), '(?<=[.!?])\s+') | Where-Object { $_ })
    $totalChars = ($sentences | Measure-Object -Property Length -Sum).Sum
    $t = $offset + $log.steps[$i].startMs / 1000.0
    $dur = $timing[$i].audioMs / 1000.0
    foreach ($sent in $sentences) {
        $len = $dur * $sent.Length / $totalChars
        [void]$srt.AppendLine("$cue")
        [void]$srt.AppendLine("$(Fmt-Srt $t) --> $(Fmt-Srt ($t + $len))")
        [void]$srt.AppendLine($sent)
        [void]$srt.AppendLine('')
        $t += $len; $cue++
    }
}
Set-Content $outSrt $srt.ToString() -Encoding UTF8
# step start times in the finished video (used for the timestamps in the narration file)
$tj = @{ offsetSec = $offset; steps = @(for ($i = 0; $i -lt $steps.Count; $i++) {
    @{ title = $steps[$i].title; videoStartSec = [Math]::Round($offset + $log.steps[$i].startMs / 1000.0, 1) } }) }
$tj | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $taskDir "task-$TaskId$sfx-demo.timing.json") -Encoding UTF8

# ---- 5. screenshots: one frame per step, taken from the finished video -----------------
if (Test-Path $shotDir) { Get-ChildItem $shotDir -Filter "${pfx}step-*.png" -ErrorAction SilentlyContinue | Remove-Item -Force } else { New-Item -ItemType Directory $shotDir | Out-Null }
for ($i = 0; $i -lt $steps.Count; $i++) {
    $slug = ($steps[$i].title.ToLower() -replace '[^a-z0-9]+', '-').Trim('-')
    if ($slug.Length -gt 50) { $slug = $slug.Substring(0, 50).Trim('-') }
    $at = $offset + [Math]::Max($log.steps[$i].cmdEndMs, $log.steps[$i].startMs + 1500) / 1000.0 + 0.4
    $png = Join-Path $shotDir ("{0}step-{1:D2}-{2}.png" -f $pfx, ($i + 1), $slug)
    & $ffmpeg -y -hide_banner -loglevel error -ss $at -i $outMp4 -frames:v 1 $png
}

# ---- 6. verify the recording is readable ------------------------------------------------
$info = & $ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height -of json $outMp4 | ConvertFrom-Json
$dur = [double]$info.format.duration
"RECORDED  $outMp4"
"  duration {0:N1}s  size {1:N2} MB  streams: {2}" -f $dur, ([double]$info.format.size / 1MB), (($info.streams | ForEach-Object { "$($_.codec_type)/$($_.codec_name)" + $(if ($_.width) { " $($_.width)x$($_.height)" }) }) -join ', ')
"  subtitles $outSrt  ($($cue - 1) cues)"
"  screenshots $((Get-ChildItem $shotDir -Filter '*step-*.png').Count) in $shotDir"
# a blank (black) frame compresses to a few KB; real terminal / browser frames are far larger
$blank = @(Get-ChildItem $shotDir -Filter "${pfx}step-*.png" | Where-Object { $_.Length -lt 15000 })
if ($blank.Count -gt 0) { Write-Host "WARNING: $($blank.Count) screenshot(s) look blank - the recording may be black. Check before using it: $($blank.Name -join ', ')" -ForegroundColor Red }
if (-not $KeepWork) { Remove-Item $work -Recurse -Force -ErrorAction SilentlyContinue }
