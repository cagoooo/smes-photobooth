# 石門國小 AI 拍貼機 — 一鍵升版（同步 version.json / sw.js / index.html 三處版本號）
# 用法：  powershell -File scripts/bump-version.ps1 -Notes "這次改了什麼"
# 升版後三處 byte 都會變 → 瀏覽器才偵測得到新版 → 跳「重新整理載入」通知
param([string]$Notes = "內容更新")
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$enc  = New-Object System.Text.UTF8Encoding($false)   # UTF-8 無 BOM
$today = Get-Date -Format "yyyy.MM.dd"

$vp = Join-Path $root "version.json"; $seq = 1
if (Test-Path $vp) {
  $old = ([System.IO.File]::ReadAllText($vp, [System.Text.Encoding]::UTF8) | ConvertFrom-Json).version
  if ($old -match "^$([regex]::Escape($today))-(\d+)$") { $seq = [int]$Matches[1] + 1 }
}
$ver = "$today-$seq"

[System.IO.File]::WriteAllText($vp, ([ordered]@{ version = $ver; notes = $Notes } | ConvertTo-Json), $enc)
foreach ($f in @(
    @("sw.js",      "const BUILD_VERSION = '[^']*';", "const BUILD_VERSION = '$ver';"),
    @("index.html", "var APP_VERSION='[^']*';",       "var APP_VERSION='$ver';"),
    @("index.html", '(favicon\.ico|favicon\.svg|apple-touch-icon\.png|manifest\.json|og-preview\.png)\?v=[^"'']*', ('$1?v=' + $ver)),
    @("wall.html",  '(favicon\.ico|favicon\.svg|apple-touch-icon\.png|manifest\.json|og-preview\.png)\?v=[^"'']*', ('$1?v=' + $ver))
)) {
  $p = Join-Path $root $f[0]
  $t = [System.IO.File]::ReadAllText($p, [System.Text.Encoding]::UTF8)
  [System.IO.File]::WriteAllText($p, [regex]::Replace($t, $f[1], $f[2]), $enc)
}
Write-Host "bumped -> $ver  ($Notes)"
Write-Host "接著： git add -A; git commit -m '...'; git push"
