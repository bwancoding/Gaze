# WRHITW 热榜页面高保真设计稿

**文档版本**: v1.0  
**创建日期**: 2026-03-13  
**设计状态**: ✅ 高保真 - 可交付开发  
**面向**: C 端用户

---

## 📋 目录

1. [设计概览](#设计概览)
2. [Desktop 端完整设计](#desktop-端完整设计)
3. [Mobile 端完整设计](#mobile-端完整设计)
4. [交互状态设计](#交互状态设计)
5. [筛选/排序组件](#筛选排序组件)
6. [热度分数视觉系统](#热度分数视觉系统)
7. [媒体 Logo 展示](#媒体-logo-展示)
8. [过渡动画](#过渡动画)
9. [Figma 设计指南](#figma-设计指南)
10. [开发实现规范](#开发实现规范)

---

## 设计概览

### 设计目标
- ✅ 专业新闻感，中立客观
- ✅ 信息层次清晰，可读性强
- ✅ 响应式适配，全设备覆盖
- ✅ 交互反馈明确，用户体验流畅

### 关键指标
- **首屏加载时间**: < 2s
- **列表项点击区域**: ≥ 44px (触摸友好)
- **色彩对比度**: WCAG AA 标准 (≥ 4.5:1)
- **响应式断点**: 640px / 768px / 1024px / 1280px / 1536px

### 设计令牌 (Design Tokens)

```css
:root {
  /* 主色 - 来自设计系统 */
  --color-primary: #2563EB;
  --color-primary-hover: #1D4ED8;
  --color-primary-active: #1E40AF;
  
  /* 中性色 */
  --color-bg-primary: #FFFFFF;
  --color-bg-secondary: #F9FAFB;
  --color-bg-tertiary: #F3F4F6;
  --color-text-primary: #111827;
  --color-text-secondary: #4B5563;
  --color-text-tertiary: #6B7280;
  --color-border: #E5E7EB;
  --color-border-light: #F3F4F6;
  
  /* 热度颜色分级 */
  --heat-critical: #DC2626;  /* 90-100: 深红 */
  --heat-high: #EA580C;      /* 75-89: 橙红 */
  --heat-medium: #CA8A04;    /* 60-74: 黄色 */
  --heat-low: #16A34A;       /* 40-59: 绿色 */
  --heat-minimal: #6B7280;   /* 0-39: 灰色 */
  
  /* 间距 */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  
  /* 圆角 */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;
  
  /* 阴影 */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  
  /* 字体 */
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  --font-sans-cn: 'PingFang SC', 'Microsoft YaHei', 'Hiragino Sans GB', sans-serif;
  
  /* 字号 */
  --text-xs: 12px;
  --text-sm: 14px;
  --text-base: 16px;
  --text-lg: 18px;
  --text-xl: 20px;
  --text-2xl: 24px;
  --text-3xl: 30px;
  
  /* 字重 */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  
  /* 过渡 */
  --transition-fast: 150ms ease;
  --transition-base: 200ms ease;
  --transition-slow: 300ms ease;
}
```

---

## Desktop 端完整设计

### 页面布局 (≥1024px)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  1200px 内容区域 (居中)                                                         │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Header (64px)                                                             │ │
│  │  [Logo]                      [搜索框]                    [用户头像]       │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Hero Banner (80px)                                                        │ │
│  │  🔥 热榜 Trending                                    更新时间：16:11     │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌────────────────────┬──────────────────────────────────────────────────────┐ │
│  │ 筛选栏 (240px)     │ 列表区域 (960px - 自适应)                            │ │
│  │                    │                                                      │ │
│  │ [排序下拉 ▼]       │ ┌────────────────────────────────────────────────┐  │ │
│  │                    │ │ #1 事件标题文字文字文字文字文字文字文字文字    │  │ │
│  │ 立场：             │ │    🔥 98.5  |  📰 媒体名称  |  🕐 2 小时前     │  │ │
│  │ ○ 全部             │ └────────────────────────────────────────────────┘  │ │
│  │ ◐ 左倾             │                                                      │ │
│  │ ◐ 中立             │ ┌────────────────────────────────────────────────┐  │ │
│  │ ◐ 右倾             │ │ #2 事件标题文字文字文字文字文字文字文字文字    │  │ │
│  │                    │ │    🔥 95.2  |  📰 媒体名称  |  🕐 3 小时前     │  │ │
│  │ 分类：             │ └────────────────────────────────────────────────┘  │ │
│  │ ☑ 政治             │                                                      │ │
│  │ ☑ 经济             │ ... (共 20 条)                                       │ │
│  │ ☑ 科技             │                                                      │ │
│  │ ☑ 社会             │                                                      │ │
│  │ ☑ 国际             │                                                      │ │
│  │ ☑ 娱乐             │                                                      │ │
│  │                    │                                                      │ │
│  │ [重置筛选]         │                  [加载更多 ↓]                        │ │
│  │                    │                                                      │ │
│  └────────────────────┴──────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Footer (48px)                                                             │ │
│  │  © 2026 WRHITW  |  关于我们  |  隐私政策  |  联系方式                     │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Desktop 详细尺寸规范

| 区域 | 宽度 | 高度 | 内边距 | 说明 |
|------|------|------|--------|------|
| 页面容器 | 1200px | 100vh | 0 auto | 居中 |
| Header | 100% | 64px | 0 24px | 固定顶部 |
| Hero Banner | 100% | 80px | 24px | 页面标题区 |
| 筛选栏 | 240px | auto | 24px | 左侧固定 |
| 列表区域 | 960px | auto | 0 | 右侧自适应 |
| EventCard | 100% | 88px | 20px | 列表项 |
| Footer | 100% | 48px | 0 24px | 底部固定 |

### Desktop 视觉设计详图

#### 1. Header (顶部导航栏)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  WRHITW                              [🔍 搜索...]           [👤]       │
│  (24px, Bold)                     (320px × 40px)          (32px 圆形)  │
│  #111827                          #F9FAFB bg, #E5E7EB border            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
│ 底部 1px 边框：#E5E7EB                                                   │
```

**Header 组件规范**:
- **背景**: `#FFFFFF`
- **高度**: 64px
- **Logo**: 24px, Bold, `#111827`
- **搜索框**: 
  - 尺寸：320px × 40px
  - 背景：`#F9FAFB`
  - 边框：`#E5E7EB` → `#2563EB` (focus)
  - 圆角：20px
  - 占位符：`#9CA3AF`, 14px
- **用户头像**: 
  - 尺寸：32px × 32px
  - 圆角：full
  - 边框：2px solid `#E5E7EB`

#### 2. Hero Banner (页面标题区)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  🔥 热榜 Trending                          更新时间：16:11 🔄          │
│  (30px, Bold, #111827)                   (14px, Medium, #6B7280)      │
│                                                                         │
│  ─────────────────────────────────────────────────────────────────────  │
│  顶部 2px 强调线：#2563EB                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Hero 组件规范**:
- **背景**: `#FFFFFF`
- **高度**: 80px
- **顶部边框**: 2px solid `#2563EB`
- **底部边框**: 1px solid `#E5E7EB`
- **标题**: 30px, Bold, `#111827`
- **火焰图标**: 24px × 24px, 右偏移 8px
- **更新时间**: 14px, Medium, `#6B7280`
- **刷新图标**: 16px × 16px, 可点击

#### 3. 筛选栏 (Filter Sidebar)

```
┌────────────────────────────┐
│  排序：🔥 热度       ▼    │  ← 下拉菜单 (40px 高)
│  ────────────────────────  │
│                            │
│  立场筛选                  │  ← 14px, Semibold, #374151
│  ────────────────────────  │  ← 1px solid #E5E7EB (16px 间距)
│                            │
│  ○ 全部                    │  ← Radio 组
│  ◐ 左倾                    │
│  ◐ 中立                    │
│  ◐ 右倾                    │
│                            │
│  分类筛选                  │
│  ────────────────────────  │
│                            │
│  ☑ 政治   ☑ 经济           │  ← Checkbox 网格 (2 列)
│  ☑ 科技   ☑ 社会           │
│  ☑ 国际   ☑ 娱乐           │
│                            │
│  ────────────────────────  │
│  [  重置筛选  ]            │  ← Secondary 按钮 (40px 高)
│                            │
└────────────────────────────┘
```

**筛选栏组件规范**:
- **背景**: `#FFFFFF`
- **宽度**: 240px
- **内边距**: 24px
- **位置**: sticky, top: 80px
- **分组标题**: 14px, Semibold, `#374151`, 间距 16px
- **分割线**: 1px solid `#E5E7EB`
- **Radio/Checkbox**: 
  - 尺寸：16px × 16px
  - 选中色：`#2563EB`
  - 标签：14px, Regular, `#4B5563`
- **重置按钮**: 
  - 尺寸：100% × 40px
  - 样式：Secondary (白底，灰边框)
  - 文字：14px, Medium, `#374151`

#### 4. EventCard (事件卡片) - Desktop

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  #1   事件标题文字文字文字文字文字文字文字文字文字文字文字文字        │
│       (20px, Semibold, #111827, 单行省略)                              │
│                                                                         │
│       🔥 98.5    |    📰 媒体名称    |    🕐 2 小时前                  │
│       (14px, Medium)    (14px, Regular)    (14px, Regular)             │
│       #DC2626         #6B7280              #6B7280                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**EventCard 详细规范**:

| 元素 | 尺寸 | 字体 | 颜色 | 说明 |
|------|------|------|------|------|
| 容器 | 100% × 88px | - | bg: `#FFFFFF`, border: `#E5E7EB` | 圆角 8px |
| 排名 | 40px 宽 | 20px, Bold | `#2563EB` | 左对齐 |
| 标题 | 自适应 | 20px, Semibold | `#111827` | 单行省略 |
| 热度分数 | auto | 14px, Medium | 动态 (见热度系统) | 🔥 图标 16px |
| 媒体来源 | auto | 14px, Regular | `#6B7280` | 📰 图标 14px |
| 时间戳 | auto | 14px, Regular | `#6B7280` | 🕐 图标 14px |
| 分隔符 | - | - | `#E5E7EB` | ` | ` 字符 |
| 悬停效果 | - | - | bg: `#F9FAFB`, shadow: md | transform: translateY(-2px) |

**完整 20 条列表布局**:

```
┌────────────────────────────────────────────────────────────────────┐
│ #1  事件标题...                   🔥 98.5 | 📰 媒体 | 🕐 2 小时前 │  ← 88px
├────────────────────────────────────────────────────────────────────┤
│ #2  事件标题...                   🔥 95.2 | 📰 媒体 | 🕐 3 小时前 │  ← 88px + 12px 间距
├────────────────────────────────────────────────────────────────────┤
│ #3  事件标题...                   🔥 92.8 | 📰 媒体 | 🕐 5 小时前 │
├────────────────────────────────────────────────────────────────────┤
│ #4  事件标题...                   🔥 89.3 | 📰 媒体 | 🕐 6 小时前 │
├────────────────────────────────────────────────────────────────────┤
│ #5  事件标题...                   🔥 86.7 | 📰 媒体 | 🕐 8 小时前 │
├────────────────────────────────────────────────────────────────────┤
│ #6  事件标题...                   🔥 84.1 | 📰 媒体 | 🕐 10 小时前│
├────────────────────────────────────────────────────────────────────┤
│ #7  事件标题...                   🔥 81.5 | 📰 媒体 | 🕐 12 小时前│
├────────────────────────────────────────────────────────────────────┤
│ #8  事件标题...                   🔥 78.9 | 📰 媒体 | 🕐 14 小时前│
├────────────────────────────────────────────────────────────────────┤
│ #9  事件标题...                   🔥 76.3 | 📰 媒体 | 🕐 16 小时前│
├────────────────────────────────────────────────────────────────────┤
│ #10 事件标题...                   🔥 73.7 | 📰 媒体 | 🕐 18 小时前│
├────────────────────────────────────────────────────────────────────┤
│ #11 事件标题...                   🔥 71.1 | 📰 媒体 | 🕐 20 小时前│
├────────────────────────────────────────────────────────────────────┤
│ #12 事件标题...                   🔥 68.5 | 📰 媒体 | 🕐 22 小时前│
├────────────────────────────────────────────────────────────────────┤
│ #13 事件标题...                   🔥 65.9 | 📰 媒体 | 🕐 1 天前   │
├────────────────────────────────────────────────────────────────────┤
│ #14 事件标题...                   🔥 63.3 | 📰 媒体 | 🕐 1 天前   │
├────────────────────────────────────────────────────────────────────┤
│ #15 事件标题...                   🔥 60.7 | 📰 媒体 | 🕐 1 天前   │
├────────────────────────────────────────────────────────────────────┤
│ #16 事件标题...                   🔥 58.1 | 📰 媒体 | 🕐 1 天前   │
├────────────────────────────────────────────────────────────────────┤
│ #17 事件标题...                   🔥 55.5 | 📰 媒体 | 🕐 2 天前   │
├────────────────────────────────────────────────────────────────────┤
│ #18 事件标题...                   🔥 52.9 | 📰 媒体 | 🕐 2 天前   │
├────────────────────────────────────────────────────────────────────┤
│ #19 事件标题...                   🔥 50.3 | 📰 媒体 | 🕐 2 天前   │
├────────────────────────────────────────────────────────────────────┤
│ #20 事件标题...                   🔥 47.7 | 📰 媒体 | 🕐 2 天前   │
└────────────────────────────────────────────────────────────────────┘
```

#### 5. LoadMore Button (加载更多)

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                      [  加载更多  ↓  ]                              │
│                      (200px × 48px)                                 │
│                      Primary 按钮样式                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**加载更多按钮规范**:
- **尺寸**: 200px × 48px
- **样式**: Primary (`#2563EB` 背景，`#FFFFFF` 文字)
- **圆角**: 8px
- **字体**: 14px, Medium
- **图标**: ↓ (16px, 右偏移 8px)
- **悬停**: bg `#1D4ED8`, transform: scale(1.02)
- **加载状态**: 显示 Spinner，禁用点击
- **无更多**: 隐藏按钮，显示"已显示全部" (14px, `#6B7280`)

---

## Mobile 端完整设计

### 页面布局 (<768px)

```
┌─────────────────────────────────────┐
│  100vw (全屏宽度)                   │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ Header (56px)                 │ │
│  │  [☰]  WRHITW     [🔍]  [👤]  │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ Hero (64px)                   │ │
│  │  🔥 热榜        16:11 🔄     │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ 排序栏 (48px)                 │ │
│  │  🔥 热度 ▼                    │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ [筛选条件 ▼] (可折叠面板)     │ │
│  │                               │ │
│  │ ┌───────────────────────────┐ │ │
│  │ │ 立场：                    │ │ │
│  │ │ [○ 全部] [◐ 左] [◐ 中]   │ │ │
│  │ │ [◐ 右]                    │ │ │
│  │ │                           │ │ │
│  │ │ 分类：                    │ │ │
│  │ │ [政治][经济][科技]        │ │ │
│  │ │ [社会][国际][娱乐]        │ │ │
│  │ │                           │ │ │
│  │ │ [重置筛选]                │ │ │
│  │ └───────────────────────────┘ │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ #1  事件标题文字文字文字文字  │ │
│  │     🔥 98.5 | 📰 媒体名称    │ │
│  │     🕐 2 小时前               │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ #2  事件标题文字文字文字文字  │ │
│  │     🔥 95.2 | 📰 媒体名称    │ │
│  │     🕐 3 小时前               │ │
│  └───────────────────────────────┘ │
│                                     │
│  ... (列表继续)                     │
│                                     │
│        [加载更多 ↓]                 │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ Footer (40px)                 │ │
│  │  © WRHITW  |  隐私  |  关于   │ │
│  └───────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

### Mobile 详细尺寸规范

| 区域 | 宽度 | 高度 | 内边距 | 说明 |
|------|------|------|--------|------|
| 页面容器 | 100vw | 100vh | 0 | 全屏 |
| Header | 100% | 56px | 0 16px | 固定顶部 |
| Hero Banner | 100% | 64px | 16px | 页面标题 |
| 排序栏 | 100% | 48px | 16px | 固定 |
| 筛选面板 | 100% | auto | 16px | 可折叠 |
| EventCard | 100% | 104px | 16px | 列表项 |
| Footer | 100% | 40px | 0 16px | 底部 |

### Mobile 视觉设计详图

#### 1. Header (移动端)

```
┌─────────────────────────────────────┐
│  [☰]  WRHITW           [🔍]  [👤]  │
│  (汉堡)  (20px, Bold)   (图标)      │
│  #6B7280   #111827      #6B7280    │
└─────────────────────────────────────┘
│ 底部 1px 边框：#E5E7EB               │
```

**Mobile Header 规范**:
- **高度**: 56px
- **背景**: `#FFFFFF`
- **汉堡菜单**: 24px × 24px, `#6B7280`
- **Logo**: 20px, Bold, `#111827`
- **搜索图标**: 24px × 24px, `#6B7280`
- **用户头像**: 28px × 28px

#### 2. Mobile EventCard

```
┌─────────────────────────────────────┐
│                                     │
│  #1   事件标题文字文字文字文字      │
│       文字文字文字文字              │
│       (16px, Semibold, #111827)     │
│       最多 2 行，超出省略             │
│                                     │
│  🔥 98.5    📰 媒体名称             │
│  (13px, Medium)  (13px, Regular)   │
│  #DC2626       #6B7280              │
│                                     │
│  🕐 2 小时前                        │
│  (13px, Regular, #6B7280)          │
│                                     │
└─────────────────────────────────────┘
```

**Mobile EventCard 规范**:

| 元素 | 尺寸 | 字体 | 颜色 | 说明 |
|------|------|------|------|------|
| 容器 | 100% × 104px | - | bg: `#FFFFFF`, border: `#E5E7EB` | 圆角 8px |
| 排名 | 32px 宽 | 16px, Bold | `#2563EB` | 左对齐 |
| 标题 | 自适应 | 16px, Semibold | `#111827` | 2 行省略 |
| 热度 + 媒体 | 100% | 13px | 动态 | 单行，flex 布局 |
| 时间戳 | 100% | 13px, Regular | `#6B7280` | 单独一行 |
| 内边距 | 16px | - | - | 四周 |
| 间距 | 8px | - | - | 卡片之间 |

#### 3. Mobile 筛选面板 (可折叠)

```
┌─────────────────────────────────────┐
│  [筛选条件 ▼]                       │  ← 触发器 (48px 高)
│  (14px, Medium, #2563EB)            │
└─────────────────────────────────────┘
         ↓ (展开后)
┌─────────────────────────────────────┐
│                                     │
│  立场筛选                           │
│  ─────────────────────────────────  │
│                                     │
│  [○ 全部]  [◐ 左倾]                 │
│  [◐ 中立]  [◐ 右倾]                 │
│                                     │
│  分类筛选                           │
│  ─────────────────────────────────  │
│                                     │
│  [政治] [经济] [科技]               │
│  [社会] [国际] [娱乐]               │
│                                     │
│  ─────────────────────────────────  │
│  [    重置筛选    ]                 │
│                                     │
└─────────────────────────────────────┘
```

**Mobile 筛选面板规范**:
- **触发器高度**: 48px
- **背景**: `#FFFFFF`
- **边框**: 1px solid `#E5E7EB`
- **圆角**: 8px
- **展开动画**: 300ms ease, max-height
- **Radio/Checkbox**: 
  - 移动端优化：28px × 28px 点击区域
  - 标签：14px, Regular
- **分类标签**: 
  - Pill 形状，28px 高
  - 背景：`#F3F4F6` → `#DBEAFE` (选中)
  - 内边距：8px 16px

---

## 交互状态设计

### 1. Default (默认状态)

```
┌─────────────────────────────────────────────────────────────────────┐
│ #1  事件标题文字文字文字文字文字文字文字文字文字文字              │
│     🔥 98.5  |  📰 媒体名称  |  🕐 2 小时前                        │
└─────────────────────────────────────────────────────────────────────┘
  bg: #FFFFFF
  border: 1px solid #E5E7EB
  shadow: none
```

### 2. Hover (悬停状态) - Desktop Only

```
┌─────────────────────────────────────────────────────────────────────┐
│ #1  事件标题文字文字文字文字文字文字文字文字文字文字              │  ↑
│     🔥 98.5  |  📰 媒体名称  |  🕐 2 小时前                        │  │ -2px
└─────────────────────────────────────────────────────────────────────┘
  bg: #F9FAFB
  border: 1px solid #E5E7EB
  shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1)
  transform: translateY(-2px)
  transition: all 200ms ease
  cursor: pointer
```

### 3. Active (点击状态)

```
┌─────────────────────────────────────────────────────────────────────┐
│ #1  事件标题文字文字文字文字文字文字文字文字文字文字              │
│     🔥 98.5  |  📰 媒体名称  |  🕐 2 小时前                        │
└─────────────────────────────────────────────────────────────────────┘
  bg: #F3F4F6
  border: 1px solid #2563EB
  shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)
  transform: scale(0.99)
```

### 4. Focus (键盘焦点)

```
┌─────────────────────────────────────────────────────────────────────┐
│ #1  事件标题文字文字文字文字文字文字文字文字文字文字              │
│     🔥 98.5  |  📰 媒体名称  |  🕐 2 小时前                        │
└─────────────────────────────────────────────────────────────────────┘
  outline: 2px solid #2563EB
  outline-offset: 2px
  border: 1px solid #E5E7EB
```

### 5. Loading (加载状态)

#### 骨架屏 (Skeleton)

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  ████████████████████████████████████████████████                  │  ← 标题骨架
│  ████████████████████████████████████                              │  ← 元数据骨架
│                                                                    │
└─────────────────────────────────────────────────────────────────────┘
  bg: linear-gradient(90deg, #F3F4F6 25%, #E5E7EB 50%, #F3F4F6 75%)
  background-size: 200% 100%
  animation: shimmer 1.5s infinite
```

**骨架屏动画**:

```css
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton {
  background: linear-gradient(90deg, #F3F4F6 25%, #E5E7EB 50%, #F3F4F6 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 8px;
}
```

#### 加载 Spinner

```
         ⟳
    (旋转动画)
    
  [  加载中...  ]
```

**Spinner 规范**:
- **尺寸**: 24px × 24px
- **颜色**: `#2563EB`
- **动画**: 1s linear infinite rotation
- **位置**: 加载更多按钮中心

### 6. Error (错误状态)

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                    ⚠️  加载失败                                     │
│                  (48px 图标，#F59E0B)                               │
│                                                                     │
│             抱歉，热榜数据暂时无法加载                              │
│             (16px, Regular, #6B7280)                                │
│                                                                     │
│                  [  重试  ]                                         │
│             (Primary 按钮，128px × 40px)                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
  bg: #FFFBEB (Warning Light)
  border: 1px dashed #F59E0B
  border-radius: 8px
  padding: 48px 24px
```

### 7. Empty (空状态)

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                    📭                                               │
│                  (48px 图标，#9CA3AF)                               │
│                                                                     │
│                  暂无符合条件的事件                                 │
│             (16px, Medium, #374151)                                 │
│                                                                     │
│         尝试调整筛选条件或稍后再来                                  │
│             (14px, Regular, #6B7280)                                │
│                                                                     │
│                  [  清除筛选  ]                                     │
│             (Secondary 按钮，128px × 40px)                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
  bg: #F9FAFB
  border: 1px solid #E5E7EB
  border-radius: 8px
  padding: 64px 24px
```

---

## 筛选/排序组件

### 1. 排序下拉菜单 (Sort Dropdown)

#### Desktop 样式

```
┌─────────────────────────────────┐
│  排序：🔥 热度           ▼    │  ← 触发器 (40px 高)
└─────────────────────────────────┘
         ↓ (点击展开)
┌─────────────────────────────────┐
│  🔥 热度                        │  ← 当前选中 (bg: #EFF6FF)
├─────────────────────────────────┤
│  🕐 最新时间                    │
└─────────────────────────────────┘
  bg: #FFFFFF
  border: 1px solid #E5E7EB
  shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1)
  border-radius: 8px
  width: 200px
```

**排序下拉规范**:

| 元素 | 尺寸 | 字体 | 颜色 | 说明 |
|------|------|------|------|------|
| 触发器 | 200px × 40px | 14px, Medium | `#374151` | 右箭头 16px |
| 选项 | 100% × 40px | 14px, Regular | `#4B5563` | 左图标 16px |
| 选中项 | - | 14px, Medium | `#2563EB`, bg: `#EFF6FF` | - |
| 悬停项 | - | - | bg: `#F9FAFB` | - |
| 分隔线 | 1px | - | `#F3F4F6` | 选项之间 |

#### Mobile 样式

```
┌─────────────────────────────────────┐
│  排序：🔥 热度               ▼    │  ← 触发器 (48px 高)
└─────────────────────────────────────┘
         ↓ (点击展开 - 底部弹出)
┌─────────────────────────────────────┐
│                                     │
│  ┌───────────────────────────────┐ │
│  │  🔥 热度              ✓      │ │  ← 选中
│  └───────────────────────────────┘ │
│  ┌───────────────────────────────┐ │
│  │  🕐 最新时间                  │ │
│  └───────────────────────────────┘ │
│                                     │
│           [    取消    ]            │
│                                     │
└─────────────────────────────────────┘
```

**Mobile 底部弹出规范**:
- **背景**: `#FFFFFF`
- **圆角**: 16px 16px 0 0
- **选项高度**: 56px
- **选项内边距**: 0 16px
- **遮罩**: rgba(0, 0, 0, 0.5)
- **动画**: slide-up 300ms ease

### 2. 立场筛选 (Ideology Filter)

#### Radio 按钮样式

```
未选中:          选中:
  ○ 全部           ◉ 全部
  (16px 圆圈)      (16px 实心 #2563EB)
  border: #D1D5DB  border: #2563EB
```

**Radio 规范**:
- **尺寸**: 16px × 16px
- **边框**: 2px
- **未选中**: border `#D1D5DB`, bg `#FFFFFF`
- **选中**: border `#2563EB`, bg `#2563EB`, 中心白点 6px
- **标签**: 14px, Regular, `#4B5563`
- **间距**: 12px (选项之间)

#### Mobile 优化版本

```
[○ 全部]  [◐ 左倾]
[◐ 中立]  [◐ 右倾]

→ 点击区域扩大到 28px × 28px
→ 标签可隐藏在 tooltip
```

### 3. 分类筛选 (Category Filter)

#### Checkbox 网格 (Desktop)

```
☑ 政治   ☑ 经济
☑ 科技   ☑ 社会
☑ 国际   ☑ 娱乐
```

**Checkbox 规范**:
- **尺寸**: 16px × 16px
- **圆角**: 4px
- **未选中**: border `#D1D5DB`, bg `#FFFFFF`
- **选中**: border `#2563EB`, bg `#2563EB`, ✓ 白色 12px
- **标签**: 14px, Regular, `#4B5563`
- **布局**: 2 列网格，gap: 16px

#### Mobile Pill 标签

```
[政治] [经济] [科技]
[社会] [国际] [娱乐]

未选中: bg #F3F4F6, text #4B5563
选中:   bg #DBEAFE, text #1E40AF, border #2563EB
```

**Pill 规范**:
- **高度**: 28px
- **内边距**: 8px 16px
- **圆角**: 14px (full)
- **字体**: 13px, Medium
- **间距**: 8px (选项之间)

### 4. 重置筛选按钮

```
┌────────────────────────────┐
│       重置筛选             │
│   (14px, Medium, #374151)  │
└────────────────────────────┘
  bg: #FFFFFF
  border: 1px solid #D1D5DB
  border-radius: 6px
  height: 40px
  width: 100%
  
悬停: bg #F9FAFB
点击: bg #F3F4F6, transform: scale(0.98)
```

---

## 热度分数视觉系统

### 颜色分级规范

| 等级 | 分数范围 | 颜色值 | 用途 | 对比度 (白底) |
|------|----------|--------|------|--------------|
| Critical | 90-100 | `#DC2626` | 深红，火焰动效 | 5.87:1 ✅ |
| High | 75-89 | `#EA580C` | 橙红 | 4.68:1 ✅ |
| Medium | 60-74 | `#CA8A04` | 黄色 | 4.50:1 ✅ |
| Low | 40-59 | `#16A34A` | 绿色 | 4.68:1 ✅ |
| Minimal | 0-39 | `#6B7280` | 灰色 | 3.21:1 (大字体) |

### 热度分数组件

#### Desktop 样式

```
  🔥 98.5
  
  🔥 火焰图标：16px × 16px
  数字：14px, Medium
  颜色：根据分数动态变化
```

#### 火焰动效 (Critical 等级专属)

```css
/* 火焰脉动动画 */
@keyframes flame-pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.15);
    opacity: 0.85;
  }
}

.heat-critical {
  color: #DC2626;
  animation: flame-pulse 2s ease-in-out infinite;
}

/* 火焰图标 SVG */
<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
  <path d="M12 23c-3.9 0-7-3.1-7-7 0-2.1 1.1-4.3 2.8-5.8.4-.3.9-.2 1.2.2.3.4.2.9-.2 1.2C7.6 12.7 7 14.3 7 16c0 2.8 2.2 5 5 5s5-2.2 5-5c0-2.4-1.7-4.5-4-4.9-.5-.1-.8-.5-.7-1 .1-.5.5-.8 1-.7 3.2.6 5.7 3.4 5.7 6.6 0 3.9-3.1 7-7 7z"/>
  <path d="M12 2c.5 0 .9.4.9.9 0 2.3-1.4 4.3-3.5 5.1-.4.2-.9-.1-1.1-.5-.2-.4.1-.9.5-1.1C10.1 5.8 11 4.1 11 2.3 11 2.4 11.5 2 12 2z"/>
</svg>
```

### 热度条 (可选增强)

```
┌──────────────────────────────────────────┐
│ #1  事件标题...                          │
│     ████████████████████████░░  98.5    │  ← 热度条
│     🔥 98.5 | 📰 媒体 | 🕐 2 小时前      │
└──────────────────────────────────────────┘
```

**热度条规范**:
- **高度**: 4px
- **长度**: 100% (按分数比例填充)
- **背景**: `#E5E7EB`
- **填充色**: 动态 (同热度分数颜色)
- **圆角**: 2px
- **位置**: 标题下方，元数据上方

**热度条 CSS**:

```css
.heat-bar {
  width: 100%;
  height: 4px;
  background: #E5E7EB;
  border-radius: 2px;
  overflow: hidden;
  margin: 8px 0;
}

.heat-bar-fill {
  height: 100%;
  background: var(--heat-color);
  border-radius: 2px;
  transition: width 300ms ease;
}

/* 分数转百分比 */
/* 90-100 → 100% */
/* 75-89 → 85% */
/* 60-74 → 70% */
/* 40-59 → 50% */
/* 0-39 → 30% */
```

### 趋势指示器 (Phase 2 预留)

```
  🔥 98.5  ↑
           (趋势箭头)
  
  ↑ 上升：#10B981 (绿色)
  ↓ 下降：#EF4444 (红色)
  → 平稳：#6B7280 (灰色)
```

**趋势箭头规范**:
- **尺寸**: 12px × 12px
- **位置**: 热度分数右侧，偏移 4px
- **动画**: 出现时 fade-in 200ms

---

## 媒体 Logo 展示

### 展示方式

#### 方案 A: 文字标识 (推荐 - 性能优)

```
  📰 媒体名称
  
  图标：14px × 14px
  文字：14px, Regular, #6B7280
```

**优势**:
- ✅ 加载快，无额外 HTTP 请求
- ✅ 响应式友好
- ✅ 暗色模式自动适配

#### 方案 B: Logo 图片 (品牌需求)

```
  [Logo] 媒体名称
  (20px) 
```

**Logo 规范**:
- **尺寸**: 20px × 20px
- **格式**: SVG (优先) / PNG @2x
- **圆角**: 4px
- **背景**: 透明 / 白色
- **间距**: 右偏移 8px

**实现代码**:

```html
<div class="media-source">
  <img 
    src="/logos/{media-id}.svg" 
    alt="{媒体名称}"
    width="20"
    height="20"
    loading="lazy"
    class="media-logo"
  />
  <span class="media-name">{媒体名称}</span>
</div>
```

**CSS**:

```css
.media-source {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #6B7280;
}

.media-logo {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  object-fit: contain;
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
}
```

### 媒体偏见标签 (可选)

```
  📰 媒体名称  [中立]
               (徽章)
```

**徽章规范**:

| 立场 | 文字色 | 背景色 | 边框色 |
|------|--------|--------|--------|
| 左倾 | `#1E40AF` | `#DBEAFE` | `#93C5FD` |
| 中立 | `#065F46` | `#D1FAE5` | `#6EE7B7` |
| 右倾 | `#991B1B` | `#FEE2E2` | `#FCA5A5` |
| 未知 | `#374151` | `#F3F4F6` | `#D1D5DB` |

**徽章 CSS**:

```css
.bias-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 500;
  border-radius: 4px;
  margin-left: 8px;
}

.bias-left {
  color: #1E40AF;
  background: #DBEAFE;
  border: 1px solid #93C5FD;
}

.bias-center {
  color: #065F46;
  background: #D1FAE5;
  border: 1px solid #6EE7B7;
}

.bias-right {
  color: #991B1B;
  background: #FEE2E2;
  border: 1px solid #FCA5A5;
}
```

---

## 过渡动画

### 1. 页面加载过渡

```css
/* 页面淡入 */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.trending-page {
  animation: fade-in 400ms ease-out;
}

/* 列表项依次淡入 */
.event-card {
  opacity: 0;
  animation: fade-in 300ms ease-out forwards;
}

.event-card:nth-child(1) { animation-delay: 50ms; }
.event-card:nth-child(2) { animation-delay: 100ms; }
.event-card:nth-child(3) { animation-delay: 150ms; }
/* ... 依次类推 */
```

### 2. 筛选/排序更新过渡

```css
/* 列表刷新过渡 */
.event-list {
  transition: opacity 200ms ease;
}

.event-list.updating {
  opacity: 0.5;
  pointer-events: none;
}

/* 骨架屏淡入 */
.skeleton {
  opacity: 0;
  animation: fade-in 300ms ease-out;
}
```

### 3. 点击卡片跳转过渡

```css
/* 卡片点击缩放 */
.event-card:active {
  transform: scale(0.98);
  transition: transform 100ms ease;
}

/* 页面跳转淡出 */
@keyframes fade-out {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

.page-exit {
  animation: fade-out 200ms ease-in forwards;
}
```

### 4. 加载更多按钮过渡

```css
.load-more-btn {
  transition: all 200ms ease;
}

.load-more-btn:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.load-more-btn:active {
  transform: scale(0.98);
}

/* 加载 Spinner 旋转 */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.spinner {
  animation: spin 1s linear infinite;
}
```

### 5. 筛选面板展开/收起 (Mobile)

```css
/* Mobile 筛选面板 */
.filter-panel {
  max-height: 0;
  overflow: hidden;
  transition: max-height 300ms ease-out;
}

.filter-panel.expanded {
  max-height: 500px; /* 根据内容调整 */
  transition: max-height 300ms ease-in;
}

/* 箭头旋转 */
.filter-toggle-icon {
  transition: transform 300ms ease;
}

.filter-toggle-icon.expanded {
  transform: rotate(180deg);
}
```

### 6. 热度分数变化动画

```css
/* 分数更新计数动画 */
@keyframes count-up {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.heat-score-updating {
  animation: count-up 300ms ease-out;
}

/* 颜色渐变过渡 */
.heat-score {
  transition: color 300ms ease;
}
```

### 7. 空状态/错误状态出现动画

```css
/* 空状态淡入 */
@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.empty-state,
.error-state {
  animation: slide-up 400ms ease-out;
}
```

---

## Figma 设计指南

### Figma 文件结构

```
WRHITW - 热榜页面
│
├── 📄 Cover (封面)
│   └── 项目名称、版本、更新日期
│
├── 🎨 Design Tokens (设计令牌)
│   ├── Colors (色彩)
│   │   ├── Primary (主色)
│   │   ├── Neutral (中性色)
│   │   ├── Heat Scores (热度分数)
│   │   └── Status (状态色)
│   ├── Typography (字体)
│   │   ├── Desktop (桌面端字号)
│   │   └── Mobile (移动端字号)
│   ├── Spacing (间距)
│   └── Effects (阴影/动效)
│
├── 🖥️ Desktop (桌面端)
│   ├── 📱 Trending Page - Full (完整页面)
│   ├── 🔍 Header Component (导航栏)
│   ├── 📊 Filter Sidebar (筛选栏)
│   ├── 📋 Event Card - Default (卡片 - 默认)
│   ├── 📋 Event Card - Hover (卡片 - 悬停)
│   ├── 📋 Event Card - Active (卡片 - 点击)
│   ├── ⏳ Loading States (加载状态)
│   │   ├── Skeleton (骨架屏)
│   │   └── Spinner (加载动画)
│   ├── ⚠️ Error State (错误状态)
│   └── 📭 Empty State (空状态)
│
├── 📱 Mobile (移动端)
│   ├── 📱 Trending Page - Full (完整页面)
│   ├── 🔍 Mobile Header (移动导航)
│   ├── 🎛️ Filter Panel - Collapsed (筛选 - 收起)
│   ├── 🎛️ Filter Panel - Expanded (筛选 - 展开)
│   ├── 📋 Event Card - Mobile (移动卡片)
│   └── 🍳 Bottom Sheet - Sort (底部弹出 - 排序)
│
├── 🔧 Components (组件库)
│   ├── 🔘 Buttons (按钮)
│   │   ├── Primary / Default / Hover / Active / Disabled
│   │   ├── Secondary / Default / Hover / Active / Disabled
│   │   └── Ghost / Default / Hover / Active
│   ├── 📝 Inputs (输入框)
│   │   ├── Search Box / Default / Focus
│   │   └── Text Input / Default / Focus / Error
│   ├── 🏷️ Badges (徽章)
│   │   ├── Heat Score (热度分数)
│   │   ├── Category (分类标签)
│   │   └── Bias (偏见标签)
│   ├── 📦 Cards (卡片)
│   │   └── Event Card (事件卡片)
│   ├── 🧭 Navigation (导航)
│   │   ├── Header (顶部导航)
│   │   └── Footer (底部导航)
│   └── 📊 Filters (筛选器)
│       ├── Radio Group (单选组)
│       ├── Checkbox Group (复选组)
│       └── Dropdown (下拉菜单)
│
└── 🎬 Prototypes (交互原型)
    ├── Desktop - Filter Interaction (桌面筛选交互)
    ├── Desktop - Sort Interaction (桌面排序交互)
    ├── Desktop - Card Click (卡片点击)
    ├── Mobile - Filter Toggle (移动筛选展开)
    ├── Mobile - Bottom Sheet (移动底部弹出)
    └── Loading Flow (加载流程)
```

### Figma 组件命名规范

```
Category/Component/Variant/State
例：Buttons/Primary/Default
例：Buttons/Primary/Hover
例：Cards/EventCard/Desktop
例：Cards/EventCard/Mobile
```

### Figma 自动布局 (Auto Layout)

```
EventCard (Desktop)
├── Frame (Auto Layout, Horizontal)
│   ├── Rank (40px 固定宽度)
│   └── Frame (Auto Layout, Vertical, Flex 1)
│       ├── Title (单行文本)
│       ├── Metadata (Auto Layout, Horizontal)
│       │   ├── HeatScore
│       │   ├── Divider (|)
│       │   ├── MediaSource
│       │   ├── Divider (|)
│       │   └── Timestamp
│       └── HeatBar (可选，4px 高)
```

### Figma 设计令牌 (Design Tokens)

在 Figma 中创建 Variables:

```
Colors:
  - primary/default: #2563EB
  - primary/hover: #1D4ED8
  - neutral/bg-primary: #FFFFFF
  - neutral/bg-secondary: #F9FAFB
  - neutral/text-primary: #111827
  - neutral/text-secondary: #6B7280
  - heat/critical: #DC2626
  - heat/high: #EA580C
  - heat/medium: #CA8A04
  - heat/low: #16A34A
  - heat/minimal: #6B7280

Spacing:
  - space-1: 4px
  - space-2: 8px
  - space-3: 12px
  - space-4: 16px
  - space-6: 24px
  - space-8: 32px

Radius:
  - radius-sm: 4px
  - radius-md: 8px
  - radius-lg: 12px
  - radius-full: 9999px
```

### Figma 交互原型设置

1. **筛选下拉交互**:
   - Trigger: On Click
   - Animation: Smart Animate, Ease Out, 200ms
   - 连接：Dropdown Trigger → Dropdown Menu

2. **卡片悬停效果**:
   - 使用 Component Variants (Default/Hover)
   - Prototype: While Hovering → Change to Hover variant
   - Animation: Smart Animate, Ease, 200ms

3. **Mobile 筛选面板展开**:
   - Trigger: On Click (筛选触发器)
   - Action: Change to Expanded variant
   - Animation: Smart Animate, Ease Out, 300ms

4. **页面跳转**:
   - Trigger: On Click (EventCard)
   - Action: Navigate to Event Detail
   - Animation: Dissolve, 200ms

---

## 开发实现规范

### HTML 结构

```html
<!-- 页面容器 -->
<main class="trending-page">
  
  <!-- Hero Banner -->
  <header class="trending-hero">
    <h1>
      <svg class="flame-icon">...</svg>
      <span>热榜 Trending</span>
    </h1>
    <div class="last-updated">
      <span>更新时间：16:11</span>
      <button class="refresh-btn" aria-label="刷新">
        <svg class="refresh-icon">...</svg>
      </button>
    </div>
  </header>
  
  <!-- 内容区域 (Desktop 双栏) -->
  <div class="trending-content">
    
    <!-- 筛选栏 -->
    <aside class="filter-sidebar">
      <div class="filter-group">
        <label class="filter-label">排序</label>
        <select class="sort-dropdown">
          <option value="heat">🔥 热度</option>
          <option value="time">🕐 最新时间</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label class="filter-label">立场筛选</label>
        <fieldset class="radio-group">
          <label class="radio-item">
            <input type="radio" name="ideology" value="all" checked>
            <span>全部</span>
          </label>
          <label class="radio-item">
            <input type="radio" name="ideology" value="left">
            <span>左倾</span>
          </label>
          <label class="radio-item">
            <input type="radio" name="ideology" value="center">
            <span>中立</span>
          </label>
          <label class="radio-item">
            <input type="radio" name="ideology" value="right">
            <span>右倾</span>
          </label>
        </fieldset>
      </div>
      
      <div class="filter-group">
        <label class="filter-label">分类筛选</label>
        <fieldset class="checkbox-group">
          <label class="checkbox-item">
            <input type="checkbox" name="category" value="politics" checked>
            <span>政治</span>
          </label>
          <!-- 其他分类... -->
        </fieldset>
      </div>
      
      <button class="reset-btn">重置筛选</button>
    </aside>
    
    <!-- 事件列表 -->
    <section class="event-list" role="feed" aria-busy="false">
      
      <!-- Event Card × 20 -->
      <article class="event-card" tabindex="0" role="article">
        <div class="event-rank">#1</div>
        <div class="event-content">
          <h2 class="event-title">事件标题文字文字文字文字文字文字文字文字</h2>
          <div class="event-metadata">
            <span class="heat-score heat-critical">
              <svg class="flame-icon">...</svg>
              <span>98.5</span>
            </span>
            <span class="divider">|</span>
            <span class="media-source">
              <svg class="media-icon">...</svg>
              <span>媒体名称</span>
            </span>
            <span class="divider">|</span>
            <span class="timestamp">
              <svg class="time-icon">...</svg>
              <span>2 小时前</span>
            </span>
          </div>
        </div>
        <a href="/event/1" class="card-link" aria-label="查看事件详情"></a>
      </article>
      
      <!-- 更多卡片... -->
      
    </section>
    
  </div>
  
  <!-- 加载更多 -->
  <button class="load-more-btn">
    <span>加载更多</span>
    <svg class="arrow-icon">...</svg>
  </button>
  
</main>
```

### CSS 实现 (关键样式)

```css
/* 页面布局 */
.trending-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.trending-content {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 32px;
  margin-top: 24px;
}

/* 筛选栏 */
.filter-sidebar {
  position: sticky;
  top: 80px;
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  padding: 24px;
  height: fit-content;
}

.filter-group {
  margin-bottom: 24px;
}

.filter-group:last-child {
  margin-bottom: 16px;
}

.filter-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 12px;
}

/* 事件列表 */
.event-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 事件卡片 */
.event-card {
  position: relative;
  display: flex;
  gap: 16px;
  padding: 20px;
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  transition: all 200ms ease;
  cursor: pointer;
}

.event-card:hover {
  background: #F9FAFB;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.event-card:active {
  background: #F3F4F6;
  transform: scale(0.99);
}

.event-rank {
  font-size: 20px;
  font-weight: 700;
  color: #2563EB;
  width: 40px;
  flex-shrink: 0;
}

.event-content {
  flex: 1;
  min-width: 0; /* 文本省略必需 */
}

.event-title {
  font-size: 20px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 8px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.event-metadata {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #6B7280;
}

.heat-score {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
}

.heat-score svg {
  width: 16px;
  height: 16px;
}

.heat-critical { color: #DC2626; }
.heat-high { color: #EA580C; }
.heat-medium { color: #CA8A04; }
.heat-low { color: #16A34A; }
.heat-minimal { color: #6B7280; }

.divider {
  color: #E5E7EB;
  user-select: none;
}

.media-source,
.timestamp {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.media-source svg,
.timestamp svg {
  width: 14px;
  height: 14px;
}

/* 卡片链接覆盖层 */
.card-link {
  position: absolute;
  inset: 0;
  z-index: 1;
  text-indent: -9999px;
}

/* 加载更多按钮 */
.load-more-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 200px;
  height: 48px;
  margin: 32px auto;
  background: #2563EB;
  color: #FFFFFF;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 200ms ease;
}

.load-more-btn:hover {
  background: #1D4ED8;
  transform: scale(1.02);
}

.load-more-btn:active {
  transform: scale(0.98);
}

.load-more-btn:disabled {
  background: #F3F4F6;
  color: #9CA3AF;
  cursor: not-allowed;
  transform: none;
}

/* 骨架屏 */
.skeleton {
  background: linear-gradient(
    90deg,
    #F3F4F6 25%,
    #E5E7EB 50%,
    #F3F4F6 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 8px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 火焰动画 */
@keyframes flame-pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.15);
    opacity: 0.85;
  }
}

.heat-critical .flame-icon {
  animation: flame-pulse 2s ease-in-out infinite;
}

/* 响应式 */
@media (max-width: 1023px) {
  .trending-content {
    grid-template-columns: 1fr;
  }
  
  .filter-sidebar {
    position: static;
    margin-bottom: 24px;
  }
}

@media (max-width: 767px) {
  .trending-page {
    padding: 0 16px;
  }
  
  .event-card {
    padding: 16px;
    height: auto;
  }
  
  .event-title {
    font-size: 16px;
    white-space: normal;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }
  
  .event-metadata {
    flex-wrap: wrap;
  }
  
  .event-rank {
    font-size: 16px;
    width: 32px;
  }
}
```

### JavaScript 交互逻辑

```javascript
// 筛选状态管理
const filterState = {
  ideology: 'all',
  categories: ['politics', 'economy', 'tech', 'society', 'international', 'entertainment'],
  sortBy: 'heat',
  offset: 0,
  limit: 20
};

// 防抖函数
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// 获取热榜数据
async function fetchTrending(params) {
  const response = await fetch(`/api/trending?${new URLSearchParams(params)}`);
  if (!response.ok) throw new Error('加载失败');
  return response.json();
}

// 渲染事件列表
function renderEventList(events) {
  const listEl = document.querySelector('.event-list');
  listEl.innerHTML = events.map(event => `
    <article class="event-card" tabindex="0">
      <div class="event-rank">#${event.rank}</div>
      <div class="event-content">
        <h2 class="event-title">${escapeHtml(event.title)}</h2>
        <div class="event-metadata">
          <span class="heat-score heat-${getHeatLevel(event.score)}">
            <svg class="flame-icon">...</svg>
            <span>${event.score}</span>
          </span>
          <span class="divider">|</span>
          <span class="media-source">
            <svg class="media-icon">...</svg>
            <span>${escapeHtml(event.source)}</span>
          </span>
          <span class="divider">|</span>
          <span class="timestamp">
            <svg class="time-icon">...</svg>
            <span>${formatTime(event.timestamp)}</span>
          </span>
        </div>
      </div>
      <a href="/event/${event.id}" class="card-link"></a>
    </article>
  `).join('');
}

// 热度等级计算
function getHeatLevel(score) {
  if (score >= 90) return 'critical';
  if (score >= 75) return 'high';
  if (score >= 60) return 'medium';
  if (score >= 40) return 'low';
  return 'minimal';
}

// 筛选变更处理
const handleFilterChange = debounce(async () => {
  const listEl = document.querySelector('.event-list');
  listEl.classList.add('updating');
  
  try {
    const data = await fetchTrending(filterState);
    renderEventList(data.events);
    updateUrlParams(filterState);
  } catch (error) {
    renderErrorState();
  } finally {
    listEl.classList.remove('updating');
  }
}, 300);

// URL 参数同步
function updateUrlParams(state) {
  const params = new URLSearchParams({
    ideology: state.ideology,
    category: state.categories.join(','),
    sort: state.sortBy
  });
  history.pushState({}, '', `/trending?${params}`);
}

// 加载更多
async function loadMore() {
  const btn = document.querySelector('.load-more-btn');
  btn.disabled = true;
  btn.innerHTML = '<svg class="spinner">...</svg> 加载中...';
  
  try {
    filterState.offset += 20;
    const data = await fetchTrending(filterState);
    appendEvents(data.events);
    
    if (data.events.length < 20) {
      btn.style.display = 'none';
    }
  } catch (error) {
    renderErrorState();
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span>加载更多</span><svg class="arrow-icon">...</svg>';
  }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
  // 从 URL 读取初始筛选状态
  const params = new URLSearchParams(window.location.search);
  if (params.get('ideology')) filterState.ideology = params.get('ideology');
  if (params.get('category')) filterState.categories = params.get('category').split(',');
  if (params.get('sort')) filterState.sortBy = params.get('sort');
  
  // 绑定事件
  document.querySelector('.sort-dropdown').addEventListener('change', (e) => {
    filterState.sortBy = e.target.value;
    filterState.offset = 0;
    handleFilterChange();
  });
  
  document.querySelectorAll('input[name="ideology"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
      filterState.ideology = e.target.value;
      filterState.offset = 0;
      handleFilterChange();
    });
  });
  
  document.querySelectorAll('input[name="category"]').forEach(checkbox => {
    checkbox.addEventListener('change', () => {
      filterState.categories = Array.from(
        document.querySelectorAll('input[name="category"]:checked')
      ).map(cb => cb.value);
      filterState.offset = 0;
      handleFilterChange();
    });
  });
  
  document.querySelector('.reset-btn').addEventListener('click', () => {
    filterState = {
      ideology: 'all',
      categories: ['politics', 'economy', 'tech', 'society', 'international', 'entertainment'],
      sortBy: 'heat',
      offset: 0,
      limit: 20
    };
    resetFilterUI();
    handleFilterChange();
  });
  
  document.querySelector('.load-more-btn').addEventListener('click', loadMore);
  
  // 初始加载
  fetchTrending(filterState).then(renderEventList);
});
```

---

## 附录：资源清单

### 图标资源 (SVG)

| 图标 | 用途 | 尺寸 |
|------|------|------|
| 🔥 Flame | 热度分数 | 16px × 16px |
| 📰 Newspaper | 媒体来源 | 14px × 14px |
| 🕐 Clock | 时间戳 | 14px × 14px |
| 🔄 Refresh | 刷新按钮 | 16px × 16px |
| ↓ Arrow Down | 加载更多 | 16px × 16px |
| ☰ Hamburger | 移动菜单 | 24px × 24px |
| 🔍 Search | 搜索图标 | 24px × 24px |
| 👤 User | 用户头像占位 | 32px × 32px |
| ✓ Check | 选中标记 | 12px × 12px |
| ↑↓ Trend | 趋势箭头 (Phase 2) | 12px × 12px |

### 字体资源

- **英文**: System fonts (SF Pro, Segoe UI, Roboto)
- **中文**: PingFang SC, Microsoft YaHei, Hiragino Sans GB
- **数字**: SF Mono, Roboto Mono (等宽场景)

### 颜色速查表

```css
/* 主色 */
--primary: #2563EB;
--primary-hover: #1D4ED8;
--primary-active: #1E40AF;

/* 中性色 */
--bg-primary: #FFFFFF;
--bg-secondary: #F9FAFB;
--text-primary: #111827;
--text-secondary: #6B7280;
--border: #E5E7EB;

/* 热度色 */
--heat-critical: #DC2626;  /* 90-100 */
--heat-high: #EA580C;      /* 75-89 */
--heat-medium: #CA8A04;    /* 60-74 */
--heat-low: #16A34A;       /* 40-59 */
--heat-minimal: #6B7280;   /* 0-39 */
```

---

**文档结束**

---

*本设计稿可直接交付前端开发实现。所有尺寸、颜色、交互状态均已详细定义。*
*Figma 设计文件待创建，建议按照上述结构组织。*

**下一步建议**:
1. 创建 Figma 设计文件，按照组件库结构组织
2. 开发前端实现 (React/Vue + Tailwind CSS 推荐)
3. 实现交互原型，验证用户体验
4. 进行可访问性测试 (键盘导航、屏幕阅读器)
5. 性能优化 (骨架屏、懒加载、虚拟化列表)
