/**
 * MDK (Keil UV4) 编译/烧录 slash 命令插件，供「嵌入式开发工作台」preset 使用。
 *
 * 两个独立命令（编译归编译，烧录归烧录——烧录是显式决定）：
 *   /build [工程昵称] [-r]   增量编译；-r 全量重编译
 *   /flash [工程昵称]        烧录下载（走 mdk.config.ps1 配置的后端）
 *
 * 参数规则：
 *   - 以 - 开头的词视为开关，其余第一个词视为工程昵称
 *     （昵称定义在 mdk.config.ps1 的 $MdkProjects 表）
 *   - 不带昵称：工作区内唯一工程自动选中；多工程时报错并列出候选
 *   - 烧录不提供"先编译"链式开关——需要时先 /build 再 /flash，
 *     让编译结果肉眼确认后再做烧录这个显式决定
 *
 * 命令 host-side 执行，调用 scripts/mdk/mdk.ps1（UV4 路径走注册表自动探测，
 * 工程从会话工作区只向下递归搜索 *.uvprojx，默认 6 层深，不向上爬父目录），返回结果摘要。
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

/**
 * 解析命令参数。
 * @param {string} rawInput 用户输入的原始参数
 * @param {Set<string>} allowed 允许的开关字母集合（如 new Set(['r'])）
 * @returns {{valid:true, project?:string, flags:Set<string>} |
 *           {valid:false, message:string}}
 */
export function parseArgs(rawInput, allowed) {
  const tokens = (rawInput || '').trim().split(/\s+/).filter(Boolean)
  let project
  const flags = new Set()
  for (const tok of tokens) {
    if (tok.startsWith('-')) {
      const letters = tok.replace(/^-+/, '')
      if (letters === '' || [...letters].some(ch => !allowed.has(ch))) {
        const allowedList = [...allowed].map(c => `-${c}`).join(' ')
        return { valid: false,
                 message: `无效开关：${tok}（可用：${allowedList || '无'}）` }
      }
      for (const ch of letters) flags.add(ch)
    } else if (project === undefined) {
      project = tok
    } else {
      return { valid: false, message: `多余的参数：${tok}（只需一个工程昵称或路径）` }
    }
  }
  return { valid: true, project, flags }
}

async function runOne(action, cwd, project) {
  const args = ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', MDK_PS1, action]
  if (cwd) args.push('-Root', cwd)
  if (project) args.push('-Project', project)
  try {
    const { stdout, stderr } = await execFileAsync(
      'powershell.exe',
      args,
      { timeout: BUILD_TIMEOUT_MS, maxBuffer: 8 * 1024 * 1024, windowsHide: true, cwd: cwd || undefined },
    )
    const text = [stdout, stderr].map(s => (s || '').trim()).filter(Boolean).join('\n').trim()
    return { ok: true, text: text || `${action} finished` }
  } catch (error) {
    // 非零退出码：把 stdout（含"编译完成：N 个错误"/"烧录失败"等摘要）一并带回
    const out = (error?.stdout ?? '').trim()
    const err = (error?.stderr ?? '').trim()
    const detail = [out, err].filter(Boolean).join('\n').trim()
    return { ok: false, text: `${action} 失败：${detail || error.message}` }
  }
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
    description: '编译 Keil 工程（默认增量；-r 全量重编译）。可带工程昵称，多工程仓库用昵称指定。',
    input: { hint: '[工程昵称] [-r]' },
    handler: async (invocation) => {
      const parsed = parseArgs(invocation.rawInput, new Set(['r']))
      if (!parsed.valid) {
        return { kind: 'error', text: parsed.message }
      }
      const action = parsed.flags.has('r') ? 'rebuild' : 'build'
      const res = await runOne(action, sessionCwd(invocation), parsed.project)
      return res.ok ? { kind: 'success', text: res.text }
                    : { kind: 'error', text: res.text }
    },
  })

  ctx.commands.register({
    name: 'flash',
    description: '烧录 Keil 工程（走 mdk.config.ps1 配置的后端）。可带工程昵称；多工程仓库建议显式指定。',
    input: { hint: '[工程昵称]' },
    handler: async (invocation) => {
      const parsed = parseArgs(invocation.rawInput, new Set())
      if (!parsed.valid) {
        return { kind: 'error', text: parsed.message }
      }
      const res = await runOne('flash', sessionCwd(invocation), parsed.project)
      return res.ok ? { kind: 'success', text: res.text }
                    : { kind: 'error', text: res.text }
    },
  })
}
