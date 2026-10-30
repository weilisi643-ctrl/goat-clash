# 美术一致性检查报告 2026-10-29

范围：`/workspace/gc_repo/art`（分支 physics-v2-fixed-step）与 `/workspace/goat-game/art`（不含 `_v*` 旧版）。方法：`director/measure.py` 只读统计，原始数据 `director/measurements.json`。未修改任何素材或代码。

## 总体
- repo 与 goat-game/art 同名 PNG **md5 完全一致**（差异 0）。
- 尺寸：1152×1024 ×39、360×320 ×39，parts/ 全部为这两种；**尺寸异常 0**。fx 32/64/128/192 px 与 UI 9-slice 正常。
- 灰度层（wool/beard/horn/knee）彩色像素 = 0；单张素材绿色像素（G−max(R,B)>25）= 0 → 绿边只出现在**合成渲染后**。

## 已知问题量化
### P1 残余绿边 455 px（`docs/p13_green_fringe.json`）
修复前 fringe_green 808 → 修复后 **455**；小孔 pinholes 1176 → **734**。按 `p13_green_coords.json` 分布：
| 羊毛 | idle | jump | clash | 合计 |
|---|---|---|---|---|
| short | 206（horn 62、head 42、无部件 102）| **464**（无部件 412、body 52）| 12 | **682** |
| cloud | 182（body 112…）| 114 | 82 | **378** |
| fluffy | 29 | 30 | 8 | 67 |
| spots | 24 | 30 | 8 | 62 |
（coords 文件按 透绿+小孔 合并计数。）**short_jump 单帧占约 40%**，其中 412 px 不在任何部件之下 = 羊毛本身缺口。

### P2 短毛跳跃帧破洞
`wool/short_jump.png` 内部透明孔 9 个、共 **1384 px**；同姿态 `fluffy_jump.png` 只有 573 px → 多出 **811 px**。小图 `short_jump_320.png` 112 px vs fluffy 33 px。与 P1 的 412 px “无部件”透绿对应。

### P3 云朵羊毛边缘
`wool/cloud_idle.png` 半透明边缘像素 **10,007**，fluffy_idle 6,006（**+67%**）；内部孔 26 个/1,246 px（fluffy 6 个）。cloud_jump 7,606 vs 5,068（+50%），cloud_clash 7,995 vs 5,432（+47%）。渲染后 cloud 透绿 378 px，位于 body/tail/腿。→ 边缘雾化+碎孔。

### P4 腿部没有补丁
`art/parts/*/head_patch`、`tail_patch` 各 48 个文件，四个 leg_* 目录 **0 个 patch**。`wool/knee_*` 与“身体可见且无羊毛覆盖”区域重叠 = **0 px**（idle 裸露 2,026 px、jump 957、clash 1,488 全部没补丁），即膝补丁全落在羊毛下方、不可见。

## 其他发现
- P5 胡子小图可读性：`beard_*_320.png` 不透明像素仅 39–62，jump 最少（39）；手机上胡子接近消失。
- P6 spots_mask 大图半透明像素 182,025（idle）远多于不透明 61,975，且内部孔 117 个/11,650 px；小图孔 11 个 → 二色斑点会有麻点。
- P7 光源：羊毛/身体上亮下暗一致（fluffy 211/181，body 96/58）；羊角为右亮左暗（curl_idle 127/99），可接受但新角需统一“上沿高光”。
- P8 branch/curl 羊角内部孔 1,332 / 2,414 px —— 为造型本身的镂空（卷曲中心/分叉），确认属设计，非缺陷。
- P9 命名：规则统一；根目录有大量对比图（fix_compare_*、parts_joint_test_v*）与 `_v1…_v8d_pre` 历史目录混放，建议归档到 `_archive/`（需负责人同意）。
- UI：`ui_mock_v2` 实测色与 `js/theme.js` 完全一致（#CFFC98/#FFFFFF/#2F3727/#FCD800/#8CCB4E/#2E6FD8/#FF9E3D/#FF7A6B），无漂移。

## 优先级修复清单（全部只改画面，不动画布/锚点/帧数）
1. **short_jump 羊毛补洞**（P2→消除 P1 中 464 px，约 40% 残绿）。
2. **cloud 三帧边缘收紧**：半透明边缘降到 fluffy 水平（≤6k/帧），填碎孔（P3，−378 px）。
3. **四条腿补丁层**：为 leg_* 出 patch，覆盖裸腿 2,026/957/1,488 px（P4）。
4. short_idle 角根/头部 104 px 透绿（horn 62 + head 42）。
5. 胡子小图加粗到 ≥60 px（P5）。
6. spots_mask 去麻点（P6）。
7. 历史文件归档（P9，需同意）。
验收：重跑 p13 统计 fringe_green 目标 <100，`measure.py` 新图孔数不高于 fluffy 同帧。
