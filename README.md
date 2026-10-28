# 咩咩顶角王 原型
- 微信开发者工具：导入项目 → 选择本目录 → 类型「小游戏」→ AppID 可选「测试号」或填自己的（替换 project.config.json 中 touristappid）。
- 浏览器预览：在本目录运行 `python3 -m http.server 8000`，打开 http://localhost:8000/index.html （鼠标点击代替触摸）。

## 第一期：角力推理 + 每日擂主（2026-10-28）
- 浏览器预览：在项目根目录 `python3 -m http.server 8765`，打开 http://localhost:8765/index.html（数据从 design/data/*.json 同步读取，需 http 方式打开）。
- 定制页右下「🏆 每日擂主」进入；自由对战玩法不变。
- 新增 js/arena.js（线索生成、倍率、日期/擂主、进度、阵营积分，纯逻辑）；main.js 增加 observe 推理阶段、擂台/牧场/结算界面；goat.js 增加 drawShadow。
- 进度暂存本地（wx.setStorageSync / localStorage），广告为模拟按钮；正式版需云函数校验次数与得分。
- 牧场显示统一走 A.factionLabel(f, opts)，以后加省份：factions.json 加 regions 字段并传 {withRegions:true}。

## 2026-10-28 改版：去掉角力推理与蓄力答题
- 流程（自由对战 / 每日擂主相同）：选角度 → 看准力量条起跳 → 对撞。
- 开关：`js/arena.js` 的 `REASONING_ENABLED = false`（不出观察线索/猜角度，无 guessMul/readCancelsCounter/maxMul，AI readAcc/counterPick 不生效，只保留原型角形克制 ×1.3）；`js/main.js` 的 `QUIZ_ENABLED = false`（不出蓄力题、无答题力量加成）。改为 true 即恢复，相关代码与 design/data 数据文件均保留。
- 擂主难度由 AI 强度（timingHit、powBonus、hpBonus）与第 2 场角形限制区分。
- 阵营分中的"预判命中率×5"一项在推理关闭时恒为 0（单次最多 15 分）。

## 顶顶乐（2026-10-28）
- 入口：首页「🎮 顶顶乐」→ 选关 → 拖动瞄准 + 力量条顶撞。
- 物理：`js/ddl_physics.js` 为 `design/sim/physics.py` 的逐行移植（固定 dt=1/60，无随机）。`Math.hypot` 用双倍精度实现以对齐 CPython。
- 数据：`design/data/levels.json`。激励视频为占位按钮（+1 次顶撞 / 显示第 1 步瞄准线）。
- 验证：`tools/` 下有 py/js 轨迹对比与参考解复验脚本。

## 擂主 v2
- 数值来自 `design/data/champions.v2.json`（arena.js 已改加载路径）。
- 第 1 场 `angleReveal: public`，第 2 场 `hidden`（撞后揭晓）。
- 牧场积分：`round(8 + 6×timingAvg + 4×hpPct + (2:0?2:0))`，见 factions.json 的 score 字段。

## 顶顶乐容错 v2（2026-10-28）
- 加载 `design/data/levels.v2.json`（`levels.json` 保留不动）。
- 开火前 `applyAssist`：力度吸附 ±0.05 → 0.5–1.0 档；角度吸附 ±3° → 最近可推物件/草堆（L3/L8 的 `assist.angleMagnet=false` 关闭）。
- 物理核心 `js/ddl_physics.js` 未改。
