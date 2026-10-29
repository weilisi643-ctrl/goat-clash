# 《山羊对撞》physics v2 新旧对比回归报告（2026-10-29）

## 0. 备份与旧基准
- 备份：`_backup_physics_v1/`（js/、design/data/、tools/、410 例用例、旧基准输出，含 SHA256SUMS）；已加入 `project.config.json` packOptions.ignore（另加 docs/）。
- 旧基准（改动前当场复现确认）：对战帧哈希 `45b64984f7fa7685d074ce71a26516e63c23cd93449a5e2b663a9726a41756fb`（9649 帧）；顶顶乐 410 例 trace 哈希 `d1eb51ffa802ea1a14c3d0e8d43f7d7ce30112e014106b08aa421d464f30c887`；10 关参考解全三星。
- /workspace/goat-game **不是 git 仓库**（无 .git），未关联 weilisi643-ctrl/goat-clash；未推送、未发布。

## 1. 改动文件
| 文件 | 改动 |
|---|---|
| js/battle_physics.js（新增） | 对撞物理：抛物线、角判定点、接触/防穿模、伤害、击退、回位 |
| js/main.js | jump()/clash()/drawBattle 的物理部分改为调用 battle_physics（绘制调用不变） |
| js/ddl_physics.js | 顶顶乐推动物理 v2（用户授权修改） |
| project.config.json | ignore 加 _backup_physics_v1、docs |
| tools/battle_check.js、tools/p8_shots.py、tools/ddl_cases.json（新增） | 统计/穿模卡死检测、截图、410 例用例固化（原在 /tmp） |
| docs/* | 本报告与数据 |
未改：goat.js（绘制）、arena.js、ddl.js、levels*.json、champions*.json、factions.json、美术、manifest（逐字节比对一致）。

## 2. 每块改动
### 2.1 起跳抛物线与手感
| | v1 | v2 |
|---|---|---|
| 模型 | 帧制：vy=-9，每帧 vy+=0.45（显式欧拉，有离散误差） | 时间制解析抛物线 y(t)=-v0·t+½g·t²，DT=1/60 |
| 顶点 | 固定约 90–94px，20 帧到顶 | apex = 70+30×timing（完美 100px，最差 70px），tApex=0.32s |
| 水平 | 4px/帧 | 240px/s（同速） |
| 对手 | 同参数 | 对手时机在起跳时决定（擂主：timingHit→1 否则 0–0.7；自由：0–1），也决定其高度 |
| 落地 | result 阶段 y 每帧 +4 线性回落 | 同一抛物线自然落地 |

### 2.2 羊角碰撞判定（贴合 art v7）
- 判定点 = (horn_root − anchor)×0.1×s，y 加 40·s（anchor 为脚底）；s=1.1。1152×1024 与 360×320 等比，结果一致；tools 校验 manifest v7 数值一致（match=true）。
| 姿态 | horn_root | 相对物理中心偏移 (px) |
|---|---|---|
| idle | (806,277) | (+32.45, −34.98) |
| jump | (782,326) | (+29.81, −29.59) |
| clash | (860,687) | (+38.39, +10.12) |
- v1：`p.x ≥ W/2−50` 即判定（与角无关，约第 11 帧）。v2：空中用 jump 判定点，角半径 10px，水平 ≤20px 且竖直差 ≤40px（头高）即接触，平均约 13 帧；接触时把穿透量对半推开（防穿模）。
- 竖直差 dy 决定 align=1−|dy|/40。

### 2.3 顶撞力度与击退
| | v1 | v2 |
|---|---|---|
| 力度 | pp=20+pow+bonus+timing×30+spd×0.3（擂主乘克制倍率） | 同，再 × heightMul：高的一方最多 +3%（按 dy/30 线性）；8% 时自由对战胜率偏离过大，已回调 |
| 伤害 | round(\|pp−ep\|)+8 | round(8+\|pp−ep\|×q)，q=0.85+0.15×align（擦角略减） |
| 击退 | 双方每帧固定后退 3px×20 帧，x 钳到 W·0.25 | 冲量式：输家 150+6×差值 px/s（≤600），赢家反冲 90px/s，摩擦 900px/s² 减速，然后 150px/s 走回原位；x 钳在 [0.1W,0.9W] |
| 回位 | 无（敌方回合间位置逐渐偏移） | 自动回原位，双方对称 |

### 2.4 顶顶乐推动物理（ddl_physics.js）
1. 修复 v1 的 `ns` 跨物体沿用 bug（绵羊冲刺触发看的是上一个物体的速度），改为每个物体自己的速度。
2. 墙反弹由固定 0.5 改为 0.5×(1+e)/1.6（上限 0.75），与材质相关。
3. 碰撞位置修正加 SLOP=0.05 容差、2 次迭代（冲量只在第 1 次施加），减少叠压抖动。
4. 自适应子步：单帧位移 > 自身半径时细分（上限 4），防高速穿透。说明：试过固定 2 子步，会让 L3/4/6/8/10 参考解失效，因此改为自适应；现有速度上限（直角 1035px/s≈17px/帧 < 半径 18）下实际不触发，属于保护。
5. Shot 增加 timeout/maxSub 标记。levels 数据**未改动**。

## 3. 对比数据
### 3.1 回归哈希
| 项 | v1 | v2 |
|---|---|---|
| 对战帧哈希（p6_regress） | 45b64984…56fb / 9649 帧 | `af021cefc4c4b3c0da1f2e750106a6159ab57063e8b5a76d0cd44760f90086ce` / 9074 帧 |
| p6 输出整体 sha256 | — | 8de1a12a47af9028e7c37e81dddc2b34be9836fceec8458f2c153f2a1d8b8885（两次运行一致，确定性） |
| 410 例 trace 哈希 | d1eb51ff…c887 | `fe6ea1d99559d86045cf7b2584999e9937882c678f39f575baf2aaac67d64548` |
| ddl_physics.js sha256 | 9f290da1… | 49fc9e8ed2e1f6506a1564b574f21bf005ee96feef5cee2e874bc128a6085c1c |
| 410 例逐项 | — | 146 例完全一致，409/410 solved 标志一致；solved 12→13（多数用例本就是失败扰动） |

### 3.2 10 关参考解（levels.v2.json，未改）
全部 solved 且三星：L1–L10 = 3,3,3,3,3,3,3,3,3,3（v1 同）。

### 3.3 容错过关率（ddl_v2_robust，N=400，adapt+力度吸附 主指标）
| 关 | 目标 | v1 | v2 | blind+吸附 v1→v2 |
|---|---|---|---|---|
| L1 | .70 | .860 | .860 | .768→.768 |
| L2 | .35 | .665 | .665 | .295→.298 |
| L3 | .35 | .370 | .390 | .135→.140 |
| L4 | .35 | .645 | .650 | .130→.130 |
| L5 | .35 | .738 | .738 | .338→.338 |
| L6 | .40 | .493 | .493 | .445→.445 |
| L7 | .20 | .470 | .450 | .055→.055 |
| L8 | .35 | .530 | .545 | .228→.228 |
| L9 | .20 | .830 | .828 | .208→.208 |
| L10 | .20 | .243 | .238 | .085→.075 |
全部达标（miss=[]）。

### 3.4 AI 对手（tools/battle_check.js，每组 300 局，固定种子；技能=蓄力点围绕 0.8 的标准差）
| 组 | v1 胜率 | v2 胜率 | v2 回合交换/局 | v2 平均伤害 | 最大帧/局 | 卡死 |
|---|---|---|---|---|---|---|
| 自由·高手 σ0.05 | .717 | .790 | 19.4 | 18.2 | 3271 | 0 |
| 自由·普通 σ0.15 | .577 | .610 | 20.4 | 17.9 | 3363 | 0 |
| 自由·新手 σ0.35 | .413 | .450 | 19.6 | 18.1 | 3390 | 0 |
| 擂主第1场·高手 | .707 | .720 | 16.2 | 19.1 | — | 0 |
| 擂主第1场·普通 | .653 | .690 | 18.4 | 18.6 | — | 0 |
| 擂主第2场·高手 | .480 | .467 | 20.1 | 18.8 | — | 0 |
| 擂主第2场·普通 | .310 | .300 | 21.2 | 18.7 | — | 0 |
（单场三局两胜胜率；策划口径的"整关胜率 5–15%"为两场连胜+次数限制，第 2 场基本不变。）

### 3.5 穿模 / 卡死自动检测
| 检测 | v1 | v2 |
|---|---|---|
| 对战：空中角判定点穿透 >0.5px 帧数 | （v1 无角判定） | 0（最大 0） |
| 对战：双方左右交叉帧 | 0 | 0 |
| 对战：>20000 帧未结束 | 0 | 0 |
| 顶顶乐 5241 次顶撞（410 例+每关 200 次大扰动）超时(480 帧) | 0 | 0 |
| 最大物体重叠深度 | 5.77px | 3.54px |
| 重叠 >2px 帧数 | 4 | 2 |
| NaN | 0 | 0 |
| 最长单次顶撞 | 137 帧 | 139 帧 |

## 4. 截图（Playwright + /usr/bin/google-chrome）
screenshots/p8_01_jump、p8_02_clash、p8_03_jump_debug、p8_04_clash_debug、p8_05_knockback、p8_06_ddl_aim、p8_07_ddl_push、p8_08_ddl_after（L1 三星）。浏览器无脚本错误（仅 1 条 404 资源，疑为 favicon）。

## 5. 遗留风险
- 自由对战玩家胜率上升 3–7 个百分点（时机同时影响力度和高度）；需要的话可把 heightAdv 调为 0 恢复 v1 平衡。
- 擂主第 1 场略易（+1–4pt）；第 2 场持平。
- 顶顶乐自适应子步在当前速度上限下不触发，新增更快物体时才生效；届时参考解需复核。
- 顶顶乐墙反弹改动让 L7/L10 容错率小降（仍达标，L10 .238 接近 .20 下限）。
- 对撞 clash 姿态判定点 y 在身体中心下方（+10px，因 v7 clash shift_y=126）；判定只用 jump 姿态，clash 点仅记录。
- 浏览器帧率按 rAF=60Hz 假设（与 v1 相同）；高刷屏会加快，未做时间累加器。
- 尚未在微信开发者工具真机跑过。

## 6. 固定时间步（2026-10-29 追加）
- main.js：`loop(ts)` 按 rAF 时间戳累加真实经过时间，每 STEP=1/60s 调一次 `update()`（updateBattle/updateDdl：抛物线、接触、clash、击退回位、B.t、蓄力条、顶顶乐 Shot.tick），单帧最多补 MAX_STEPS=5 步，超出部分丢弃并计入 `clock.dropped`（防螺旋死亡）；`render()` 每帧一次，绘制函数只读状态（绘制代码本身未改，只把其中的状态推进行挪进 update）。无时间戳调用（回归脚本 raf()）恰好 1 步。
- 回归（必须与 v2 基准一致）：对战帧哈希 af021cefc4c4b3c0da1f2e750106a6159ab57063e8b5a76d0cd44760f90086ce / 9074 帧 ✅；p6 输出 sha256 8de1a12a… ✅；410 例 fe6ea1d9…4548 ✅；10 关全三星 ✅。
- 多帧率（tools/p9_hz_check.py：Playwright + 系统 Chrome，虚拟 rAF 时钟，同一 Math.random 种子；蓄力 1.0s → 起跳 0.5s → 顶顶乐 L1 1.5s）：

| 刷新率 | 蓄力步数/1s | 蓄力条 | 起跳后步数/0.5s | 阶段/B.t | p.x | e.x | p.y | 敌HP | 顶顶乐步数/1.5s | 渲染帧 | 丢步 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 30Hz | 60 | 0.936 | 30 | result/17 | 116.440 | 256.838 | −62.229 | 83 | 90 | 94 | 0 |
| 60Hz | 60 | 0.936 | 30 | result/17 | 116.440 | 256.838 | −62.229 | 83 | 90 | 187 | 0 |
| 120Hz | 60 | 0.936 | 30 | result/17 | 116.440 | 256.838 | −62.229 | 83 | 90 | 373 | 0 |
| 144Hz | 60 | 0.936 | 30 | result/17 | 116.440 | 256.838 | −62.229 | 83 | 90 | 448 | 0 |
| 45Hz±50% 抖动 | 60 | 0.936 | 30 | result/17 | 116.440 | 256.838 | −62.229 | 83 | 90 | 147 | 0 |
| 5Hz（卡顿，防螺旋） | 25 | 0.45 | 15 | — | — | — | — | — | 40 | 18 | 100 |

30–144Hz 及抖动帧率下进度逐项一致（v1 循环在 30Hz 会慢一半、144Hz 快 2.4 倍）。5Hz 时每帧最多补 5 步，游戏按设计变慢而不是卡死。数据：docs/fixed_step_hz_check.json。

## 7. 画面升级第一步（2026-10-29）
- 新增 js/fx.js（3.8KB，固定 240 粒子池；自带 RNG，不调用 Math.random）：扬尘、草屑、火花、羊毛（输家毛色）、冠军彩带；冲击波圈、速度线、白闪、屏震、顿帧、挤压拉伸。未引入 tween.js（体积/必要性考虑，后续 UI 缓动再加并附 MIT 许可证）。
- 事件来源（只读）：jump()（起跳尘+拉伸）、接触瞬间 clash（顿帧 60–100ms，按力度差线性；屏震 4–10px、220ms 衰减；白闪；冲击波；速度线；火花/羊毛/扬尘）、result 阶段落地（扬尘+草屑+挤压）、顶顶乐 Shot.ev 增量（wall/rock/break/hay）、回合胜/擂主胜/顶顶乐过关（彩带）。
- 顿帧只冻结画面：drawBattle 在冻结期用接触瞬间的位置快照绘制，物理固定步照常推进；屏震只是 render 外层 ctx.translate；挤压拉伸只在 main.js 绕脚底 ctx.scale 包住 drawGoatArt 调用，goat.js 未改。`FX.enabled=false` 即关闭全部特效（用于 before 截图）。
- 回归（与 v2 基准完全一致）：对战帧哈希 af021cef…86ce / 9074 帧 ✅，p6 输出 sha256 8de1a12a…8885 ✅，410 例 fe6ea1d9…4548 ✅，10 关全三星 ✅，tools/battle_check.js 7 组 AI 胜率/帧数/伤害输出与 v2 逐字节相同 ✅，30/60/120/144/抖动帧率进度仍一致 ✅。主包约 0.45MB。
- 截图（同一虚拟时刻、同一种子，before=FX 关 / after=FX 开）：screenshots/p9_01_jump、p9_02_clash_hitstop（接触后 30ms：after 仍定格在接触位置+白闪+冲击波）、p9_03_clash_spark（160ms）、p9_04_land（520ms）、p9_05_ddl_hay、p9_06_ddl_confetti，各 _before/_after；录屏 screenshots/p9_clash_fx.webm（真实时间 3 次对撞，FX 开）。脚本 tools/p9_fx_shots.py。
- 风险：屏震会让 HUD 一起抖（整画面平移）；顿帧期间画面与物理有 ≤100ms 不同步，之后瞬间追上（输家被击退的起点会"跳"一下，录屏可见，后续可改为顿帧后插值追帧）；对撞扬尘 y 略低于地面线。

## 8. FX 修正（仅渲染层）
1. 屏震只作用于场景层（对战：影子/羊/💥/粒子；顶顶乐：草堆/物体/羊/瞄准/粒子），HUD、按钮、文字不抖；白闪在最上层不平移。
2. 顿帧结束后 100ms cubic ease-out 插值，显示位置从冻结快照追上物理位置，击退起点不跳；物理不受影响。
3. 对撞扬尘与起跳/落地尘都用地面线 GY()+45。
回归：p6 sha 8de1a12a…（对战哈希 af021cef…86ce / 9074 帧）、410 例 fe6ea1d9…4548、AI 统计逐字节一致、L1–L10 全部达成、30/60/120/144/45抖动 Hz 结果一致。截图 screenshots/p10_*，录屏 screenshots/p10_clash_fx.webm。

## 9. 画面升级第二步（仅渲染层）
- 暗角：js/ui.js vignette（场景+HUD 之上、白闪之下）。影子：goat.js drawShadow 改为径向渐变柔和椭圆，中心 (x, y+41s)、尺寸与离地衰减 k=max(0.4,1-lift/160) 与原版一致，位置仍与物理对齐。撞击光晕：fx.js clash 事件加 lighter 径向光晕 + spark_burst 贴图。
- 位图字体：tools/gen_ui_assets.py 用 Noto Sans CJK SC Bold（SIL OFL 1.1，许可 art/ui/OFL.txt）离线生成 art/ui/font_title.png / font_btn.png + font.json，只含标题/按钮/关卡名/牧场名/数字 198 字；缺字整串回退系统字体，emoji 单字回退。九宫格：art/ui/btn9.png、panel9.png（灰度，运行时乘色）。
- tween.js 23.1.3（MIT，libs/tween.umd.js + libs/tween.LICENSE）：UMD 在微信 require 与 index.html shim 下均可加载；场景切换时标题 Back.Out 弹出、按钮/面板淡入上浮，时间由渲染时钟显式传入，命中区不变。
- 擂主阵营色调：arena/faction/arenaResult/擂主对战画面按玩家牧场叠加色调，文字仍只显示牧场名。
- art/fx 贴图替换程序化粒子（dust_0..2 按寿命换帧、grass_blade、spark_streak 沿速度旋转 lighter、wool_fluff 按羊毛色乘色、shockwave_ring 0.2→1.2 渐隐）；未加载/失败回退原绘制。art/parts 未使用，未删任何美术文件。
- project.config.json：原 ignore 正则 `^art/.*(?<!_320)\.(png|jpg)$` 会把 art/fx、art/ui 排除出主包，改为 `^art/(?!fx/|ui/).*(?<!_320)\.(png|jpg)$`。主包实测见 tools/pkg_size.py。
- 回归与 v2 一致：battleHash af021cef…86ce / 9074 帧，逐帧 dump 1692fd26…，410 例 fe6ea1d9…4548，10 关三星，AI 统计逐字节一致，多帧率一致。截图 screenshots/p11_*（before=2286c4b / after / compare）。

## 10. 画面 v2.1（仅渲染层）
- 集中配置 js/visual_config.js：暗角 alpha 0.10（inner 0.5 / outer 0.8）、阵营色调 alpha 0.05 + 顶部色带 0.22（高 22%）、撞击光晕 220ms / alpha 0.55 / 半径 26+46e+20pw / 星爆 0.8×80px、按钮提亮 1.07。
- 九宫格按钮调亮（btn9 主体 255→250、底边 222，乘色前按 brightness 提亮）；亮度见 docs/p12_button_luma.json。
- 字形视觉中心写入 font.json（cy），文字与 emoji 都以 y 居中；标题支持传入颜色（title_mask 蒙版字体乘色）。
- 回归与 v2 一致；截图 screenshots/p12_*（orig=2286c4b / v2=5b84a85 / v21）。

## 11. UI 主题化（范围变更后）
- UI 将整体重做：v2.1 中的按钮调亮、标题传色、emoji 居中保留为当前默认主题的一部分（不再继续打磨）。
- 新增 js/theme.js（颜色/圆角/字体位图或系统/按钮与面板 nine|solid+描边+阴影/缓动/间距/effects 强度），js/ui.js 提供 drawButton/drawPanel/drawText/drawBg，main.js 的 btn/panel/text/bg 全部委托。js/visual_config.js 改为 theme.effects 兼容入口。字段说明 docs/theme.md。
- 默认主题与 v2.1（dfcaa6d）逐像素一致（p12 四个场景差异 bbox=None）；theme_demo.py 演示 solid 主题。回归与 v2 一致。

## 12. v2.3 美术修复接入（v8c 整图）
- 接入 goat-game 修好的 v7 整图（beard 6、wool 24 及 v8 修复的 body/face/wool 等，共 49 个大图/_320 文件）+ art/manifest.json；art/parts、parts.json、_v8_pre/_v8b_pre/_v8c_pre、fix_compare_* 未接入（packOptions `^art/_[^/]+/` 排除下划线备份目录）。
- manifest 核对：poses（anchor/horn_root/head_box/foot_y）、horn_bboxes、draw_order 与提交版一致；仅新增 edge_fix 说明、recolor.beard、beard_recolor，beard 三个文件 kind 由 color → gray_mask。
- 渲染：goat.js 中 beard 层与 wool 共用 woolColor 着色和 layer() 离屏缓存（manifest kind=gray_mask 时生效）。
- 绿边检测（tools/p13_shots.py，s=7 绿底合成，3 姿势×4 毛型×2 毛色）：内部绿色像素 13454 → 8480，闭合小孔 2774 → 2060，图层自身偏绿 0 → 0。详见 docs/p13_green_fringe.json。
