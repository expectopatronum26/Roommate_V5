# Violet Cloud — Roommate Finder Design System
*Version 1.0 | Light Mode Only*

---

## 0. 使用说明（给 AI 读的）

这是一份**设计操作手册**，不是代码文件。
每次生成或修改模板时，必须：
1. 以本文件的 Token 定义为唯一色彩/间距依据
2. 不得自行发明颜色、圆角、阴影
3. 响应式必须覆盖全部三档断点
4. 不实现系统级夜间模式（`prefers-color-scheme: dark` 不处理）

---

## 1. Visual Theme & Atmosphere

Violet Cloud 是一个服务港硕学生的室友匹配平台。
视觉目标：**轻盈、可信赖、有技术感但不冷漠。**

整体风格以柔和薰衣草渐变为氛围底色，白色画布承载操作内容，
紫色调作为唯一主品牌色，贯穿按钮、焦点态和关键交互。

**核心特征：**
- 暖白画布（`#FFFBFE`）+ 薰衣草紫色调（`#6750A4`）
- 柔和渐变仅用于 Hero、Section 氛围背景，不染 UI 组件
- 字体呈现现代几何感，展示级标题使用负字距
- 卡片投影带紫调，不用纯黑阴影
- 形状系统：小元素锐（4–8px），大容器适度圆（12–16px）
- 无夜间模式，无深色分区，全程浅色

---

## 2. Color System

### 2.1 CSS Custom Properties（命名规范）

AI 生成代码时，**必须使用以下变量名**，禁止直接写色值。

```css
/* ── Backgrounds ── */
--color-bg               /* #FFFBFE  页面底色，非纯白 */
--color-surface          /* #F3EDF7  卡片、面板底色 */
--color-surface-low      /* #E7E0EC  输入框、内凹区域 */

/* ── Primary ── */
--color-primary          /* #6750A4  主按钮、焦点环、激活态 */
--color-on-primary       /* #FFFFFF  Primary 上的文字 */
--color-primary-container/* #EADDFF  轻量强调区块背景 */

/* ── Secondary ── */
--color-secondary-container /* #E8DEF8  Chip、标签背景 */
--color-on-secondary-container /* #1D192B */

/* ── Accent ── */
--color-lavender-soft    /* #bdbbff  次级装饰、软高亮 */

/* ── Text ── */
--color-on-surface       /* #1C1B1F  主文字 */
--color-on-surface-variant /* #49454F  次级文字、图标、占位符 */

/* ── Borders ── */
--color-outline          /* #79747E  明显边框（输入框） */
--color-outline-subtle   /* rgba(0,0,0,0.08)  卡片轻边框 */

/* ── Gradient（仅装饰用）── */
--gradient-pastel: linear-gradient(135deg, #EAE4FF 0%, #E8DEF8 40%, #F0ECFF 100%)
```

### 2.2 色彩使用规则

| 场景 | 使用变量 | 禁止 |
|------|----------|------|
| 页面背景 | `--color-bg` | 纯白 `#fff` |
| 卡片背景 | `--color-surface` | 自定义灰色 |
| 输入框背景 | `--color-surface-low` | 白色输入框 |
| 主 CTA 按钮 | `--color-primary` | 其他紫色变体 |
| Chip / 筛选标签 | `--color-secondary-container` | Pill 之外形状（允许） |
| 装饰渐变 | `--gradient-pastel` | 将渐变用于按钮 |
| 阴影 | 见第 6 节 | `rgba(0,0,0,x)` 纯黑阴影 |

---

## 3. Typography

### 3.1 字体栈

```
展示 / 正文：'Plus Jakarta Sans', 'Noto Sans SC', sans-serif
技术标签 / Mono：'JetBrains Mono', 'IBM Plex Mono', monospace
```

> 中文内容由 Noto Sans SC 兜底，英文主视觉由 Plus Jakarta Sans 承担。
> 两者都是 Google Fonts 免费字体，无需付费许可。

### 3.2 字阶规范

| 角色 | Size (rem) | Weight | Letter-spacing | Line-height | 适用场景 |
|------|-----------|--------|----------------|-------------|----------|
| Display | 2.5rem / 40px | 500 | **-1.0px** | 1.10 | 页面 Hero 主标题 |
| H1 | 2rem / 32px | 500 | **-0.64px** | 1.15 | 页面级标题 |
| H2 | 1.75rem / 28px | 500 | **-0.42px** | 1.20 | Section 标题 |
| H3 | 1.375rem / 22px | 500 | **-0.22px** | 1.25 | 卡片标题 |
| Body L | 1.125rem / 18px | 400 | **-0.18px** | 1.55 | 描述文本 |
| Body | 1rem / 16px | 400 | **-0.16px** | 1.60 | 正文、按钮文字 |
| Caption | 0.875rem / 14px | 400 | 0 | 1.45 | 元数据、辅助说明 |
| Mono Label | 0.6875rem / 11px | 500 | **+0.055px** | 1.00 | 全大写区块标记 |

**铁律：**
- 展示类字体（Display ～ H3）永远使用负字距
- Mono Label 永远全大写（`text-transform: uppercase`）+ 正字距
- 正文 weight 范围：400–500，禁止 700+（Bold）

---

## 4. Shape System

```
--radius-xs:   4px    /* Badge、Mono Tag */
--radius-sm:   8px    /* Button、Input */
--radius-md:   12px   /* 卡片、容器（默认） */
--radius-lg:   16px   /* 大型面板、底部抽屉 */
--radius-pill: 9999px /* Chip、筛选标签 */
```

**规则：**
- 越小的元素越锐（4px），越大的容器越圆（12–16px）
- Chip 和 FAB 是唯一允许 Pill 形状的元素
- 禁止在静态矩形卡片上使用超过 16px 的圆角

---

## 5. Spacing System

基础单位：**8px**

```
4px   — 内部微间距（图标与文字间距）
8px   — 组件内 padding 基准
12px  — 紧凑型组件内边距
16px  — 标准组件内边距
20px  — 卡片内边距（移动端）
24px  — 卡片内边距（桌面端）
32px  — 组件间间距
48px  — Section 内部间距（最小值）
64px  — Section 间距（移动端）
80px  — Section 间距（桌面端）
```

**原则：**
- Section 垂直间距不得低于 48px
- 卡片内边距移动端 20px，桌面端 24px
- 表单字段间距统一 16px

---

## 6. Elevation & Shadow

**阴影统一带紫调，禁止纯黑**

| 层级 | 处理 | 使用场景 |
|------|------|----------|
| Level 0（Flat） | 无阴影，无边框 | 页面背景、纯文本块 |
| Level 1（Contained） | `1px solid rgba(0,0,0,0.08)` | 卡片、Badge 轻边框 |
| Level 2（Elevated） | `rgba(103,80,164,0.10) 0px 4px 12px` | 卡片 Hover、输入框聚焦 |
| Level 3（Floating） | `rgba(103,80,164,0.16) 0px 8px 24px` | Modal、Dropdown |

---

## 7. Components

### 7.1 Button

**Primary（主 CTA）**
- Background: `--color-primary`
- Text: `--color-on-primary`（白色）
- Radius: `--radius-sm`（8px）
- Padding: 10px 24px
- Hover: 亮度提升 8%（`filter: brightness(1.08)`）
- Focus: 3px offset `--color-primary` 轮廓环

**Secondary（次要操作）**
- Background: transparent
- Border: `1px solid --color-outline-subtle`
- Text: `--color-primary`
- Radius: `--radius-sm`

**Danger（删除/解绑）**
- Background: `#B3261E`（Material Error 色）
- Text: `#FFFFFF`
- Radius: `--radius-sm`
- 仅在确认删除场景使用

### 7.2 Card（房源卡片）

- Background: `#FFFFFF`（比页面底色亮一级）
- Border: `1px solid --color-outline-subtle`
- Radius: `--radius-md`（12px）
- Shadow: Level 2
- Padding: 移动端 20px / 桌面端 24px
- Hover: Shadow 升至 Level 2，轻微上移 `translateY(-2px)`，过渡 200ms

**房源图片区域：**
- 宽高比固定 `aspect-ratio: 4/3`
- `object-fit: cover`
- Radius 继承卡片顶部圆角，底部不圆

**卡片信息层级：**
1. 图片
2. Mono Label（楼盘类型 / 出租状态）
3. H3 标题（小区名/房型）
4. Body 描述（地区、价格区间）
5. Tag 组（配套设施 Chip）
6. 操作区（Primary Button）

### 7.3 Chip / Filter Tag

- Background: `--color-secondary-container`
- Text: `--color-on-secondary-container`
- Radius: `--radius-pill`
- Padding: 4px 12px
- Font: Body（14px），不大写
- 激活态：Background 换为 `--color-primary`，Text 换为白色

### 7.4 Badge / Mono Tag

- Background: `rgba(0,0,0,0.04)`
- Border: `1px solid --color-outline-subtle`
- Radius: `--radius-xs`（4px）——锐角，区别于 Chip
- Padding: 2px 8px
- Font: Mono Label（11px，全大写）
- 用于：房间类型标记（ENTIRE FLAT / ROOM）、状态标记（AVAILABLE）

### 7.5 Input / Form Field

- Background: `--color-surface-low`
- Border: `1px solid --color-outline`
- Radius: `--radius-sm`（8px）
- Padding: 12px 16px
- Placeholder: `--color-on-surface-variant`
- Focus: Border 变为 `--color-primary`，Shadow Level 2
- Error: Border 变为 `#B3261E`，下方显示红色 Caption

### 7.6 Navigation Bar（顶部）

- Background: `--color-bg`，底部 `1px solid --color-outline-subtle`
- 高度：移动端 56px / 桌面端 64px
- Logo：左对齐
- Nav Links：Body（16px），`--color-on-surface`
- 激活 Link：`--color-primary`，无下划线
- CTA Button：Primary 样式，右对齐
- 移动端：Nav Links 收入 Hamburger Menu

### 7.7 Section Label（Mono 区块标记）

- Font: Mono Label（11px，全大写，letter-spacing +0.055px）
- Color: `--color-on-surface-variant`
- 出现在各区块标题上方，作导航锚点
- 示例：`FEATURED LISTINGS` / `AI SEARCH` / `HOW IT WORKS`

### 7.8 AI 搜索助手区块

- 背景：`--gradient-pastel`（渐变仅此场景允许作背景）
- 容器：`--radius-lg`（16px），Shadow Level 2
- 输入框：白色底（`#FFFFFF`），与区块背景形成层次
- 提交按钮：Primary 样式
- 结果卡片：继承 7.2 Card 规范

---

## 8. Responsive Breakpoints

### 8.1 断点定义

| 档位 | 范围 | 典型设备 |
|------|------|----------|
| Mobile S | ≤ 374px | iPhone SE、小屏安卓 |
| Mobile | 375px – 767px | 主流手机竖屏 |
| Tablet | 768px – 1199px | iPad、大屏手机横屏 |
| Desktop | ≥ 1200px | 笔记本、显示器 |

**容器最大宽度：**
```
Mobile:  100%，左右 padding 16px
Tablet:  100%，左右 padding 32px
Desktop: max-width 1200px，居中
```

### 8.2 组件响应规则

**导航栏：**
- Mobile/Tablet：Hamburger Menu，点击展开全屏或侧滑抽屉
- Desktop：横向导航，全部链接可见

**房源卡片网格：**
- Mobile S：单列（1 column）
- Mobile：单列，卡片左右撑满减 32px
- Tablet：2 列（`grid-template-columns: repeat(2, 1fr)`）
- Desktop：3 列（`grid-template-columns: repeat(3, 1fr)`）

**筛选栏：**
- Mobile：横向滚动 Chip 行（`overflow-x: auto`，隐藏滚动条）
- Tablet：2 行 Chip 展示，"更多筛选"折叠
- Desktop：全部 Chip 可见，侧边栏或顶部横排

**表单（发帖页）：**
- Mobile：单列，全宽输入框
- Tablet：关键字段可 2 列排列（如：租金 + 面积同行）
- Desktop：主内容 + 右侧预览面板（2 列布局）

**Hero Section：**
- Mobile：Display 缩至 H1（32px），文字居中，无插图或插图下移
- Tablet：Display 40px，插图缩小右置
- Desktop：Display 40px，完整图文并排

**字体响应缩放：**
- Mobile：Display → 28px，H1 → 24px，其余不变
- Tablet：Display → 36px，H1 → 28px
- Desktop：按 3.2 字阶全量

**Touch Target 最小尺寸：**
- 所有可点击元素：最小 `44px × 44px`（含 padding）
- 移动端卡片整体可点击（不只是按钮）

**图片：**
- 房源图片：`aspect-ratio: 4/3`，`object-fit: cover`，`width: 100%`
- 上传预览：同比例，移动端单列，桌面端网格

---

## 9. Interaction & Motion

- Hover 过渡：`transition: all 200ms ease`（统一）
- 卡片 Hover：`translateY(-2px)` + Shadow 升级
- 按钮 Active：`scale(0.97)`，100ms
- 焦点环：`outline: 3px solid --color-primary; outline-offset: 2px`（所有可聚焦元素必须有）
- 页面加载：Skeleton Screen（骨架屏）优于 Spinner，用 `--color-surface` 填充

---

## 10. Do's and Don'ts

### ✅ 必须
- 页面背景使用 `#FFFBFE`，不用纯白
- 阴影带紫调 `rgba(103,80,164,x)`
- 展示字体使用负字距
- Mono Label 全大写
- 所有断点（Mobile S / Mobile / Tablet / Desktop）都处理
- Touch Target ≥ 44px
- 输入框聚焦有明显视觉反馈

### ❌ 禁止
- `background: #ffffff` 作页面底色
- 阴影用 `rgba(0,0,0,x)` 纯黑
- 圆角超过 16px 用于静态矩形卡片
- Pill 形状用于 Badge（Pill 只属于 Chip）
- 渐变用于按钮或输入框
- 字重使用 700+
- 只写桌面端样式，不处理移动端
- 实现 `prefers-color-scheme: dark`

---

## 11. Quick Color Reference（AI 速查）

```
页面背景:        #FFFBFE
卡片背景:        #F3EDF7
输入框背景:      #E7E0EC
主色 / CTA:     #6750A4
主色文字:        #FFFFFF
次级容器:        #E8DEF8
次级容器文字:    #1D192B
主文字:          #1C1B1F
次级文字:        #49454F
边框（明显）:    #79747E
边框（轻）:      rgba(0,0,0,0.08)
薰衣草装饰:      #bdbbff
装饰渐变:        linear-gradient(135deg, #EAE4FF, #E8DEF8, #F0ECFF)
卡片阴影:        rgba(103,80,164,0.10) 0px 4px 12px
```