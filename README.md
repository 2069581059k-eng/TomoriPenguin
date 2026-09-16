# 咕咕嘎嘎臭企鹅 · TomoriPenguin

小米手环 9 Pro / 10 Pro（336×480，Xiaomi Vela miwear 5.0）动态表盘。
Lua + LVGL 实现，基于社区逆向工具链开发。

![表盘实拍](qa/v3-final.png)

## 效果

- **视频卡片**：mp4 素材抽帧 16 帧 @12fps 循环播放，相纸卡片 + 投影 + 悬浮动效
- **景深设计**：时间/日期/电量信息永不遮挡素材——素材居于下方卡片，信息独立分区
- **氛围动效**：双层视差雪（前景快亮 / 远景慢暗）、四个漂移光斑、大时间微呼吸
- **数据**：MiSans 64px 大时间（`os.date` 种子 + 30s 对表）、中文日期（几月几日 周几）、电量胶囊

## 平台踩坑实录（miwear 5.0 镜像开机生存四法则）

以下每一条都经过逐项对照实验定位（Face C/D/E/…/L 系列），写表盘前务必阅读 `watchface/fprj/app/lua/main.lua` 头部注释：

| 禁忌 | 后果 | 解法 |
|---|---|---|
| `lvgl.Font("montserrat", *)` | 光栅化原生崩溃，LVGL 循环死亡（屏幕变崩溃转储文本页）| 只用 MiSans（CJK 可用）|
| `dataman.subscribe` 在 init 调用 | 破坏「静态合成 → Live」交接，永远卡在静态渲染 | 禁用 |
| `dataman.subscribe` 在 Timer 内调用 | 显示刷新冻结（Timer 仍在跑但屏幕逐帧不变）| 禁用，时间改 `os.date` + 定时重播 |
| `lvgl.Image`(RGB565) 在 init 创建 | 显示刷新冻结 | 500ms 一次性 Timer 回调内创建帧堆 |

其它：全局 `Timer()` 不存在（只有 `lvgl.Timer`）；`print()` 输出不可见（无 logcat），调试用 `io.open` 文件日志 + `adb pull`；开机时系统先静态渲染 `resource.bin` 再二次启动 Lua 进 Live（日志出现两个 boot 块 = 交接成功）。

## 环境与构建

```bash
# 1) Python 依赖（--user 即可，不动全局）
python -m pip install --user pypng lz4 Pillow

# 2) 全量部署到模拟器（含 .face 构建 + 推送 + 重启）
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\pushlua.ps1

# 3) 改 Lua 后热重载（仅 Live 状态下有效）
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\pushlua.ps1 -Hot

# 4) 模拟器截图验收（前后两帧 changed=true = 动效存活）
node tools\shot.mjs qa\shot.png
```

脚本已按本机环境适配：`scripts/internal/load_config.ps1` 注入 adb（进程级 PATH）并锁定 `emulator-5578`，不修改任何全局环境。

## 素材管线

素材源视频放 `mp4/` 目录（不入库），管线一键重建：

```bash
# 抽帧：自动定位运动主体并裁剪 240×320 卡片段（16 帧 @12fps，改脚本头部 SS/DUR/FPS/N）
python watchface\assets-src\extract-frames.py

# 转 LVGL RGB565 .bin（I8 仅可用于 preview.bin，渲染图片必须 RGB565/ARGB8888）
python watchface\tools\LVGLImage.py --cf RGB565 --ofmt BIN --compress NONE --align 1 \
  --rgb565dither --output watchface\fprj\app\images --name f01 <帧>.png

# 生成市场缩略图（DeviceType=367 强校验 230×328）
python watchface\assets-src\make-preview.py
```

## 真机打包

`.fprj` 已设 `DeviceType="367"`（Band 9 Pro；Band 10 Pro 同屏，专属码未公开前按 9 Pro 打包），`scripts\build_face.ps1` 产出 `bin\TomoriPenguin.face`（约 2.7MB，输出 `Watch: MiBand9Pro`）。`watchfaceId` 见 `watchface.config.json`（可用「生成表盘ID」任务更换）。

## 目录结构

```
watchface/fprj/app/        # 表盘本体（真机释放内容）
  lua/main.lua             # 入口：景深分层 + 帧播放器 + 开机生存法则
  images/f01-f16.bin       # RGB565 帧堆（2.4MB）
watchface/assets-src/      # 素材管线脚本 + 16 帧源图 + 设计稿
watchface/tools/           # LVGLImage 转换器 + Compiler.exe（.face 打包）
scripts/                   # 部署/热重载/构建脚本（已适配 5578 模拟器）
tools/                     # 截图/手势/分析工具（gRPC）
qa/                        # 验收截图（前后双帧 = 动效证据）
```

## 致谢

- [FangAiden/LuaDevTemplate](https://github.com/FangAiden/LuaDevTemplate) — 本项目脚手架与热重载器
- [FangAiden/Vela_Application_Documentation](https://github.com/FangAiden/Vela_Application_Documentation) — Vela Lua 逆向文档
- [米坛社区 BandBBS](https://www.bandbbs.cn/) — Vela 表盘生态与工具
- 高松灯企鹅素材由使用者自备，本仓库不含源视频
