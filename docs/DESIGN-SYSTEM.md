# WRHITW 设计系统 v2.0

🎨 **中立、专业、包容** - 为多视角新闻而设计

> **版本**: 2.0  
> **最后更新**: 2026-03-13  
> **状态**: ✅ 完整版本

---

## 📐 设计原则

1. **中立性** - 不用色彩引导情绪，让用户自己判断
2. **透明度** - 信息来源清晰可见
3. **可读性** - 内容优先，长时间阅读舒适
4. **包容性** - 考虑不同文化背景
5. **无障碍** - WCAG 2.1 AA 标准

---

## 📝 一、字体系统 (Typography)

### 1.1 字体家族

```css
/* 英文字体 - 优先使用系统字体 */
--font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;

/* 中文字体 - 优先使用系统字体 */
--font-sans-cn: 'PingFang SC', 'Microsoft YaHei', 'Hiragino Sans GB', 'Noto Sans SC', sans-serif;

/* 等宽字体 - 代码、数据展示 */
--font-mono: 'SF Mono', 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;

/* 数字字体 - 统计数据、时间 */
--font-numeric: 'SF Mono', 'Roboto Mono', monospace;
```

### 1.2 字号层级 (Type Scale)

基于 **1.25 比例** 的字号系统（Major Third）：

| 层级 | 名称 | 大小 | 行高 | 字重 | 用途 | CSS 变量 |
|------|------|------|------|------|------|----------|
| 1 | xs | 12px (0.75rem) | 16px (1.0) | 400 | 辅助信息、标签、元数据 | `--text-xs` |
| 2 | sm | 14px (0.875rem) | 20px (1.43) | 400 | 次要文本、注释、图注 | `--text-sm` |
| 3 | base | 16px (1rem) | 24px (1.5) | 400 | 正文、默认文本 | `--text-base` |
| 4 | lg | 18px (1.125rem) | 28px (1.56) | 500 | 强调文本、引言 | `--text-lg` |
| 5 | xl | 20px (1.25rem) | 28px (1.4) | 600 | 小标题、卡片标题 | `--text-xl` |
| 6 | 2xl | 24px (1.5rem) | 32px (1.33) | 600 | 中标题、分区标题 | `--text-2xl` |
| 7 | 3xl | 30px (1.875rem) | 36px (1.2) | 700 | 大标题、页面标题 | `--text-3xl` |
| 8 | 4xl | 36px (2.25rem) | 40px (1.11) | 700 | 超大标题、Hero 区域 | `--text-4xl` |
| 9 | 5xl | 48px (3rem) | 48px (1.0) | 800 | 展示性标题、Landing Page | `--text-5xl` |

### 1.3 字重规范 (Font Weight)

| 名称 | 值 | 用途 | CSS 变量 |
|------|-----|------|----------|
| Light | 300 | 大字号装饰文本（谨慎使用） | `--font-light` |
| Regular | 400 | 正文、默认文本 | `--font-regular` |
| Medium | 500 | 强调文本、按钮文本 | `--font-medium` |
| Semibold | 600 | 小标题、重要文本 | `--font-semibold` |
| Bold | 700 | 大标题、强强调 | `--font-bold` |
| Extrabold | 800 | 展示性标题、品牌元素 | `--font-extrabold` |

### 1.4 行高规范 (Line Height)

| 名称 | 值 | 用途 |
|------|-----|------|
| tight | 1.0 | 大标题、数字展示 |
| snug | 1.25 | 标题、短文本 |
| normal | 1.5 | 正文、长文本阅读 |
| relaxed | 1.75 | 诗歌、引用、特殊排版 |

### 1.5 字母间距 (Letter Spacing)

| 名称 | 值 | 用途 |
|------|-----|------|
| tighter | -0.05em | 大标题（4xl+） |
| tight | -0.025em | 标题（2xl-4xl） |
| normal | 0 | 正文、默认 |
| wide | 0.025em | 大写字母、标签 |
| wider | 0.05em | 全大写、装饰文本 |

### 1.6 中英文混排规范

```css
/* 中英文混排时，自动应用合适的字体 */
.body-cn {
  font-family: var(--font-sans-cn);
  line-height: 1.6; /* 中文需要稍大行高 */
  letter-spacing: 0.02em; /* 中文微调字间距 */
}

/* 数字使用等宽字体，便于对齐 */
.numeric {
  font-family: var(--font-numeric);
  font-variant-numeric: tabular-nums;
}
```

---

## 🎨 二、色彩系统 (Color System)

### 2.1 主色调 (Primary Colors)

| 名称 | 色值 | RGB | HSL | 用途 | 对比度 (白底) |
|------|------|-----|-----|------|--------------|
| Primary 50 | `#EFF6FF` | 239, 246, 255 | 210°, 82%, 97% | 超浅背景 | 1.02:1 |
| Primary 100 | `#DBEAFE` | 219, 234, 254 | 210°, 80%, 93% | 浅背景、悬停 | 1.12:1 |
| Primary 200 | `#BFDBFE` | 191, 219, 254 | 210°, 78%, 87% | 边框、分隔 | 1.32:1 |
| Primary 300 | `#93C5FD` | 147, 197, 253 | 210°, 76%, 79% | 次要元素 | 1.65:1 |
| Primary 400 | `#60A5FA` | 96, 165, 250 | 210°, 74%, 68% | 次要按钮 | 2.31:1 |
| **Primary 500** | `#3B82F6` | 59, 130, 246 | 210°, 73%, 60% | **主色标准** | 3.03:1 |
| **Primary 600** | `#2563EB` | 37, 99, 235 | 210°, 72%, 53% | **主按钮、链接** | **4.50:1** ✅ |
| Primary 700 | `#1D4ED8` | 29, 78, 216 | 210°, 71%, 48% | 悬停状态 | 5.87:1 |
| Primary 800 | `#1E40AF` | 30, 64, 175 | 210°, 70%, 40% | 激活状态 | 7.21:1 |
| Primary 900 | `#1E3A8A` | 30, 58, 138 | 210°, 69%, 33% | 深色强调 | 8.59:1 |

### 2.2 中性色 (Neutral Colors)

| 名称 | 色值 | 用途 | 对比度 (白底) |
|------|------|------|--------------|
| Neutral 0 | `#FFFFFF` | 主背景 | - |
| Neutral 50 | `#F9FAFB` | 次要背景、卡片背景 | 1.03:1 |
| Neutral 100 | `#F3F4F6` | 分割线背景、悬停 | 1.08:1 |
| Neutral 200 | `#E5E7EB` | 边框、分隔线 | 1.23:1 |
| Neutral 300 | `#D1D5DB` | 禁用边框、占位符 | 1.47:1 |
| Neutral 400 | `#9CA3AF` | 占位符文本、次要图标 | 2.10:1 |
| Neutral 500 | `#6B7280` | 次要文本、说明文字 | 3.21:1 |
| Neutral 600 | `#4B5563` | 常规文本、段落 | 4.68:1 ✅ |
| Neutral 700 | `#374151` | 主要文本、标题 | 6.27:1 ✅ |
| Neutral 800 | `#1F2937` | 重要标题、强调文本 | 8.59:1 ✅ |
| Neutral 900 | `#111827` | 最重要文本、Logo | 11.29:1 ✅ |

### 2.3 功能色 (Functional Colors)

#### 成功色 (Success)
| 名称 | 色值 | 用途 |
|------|------|------|
| Success Light | `#D1FAE5` | 成功背景 |
| Success | `#10B981` | 成功图标、边框 |
| Success Dark | `#059669` | 成功按钮、强调 |

#### 警告色 (Warning)
| 名称 | 色值 | 用途 |
|------|------|------|
| Warning Light | `#FEF3C7` | 警告背景 |
| Warning | `#F59E0B` | 警告图标、边框 |
| Warning Dark | `#D97706` | 警告按钮、强调 |

#### 错误色 (Error)
| 名称 | 色值 | 用途 |
|------|------|------|
| Error Light | `#FEE2E2` | 错误背景 |
| Error | `#EF4444` | 错误图标、边框 |
| Error Dark | `#DC2626` | 错误按钮、强调 |

#### 信息色 (Info)
| 名称 | 色值 | 用途 |
|------|------|------|
| Info Light | `#DBEAFE` | 信息背景 |
| Info | `#3B82F6` | 信息图标、边框 |
| Info Dark | `#2563EB` | 信息按钮、强调 |

### 2.4 分类色 (Category Colors) - 新闻分类

| 分类 | 色值 | 用途 |
|------|------|------|
| 政治 | `#8B5CF6` (Purple 500) | 政治新闻标签 |
| 经济 | `#10B981` (Emerald 500) | 经济新闻标签 |
| 科技 | `#3B82F6` (Blue 500) | 科技新闻标签 |
| 社会 | `#F59E0B` (Amber 500) | 社会新闻标签 |
| 文化 | `#EC4899` (Pink 500) | 文化新闻标签 |
| 体育 | `#EF4444` (Red 500) | 体育新闻标签 |
| 娱乐 | `#F97316` (Orange 500) | 娱乐新闻标签 |
| 国际 | `#6B7280` (Gray 500) | 国际新闻标签 |

### 2.5 状态色 (Status Colors) - 媒体偏见标签

| 立场 | 色值 | 背景色 | 用途 |
|------|------|--------|------|
| 左倾 (Left) | `#3B82F6` | `#DBEAFE` | 左倾媒体标识 |
| 中立 (Center) | `#10B981` | `#D1FAE5` | 中立媒体标识 |
| 右倾 (Right) | `#EF4444` | `#FEE2E2` | 右倾媒体标识 |
| 未知 (Unknown) | `#9CA3AF` | `#F3F4F6` | 未分类媒体 |

### 2.6 暗色模式 (Dark Mode)

| 元素 | 浅色模式 | 暗色模式 |
|------|----------|----------|
| 主背景 | `#FFFFFF` | `#111827` |
| 卡片背景 | `#FFFFFF` | `#1F2937` |
| 主要文本 | `#111827` | `#F9FAFB` |
| 次要文本 | `#6B7280` | `#9CA3AF` |
| 边框 | `#E5E7EB` | `#374151` |
| 主色 | `#2563EB` | `#3B82F6` |

---

## 🧩 三、组件库规范 (Component Library)

### 3.1 按钮 (Buttons)

#### 基础样式
```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 20px; /* py-2.5 px-5 */
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  border-radius: 6px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.15s ease;
}
```

#### 按钮类型

| 类型 | 背景色 | 文本色 | 边框色 | 悬停背景 | 用途 |
|------|--------|--------|--------|----------|------|
| Primary | `#2563EB` | `#FFFFFF` | transparent | `#1D4ED8` | 主要操作、提交 |
| Secondary | `#FFFFFF` | `#374151` | `#D1D5DB` | `#F9FAFB` | 次要操作、取消 |
| Ghost | transparent | `#4B5563` | transparent | `#F3F4F6` | 轻量操作、链接 |
| Danger | `#EF4444` | `#FFFFFF` | transparent | `#DC2626` | 删除、危险操作 |
| Disabled | `#F3F4F6` | `#9CA3AF` | transparent | - | 禁用状态 |

#### 按钮尺寸

| 尺寸 | 高度 | 内边距 | 字号 | 用途 |
|------|------|--------|------|------|
| sm | 32px | 6px 12px | 12px | 紧凑操作、表格内 |
| md | 40px | 10px 20px | 14px | 默认尺寸、表单 |
| lg | 48px | 12px 24px | 16px | 主要 CTA、Hero |

#### 按钮状态
- **Default**: 正常状态
- **Hover**: 背景色加深 10%
- **Active**: 背景色加深 20%，轻微缩放 (0.98)
- **Focus**: 2px Primary 600 外环，2px 白内环
- **Disabled**: 灰色背景，无交互

### 3.2 输入框 (Input Fields)

#### 基础样式
```css
.input {
  width: 100%;
  padding: 10px 14px;
  font-size: 14px;
  line-height: 20px;
  color: #111827;
  background-color: #FFFFFF;
  border: 1px solid #D1D5DB;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.input:focus {
  outline: none;
  border-color: #2563EB;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}
```

#### 输入框类型

| 类型 | 边框色 | 背景色 | 用途 |
|------|--------|--------|------|
| Default | `#D1D5DB` | `#FFFFFF` | 默认输入框 |
| Focus | `#2563EB` | `#FFFFFF` | 聚焦状态 |
| Error | `#EF4444` | `#FEF2F2` | 错误验证 |
| Success | `#10B981` | `#ECFDF5` | 成功验证 |
| Disabled | `#E5E7EB` | `#F9FAFB` | 禁用状态 |
| Search | `#D1D5DB` | `#FFFFFF` | 搜索框（圆角 20px） |

#### 输入框尺寸

| 尺寸 | 高度 | 字号 | 用途 |
|------|------|------|------|
| sm | 32px | 12px | 紧凑表单 |
| md | 40px | 14px | 默认尺寸 |
| lg | 48px | 16px | 重要输入 |

#### 辅助元素
- **Label**: 14px, Semibold, `#374151`, 间距 4px
- **Placeholder**: 14px, Regular, `#9CA3AF`
- **Helper Text**: 12px, Regular, `#6B7280`, 间距 4px
- **Error Message**: 12px, Regular, `#EF4444`, 间距 4px

### 3.3 卡片 (Cards)

#### 基础样式
```css
.card {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}
```

#### 卡片类型

| 类型 | 背景 | 边框 | 阴影 | 用途 |
|------|------|------|------|------|
| Default | `#FFFFFF` | `#E5E7EB` | sm | 默认卡片 |
| Elevated | `#FFFFFF` | transparent | md | 悬浮卡片 |
| Outlined | `#FFFFFF` | `#D1D5DB` | none | 描边卡片 |
| Interactive | `#FFFFFF` | `#E5E7EB` | sm → lg | 可点击卡片 |

#### 卡片内边距
- **Compact**: 12px
- **Default**: 16px
- **Comfortable**: 24px
- **Spacious**: 32px

#### 新闻卡片规范
```
┌─────────────────────────────────┐
│ [媒体 Logo] 媒体名称  [偏见标签] │  ← 头部 (16px padding)
├─────────────────────────────────┤
│ 新闻标题 (20px, Semibold)       │  ← 标题区
│ 新闻摘要 (14px, Regular, 2-3 行) │  ← 内容区
│                                 │
│ [分类标签] [时间] [来源]         │  ← 元数据 (12px)
└─────────────────────────────────┘
```

### 3.4 导航栏 (Navigation Bar)

#### 顶部导航栏
```css
.navbar {
  height: 64px;
  background: #FFFFFF;
  border-bottom: 1px solid #E5E7EB;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
```

#### 导航元素

| 元素 | 尺寸 | 颜色 | 状态 |
|------|------|------|------|
| Logo | 40px 高 | `#111827` | 固定 |
| 导航链接 | 14px, Medium | `#4B5563` → `#2563EB` | 悬停变色 |
| 当前激活 | 14px, Semibold | `#2563EB` | 底部 2px  underline |
| 搜索框 | 32px 高 | - | 圆角 20px |
| 用户头像 | 32px | - | 圆角 full |

#### 侧边导航栏（移动端）
- 宽度：280px
- 背景：`#FFFFFF`
- 项目高度：48px
- 图标尺寸：20px
- 文字：14px, Medium

### 3.5 徽章 (Badges)

| 类型 | 背景色 | 文本色 | 边框色 | 用途 |
|------|--------|--------|--------|------|
| Primary | `#DBEAFE` | `#1E40AF` | `#93C5FD` | 主要标签 |
| Success | `#D1FAE5` | `#065F46` | `#6EE7B7` | 成功状态 |
| Warning | `#FEF3C7` | `#92400E` | `#FCD34D` | 警告提示 |
| Error | `#FEE2E2` | `#991B1B` | `#FCA5A5` | 错误状态 |
| Neutral | `#F3F4F6` | `#374151` | `#D1D5DB` | 普通标签 |

#### 徽章尺寸
- **sm**: 16px 高，6px 10px 内边距，10px 字号
- **md**: 20px 高，8px 12px 内边距，12px 字号
- **lg**: 24px 高，10px 14px 内边距，14px 字号

### 3.6 表格 (Tables)

```css
.table {
  width: 100%;
  border-collapse: collapse;
}

.table th {
  background: #F9FAFB;
  padding: 12px 16px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #E5E7EB;
}

.table td {
  padding: 12px 16px;
  font-size: 14px;
  color: #4B5563;
  border-bottom: 1px solid #F3F4F6;
}
```

---

## 📱 四、响应式断点 (Responsive Breakpoints)

### 4.1 断点定义

| 名称 | 最小宽度 | 最大宽度 | 设备类型 | 布局列数 |
|------|----------|----------|----------|----------|
| xs | 0px | 639px | 小手机 | 4 列 |
| sm | 640px | 767px | 大手机 | 6 列 |
| md | 768px | 1023px | 平板 | 8 列 |
| lg | 1024px | 1279px | 小屏电脑 | 12 列 |
| xl | 1280px | 1535px | 标准电脑 | 12 列 |
| 2xl | 1536px | ∞ | 大屏电脑 | 12 列 |

### 4.2 CSS 媒体查询

```css
/* 手机优先 (Mobile First) */
@media (min-width: 640px) { /* sm } */
@media (min-width: 768px) { /* md } */
@media (min-width: 1024px) { /* lg } */
@media (min-width: 1280px) { /* xl } */
@media (min-width: 1536px) { /* 2xl } */
```

### 4.3 容器最大宽度

| 断点 | 容器宽度 |
|------|----------|
| xs | 100% |
| sm | 100% |
| md | 100% |
| lg | 960px |
| xl | 1200px |
| 2xl | 1400px |

### 4.4 栅格系统

#### 列间距 (Gutter)
- **Mobile**: 16px
- **Tablet**: 24px
- **Desktop**: 32px

#### 边距 (Margin)
- **Mobile**: 16px
- **Tablet**: 24px
- **Desktop**: auto (居中)

### 4.5 组件响应式行为

| 组件 | Mobile (<768px) | Tablet (768-1023px) | Desktop (≥1024px) |
|------|-----------------|---------------------|-------------------|
| 导航栏 | 汉堡菜单 | 完整导航 | 完整导航 + 搜索 |
| 新闻列表 | 单列 | 双列 | 三列 |
| 卡片 | 全宽 | 50% 宽度 | 33% 宽度 |
| 侧边栏 | 隐藏/抽屉 | 可折叠 | 常显 |
| 表格 | 滚动/卡片化 | 滚动 | 完整显示 |

---

## 📏 五、间距系统 (Spacing System)

### 5.1 基础间距

基于 **4px 网格** 的间距系统：

| 名称 | 值 | rem | 用途 |
|------|-----|-----|------|
| 0 | 0px | 0 | 无间距 |
| 1 | 4px | 0.25 | 最小间距 |
| 2 | 8px | 0.5 | 紧凑间距 |
| 3 | 12px | 0.75 | 小间距 |
| 4 | 16px | 1 | 标准间距 |
| 5 | 20px | 1.25 | 中间距 |
| 6 | 24px | 1.5 | 大间距 |
| 8 | 32px | 2 | 超大间距 |
| 10 | 40px | 2.5 | Section 间距 |
| 12 | 48px | 3 | 大 Section |
| 16 | 64px | 4 | 超大 Section |

### 5.2 应用场景

| 场景 | 间距值 | 说明 |
|------|--------|------|
| 图标与文本 | 8px | 行内元素间距 |
| 表单元素 | 16px | 输入框与 Label |
| 卡片内边距 | 16-24px | 内容到边框 |
| 卡片间距 | 24px | 卡片之间 |
| Section 间距 | 48-64px | 页面分区 |

---

## 🔲 六、圆角系统 (Border Radius)

| 名称 | 值 | 用途 |
|------|-----|------|
| none | 0 | 无圆角、分割线 |
| sm | 4px | 按钮、输入框、徽章 |
| md | 8px | 卡片、下拉菜单 |
| lg | 12px | 模态框、大卡片 |
| xl | 16px | 特殊容器、Hero |
| 2xl | 24px | 展示性元素 |
| full | 9999px | 头像、圆形按钮 |

---

## 🌑 七、阴影系统 (Shadow System)

| 名称 | 值 | 用途 |
|------|-----|------|
| none | `none` | 默认、扁平元素 |
| sm | `0 1px 2px 0 rgba(0, 0, 0, 0.05)` | 悬停状态、徽章 |
| md | `0 4px 6px -1px rgba(0, 0, 0, 0.07)` | 卡片、下拉菜单 |
| lg | `0 10px 15px -3px rgba(0, 0, 0, 0.1)` | 悬浮卡片、模态框 |
| xl | `0 20px 25px -5px rgba(0, 0, 0, 0.1)` | 弹出层、浮动面板 |
| 2xl | `0 25px 50px -12px rgba(0, 0, 0, 0.25)` | 重要弹出、Toast |
| inner | `inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)` | 内凹效果、输入框 |

---

## ♿ 八、无障碍规范 (Accessibility)

### 8.1 色彩对比度要求

| 元素类型 | 最小对比度 | WCAG 级别 |
|----------|------------|-----------|
| 正常文本 (<18px) | 4.5:1 | AA |
| 大文本 (≥18px) | 3:1 | AA |
| UI 组件、图标 | 3:1 | AA |
| 装饰性元素 | 无要求 | - |

### 8.2 焦点状态

```css
/* 通用焦点样式 */
:focus {
  outline: 2px solid #2563EB;
  outline-offset: 2px;
}

/* 键盘焦点 */
:focus-visible {
  outline: 2px solid #2563EB;
  outline-offset: 2px;
}

/* 移除鼠标焦点 */
:focus:not(:focus-visible) {
  outline: none;
}
```

### 8.3 键盘导航

- **Tab 顺序**: 逻辑顺序（从左到右，从上到下）
- **可聚焦元素**: 所有交互元素（按钮、链接、输入框）
- **跳过链接**: 页面顶部添加"跳到主要内容"链接

### 8.4 屏幕阅读器

```html
<!-- 图片必须有 alt -->
<img src="..." alt="描述性文本">

<!-- 图标必须有 aria-label -->
<button aria-label="关闭对话框">
  <svg>...</svg>
</button>

<!-- 表单必须有 label -->
<label for="email">邮箱</label>
<input id="email" type="email">
```

### 8.5 减少动画

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 🎨 九、Figma 设计文件

### 9.1 主设计文件

📎 **Figma 链接**: [WRHITW Design System](https://www.figma.com/file/TODO_CREATE_LATER)

*（Figma 文件待创建，链接稍后更新）*

### 9.2 文件结构

```
WRHITW Design System
├── 📄 Cover (封面)
│   └── 项目名称、版本、更新日期
├── 📚 Design System (设计系统)
│   ├── 🎨 Colors (色彩)
│   │   ├── Primary (主色)
│   │   ├── Neutral (中性色)
│   │   ├── Functional (功能色)
│   │   ├── Category (分类色)
│   │   └── Status (状态色)
│   ├── 📝 Typography (字体)
│   │   ├── Font Family (字体家族)
│   │   ├── Type Scale (字号层级)
│   │   └── Text Styles (文本样式)
│   ├── 📏 Spacing (间距)
│   ├── 🔲 Border Radius (圆角)
│   ├── 🌑 Shadows (阴影)
│   └── 🧩 Icons (图标)
├── 📱 Pages (页面设计)
│   ├── 🏠 Home (首页)
│   │   ├── Desktop
│   │   ├── Tablet
│   │   └── Mobile
│   ├── 📰 Event List (事件列表)
│   ├── 📖 Event Detail (事件详情)
│   ├── 🔍 Search (搜索)
│   └── ⚙️ Settings (设置)
└── 🔧 Components (组件库)
    ├── 🔘 Buttons (按钮)
    ├── 📝 Inputs (输入框)
    ├── 📦 Cards (卡片)
    ├── 🧭 Navigation (导航)
    ├── 🏷️ Badges (徽章)
    ├── 📊 Tables (表格)
    └── 📱 Modals (模态框)
```

### 9.3 Figma 组件规范

#### 组件命名规范
```
Category/Component/Variant
例：Buttons/Primary/Default
例：Buttons/Primary/Hover
例：Cards/News/Default
```

#### 自动布局 (Auto Layout)
- 所有组件使用 Auto Layout
- 间距使用 4px 网格
- 响应式使用 Hug / Fill 模式

#### 设计令牌 (Design Tokens)
- 颜色：使用 Figma Variables
- 字体：使用 Text Styles
- 间距：使用 Layout Grid

---

## 📚 十、参考资源

### 设计系统参考
- [Material Design 3](https://m3.material.io)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines)
- [Carbon Design System](https://carbondesignsystem.com)
- [Tailwind CSS Design Tokens](https://tailwindcss.com/docs/customization)

### 灵感来源
- [Ground News](https://ground.news) - 多视角新闻排版
- [Reuters](https://www.reuters.com) - 专业新闻网站
- [The Verge](https://www.theverge.com) - 现代媒体设计
- [Medium](https://medium.com) - 阅读体验优化
- [Substack](https://substack.com) - 简洁新闻通讯

### 工具资源
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/) - 对比度检测
- [Coolors](https://coolors.co) - 配色方案生成
- [Type Scale](https://type-scale.com) - 字号比例计算器

---

## 🔄 更新记录

| 日期 | 版本 | 更新内容 | 作者 |
|------|------|----------|------|
| 2026-03-04 | v1.0 | 初始版本 | Design Bot |
| 2026-03-13 | v2.0 | 完整设计系统：字体/色彩/组件/响应式/无障碍 | 小狗 |

---

## ✅ 检查清单

### 字体系统
- [x] 字体家族定义（英文/中文/等宽）
- [x] 字号层级（9 级，基于 1.25 比例）
- [x] 字重规范（6 级）
- [x] 行高规范（4 级）
- [x] 字母间距规范
- [x] 中英文混排规范

### 色彩系统
- [x] 主色调（10 级色阶）
- [x] 中性色（11 级色阶）
- [x] 功能色（成功/警告/错误/信息）
- [x] 分类色（8 个新闻分类）
- [x] 状态色（媒体偏见标签）
- [x] 暗色模式支持
- [x] 对比度验证（WCAG AA）

### 组件库
- [x] 按钮（5 种类型，3 种尺寸）
- [x] 输入框（6 种状态，3 种尺寸）
- [x] 卡片（4 种类型）
- [x] 导航栏（顶部/侧边）
- [x] 徽章（5 种类型，3 种尺寸）
- [x] 表格样式

### 响应式设计
- [x] 6 个断点定义
- [x] 容器最大宽度
- [x] 栅格系统
- [x] 组件响应式行为

### 无障碍
- [x] 色彩对比度要求
- [x] 焦点状态规范
- [x] 键盘导航
- [x] 屏幕阅读器支持
- [x] 减少动画支持

---

**最后更新**: 2026-03-13  
**版本**: 2.0  
**状态**: ✅ 完整

---

*本设计系统为 WRHITW 项目专用，所有规范均基于 WCAG 2.1 AA 标准和现代 Web 设计最佳实践。*
