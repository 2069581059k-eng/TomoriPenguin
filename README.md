# 咕咕嘎嘎臭企鹅 · TomoriPenguin

小米手环 9 Pro / 10 Pro（336×480）动态表盘。
**v2.0 起为原生控件格式**（与官方动态表盘同引擎），真机动画/电量/日期/全屏/表盘库长按全支持。

![表盘实拍](qa/native-shot2.png)

## 效果（v2.0 原生版）

- **全屏视频动画**：20 帧 256 色索引动画 @10fps 无限循环（4.8MB，对齐官方「相变临界」的满屏帧技法）
- **数据齐全**：图片数字 时:分、9月17日 周X 日期、右上角电量百分比——全部图片字形，零字体渲染问题
- **系统级表盘行为**：表盘库长按管理、原生引擎渲染，真机与模拟器表现一致

## 平台踩坑实录（miwear 原生工程生存法则）

以下每一条都经过受控二分实验定位，做原生表盘前务必阅读：

| 规则 | 后果 | 说明 |
|---|---|---|
| 工程根目录只放一个 `.fprj` | 多个工程文件 → 编译器索引越界崩溃 | 每次编译前清理多余 .fprj |
| `output/` 目录必须预建 | 缺失 → 崩溃（伪装成索引越界） | 构建脚本先 mkdir |
| `.fprj` 保存为 **UTF-16** | UTF-8 可能解析异常 | 对齐官方工具产物 |
| XML **不要写 @Id 属性** | 部分 Compiler 版本崩溃 | ID 由命令行参数传入 |
| ImageList(Shape=31) 用 **@Index_Src** | 用 @Value_Src 崩溃 | 序列图专用属性名 |
| ImageList 的 BitmapList 用 **`(N):file`** | 纯文件名列表崩溃 | 每帧必须带索引映射 |
| 动画命名 **`anim_[count@delay]`** | 缺方括号/用 `anim_0@100` 崩溃 | 教程格式，方括号必须 |
| 索引色 PNG（P 模式 256 色） | RGB 帧体积翻倍（9.4MB→4.8MB） | Compiler 自动走 rle=0x10 索引路径 |

## 环境与构建

```bash
# 1) Python 依赖（--user 即可，不动全局）
python -m pip install --user pypng lz4 Pillow

# 2) 生成原生表盘素材（数字/星期/汉字/电量 + 20帧调色板动画）
python watchface\assets-src\gen-native-assets.py

# 3) 编译 .face（素材校验 + 工程净化 + Compiler-4.22 一键构建）
python watchface\assets-src\build-native.py
# 产出 watchface\native\output\TomoriPenguinNative.face（约 4.8MB）

# 4) 模拟器部署验证（adb push 到 market/<id>/resource.bin + 重启）
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\push_native.ps1

# 5) 模拟器截图验收（前后两帧 changed=true = 动效存活）
node tools\shot.mjs qa\shot.png
```

真机安装：下载 [Releases](https://github.com/2069581059k-eng/TomoriPenguin/releases) 的 `.bin`，表盘自定义工具选「小米手环 9 Pro」推送（9 Pro 与 10 Pro 同屏通用）。

## 原生 .fprj 工程结构

```
watchface/native/
  TomoriPenguin.fprj      # XML 工程（utf-16；动画 anim_[0@100]）
  images/
    f01-f20.png           # 20 帧全屏 256 色索引动画（共享调色板）
    n0-n9/colon.png       # 时钟数字 + 冒号
    d0-d9/m月d日w周.png    # 日期数字 + 汉字 + 星期序列
    b0-b9/t_pct.png       # 电量数字 + %
    preview.png           # 市场缩略图 230×328
  output/                 # 编译产物（预建）
```

widget 速查：`Shape=30` 图片 / `31` 序列图(动画) / `32` 数字时钟 / `27` 指针 / `34` 容器。
数据源速查：时`0811` 分`1011` 秒`1811` 日`1812` 月`1012` 周`2012` 电量`0841` 步数`0821` 心率`0822`。

## 旧版 Lua 方案（已弃用，留档）

v1.x 的 Lua 快应用方案（`watchface/fprj/`）在模拟器完美但真机存在动画冻结/字体异常，
已被 v2.0 原生方案替代。miwear 5.0 Lua 镜像开机生存四法则等经验仍保留在
`watchface/fprj/app/lua/main.lua` 头部注释，供 Lua 表盘开发参考。

## 参考 .bin 表盘解包分析

`tools/unpack-ref.py`（移植 [m0tral/UnpackMiColorFace](https://github.com/m0tral/UnpackMiColorFace) 的 FaceV2 格式）可解包官方/第三方动态表盘研究其做法——已验证「相变临界」（46 帧全屏索引色动画 + Animation 对象 count/delay）与「哥伦比亚」（4 帧全屏 + 数字图片时间 + 星期序列）。

## 致谢

- [FangAiden/LuaDevTemplate](https://github.com/FangAiden/LuaDevTemplate) — v1.x Lua 方案脚手架与热重载器
- [FangAiden/Vela_Application_Documentation](https://github.com/FangAiden/Vela_Application_Documentation) — Vela Lua 逆向文档
- [m0tral/UnpackMiColorFace](https://github.com/m0tral/UnpackMiColorFace) — 表盘解包器（逆向参考格式的基础）
- [nicemicro/Mi-Create](https://github.com/nicemicro/Mi-Create) — 开源表盘设计工具（fprj 格式交叉验证、Compiler 4.22）
- [米坛社区 BandBBS](https://www.bandbbs.cn/) — Vela 表盘生态、EasyFace 教程（动画命名 `anim_[xx@yy]` 出处）
- 高松灯企鹅素材由使用者自备，本仓库不含源视频
