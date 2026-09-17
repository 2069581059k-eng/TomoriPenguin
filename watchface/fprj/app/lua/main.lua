-- 咕咕嘎嘎臭企鹅 · 动态表盘 v4 全屏版（小米手环10 Pro / 336×480）
-- 参考技法：相变临界/哥伦比亚 = 全屏帧动画底图 + 顶部暗区承载信息
-- ===== 本镜像开机生存四法则（实验验证，勿回退）=====
-- 1) 仅 MiSans 字体（montserrat 光栅化原生崩溃）
-- 2) dataman 禁用（init 调用破坏静态→Live 交接；Timer 内调用杀死刷新）
--    → 时间用 os.date 种子 + 30s 重播
-- 3) RGB565/I8 图片禁在 init 创建 → 500ms 一次性 Timer 回调内创建帧堆
-- 4) 帧播放：全屏 20 帧 @10fps（I8 索引色，含烘焙顶部渐变暗区）
local app_module = "app.tomori_penguin"
local project_name = "TomoriPenguin"

local lvgl = require("lvgl")
local W, H = lvgl.HOR_RES(), lvgl.VER_RES()

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
dbg("===== v4 boot W=" .. tostring(W) .. " H=" .. tostring(H))

-- ===== 字体（仅 MiSans）=====
local function load_font(name, size)
  local ok, f = pcall(lvgl.Font, name, size, "normal")
  if ok and f then return f end
  return nil
end
local F_HERO = load_font("MiSansF-Demibold", 64) or load_font("MiSans-Demibold", 64)
local F_SMALL = load_font("MiSansF-Medium", 18) or load_font("MiSans-Medium", 18)
local CJK_OK = (F_SMALL ~= nil)
dbg("fonts hero=" .. tostring(F_HERO ~= nil) .. " small=" .. tostring(F_SMALL ~= nil))

local C_INK    = 0xEAF0F7
local C_DIM    = 0x9FB3C8
local C_ACCENT = 0x8ED4EF
local C_LOWBAT = 0xE8736A

-- ===== 根 =====
local root = lvgl.Object(nil, { w = W, h = H, bg_color = 0x0F1420, border_width = 0 })
root:clear_flag(lvgl.FLAG.SCROLLABLE)

-- 占位底（帧堆延迟创建前的第一帧静置）
local placeholder = lvgl.Object(root, { x = 0, y = 0, w = W, h = H, bg_color = 0x0F1420, border_width = 0 })
placeholder:clear_flag(lvgl.FLAG.SCROLLABLE)

-- ===== 信息区（顶部烘焙暗区内，永不遮挡视频主体）=====
local WEEK_CN = { "日", "一", "二", "三", "四", "五", "六" }
local WEEK_EN = { "SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT" }
local hh, mm = 0, 0
local dd, mo, wd = 1, 1, 1

local dateLabel, pctLabel, timeLabel, batFill
-- miwear 状态栏占位：LVGL y 坐标 = 视觉 y - 28（参考表盘首元素 y=27 同款补偿）
if F_SMALL then
  dateLabel = lvgl.Label(root, {
    text = "", text_color = 0xC9D6E4, text_font = F_SMALL, x = 24, y = 28,
  })
  pctLabel = lvgl.Label(root, {
    text = "--%", text_color = 0xC9D6E4, text_font = F_SMALL, x = W - 96, y = 28,
  })
end
local cap = lvgl.Object(root, {
  x = W - 46, y = 31, w = 26, h = 13, radius = 6,
  border_width = 2, border_color = 0xC9D6E4, bg_opa = 0,
})
cap:clear_flag(lvgl.FLAG.SCROLLABLE)
batFill = lvgl.Object(cap, {
  x = 2, y = 2, w = 22, h = 9, radius = 4,
  bg_color = C_ACCENT, bg_opa = 200, border_width = 0,
})
batFill:clear_flag(lvgl.FLAG.SCROLLABLE)
if F_HERO then
  timeLabel = lvgl.Label(root, {
    text = "00:00", text_color = C_INK, text_font = F_HERO, x = 22, y = 48,
  })
end

-- ===== 前景雪（少量微光，画龙点睛）=====
local snow = {
  { x = 30,  y = 300, r = 3, v = 1.4, ph = 0.9, opa = 200 },
  { x = 310, y = 180, r = 2, v = 1.1, ph = 2.6, opa = 180 },
  { x = 120, y = 420, r = 3, v = 1.6, ph = 4.0, opa = 210 },
  { x = 265, y = 60,  r = 2, v = 0.9, ph = 5.2, opa = 160 },
}
for _, s in ipairs(snow) do
  local o = lvgl.Object(root, {
    x = s.x, y = s.y, w = s.r * 2, h = s.r * 2,
    radius = lvgl.RADIUS_CIRCLE, bg_color = 0xEAF3FB, bg_opa = s.opa, border_width = 0,
  })
  o:clear_flag(lvgl.FLAG.SCROLLABLE)
  s.obj = o
end

-- ===== 时间种子（os.date，无 dataman）=====
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

-- ===== 引导 Timer：500ms 后创建全屏帧堆 + 动效 =====
local N_FRAMES = 20
local frames = {}
local fi = 1
local tsec = 0

local bootTimer = lvgl.Timer({
  period = 500, repeat_count = 1,
  cb = function(self)
    local okF, errF = pcall(function()
      for i = 1, N_FRAMES do
        frames[i] = lvgl.Image(root, {
          x = 0, y = 0, w = W, h = H,
          src = IMG(string.format("f%02d.bin", i)),
        })
        frames[i]:set({ hidden = (i ~= 1) })
      end
      pcall(function() placeholder:delete() end)
    end)
    dbg("frames deferred=" .. tostring(okF) .. (okF and "" or (" " .. tostring(errF))))

    if okF then
      -- 信息区/雪在帧堆之下会被盖住：提升 z 序 = 重新挂到最后
      local function lift(o)
        if o then pcall(function() o:set_parent(root) end) end
      end
      lift(dateLabel); lift(pctLabel); lift(cap); lift(timeLabel)
      for _, s in ipairs(snow) do lift(s.obj) end

      -- 全屏帧播放器 10fps
      local playTimer = lvgl.Timer({
        period = 100, repeat_count = -1,
        cb = function()
          frames[fi]:set({ hidden = true })
          fi = (fi % N_FRAMES) + 1
          frames[fi]:set({ hidden = false })
        end,
      })
      playTimer:resume()
    end

    -- 雪 + 时间呼吸
    local motionTimer = lvgl.Timer({
      period = 60, repeat_count = -1,
      cb = function()
        tsec = tsec + 0.06
        for _, s in ipairs(snow) do
          s.y = s.y + s.v
          if s.y > H then s.y = -6 end
          s.obj:set({
            y = math.floor(s.y),
            x = s.x + math.floor(math.sin(tsec * 1.1 + s.ph) * 9),
          })
        end
        if timeLabel then
          timeLabel:set({ opa = 210 + math.floor(math.sin(tsec * 1.1) * 25) })
        end
      end,
    })
    motionTimer:resume()

    -- 时钟重播
    local clockTimer = lvgl.Timer({
      period = 30000, repeat_count = -1,
      cb = function() seedFromClock() end,
    })
    clockTimer:resume()

    pcall(function() self:delete() end)
  end,
})
bootTimer:resume()

dbg("===== v4 init done")
