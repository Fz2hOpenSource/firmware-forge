<#
.SYNOPSIS
  一键安装/更新「嵌入式开发工作台」到 DSH 的 agent preset 目录。

.DESCRIPTION
  将本仓库的 preset、plugins、scripts、skills 同步到
  $DSH_HOME\.agent-presets\embedded\（DSH_HOME 默认 ~/.dsh）。
  重复执行即更新。默认复制（稳定）；加 -Symlink 改为符号链接（实时，需开发者模式/管理员）。

.EXAMPLE
  .\install.ps1
  .\install.ps1 -Symlink
#>
param([switch]$Symlink)

$ErrorActionPreference = 'Stop'

function Sync-Tree {
  param([string]$Src, [string]$Dst)
  if (Test-Path $Dst) { Remove-Item $Dst -Recurse -Force }
  if ($Symlink) {
    New-Item -ItemType SymbolicLink -Path $Dst -Target $Src -ErrorAction Stop | Out-Null
  } else {
    Copy-Item -Recurse -Force $Src $Dst
  }
}

# 把任意编码的 .ps1 归一化为 UTF-8 BOM（内容仍为 UTF-8）。
# 自动识别：UTF-8（有/无 BOM）、UTF-16 LE/BE、以及无 BOM 且非 UTF-8 时按系统默认码页（GBK）。
function Convert-ToUtf8Bom {
  param([string]$Path)
  $bytes = [System.IO.File]::ReadAllBytes($Path)
  if ($bytes.Length -eq 0) { return }

  $text = $null
  if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    # UTF-8 BOM
    $text = [System.Text.Encoding]::UTF8.GetString($bytes, 3, $bytes.Length - 3)
  }
  elseif ($bytes.Length -ge 2 -and $bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE) {
    # UTF-16 LE BOM
    $text = [System.Text.Encoding]::Unicode.GetString($bytes, 2, $bytes.Length - 2)
  }
  elseif ($bytes.Length -ge 2 -and $bytes[0] -eq 0xFE -and $bytes[1] -eq 0xFF) {
    # UTF-16 BE BOM
    $text = [System.Text.Encoding]::BigEndianUnicode.GetString($bytes, 2, $bytes.Length - 2)
  }
  else {
    # 无 BOM：先按严格 UTF-8 试；含非法字节则按系统默认码页（中文 Windows = GBK）读
    try {
      $strict = [System.Text.UTF8Encoding]::new($false, $true)
      $text = $strict.GetString($bytes)
    }
    catch {
      $text = [System.Text.Encoding]::Default.GetString($bytes)
    }
  }

  [System.IO.File]::WriteAllText($Path, $text, [System.Text.UTF8Encoding]::new($true))
}

$repo    = Split-Path -Parent $MyInvocation.MyCommand.Path
$dshHome = if ($env:DSH_HOME) { $env:DSH_HOME } else { Join-Path $env:USERPROFILE '.dsh' }
$dest    = Join-Path $dshHome '.agent-presets\embedded'

Write-Output "源：   $repo"
Write-Output "目标： $dest"

New-Item -ItemType Directory -Force (Join-Path $dest 'skills') | Out-Null

# preset 两个文件（小文件直接复制）
Copy-Item -Force (Join-Path $repo 'preset\preset.yml')       $dest
Copy-Item -Force (Join-Path $repo 'preset\agent.cordis.yml') $dest

# 备份本机 MDK 配置：Sync-Tree 会整目录替换 scripts，重复安装不得丢用户手工配置
$cfgPath   = Join-Path $dest 'scripts\mdk\mdk.config.ps1'
$cfgBackup = $null
if (Test-Path $cfgPath) { $cfgBackup = [System.IO.File]::ReadAllText($cfgPath) }

# plugins / scripts / skills
$skillList = @('arm-cortex-expert', 'embedded-test-engineer', 'embedded-protocol-designer')
Sync-Tree (Join-Path $repo 'plugins') (Join-Path $dest 'plugins')
Sync-Tree (Join-Path $repo 'scripts') (Join-Path $dest 'scripts')
foreach ($s in $skillList) {
  Sync-Tree (Join-Path $repo $s) (Join-Path $dest ('skills\' + $s))
}

# 清理 skills 下不再随仓库分发的残留技能目录（改名/删除后的旧副本），保持"安装即镜像"；
# 放在同步之后执行，避免同步中途失败时误删
$skillsRoot = Join-Path $dest 'skills'
Get-ChildItem -Path $skillsRoot -Directory -ErrorAction SilentlyContinue |
  Where-Object { $skillList -notcontains $_.Name } |
  ForEach-Object {
    Remove-Item $_.FullName -Recurse -Force
    Write-Output "已清理不再分发的残留技能：$($_.Name)"
  }

# 恢复本机配置；仅在无备份且新树中也不存在时才从模板生成
if ($null -ne $cfgBackup) {
  [System.IO.File]::WriteAllText($cfgPath, $cfgBackup, [System.Text.UTF8Encoding]::new($true))
}
elseif (-not (Test-Path $cfgPath)) {
  Copy-Item -Force (Join-Path $dest 'scripts\mdk\mdk.config.ps1.example') $cfgPath
}

# 归一化所有 .ps1 编码为 UTF-8 BOM（自动识别 UTF-8/UTF-16/GBK，统一转 UTF-8）
Get-ChildItem -Path $dest -Recurse -Filter '*.ps1' | ForEach-Object {
  Convert-ToUtf8Bom -Path $_.FullName
}

Write-Output ''
Write-Output '完成。UV4 路径与工程路径会自动探测，通常无需配置。'
Write-Output '如需手动指定，编辑：'
Write-Output "  $cfgPath"
Write-Output '然后在 DSH 新建会话并选择「嵌入式开发工作台」。'
