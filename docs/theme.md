# UI 主题字段说明（js/theme.js）

所有按钮、面板、标题和文字都经 js/ui.js 的统一函数绘制：`drawButton` / `drawPanel` / `drawText` / `drawBg`，绘制时读取 `js/theme.js`。
换美术样稿时，只改 `js/theme.js` 和 `art/ui/` 下的资源，不改绘制代码。主题只影响画面，不影响物理、逻辑和按钮命中区。
`tools/theme_demo.py` 在运行时改用纯色、描边和阴影主题，效果见 `screenshots/p12_05_theme_solid_demo.png`。

## colors
| 字段 | 说明 | 默认 |
|---|---|---|
| skyTop / skyBottom | 背景天空的上下渐变色 | #bfe9ff / #fff6d8 |
| ground / groundY | 地面颜色；地面起点（屏幕高度比例） | #8fd17a / 0.72 |
| text | 系统字体文字的默认颜色 | #333333 |
| title | 设了颜色：所有标题统一用此色；null：用调用处传入的颜色 | null |
| buttonDefault | 调用处没给颜色时的按钮色 | #ffb347 |
| buttonText | 按钮用系统字体回退时的文字颜色 | #4a2c00 |

## font
| 字段 | 说明 | 默认 |
|---|---|---|
| family / weight | 系统字体（位图缺字或关闭时使用） | sans-serif / bold |
| bitmap.enabled | 是否启用位图字体 | true |
| bitmap.atlas | 图集描述 JSON，由 tools/gen_ui_assets.py 生成 | art/ui/font.json |
| bitmap.titleStyle / titleColorStyle / bodyStyle | 图集里的样式名：标题默认配色 / 可乘色的标题蒙版 / 正文与按钮 | title / title_mask / btn |
| bitmap.titleMinSize / bodyMinSize | 字号阈值：≥titleMinSize 用标题位图；≥bodyMinSize 用正文位图；更小用系统字体 | 18 / 16 |
| bitmap.emojiScale | 混排时 emoji 相对字号的比例（emoji 用系统字体绘制，与字形视觉中心对齐） | 0.9 |

位图字体用 Noto Sans CJK SC Bold 生成，许可为 SIL OFL 1.1，见 `art/ui/OFL.txt`。
如果整串文字里有图集没有的字（emoji 除外），这一串整体回退到系统字体。新增文案后，重跑 `python3 tools/gen_ui_assets.py`。
更换字体时，改 gen_ui_assets.py 里的 FONT 和 STY（字号、描边、渐变色），并确认新字体的许可。

## button / panel
| 字段 | 说明 | 默认（button / panel） |
|---|---|---|
| style | `nine`：九宫格贴图乘色；`solid`：纯色圆角 | nine / nine |
| image / slice | 九宫格贴图和切片边宽（贴图像素）；贴图用灰度，运行时乘按钮色 | art/ui/btn9.png, 20 / art/ui/panel9.png, 20 |
| brightness | 仅 button：乘色前的提亮倍数，补偿灰度贴图带来的变暗 | 1.07 |
| tint / fill / alpha | 仅 panel：九宫格乘色 / solid 填充色 / 不透明度 | #fff8e8 / rgba(255,255,255,0.85) / 0.92 |
| radius | solid 风格的圆角（九宫格加载失败回退时也用它） | 12 / 10 |
| stroke.width / color | 描边，0 为不描边 | 0 |
| shadow.color / blur / offsetY | 投影，blur 和 offsetY 都为 0 时不画 | 无 |
| fontSize / fontSizeRatio | 仅 button：文字字号 = min(fontSize, 按钮高 × ratio) | 16 / 0.42 |
| textOffsetY / sysTextOffsetY | 仅 button：位图文字 / 系统字体文字的竖直微调（像素） | -1 / -1 |

## motion（tween.js，场景切换时）
- titlePopFrom / titlePopMs / titleEasing：标题弹出。默认 0.6 / 380 / Back.Out。
- fadeMs / fadeEasing：按钮和面板淡入。默认 260 / Quadratic.Out。
- buttonRise / buttonMinAlpha / panelMinAlpha：按钮上浮距离和起始不透明度。默认 10 / 0.25 / 0.3。
- 缓动名用 tween.js 的 Easing 写法 `组.方式`，例如 `Elastic.Out`、`Linear.None`。

## spacing
- screenPad 16、gap 8、rowGap 48：布局间距令牌。
- 当前各界面布局仍是 main.js 里的坐标，这些令牌是给新样稿布局用的。重做布局时按令牌改写对应的 draw* 函数。

## effects（强度，默认克制）
- vignette：暗角。color 为 RGB 三元组，alpha 为边缘最大不透明度；inner / outer 是相对屏幕尺寸的内外半径。默认 0.10 / 0.5 / 0.8。
- factionTint：擂主相关画面的阵营色调。alpha 为全屏薄色调，topAlpha / topHeight 为顶部色带；colors 为各牧场 id 对应的颜色。默认 0.05 / 0.22 / 0.22。界面上只显示牧场名。
- impactGlow：撞击光晕。ms 为时长，alpha 为强度；半径 = radius + grow × 进度 + powerRadius × 撞击力度；burstAlpha / burstSize 控制 spark_burst 星爆贴图。默认 220 / 0.55 / 26 / 46 / 20 / 0.8 / 80。
- 每项都有 `enabled`，设为 false 即关闭。`js/visual_config.js` 只是兼容入口，实际数值在 theme.effects。

## 不在主题内（后续可扩展）
顶顶乐场地的配色、血条、蓄力条、瞄准线目前仍写在 main.js 的绘制代码里。
