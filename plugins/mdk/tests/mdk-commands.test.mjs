import assert from 'node:assert/strict'
import { test } from 'node:test'
import childProcess from 'node:child_process'
import { syncBuiltinESMExports } from 'node:module'
import { promisify } from 'node:util'

// Replace the process boundary before importing the plugin. No PowerShell,
// compiler or programmer is launched by these tests.
const originalExecFile = childProcess.execFile
let calls = []
let nextError
childProcess.execFile = (file, args, options, callback) => {
  calls.push({ file, args, options })
  callback(nextError ?? null, nextError ? 'partial log' : 'completed', '')
}
// execFile has a custom promisified result and attaches output to errors.
const fakeExecFile = childProcess.execFile
fakeExecFile[promisify.custom] = (file, args, options) => new Promise((resolve, reject) => {
  fakeExecFile(file, args, options, (error, stdout, stderr) => {
    if (error) reject(Object.assign(error, { stdout, stderr }))
    else resolve({ stdout, stderr })
  })
})
syncBuiltinESMExports()
const { apply } = await import('../mdk-commands.mjs')
childProcess.execFile = originalExecFile
syncBuiltinESMExports()
const commands = new Map()
apply({ commands: { register: command => commands.set(command.name, command) } })

test('build, rebuild and flash have separate actions and nested deadlines', async () => {
  assert.deepEqual([...commands.keys()], ['build', 'flash'])
  for (const [name, input, action] of [
    ['build', 'sensor', 'build'], ['build', 'sensor -r', 'rebuild'], ['flash', 'sensor', 'flash'],
  ]) {
    calls = []; nextError = undefined
    const result = await commands.get(name).handler({
      rawInput: input, agent: { session: { header: { cwd: 'workspace with spaces' } } },
    })
    assert.equal(result.kind, 'success')
    assert.equal(calls.length, 1)
    const { args, options } = calls[0]
    assert.equal(args[args.indexOf('-File') + 2], action)
    assert.equal(args[args.indexOf('-Project') + 1], 'sensor')
    assert.equal(args[args.indexOf('-Root') + 1], 'workspace with spaces')
    const innerSeconds = Number(args[args.indexOf('-WaitTimeoutSec') + 1])
    assert.equal(innerSeconds, 900)
    assert(options.timeout >= (innerSeconds + 60) * 1000)
    assert.equal(options.windowsHide, true)
  }
})

test('obsolete flash flags and ambiguous projects never start a process', async () => {
  calls = []; nextError = undefined
  for (const [name, input] of [['build', '-f'], ['build', '-rf'], ['flash', '-r'], ['build', 'main sensor']]) {
    assert.equal((await commands.get(name).handler({ rawInput: input })).kind, 'error')
  }
  assert.equal(calls.length, 0)
})

test('outer interruption reports uncertainty and does not retry', async () => {
  for (const failure of [{ killed: true }, { code: 'ETIMEDOUT' }]) {
    calls = []; nextError = Object.assign(new Error('interrupted'), failure)
    const result = await commands.get('flash').handler({ rawInput: 'sensor' })
    assert.equal(result.kind, 'error')
    assert.match(result.text, /结果不确定/)
    assert.match(result.text, /partial log/)
    assert.equal(calls.length, 1)
  }
})

test('ordinary tool failure preserves diagnostics and does not retry', async () => {
  calls = []; nextError = Object.assign(new Error('failed'), { code: 1 })
  const result = await commands.get('build').handler({ rawInput: 'sensor' })
  assert.equal(result.kind, 'error')
  assert.match(result.text, /partial log/)
  assert.equal(calls.length, 1)
})
