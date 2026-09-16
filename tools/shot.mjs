// 表盘截图：node tools/shot.mjs [输出.png]
// 唤醒机制复用 Everyday capture-full.mjs 的经验：KEYCODE_WAKEUP 常无效，
// 需在显示区外的底部边框 (168,474) 轻点；亮度 <170 判定休眠并重试
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { spawnSync } from 'node:child_process'
import { createRequire } from 'node:module'

const require = createRequire('D:\\AGI\\TraeCode\\Workspace\\Everyday\\package.json')
const { createGrpcClient } = require('@aiot-toolkit/emulator/lib/vvd/grpc')

const ADB = 'D:\\AGI\\TraeCode\\Simulator\\Simulator-Tools\\platform-tools\\adb.exe'
const SERIAL = process.env.VELA_SERIAL || 'emulator-5578'
const wait = (ms) => new Promise((r) => setTimeout(r, ms))

function readRunningConfig(name) {
  const runningDir = path.join(os.tmpdir(), 'avd', 'running')
  if (!fs.existsSync(runningDir)) return null
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

async function wakeScreen(client) {
  try { spawnSync(ADB, ['-s', SERIAL, 'shell', 'input', 'keyevent', 'KEYCODE_WAKEUP'], { timeout: 10000 }) } catch {}
  try {
    client.sendMouse({ x: 168, y: 474, buttons: 1 })
    await wait(60)
    client.sendMouse({ x: 168, y: 474, buttons: 0 })
  } catch {}
  await wait(1600)
}

function meanLum(buf) {
  // PNG 灰度粗估：字节均值（简单启发式，与 Everyday 一致即可）
  let sum = 0
  const step = Math.max(1, Math.floor(buf.length / 4096))
  let n = 0
  for (let i = 0; i < buf.length; i += step) { sum += buf[i]; n++ }
  return sum / Math.max(1, n)
}

const out = process.argv[2] || 'shot.png'
const config = readRunningConfig(process.env.WB_VELA_AVD || 'Trae_AGI')
if (!config) {
  console.error('未找到 Trae_AGI 的 gRPC running 配置（模拟器未启动？）')
  process.exit(1)
}
const client = createGrpcClient(config)
await client.waitForReady()

// 唤醒 + 亮度判定重试
let img = null
for (let attempt = 1; attempt <= 5; attempt++) {
  await wakeScreen(client)
  img = await client.getScreenshot()
  const lum = meanLum(img)
  console.log(`attempt ${attempt}: ${img.length} bytes, lum ${lum.toFixed(0)}`)
  if (lum >= 60) break  // 表盘为深色底，阈值放宽
}
fs.writeFileSync(out, img)
console.log('saved', out, img.length, 'bytes')

const out2 = out.replace(/(\.[^.]+)?$/, '-b$1')
await wait(700)
const img2 = await client.getScreenshot()
fs.writeFileSync(out2, img2)
console.log('saved', out2, img2.length, 'bytes, changed =', !img2.equals(img))
