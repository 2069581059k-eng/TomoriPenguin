param()
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "internal\load_config.ps1")

$watchfaceId = [string]$config.watchfaceId
$destPath = "/data/app/watchface/market/$watchfaceId/"
$face = Join-Path $root "watchface\native\output\TomoriPenguinNative.face"
$dataDir = Join-Path $root "watchface\data"

Write-Host "=== deploy native face: $watchfaceId ==="

& adb shell "rm -rf '$destPath'"
& adb shell "mkdir '$destPath'"

# 原生表盘：resource.bin = .face 本体（内嵌预览）
Copy-Item $face (Join-Path $dataDir "resource.bin") -Force
& adb push (Join-Path $dataDir "resource.bin") $destPath

# 列表条目（沿用现有 watchface_list.json，id 相同）
& adb push (Join-Path $dataDir "watchface_list.json") "/data/app/watchface/"

# 触发刷新的 stamp
$stampName = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$stampLocal = Join-Path $env:TEMP $stampName
[System.IO.File]::WriteAllBytes($stampLocal, @())
& adb push $stampLocal "${destPath}.hotreload/$stampName"
Remove-Item $stampLocal -Force -ErrorAction SilentlyContinue

Write-Host "rebooting..."
& adb reboot
