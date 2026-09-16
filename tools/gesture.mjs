// 手势注入：node tools/gesture.mjs back|tap|x y
import os from 'node:os'
import path from 'node:path'
import fs from 'node:fs'
import { createRequire } from 'node:module'
const require = createRequire('D:\\AGI\\TraeCode\\Workspace\\Everyday\\package.json')
const { createGrpcClient } = require('@aiot-toolkit/emulator/lib/vvd/grpc')

const wait = (ms) => new Promise((r) => setTimeout(r, ms))
function readRunningConfig(name) {
  const runningDir = path.join(os.tmpdir(), 'avd', 'running')
  for (const f of fs.readdirSync(runningDir)) {
    if (!f.endsWith('.ini')) continue
    const config = {}
    for (const line of fs.readFileSync(path.join(runningDir, f), 'utf8').split(/\r?\n/u)) {
      const i = line.indexOf('=')
      if (i > 0) config[line.slice(0, i)] = line.slice(i + 1)
    }
    if (config['avd.name'] === name) return config
  }
  return null
}
const client = createGrpcClient(readRunningConfig('Trae_AGI'))
await client.waitForReady()

const mode = process.argv[2] || 'back'
if (mode === 'back') {
  // 右滑返回：从 x=300 快速滑到 x=40（6 步 × 8ms，参照 Everyday 手势参数）
  const y = 240
  client.sendMouse({ x: 300, y, buttons: 1 })
  for (let i = 1; i <= 6; i++) {
    client.sendMouse({ x: 300 - i * 43, y, buttons: 1 })
    await wait(8)
  }
  client.sendMouse({ x: 40, y, buttons: 0 })
  console.log('swipe back done')
} else if (mode === 'tap') {
  const x = parseInt(process.argv[3], 10)
  const y = parseInt(process.argv[4], 10)
  client.sendMouse({ x, y, buttons: 1 })
  await wait(60)
  client.sendMouse({ x, y, buttons: 0 })
  console.log('tap done', x, y)
}
await wait(1200)
const img = await client.getScreenshot()
fs.writeFileSync(process.argv[5] || 'gesture.png', img)
console.log('shot', img.length, 'bytes')
