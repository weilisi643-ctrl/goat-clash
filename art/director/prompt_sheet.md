# 生图提示词表（给 羊角美术 / ChatGPT 图像）v1

## 0. 交付硬性要求
- **透明背景 PNG**（RGBA），不要绿幕；如工具只能出纯色底，用纯白底并标注，由 羊角美术 抠图后再交，抠完不得有绿/白边。
- 角色素材画布：**1152×1024**，侧面**朝右**，脚底中心对齐 anchor（idle 511,995 / 以 manifest.json 为准）；另导 **360×320** 小图。**与已有同名文件的轮廓、位置、尺寸必须一致**，只换画面质感。
- 羊毛/胡子/羊角/膝补丁交**灰度图**（不要彩色）；身体/脸交彩色。
- UI：按 750×1334 样稿尺寸出图；fx 小件 32/64/128/192 px 正方形。

## 1. 基础提示词块（每次都粘）
```
Semi-realistic side view of a real domestic goat facing right, natural proportions,
slightly loose fluffy wool with soft clumps, goatee same colour as the wool,
soft top-left key light, gentle shading, no outline on the character,
clean silhouette readable at small phone size, isolated on transparent background,
game sprite, consistent with previous set
```
中文备注：半写实真山羊、朝右、羊毛略松散、胡子与羊毛同色、左上光、角色无描边、透明底。

## 2. 避免清单（Negative）
chibi / cartoon outline on goat / anime eyes / sheep (no curly sheep face) / green screen / green or white halo / semi-transparent fog edges / drop shadow on ground / text / watermark / background scenery / front view / extra legs / holes in wool / different goatee colour / gradient UI / photorealistic noise

## 3. 分项模板
### 3.1 身体（body，彩色）
`[基础块] + body only, dark brown short-haired body #4C341C–#6C4C2C, hooves, pink inner ear, pose: {idle 站立 | jump 跃起 | clash 低头冲撞}, no wool layer, no horns`

### 3.2 羊毛（灰度 mask）
`[基础块] + wool layer only, grayscale, average brightness ~200, highlights to 250, shadows ~125, style: {fluffy 蓬松卷团 | short 贴身短毛、边缘整齐 | spots 带深灰斑块 | cloud 大团云朵状但边缘清晰不起雾}, solid coverage, no holes, pose {pose}`
- short 的 jump 帧：特别强调 `no gaps between belly and legs, fully covered`。
- cloud：`crisp clumped edge, alpha either solid or 1–2px antialias only`。

### 3.3 胡子（灰度 mask）
`goatee only, grayscale, brighter than wool (avg ~228, max 250), wispy tip, readable as 8×12px at 360×320`

### 3.4 羊角（灰度 mask，中灰=目标色）
`horn only, grayscale, base mid-gray 128, ridged texture darker, highlight on top edge, shape: {curl 卷角 | straight 直角 | spiral 螺旋 | branch 分叉}, root at head position`

### 3.5 腿部/膝补丁（灰度 mask，新）
`leg patch only, grayscale avg ~160, covers bare lower leg and knee, matches leg silhouette exactly, pose {pose}, part {leg_front_near|leg_front_far|leg_back_near|leg_back_far}`

### 3.6 UI 图标 / 按钮
```
Flat cute mobile game UI in the style of 羊了个羊, white fill, thick dark olive-black outline #2F3727,
solid hard drop shadow straight down #2F3727, rounded corners, no gradient, no texture,
accent colours only: #FCD800 yellow, #8CCB4E green, #2E6FD8 blue, #FF9E3D orange, #FF7A6B red,
transparent background, {icon/button: ...}
```
主按钮：白底 + 绿色厚底 #8CCB4E；小按钮：黄 #FCD800 + 7px 黑投影。

### 3.7 背景
`flat solid grass green #CFFC98 with sparse small grass tufts #B1D198 (three-stroke tufts), no horizon, no gradient, no shading, 750×1334`

## 4. 交付前自查
1. 尺寸与同名旧图一致？ 2. 透明底、无绿边（G−max(R,B)>25 的像素 = 0）？ 3. 灰度层没有彩色？ 4. 胡子与羊毛同一 mask 逻辑？ 5. 小图上角形可辨？
交给 Art Director 跑 `measure.py` 复检。
