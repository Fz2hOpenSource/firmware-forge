# =============================================================================
# 烧录后端层（flash backends）
#
# 设计：一个「注册表」+ 每个后端一个函数，mdk.ps1 的 flash 只负责分发。
# 新增后端只需两步：
#   1) 在 $FlashBackends 里加一行  '名字' = '函数名'
#   2) 写一个 Invoke-Flash<Name> 函数（约定参数：-ProjectFile -Image -ImageDir -FlashAddress）
#
# 后端函数职责：定位工具（配置优先 → 自动探测）→ 拼命令 → 运行；
# 失败用 Write-Error + exit 1 明确报错。
# =============================================================================

# ---- 后端注册表（分发表） ----
$FlashBackends = @{
  'keil'   = 'Invoke-FlashKeil'
  'stlink' = 'Invoke-FlashStlink'
  'dap'    = 'Invoke-FlashDap'
  'jlink'  = 'Invoke-FlashJlink'
}

# ---- 目标/设备名：不设通用默认值！ ----
# 使用 dap / jlink 后端前必须在 mdk.config.ps1 明确配置 $DapTarget / $JlinkDevice，
# 否则后端会直接报错拒绝烧录——防止把 A 板固件烧进 B 板。

# ---- 通用辅助 ----

# 定位一个烧录工具：配置路径优先，再 PATH（Get-Command），再常见安装目录。
function Resolve-FlashTool {
  param([string]$Cmd, [string[]]$Paths, [string]$Configured)
  if ($Configured -and (Test-Path $Configured)) { return $Configured }
  $g = Get-Command $Cmd -ErrorAction SilentlyContinue
  if ($g) { return $g.Source }
  foreach ($p in $Paths) {
    $f = Join-Path $p $Cmd
    if (Test-Path $f) { return $f }
  }
  return $null
}

# 定位要烧录的镜像。
# 规则（防烧错）：
#   1) 优先使用 .uvprojx Target 输出目录（调用方经 -ImageDir 传入）
#   2) 自动拾取只认 .hex/.axf——.bin 没有内嵌地址，必须显式 -Image + -FlashAddress
#   3) 命中多个候选时停止并列出，绝不"取最新"猜
function Resolve-FlashImage {
  param([string]$ProjectFile, [string]$ImageDir = '')
  $dir = Split-Path -Parent $ProjectFile
  $roots = @($dir)
  if ($ImageDir) { $roots = @($ImageDir) + $roots }
  $found = @()
  foreach ($root in $roots) {
    foreach ($pat in '*.hex', '*.axf') {
      $found += @(Get-ChildItem -Path $root -Filter $pat -File -ErrorAction SilentlyContinue)
    }
  }
  $found = @($found | Sort-Object FullName -Unique | Sort-Object LastWriteTime -Descending)
  if ($found.Count -eq 0) { return $null }
  if ($found.Count -gt 1) {
    $list = ($found | ForEach-Object { $_.FullName }) -join "`n"
    Write-Error "发现多个候选镜像，请用 -Image 显式指定其一：`n$list"
    exit 1
  }
  return $found[0].FullName
}

# ---- 统一分发入口 ----
function Invoke-Flash {
  param([string]$Backend, [string]$ProjectFile, [string]$Image,
        [string]$ImageDir = '', [string]$FlashAddress = '')
  $fn = $FlashBackends[$Backend]
  if (-not $fn) {
    Write-Error "未支持的烧录后端：$Backend（可用：$($FlashBackends.Keys -join ' / ')）"
    exit 1
  }
  # .bin 没有内嵌地址，所有工具型后端都必须显式给下载地址（keil 后端不使用镜像）
  if ($Image -like '*.bin' -and -not $FlashAddress -and $Backend -ne 'keil') {
    Write-Error '.bin 镜像必须同时提供下载地址：用 mdk.ps1 -FlashAddress <0x08000000> 指定'
    exit 1
  }
  & $fn -ProjectFile $ProjectFile -Image $Image -ImageDir $ImageDir -FlashAddress $FlashAddress
}

# ---- 各后端实现 ----

# Keil：用工程里配好的调试器下载，不需要镜像文件。
# UV4 -f 同样支持 -o 落日志；但 -o 按“相对工程目录的文件名”解析——传入绝对
# 路径时目录部分被丢弃，日志实际落在工程目录。所以传裸文件名、读工程目录、
# 再归档到集中 logs\ 目录。UV4 退出码不可靠，成败以日志关键字为准。
function Invoke-FlashKeil {
  param([string]$ProjectFile, [string]$Image, [string]$ImageDir = '', [string]$FlashAddress = '')
  Write-Output "烧录（Keil -f，走工程配置的调试器）"
  $logName = 'uv4-flash.log'
  $projDir = Split-Path -Parent $ProjectFile
  $log     = Join-Path $projDir $logName    # UV4 实际写日志的位置（工程目录）
  $archive = Join-Path $logDir $logName     # 集中归档位置
  Remove-Item $log -Force -ErrorAction SilentlyContinue     # 防旧日志误判
  Remove-Item $archive -Force -ErrorAction SilentlyContinue
  $startedAt = Get-Date
  & $Uv4Path -f $ProjectFile -j0 -o $logName

  if (Test-Path $log) { Copy-Item $log $archive -Force }   # 归档到集中日志目录
  $freshLog = (Test-Path $log) -and ((Get-Item $log).LastWriteTime -ge $startedAt)
  $content = $null
  if ($freshLog) { $content = Get-Content $log -Raw -ErrorAction SilentlyContinue }
  $okPat     = '(?i)verify\s+ok|programming done|load finished|application running'
  $failLines = @()
  if ($content) {
    $failLines = @($content -split "`r?`n" |
      Where-Object { $_ -match '(?i)\berror\b|failed|cannot|no algorithm|verify failed' } |
      Select-Object -First 5)
  }

  if ($content -and ($content -match $okPat) -and ($failLines.Count -eq 0)) {
    Write-Output '烧录完成：校验通过（Verify OK）'
    Write-Output "日志：$log"
    Write-Output "归档：$archive"
    return
  }

  if (-not $freshLog) {
    Write-Output '烧录结果不确定：UV4 未生成本次日志。请检查 UV4 是否实际启动、调试器配置或目标板连接。'
    exit 3
  }

  Write-Output '烧录失败。'
  foreach ($l in $failLines) { Write-Output "  $l" }
  Write-Output "日志：$log"
  Write-Output "归档：$archive"
  exit 1
}

# ST-Link：STM32CubeProgrammer CLI。
function Invoke-FlashStlink {
  param([string]$ProjectFile, [string]$Image, [string]$ImageDir = '', [string]$FlashAddress = '')
  $tool = Resolve-FlashTool -Cmd 'STM32_Programmer_CLI.exe' -Configured $Stm32ProgPath -Paths @(
    'C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin',
    'C:\Program Files (x86)\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin'
  )
  if (-not $tool) { Write-Error '未找到 STM32_Programmer_CLI.exe：请安装 STM32CubeProgrammer，或在 mdk.config.ps1 设置 $Stm32ProgPath'; exit 1 }
  $img = $Image; if (-not $img) { $img = Resolve-FlashImage -ProjectFile $ProjectFile -ImageDir $ImageDir }
  if (-not $img) { Write-Error '未找到 .hex/.axf 镜像：请先 /build，或用 -Image 指定（.bin 必须显式指定并带 -FlashAddress）'; exit 1 }
  Write-Output "烧录（ST-Link）：$img"
  if ($FlashAddress) { & $tool -c port=SWD -w $img $FlashAddress -v -rst }
  else               { & $tool -c port=SWD -w $img -v -rst }
}

# CMSIS-DAP：pyocd。
function Invoke-FlashDap {
  param([string]$ProjectFile, [string]$Image, [string]$ImageDir = '', [string]$FlashAddress = '')
  if (-not $DapTarget) { Write-Error '使用 dap 后端必须在 mdk.config.ps1 设置 $DapTarget（pyocd 目标名，如 stm32f429xx）'; exit 1 }
  $tool = Resolve-FlashTool -Cmd 'pyocd' -Configured $PyocdPath -Paths @()
  if (-not $tool) { Write-Error '未找到 pyocd：请 pip install pyocd，或在 mdk.config.ps1 设置 $PyocdPath'; exit 1 }
  $img = $Image; if (-not $img) { $img = Resolve-FlashImage -ProjectFile $ProjectFile -ImageDir $ImageDir }
  if (-not $img) { Write-Error '未找到 .hex/.axf 镜像：请先 /build，或用 -Image 指定（.bin 必须显式指定并带 -FlashAddress）'; exit 1 }
  Write-Output "烧录（CMSIS-DAP）：$img（目标 $DapTarget）"
  if ($FlashAddress) { & $tool flash -t $DapTarget --base-address $FlashAddress $img }
  else               { & $tool flash -t $DapTarget $img }
}

# J-Link：JLink.exe + CommanderScript。
function Invoke-FlashJlink {
  param([string]$ProjectFile, [string]$Image, [string]$ImageDir = '', [string]$FlashAddress = '')
  if (-not $JlinkDevice) { Write-Error '使用 jlink 后端必须在 mdk.config.ps1 设置 $JlinkDevice（J-Link 设备名，如 STM32F429VE）'; exit 1 }
  $tool = Resolve-FlashTool -Cmd 'JLink.exe' -Configured $JLinkPath -Paths @(
    'C:\Program Files\SEGGER\JLink',
    'C:\Program Files (x86)\SEGGER\JLink'
  )
  if (-not $tool) { Write-Error '未找到 JLink.exe：请安装 SEGGER J-Link，或在 mdk.config.ps1 设置 $JLinkPath'; exit 1 }
  $img = $Image; if (-not $img) { $img = Resolve-FlashImage -ProjectFile $ProjectFile -ImageDir $ImageDir }
  if (-not $img) { Write-Error '未找到 .hex/.axf 镜像：请先 /build，或用 -Image 指定（.bin 必须显式指定并带 -FlashAddress）'; exit 1 }
  Write-Output "烧录（J-Link）：$img（设备 $JlinkDevice）"
  $script = Join-Path $env:TEMP 'mdk-flash.jlink'
  $lines = @(
    "device $JlinkDevice"
    'si SWD'
    'speed 4000'
  )
  if ($FlashAddress) { $lines += ('loadfile "' + $img + '" ' + $FlashAddress) }
  else               { $lines += ('loadfile "' + $img + '"') }
  $lines += @('r', 'g', 'q')
  $lines | Set-Content -Path $script -Encoding ASCII
  & $tool -CommanderScript $script
}
