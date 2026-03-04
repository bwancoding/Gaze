# WRHITW 设计系统

🎨 **中立、专业、包容** - 为多视角新闻而设计

---

## 📐 设计原则

1. **中立性** - 不用色彩引导情绪，让用户自己判断
2. **透明度** - 信息来源清晰可见
3. **可读性** - 内容优先，长时间阅读舒适
4. **包容性** - 考虑不同文化背景
5. **无障碍** - WCAG 2.1 AA 标准

---

## 🎨 色彩系统

### 主色调

| 名称 | 值 | 用途 |
|------|-----|------|
| Primary Blue | `#2563EB` | 主按钮、链接、强调 |
| Neutral Gray | `#6B7280` | 次要文本、边框 |

### 功能色

| 名称 | 值 | 用途 |
|------|-----|------|
| Success | `#10B981` | 成功状态 |
| Warning | `#F59E0B` | 警告提示 |
| Error | `#EF4444` | 错误状态 |
| Info | `#3B82F6` | 信息提示 |

### 中性色

| 名称 | 值 | 用途 |
|------|-----|------|
| White | `#FFFFFF` | 背景 |
| Gray 50 | `#F9FAFB` | 次要背景 |
| Gray 100 | `#F3F4F6` | 分割线 |
| Gray 200 | `#E5E7EB` | 边框 |
| Gray 300 | `#D1D5DB` | 禁用边框 |
| Gray 400 | `#9CA3AF` | 占位符文本 |
| Gray 500 | `#6B7280` | 次要文本 |
| Gray 600 | `#4B5563` | 常规文本 |
| Gray 700 | `#374151` | 主要文本 |
| Gray 800 | `#1F2937` | 标题 |
| Gray 900 | `#111827` | 重要标题 |

### 偏见标签色

| 立场 | 值 | 用途 |
|------|-----|------|
| Left | `#3B82F6` | 左倾媒体标识 |
| Center | `#10B981` | 中立媒体标识 |
| Right | `#EF4444` | 右倾媒体标识 |

---

## 📝 字体系统

### 字体家族

```css
/* 英文字体 */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* 中文字体 */
--font-sans-cn: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;

/* 等宽字体 */
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

### 字号规范

| 名称 | 大小 | 行高 | 用途 |
|------|------|------|------|
| xs | 12px | 16px | 辅助信息、标签 |
| sm | 14px | 20px | 次要文本、注释 |
| base | 16px | 24px | 正文 |
| lg | 18px | 28px | 强调文本 |
| xl | 20px | 28px | 小标题 |
| 2xl | 24px | 32px | 中标题 |
| 3xl | 30px | 36px | 大标题 |
| 4xl | 36px | 40px | 页面标题 |

### 字重

| 名称 | 值 | 用途 |
|------|-----|------|
| Regular | 400 | 正文 |
| Medium | 500 | 强调文本 |
| Semibold | 600 | 小标题 |
| Bold | 700 | 大标题 |

---

## 📏 间距系统

基于 **8px 网格** 的间距系统：

| 名称 | 值 | 用途 |
|------|-----|------|
| 1 | 4px | 最小间距（图标和文本） |
| 2 | 8px | 紧凑间距 |
| 3 | 12px | 小间距 |
| 4 | 16px | 标准间距 |
| 6 | 24px | 中间距 |
| 8 | 32px | 大间距 |
| 12 | 48px | 超大间距 |
| 16 | 64px | section 间距 |

---

## 🔲 圆角规范

| 名称 | 值 | 用途 |
|------|-----|------|
| sm | 4px | 按钮、输入框 |
| md | 8px | 卡片、下拉菜单 |
| lg | 12px | 模态框、大卡片 |
| xl | 16px | 特殊容器 |
| full | 9999px | 头像、徽章 |

---

## 🌑 阴影规范

| 名称 | 值 | 用途 |
|------|-----|------|
| sm | `0 1px 2px 0 rgba(0, 0, 0, 0.05)` | 悬停状态 |
| md | `0 4px 6px -1px rgba(0, 0, 0, 0.07)` | 卡片 |
| lg | `0 10px 15px -3px rgba(0, 0, 0, 0.1)` | 下拉菜单 |
| xl | `0 20px 25px -5px rgba(0, 0, 0, 0.1)` | 模态框 |
| 2xl | `0 25px 50px -12px rgba(0, 0, 0, 0.25)` | 弹出层 |

---

## 🧩 组件规范

### 按钮

| 类型 | 背景色 | 文本色 | 用途 |
|------|--------|--------|------|
| Primary | Primary Blue | White | 主要操作 |
| Secondary | Gray 100 | Gray 700 | 次要操作 |
| Ghost | Transparent | Gray 600 | 轻量操作 |
| Danger | Error | White | 危险操作 |

### 卡片

- 背景：White
- 边框：Gray 200, 1px
- 圆角：md (8px)
- 内边距：4 (16px)
- 阴影：md

### 输入框

- 背景：White
- 边框：Gray 300, 1px
- 圆角：sm (4px)
- 内边距：3 (12px) 垂直，4 (16px) 水平
- 焦点边框：Primary Blue, 2px

### 新闻卡片

- 背景：White
- 边框：Gray 200, 1px
- 圆角：md (8px)
- 内边距：4 (16px)
- 悬停阴影：lg

---

## 📱 响应式断点

| 名称 | 最小宽度 | 用途 |
|------|----------|------|
| sm | 640px | 大手机 |
| md | 768px | 平板 |
| lg | 1024px | 小屏电脑 |
| xl | 1280px | 标准电脑 |
| 2xl | 1536px | 大屏电脑 |

---

## ♿ 无障碍要求

### 色彩对比度

- 正常文本：至少 **4.5:1**
- 大文本 (18px+): 至少 **3:1**
- UI 组件：至少 **3:1**

### 键盘导航

- 所有交互元素可聚焦
- 焦点状态清晰可见（2px Primary Blue 边框）
- 逻辑的 Tab 顺序

### 屏幕阅读器

- 图片有 alt 文本
- 图标有 aria-label
- 表单有 label

---

## 🎨 Figma 设计文件

### 主设计文件

📎 **Figma 链接**: [WRHITW Design System](https://www.figma.com/file/TODO_CREATE_LATER)

*（Figma 文件待创建，链接稍后更新）*

### 文件结构

```
WRHITW Design System
├── 📄 Cover (封面)
├── 📚 Design System (设计系统)
│   ├── Colors (色彩)
│   ├── Typography (字体)
│   ├── Spacing (间距)
│   ├── Components (组件)
│   └── Icons (图标)
├── 📱 Pages (页面设计)
│   ├── Home (首页)
│   ├── Event List (事件列表)
│   ├── Event Detail (事件详情)
│   └── Search (搜索)
└── 🔧 Components (组件库)
    ├── Buttons (按钮)
    ├── Cards (卡片)
    ├── Inputs (输入框)
    └── Navigation (导航)
```

---

## 📚 参考资源

### 设计系统参考
- [Material Design](https://material.io/design)
- [Apple HIG](https://developer.apple.com/design/human-interface-guidelines)
- [Carbon Design System](https://carbondesignsystem.com)

### 灵感来源
- [Ground News](https://ground.news) - 多视角新闻排版
- [Reuters](https://www.reuters.com) - 专业新闻网站
- [The Verge](https://www.theverge.com) - 现代媒体设计
- [Medium](https://medium.com) - 阅读体验优化

---

## 🔄 更新记录

| 日期 | 版本 | 更新内容 | 作者 |
|------|------|----------|------|
| 2026-03-04 | v1.0 | 初始版本 | Design Bot |

---

**最后更新**: 2026-03-04

**状态**: 🟡 进行中 - Figma 文件待创建
