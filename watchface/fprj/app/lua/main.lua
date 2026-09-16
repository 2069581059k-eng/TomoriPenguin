-- 咕咕嘎嘎臭企鹅 · 动态表盘 v3（小米手环10 Pro / 336×480）
-- ===== 本镜像开机生存法则（实验验证）=====
-- 1) dataman 禁用：init 调用破坏静态→Live 交接；Timer 内调用杀死显示刷新
--    → 时间用 os.date 种子 + 周期重播；电量默认隐藏数字（pill 全宽）
-- 2) RGB565 图片禁在 init 创建（杀刷新）→ 500ms 一次性 Timer 内创建帧堆
-- 3) montserrat 字体禁用（光栅化原生崩溃）→ 仅 MiSans
-- 4) 布局：时间/日期/电量永不遮挡卡片素材（景深：卡片+阴影+双层雪）
local app_module = "app.tomori_penguin"
local project_name = "TomoriPenguin"

local lvgl = require("lvgl")
local W, H = lvgl.HOR_RES(), lvgl.VER_RES()

-- ===== 根目录定位（兼容热重载）=====
local function this_dir()
  local src = ""
  if debug and debug.getinfo then
    local info = debug.getinfo(1, "S")
    src = (info and info.source) or ""
  end
  if type(src) ~= "string" then src = "" end
  if src:sub(1, 1) == "@" then src = src:sub(2) end
  return (src:gsub("\\", "/")):match("^(.*)/[^/]+$") or "."
end
local APP_ROOT = this_dir():match("^(.*)/lua$") or (this_dir() .. "/..")
local function IMG(n) return APP_ROOT .. "/images/" .. n end

local function dbg(msg)
  pcall(function()
    local f = io.open(APP_ROOT .. "/debug.log", "a")
    if f then f:write("[" .. tostring(os.time()) .. "] " .. tostring(msg) .. "\n"); f:close() end
  end)
end
dbg("===== v3 boot W=" .. tostring(W) .. " H=" .. tostring(H))

-- ===== 字体（仅 MiSans）=====
local function load_font(name, size)
  local ok, f = pcall(lvgl.Font, name, size, "normal")
  if ok and f then return f end
  return nil
end
local F_HERO = load_font("MiSansF-Demibold", 64) or load_font("MiSans-Demibold", 64)
local F_SMALL = load_font("MiSansF-Medium", 18) or load_font("MiSans-Medium", 18)
local F_CJK = F_SMALL
local CJK_OK = (F_CJK ~= nil)
dbg("fonts hero=" .. tostring(F_HERO ~= nil) .. " small=" .. tostring(F_SMALL ~= nil))

-- ===== 调色 =====
local C_BG     = 0x0F1420
local C_INK    = 0xEAF0F7
local C_DIM    = 0x8FA3BB
local C_ACCENT = 0x8ED4EF
local C_MAT    = 0xF4F6F9
local C_MAT_BD = 0xDDE3EA
local C_CAP    = 0x5C6678

-- ===== 根 =====
local root = lvgl.Object(nil, { w = W, h = H, bg_color = C_BG, border_width = 0 })
root:clear_flag(lvgl.FLAG.SCROLLABLE)

-- ===== 远景光斑 =====
local blobs = {
  { x = -44,  y = -56,  r = 92, c = 0x1B3A5C, ph = 0.0 },
  { x = W - 36, y = -34, r = 64, c = 0x17454B, ph = 2.1 },
  { x = W - 70, y = H - 48, r = 104, c = 0x23204A, ph = 4.2 },
  { x = -30,  y = H - 90, r = 72, c = 0x14314E, ph = 1.3 },
}
for _, s in ipairs(blobs) do
  local o = lvgl.Object(root, {
    x = s.x, y = s.y, w = s.r * 2, h = s.r * 2,
    radius = lvgl.RADIUS_CIRCLE, bg_color = s.c, bg_opa = 72, border_width = 0,
  })
  o:clear_flag(lvgl.FLAG.SCROLLABLE)
  s.obj = o
end

-- ===== 远景雪 =====
local snowFar = {
  { x = 40,  y = 90,  r = 2, v = 0.5, ph = 0.3, opa = 90 },
  { x = 300, y = 60,  r = 2, v = 0.4, ph = 1.7, opa = 80 },
  { x = 180, y = 140, r = 3, v = 0.6, ph = 3.1, opa = 70 },
  { x = 90,  y = 200, r = 2, v = 0.45, ph = 4.4, opa = 85 },
}
for _, s in ipairs(snowFar) do
  local o = lvgl.Object(root, {
    x = s.x, y = s.y, w = s.r * 2, h = s.r * 2,
    radius = lvgl.RADIUS_CIRCLE, bg_color = 0xD9E6F2, bg_opa = s.opa, border_width = 0,
  })
  o:clear_flag(lvgl.FLAG.SCROLLABLE)
  s.obj = o
end

-- ===== 信息区 =====
local WEEK_CN = { "日", "一", "二", "三", "四", "五", "六" }
local WEEK_EN = { "SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT" }
local hh, mm = 0, 0
local dd, mo, wd = 1, 1, 1

local dateLabel, timeLabel
if F_SMALL then
  dateLabel = lvgl.Label(root, {
    text = "", text_color = C_DIM, text_font = F_SMALL, x = 20, y = 16,
  })
end
-- 电量胶囊（右上）
local cap = lvgl.Object(root, {
  x = W - 46, y = 19, w = 26, h = 13, radius = 6,
  border_width = 2, border_color = C_DIM, bg_opa = 0,
})
cap:clear_flag(lvgl.FLAG.SCROLLABLE)
local batFill = lvgl.Object(cap, {
  x = 2, y = 2, w = 22, h = 9, radius = 4,
  bg_color = C_ACCENT, bg_opa = 200, border_width = 0,
})
batFill:clear_flag(lvgl.FLAG.SCROLLABLE)
if F_HERO then
  timeLabel = lvgl.Label(root, {
    text = "00:00", text_color = C_INK, text_font = F_HERO,
    align = { type = lvgl.ALIGN.TOP_MID, y_ofs = 48 },
  })
end

-- ===== 卡片 =====
local CARD_W, CARD_H = 240, 320
local MAT_W, MAT_H = CARD_W + 12, CARD_H + 32
local CARD_X, CARD_Y = (W - MAT_W) // 2, 116

local shadow = lvgl.Object(root, {
  x = CARD_X + 6, y = CARD_Y + 12, w = MAT_W, h = MAT_H,
  radius = 18, bg_color = 0x000000, bg_opa = 90, border_width = 0,
})
shadow:clear_flag(lvgl.FLAG.SCROLLABLE)

local mat = lvgl.Object(root, {
  x = CARD_X, y = CARD_Y, w = MAT_W, h = MAT_H,
  radius = 10, bg_color = C_MAT, border_width = 2, border_color = C_MAT_BD,
})
mat:clear_flag(lvgl.FLAG.SCROLLABLE)

-- 帧堆延后创建（开机安全）→ 占位灰底先撑住卡片区域
local placeholder = lvgl.Object(mat, {
  x = 6, y = 6, w = CARD_W, h = CARD_H,
  bg_color = 0x1A2230, border_width = 0,
})
placeholder:clear_flag(lvgl.FLAG.SCROLLABLE)

if F_CJK then
  lvgl.Label(mat, {
    text = "咕咕嘎嘎", text_color = C_CAP, text_font = F_CJK,
    align = { type = lvgl.ALIGN.BOTTOM_MID, y_ofs = -6 },
  })
end

-- ===== 前景雪 =====
local snowNear = {
  { x = 30,  y = 300, r = 4, v = 1.6, ph = 0.9, opa = 210 },
  { x = 310, y = 180, r = 3, v = 1.3, ph = 2.6, opa = 190 },
  { x = 120, y = 420, r = 4, v = 1.8, ph = 4.0, opa = 220 },
  { x = 260, y = 40,  r = 3, v = 1.1, ph = 5.2, opa = 180 },
  { x = 70,  y = 120, r = 3, v = 1.4, ph = 1.8, opa = 200 },
}
for _, s in ipairs(snowNear) do
  local o = lvgl.Object(root, {
    x = s.x, y = s.y, w = s.r * 2, h = s.r * 2,
    radius = lvgl.RADIUS_CIRCLE, bg_color = 0xEAF3FB, bg_opa = s.opa, border_width = 0,
  })
  o:clear_flag(lvgl.FLAG.SCROLLABLE)
  s.obj = o
end

-- ===== 时间/日期（os.date 种子 + 重播，无 dataman）=====
local function refreshTime()
  if timeLabel then timeLabel:set({ text = string.format("%02d:%02d", hh, mm) }) end
end
local function refreshDate()
  if not dateLabel then return end
  if CJK_OK then
    dateLabel:set({ text = string.format("%d月%d日 周%s", mo, dd, WEEK_CN[wd]) })
  else
    dateLabel:set({ text = string.format("%d.%d %s", mo, dd, WEEK_EN[wd]) })
  end
end
local function seedFromClock()
  local ok, lt = pcall(os.date, "*t")
  if ok and type(lt) == "table" and lt.day then
    hh, mm = lt.hour, lt.min
    dd, mo, wd = lt.day, lt.month, lt.wday
    refreshTime()
    refreshDate()
  end
end
seedFromClock()

-- ===== 一次性引导 Timer：500ms 后建帧堆 + 启动动效 =====
local N_FRAMES = 16
local frames = {}
local fi = 1
local tsec = 0

local bootTimer = lvgl.Timer({
  period = 500, repeat_count = 1,
  cb = function(self)
    local okF, errF = pcall(function()
      for i = 1, N_FRAMES do
        frames[i] = lvgl.Image(mat, {
          x = 6, y = 6, w = CARD_W, h = CARD_H,
          src = IMG(string.format("f%02d.bin", i)),
        })
        frames[i]:set({ hidden = (i ~= 1) })
      end
      placeholder:delete()
    end)
    dbg("frames deferred=" .. tostring(okF) .. (okF and "" or (" " .. tostring(errF))))

    if okF then
      -- 帧播放器 12fps
      local playTimer = lvgl.Timer({
        period = 83, repeat_count = -1,
        cb = function()
          frames[fi]:set({ hidden = true })
          fi = (fi % N_FRAMES) + 1
          frames[fi]:set({ hidden = false })
        end,
      })
      playTimer:resume()
    end

    -- 环境动效
    local motionTimer = lvgl.Timer({
      period = 50, repeat_count = -1,
      cb = function()
        tsec = tsec + 0.05
        local dy = math.floor(math.sin(tsec * 2.4) * 4 + 0.5)
        mat:set({ y = CARD_Y + dy })
        shadow:set({ y = CARD_Y + 12 + dy })
        for _, s in ipairs(blobs) do
          s.obj:set({
            x = s.x + math.floor(math.sin(tsec * 0.35 + s.ph) * 10),
            y = s.y + math.floor(math.cos(tsec * 0.27 + s.ph) * 8),
          })
        end
        for _, s in ipairs(snowFar) do
          s.y = s.y + s.v
          if s.y > H then s.y = -6 end
          s.obj:set({
            y = math.floor(s.y),
            x = s.x + math.floor(math.sin(tsec * 0.8 + s.ph) * 8),
          })
        end
        for _, s in ipairs(snowNear) do
          s.y = s.y + s.v
          if s.y > H then s.y = -8 end
          s.obj:set({
            y = math.floor(s.y),
            x = s.x + math.floor(math.sin(tsec * 1.1 + s.ph) * 10),
          })
        end
        if timeLabel then
          timeLabel:set({ opa = 205 + math.floor(math.sin(tsec * 1.1) * 25) })
        end
      end,
    })
    motionTimer:resume()

    -- 时钟重播（30s 对表，处理分/日翻转）
    local clockTimer = lvgl.Timer({
      period = 30000, repeat_count = -1,
      cb = function() seedFromClock() end,
    })
    clockTimer:resume()

    pcall(function() self:delete() end)
  end,
})
bootTimer:resume()

dbg("===== v3 init done")
