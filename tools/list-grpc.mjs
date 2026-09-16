// 枚举 vvd gRPC 客户端可用方法
import os from 'node:os'
import path from 'node:path'
import fs from 'node:fs'
import { createRequire } from 'node:module'
const require = createRequire('D:\\AGI\\TraeCode\\Workspace\\Everyday\\package.json')
const { createGrpcClient } = require('@aiot-toolkit/emulator/lib/vvd/grpc')

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
console.log('--- client own keys ---')
console.log(Object.keys(client))
for (const k of Object.keys(client)) {
  try {
    const v = client[k]
    console.log(k, typeof v, v && v.prototype ? 'class' : '')
  } catch (e) { console.log(k, 'err', e.message) }
}
const proto = Object.getPrototypeOf(client)
if (proto) console.log('--- proto keys ---', Object.getOwnPropertyNames(proto))
