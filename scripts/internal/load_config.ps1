$ErrorActionPreference = "Stop"

# 定位项目根目录（从 scripts/internal/ 往上两级）
$_configRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\..\"))
$_configPath = Join-Path $_configRoot "watchface.config.json"
if (-not (Test-Path $_configPath)) {
  throw "watchface.config.json not found at $_configPath"
}

$config = Get-Content -Raw -Encoding UTF8 $_configPath | ConvertFrom-Json
$root = $_configRoot

# Trae 本机适配：注入模拟器 adb 到进程级 PATH 并锁定目标设备（不修改全局环境）
$env:PATH = "D:\AGI\TraeCode\Simulator\Simulator-Tools\platform-tools;$env:PATH"
$env:ANDROID_SERIAL = "emulator-5578"

$utf8NoBom = New-Object System.Text.UTF8Encoding $false
function Write-Utf8NoBom {
  param([string]$Path, [string]$Content)
  [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBom)
}
