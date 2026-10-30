# 调色板《山羊对撞》v1（2026-10-29）

全部数值由 `measure.py`（PIL 只读统计）从已通过素材测得，或直接取自代码中的生效值；结果见 `measurements.json`。

| ID | Hex | 用途 | 来源 |
|---|---|---|---|
| ui_bg | `#CFFC98` | UI 草绿底（主背景） | ui_mock_v2/home.png 697,516px 第1名；js/theme.js bg |
| ui_tuft | `#B1D198` | 底面稀疏小草 | ui_mock_v2/hud.png 990px；theme.js tuft |
| ui_ink | `#2F3727` | 描边/文字/按钮投影（墨绿黑，禁用纯黑） | home.png 66,457px；theme.js ink |
| ui_white | `#FFFFFF` | 按钮/面板填充、标题字 | home.png 135,430px |
| ui_green | `#8CCB4E` | 主按钮厚底、我方血条 | hud.png 14,792px |
| ui_yellow | `#FCD800` | 高亮/胜利字/箭头按钮 | home.png 24,112px |
| ui_blue | `#2E6FD8` | 次级功能按钮 | home.png 6,158px |
| ui_orange | `#FF9E3D` | 活动按钮 | home.png 6,474px |
| ui_red | `#FF7A6B` | 敌方血条 | hud.png 5,975px |
| ui_alert | `#E5482F` | 警示 | theme.js alert |
| ui_gray | `#C9CCC4` | 失败字/禁用 | theme.js gray；result_lose |
| wool_white | `#FFFFFF` | 羊毛色1（默认） | js/data.js woolColors[0] |
| wool_pink | `#F6D6E6` | 羊毛色2 | data.js |
| wool_blue | `#CFE8FF` | 羊毛色3 | data.js |
| wool_black | `#3A3A3A` | 羊毛色4 | data.js |
| wool_cream | `#FFE9A8` | 羊毛色5 | data.js |
| wool_mint | `#C9F2C7` | 羊毛色6 | data.js |
| wool_ref_light | `#F4E4D4` | 写实参考羊毛亮面 | base_side_realistic.png 9.0% |
| wool_ref_mid | `#E4D4C4` | 写实参考羊毛中间调 | base_side_realistic.png 5.4% |
| wool_ref_shadow | `#D4C4AC` | 写实参考羊毛暗面 | base_side_realistic.png 2.8% |
| knee_patch | `#A8774A` | 膝部补丁默认色（绘制在羊毛之上，v10.1 已确认可见） | manifest.json recolor |
| horn_tan | `#D9B77A` | 角色1 米金（默认） | data.js hornColors[0] |
| horn_gold | `#FFD700` | 角色2 金 | data.js |
| horn_silver | `#C0C0C0` | 角色3 银 | data.js |
| horn_pink | `#FF7AA8` | 角色4 粉 | data.js |
| horn_cyan | `#7AD0FF` | 角色5 冰蓝 | data.js |
| horn_brown | `#8B5A2B` | 角色6 棕 | data.js |
| body_dark | `#4C341C` | 身体/蹄/腿 深棕主色 | body/body_idle.png 4.7%（8级量化） |
| body_mid | `#6C4C2C` | 身体中间调 | body/body_idle.png 3.0% |
| face_skin | `#AC8C6C` | 脸部皮肤 | face/face_idle.png 1.6% |
| face_eye | `#140404` | 眼/鼻深色 | face/face_idle.png 1.4% |

## 灰度 mask 规则（换色基础，不得改）
- 羊毛 mask：亮度均值 ≈196–201，最亮 244–255，5% 分位 121–132（fluffy/short/cloud）；RGB = 灰度/255 × 羊毛色。
- 胡子 mask：均值 227–230，最亮 251–254（manifest：最亮约 250）→ **胡子必须与羊毛同色**，比羊毛整体亮约 30。
- 羊角 mask：中灰 128 = 目标色；实测均值 105–117，5% 分位 34–64。
- 膝补丁 mask：均值 158–166，默认上 #A8774A。

## 新增（2026-10-29）

## v10.1 决策色（2026-10-29 晚，b22a043）
| ID | Hex | 用途 | 来源 |
|---|---|---|---|
| wool_lavender | `#CDB8F0` | 教学奖励羊毛色「薰衣草紫」 | gc_repo 提交 186d16d |
| contact_shadow | `#2F3727` α0.26 | 山羊脚下接触阴影（复用 ui_ink，不新增色相） | 负责人决策 |
| perfect_outline | `#FCD800` | 完美区描边 accentYellow（= ui_yellow） | 负责人决策 |
| perfect_text_stroke | `#FFFFFF` | 「完美！」38px 字的白色外描边 | 负责人决策 |
