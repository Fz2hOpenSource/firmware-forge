/**
 * MDK (Keil UV4) 编译/烧录 slash 命令插件，供「嵌入式开发工作台」preset 使用。
 *
 * 只注册一个 /build 命令，用后缀切换动作（减少命令数）：
 *   /build      → 增量编译（默认，等同 -b）
 *   /build -r   → 全量重编译
 *   /build -f   → 烧录下载
 *   /build -rf  → 全量重编译后烧录（重编译有错误则跳过烧录）
 *
 * 命令 host-side 执行，调用 scripts/mdk/mdk.ps1（UV4 路径走注册表自动探测，
 * 工程从会话工作区向上/一级子目录搜索 *.uvprojx），返回结果摘要。
 */
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const execFileAsync = promisify(execFile)

// 本插件位于 <preset>/plugins/mdk/，封装脚本位于 <preset>/scripts/mdk/mdk.ps1。
const here = dirname(fileURLToPath(import.meta.url))
const MDK_PS1 = join(here, '..', '..', 'scripts', 'mdk', 'mdk.ps1')

// Keil 全量编译可能耗时数分钟。
const BUILD_TIMEOUT_MS = 10 * 60 * 1000

export const name = 'mdk-commands'
export const inject = ['commands']

async function runOne(action, cwd) {
  const args = ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', MDK_PS1, action]
  if (cwd) args.push('-Root', cwd)
  try {
    const { stdout, stderr } = await execFileAsync(
      'powershell.exe',
      args,
      { timeout: BUILD_TIMEOUT_MS, maxBuffer: 8 * 1024 * 1024, windowsHide: true, cwd: cwd || undefined },
    )
    const text = [stdout, stderr].map(s => (s || '').trim()).filter(Boolean).join('\n').trim()
    return { ok: true, text: text || `${action} finished` }
  } catch (error) {
    // 非零退出码：把 stdout（含"编译完成：N 个错误"摘要）一并带回，别只报 Command failed
    const out = (error?.stdout ?? '').trim()
    const err = (error?.stderr ?? '').trim()
    const detail = [out, err].filter(Boolean).join('\n').trim()
    return { ok: false, text: `${action} 失败：${detail || error.message}` }
  }
}

/** 把 /build 的后缀解析成动作序列；无效后缀返回 null。 */
function parseActions(rawInput) {
  const s = (rawInput || '').trim()
  const flags = s.replace(/-/g, '').toLowerCase()
  if (s !== '' && !/^[brf]+$/.test(flags)) return null
  const hasR = flags.includes('r')
  const hasF = flags.includes('f')
  if (hasR && hasF) return ['rebuild', 'flash']
  if (hasR) return ['rebuild']
  if (hasF) return ['flash']
  return ['build']
}

function sessionCwd(invocation) {
  try {
    return invocation?.agent?.session?.header?.cwd
  } catch {
    return undefined
  }
}

export function apply(ctx) {
  ctx.commands.register({
    name: 'build',
    description: '编译/烧录 Keil 工程（默认增量编译；-r 全量重编译，-f 烧录，-rf 重编译后烧录）',
    input: { hint: '[-r | -f | -rf]' },
    handler: async (invocation) => {
      const actions = parseActions(invocation.rawInput)
      if (actions === null) {
        return { kind: 'error', text: `无效后缀：${invocation.rawInput}（可用 -r、-f、-rf，默认增量编译）` }
      }
      const cwd = sessionCwd(invocation)
      const out = []
      let failed = false
      for (const action of actions) {
        const res = await runOne(action, cwd)
        out.push(res.text)
        if (!res.ok) { failed = true; break } // 编译/重编译失败就停止，不继续烧录
      }
      const text = out.join('\n\n')
      return failed ? { kind: 'error', text } : { kind: 'success', text }
    },
  })
}
