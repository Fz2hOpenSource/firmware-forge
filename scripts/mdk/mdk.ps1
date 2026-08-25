<#
.SYNOPSIS
  Keil MDK (UV4) 编译/烧录统一封装。供 /build 命令与 AI 的 shell 工具共同调用。

.DESCRIPTION
  用法：
    mdk.ps1 [-Action build|rebuild|flash] [-Project <工程|昵称>] [-Root <搜索目录>]
            [-SearchDepth <层数，默认 6>] [-Backend keil|stlink|dap|jlink]
            [-Image <镜像.hex|.axf>] [-FlashAddress <bin 下载地址>] [-WhatIf]
  UV4 路径解析：配置/环境变量 → 注册表 → 常见路径。
  工程路径解析：-Project → 配置/环境变量 → 从 -Root（默认当前目录）向下递归搜索 *.uvprojx（默认 6 层，不向上爬父目录）。
  烧录后端：flash 动作分发到 flash-backends.ps1（keil / stlink / dap / jlink）。
#>
param(
  [ValidateSet('build', 'rebuild', 'flash')]
  [string]$Action = 'build',
  [string]$Project = '',
  [string]$Root = '',
  [string]$Backend = '',
  [string]$Image = '',
  [string]$FlashAddress = '',
  [int]$SearchDepth = 6,
  [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

# 让 stdout/stderr 输出为 UTF-8；否则 Node 端按 UTF-8 捕获时，中文会被当成 GBK 而乱码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# --- 运行日志目录：安装根 logs\ 下（与 scripts 解耦，重装不丢故障现场）---
# 每次启动顺带清理 30 天前的旧日志（固定文件名覆盖写 + 定期清扫，不会无限堆积）
$logDir = Join-Path (Split-Path -Parent (Split-Path -Parent $here)) 'logs'
New-Item -ItemType Directory -Force $logDir | Out-Null
Get-ChildItem -Path $logDir -Filter '*.log' -File -ErrorAction SilentlyContinue |
  Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } |
  Remove-Item -Force -ErrorAction SilentlyContinue

# --- 载入配置（可选；留空则自动探测） ---
$Uv4Path      = ''
$ProjectPath  = ''
$FlashBackend = 'keil'
$FlashImage   = ''
$ConfigFile   = Join-Path $here 'mdk.config.ps1'
if (Test-Path $ConfigFile) { . $ConfigFile }

if ($env:MDK_UV4)     { $Uv4Path     = $env:MDK_UV4 }
if ($env:MDK_PROJECT) { $ProjectPath = $env:MDK_PROJECT }
if ($Backend)         { $FlashBackend = $Backend }
if ($Image)           { $FlashImage   = $Image }

# --- 自动探测 UV4.exe ---
function Resolve-Uv4Path {
  $keys = @(
    'HKLM:\SOFTWARE\WOW6432Node\Keil\Products\MDK',
    'HKLM:\SOFTWARE\Keil\Products\MDK',
    'HKCU:\Software\Keil\Products\MDK'
  )
  foreach ($k in $keys) {
    if (Test-Path $k) {
      $regPath = (Get-ItemProperty $k -ErrorAction SilentlyContinue).Path
      if ($regPath) {
        # regPath 可能是安装根目录，也可能指向 ARM 子目录
        foreach ($c in @(
          (Join-Path $regPath 'UV4\UV4.exe'),
          (Join-Path (Split-Path -Parent $regPath) 'UV4\UV4.exe')
        )) {
          if (Test-Path $c) { return $c }
        }
      }
    }
  }
  foreach ($d in @('C:\Keil_v5\UV4\UV4.exe', 'C:\Keil\UV4\UV4.exe')) {
    if (Test-Path $d) { return $d }
  }
  return $null
}

if (-not $Uv4Path) { $Uv4Path = Resolve-Uv4Path }
if (-not $Uv4Path -or -not (Test-Path $Uv4Path)) {
  Write-Error "UV4.exe 未找到（已尝试注册表与常见路径）。请在 mdk.config.ps1 或环境变量 MDK_UV4 中配置。"
  exit 1
}

# --- 自动探测工程 ---
function Resolve-ProjectPath {
  param([string]$RootDir, [int]$MaxDepth = 6, [string]$DefaultProject = '')
  if (-not $RootDir) { $RootDir = (Get-Location).Path }
  if (-not (Test-Path $RootDir)) { return $null }
  # 只在工作区内向下递归，不向上爬父目录（避免把同盘其他工程的 .uvprojx 误当编译目标）。
  # 深度默认 6 层，覆盖 主文档\子文档\代码\MDK-ARM\xxx.uvprojx 这类多层嵌套布局。
  $found = @(Get-ChildItem -Path $RootDir -Filter '*.uvprojx' -File -Recurse -Depth $MaxDepth -ErrorAction SilentlyContinue |
    Sort-Object FullName)
  if ($found.Count -eq 0) { return $null }
  if ($found.Count -gt 1) {
    # 多候选时按默认工程名（uvprojx 文件名不含扩展名）尝试唯一自动选中
    if ($DefaultProject) {
      $pick = @($found | Where-Object { $_.BaseName -eq $DefaultProject })
      if ($pick.Count -eq 1) { return $pick[0].FullName }
    }
    $list = ($found | ForEach-Object { $_.FullName }) -join "`n"
    Write-Error "发现多个工程文件（范围：$RootDir，深度 $MaxDepth），请用 -Project 指定其一，或在 mdk.config.ps1 设置 `$MdkDefaultProject：`n$list"
    exit 1
  }
  return $found[0].FullName
}

$searchRoot = if ($Root) { $Root } else { (Get-Location).Path }

# --- 读取 uvprojx 关键信息（Target/MCU/输出目录），用于烧录确认摘要与镜像定位 ---
function Get-UvprojxInfo {
  param([string]$Path)
  try { [xml]$doc = Get-Content $Path -Raw } catch { return $null }
  $t = @($doc.Project.Targets.Target)[0]
  if (-not $t) { return $null }
  [pscustomobject]@{
    TargetName = [string]$t.TargetName
    Device     = [string]$t.Device
    OutDir     = [string]$t.TargetOption.OutputDirectory
    OutName    = [string]$t.TargetOption.OutputName
  }
}

# --- 工程昵称解析：$MdkProjects 昵称表可在 mdk.config.ps1 定义（值相对 -Root） ---
if ($Project -and $Project -notmatch '[\\/]' -and $Project -notlike '*.uvprojx') {
  if ($MdkProjects -and $MdkProjects.ContainsKey($Project)) {
    $resolved = Join-Path $searchRoot ([string]$MdkProjects[$Project])
    if (-not (Test-Path $resolved)) {
      Write-Error "工程昵称 '$Project' 指向的文件不存在：$resolved"
      exit 1
    }
    $Project = $resolved
  }
  else {
    $known = if ($MdkProjects) { $MdkProjects.Keys -join ', ' } else { '未定义' }
    Write-Error "未知的工程昵称：$Project（可用：$known）。也可直接给出 .uvprojx 路径。"
    exit 1
  }
}
elseif ($Project -and -not [System.IO.Path]::IsPathRooted($Project)) {
  # 相对路径按搜索根解析
  $cand = Join-Path $searchRoot $Project
  if (Test-Path $cand) { $Project = $cand }
}

# 参数优先级最高：昵称/相对/绝对路径在此才写入 $ProjectPath（早于默认探测）
if ($Project) { $ProjectPath = $Project }

if (-not $ProjectPath) { $ProjectPath = Resolve-ProjectPath -RootDir $searchRoot -MaxDepth $SearchDepth -DefaultProject $MdkDefaultProject }
if (-not $ProjectPath -or -not (Test-Path $ProjectPath)) {
  Write-Error "未找到 *.uvprojx 工程文件（搜索起点：$searchRoot）。请用 -Project 参数，或在 mdk.config.ps1 / MDK_PROJECT 中指定。"
  exit 1
}

Write-Output "UV4：$Uv4Path"
Write-Output "工程：$ProjectPath"

if ($WhatIf) {
  Write-Output "（WhatIf：仅探测，不执行）"
  exit 0
}

# --- 烧录：分发到后端层 ---
if ($Action -eq 'flash') {
  # 烧录前输出确认摘要：工程 / Target / MCU / 后端（镜像由后端解析后再报）
  $info = Get-UvprojxInfo -Path $ProjectPath
  if ($info) { Write-Output ("目标确认：Target={0} | MCU={1}" -f $info.TargetName, $info.Device) }
  $imgDir = $null
  if ($info -and $info.OutDir) { $imgDir = Join-Path (Split-Path -Parent $ProjectPath) $info.OutDir }
  . (Join-Path $here 'flash-backends.ps1')
  Invoke-Flash -Backend $FlashBackend -ProjectFile $ProjectPath -Image $FlashImage -ImageDir $imgDir -FlashAddress $FlashAddress
  exit $LASTEXITCODE
}

# --- 编译/重编译：UV4 + 日志解析 ---
$log = Join-Path $logDir ("uv4-{0}.log" -f $Action)
Remove-Item $log -Force -ErrorAction SilentlyContinue   # 先删旧日志，防上一次结果被误读为本次结论
$startedAt = Get-Date
switch ($Action) {
  'build'   { & $Uv4Path -b $ProjectPath -j0 -o $log }
  'rebuild' { & $Uv4Path -r $ProjectPath -j0 -o $log }
}

# UV4 退出码不可靠；编译以"本次新生成的日志"中的 Error/Warning 计数为准。
# 日志缺失、非本次生成、或无结束摘要时，一律按"结果不确定"处理并返回非零退出码。
$freshLog = (Test-Path $log) -and ((Get-Item $log).LastWriteTime -ge $startedAt)
$errors = 0; $warnings = 0; $parsed = $false
if ($freshLog) {
  $content = Get-Content $log -Raw -ErrorAction SilentlyContinue
  if ($content) {
    if ($content -match '(\d+)\s*Error\(s\)')   { $errors = [int]$Matches[1]; $parsed = $true }
    if ($content -match '(\d+)\s*Warning\(s\)') { $warnings = [int]$Matches[1] }
  }
}

switch ($Action) {
  'build'   { $verb = '编译' }
  'rebuild' { $verb = '重编译' }
}

if (-not $freshLog) {
  Write-Output "$verb 结果不确定：UV4 未生成本次日志（exit=$LASTEXITCODE）。请检查 UV4 是否实际启动、许可证弹窗或工程占用。"
  exit 3
}
if (-not $parsed) {
  Write-Output "$verb 结果不确定：日志中未找到构建结束摘要（N Error(s)），构建可能被中断。"
  Write-Output "日志：$log"
  exit 3
}

Write-Output "$verb 完成：$errors 个错误，$warnings 个警告"
Write-Output "日志：$log"
if ($errors -eq 0) { exit 0 } else { exit 1 }
