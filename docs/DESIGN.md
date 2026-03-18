# WRHITW Design System

🎨 **Neutral, Professional, Inclusive** - Designed for multi-perspective news

---

## 📐 Design Principles

1. **Neutrality** - Do not use color to guide emotions; let users judge for themselves
2. **Transparency** - Information sources are clearly visible
3. **Readability** - Content-first, comfortable for extended reading
4. **Inclusivity** - Consider diverse cultural backgrounds
5. **Accessibility** - WCAG 2.1 AA standards

---

## 🎨 Color System

### Primary Colors

| Name | Value | Usage |
|------|-------|-------|
| Primary Blue | `#2563EB` | Primary buttons, links, emphasis |
| Neutral Gray | `#6B7280` | Secondary text, borders |

### Functional Colors

| Name | Value | Usage |
|------|-------|-------|
| Success | `#10B981` | Success state |
| Warning | `#F59E0B` | Warning alerts |
| Error | `#EF4444` | Error state |
| Info | `#3B82F6` | Informational alerts |

### Neutral Colors

| Name | Value | Usage |
|------|-------|-------|
| White | `#FFFFFF` | Background |
| Gray 50 | `#F9FAFB` | Secondary background |
| Gray 100 | `#F3F4F6` | Dividers |
| Gray 200 | `#E5E7EB` | Borders |
| Gray 300 | `#D1D5DB` | Disabled borders |
| Gray 400 | `#9CA3AF` | Placeholder text |
| Gray 500 | `#6B7280` | Secondary text |
| Gray 600 | `#4B5563` | Body text |
| Gray 700 | `#374151` | Primary text |
| Gray 800 | `#1F2937` | Headings |
| Gray 900 | `#111827` | Important headings |

### Bias Label Colors

| Stance | Value | Usage |
|--------|-------|-------|
| Left | `#3B82F6` | Left-leaning media indicator |
| Center | `#10B981` | Centrist media indicator |
| Right | `#EF4444` | Right-leaning media indicator |

---

## 📝 Typography System

### Font Families

```css
/* English fonts */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Chinese fonts */
--font-sans-cn: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;

/* Monospace fonts */
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

### Font Size Scale

| Name | Size | Line Height | Usage |
|------|------|-------------|-------|
| xs | 12px | 16px | Auxiliary info, labels |
| sm | 14px | 20px | Secondary text, captions |
| base | 16px | 24px | Body text |
| lg | 18px | 28px | Emphasis text |
| xl | 20px | 28px | Subheadings |
| 2xl | 24px | 32px | Medium headings |
| 3xl | 30px | 36px | Large headings |
| 4xl | 36px | 40px | Page titles |

### Font Weights

| Name | Value | Usage |
|------|-------|-------|
| Regular | 400 | Body text |
| Medium | 500 | Emphasis text |
| Semibold | 600 | Subheadings |
| Bold | 700 | Large headings |

---

## 📏 Spacing System

Spacing system based on an **8px grid**:

| Name | Value | Usage |
|------|-------|-------|
| 1 | 4px | Minimum spacing (icons and text) |
| 2 | 8px | Compact spacing |
| 3 | 12px | Small spacing |
| 4 | 16px | Standard spacing |
| 6 | 24px | Medium spacing |
| 8 | 32px | Large spacing |
| 12 | 48px | Extra-large spacing |
| 16 | 64px | Section spacing |

---

## 🔲 Border Radius

| Name | Value | Usage |
|------|-------|-------|
| sm | 4px | Buttons, input fields |
| md | 8px | Cards, dropdown menus |
| lg | 12px | Modals, large cards |
| xl | 16px | Special containers |
| full | 9999px | Avatars, badges |

---

## 🌑 Shadow Specifications

| Name | Value | Usage |
|------|-------|-------|
| sm | `0 1px 2px 0 rgba(0, 0, 0, 0.05)` | Hover state |
| md | `0 4px 6px -1px rgba(0, 0, 0, 0.07)` | Cards |
| lg | `0 10px 15px -3px rgba(0, 0, 0, 0.1)` | Dropdown menus |
| xl | `0 20px 25px -5px rgba(0, 0, 0, 0.1)` | Modals |
| 2xl | `0 25px 50px -12px rgba(0, 0, 0, 0.25)` | Popovers |

---

## 🧩 Component Specifications

### Buttons

| Type | Background | Text Color | Usage |
|------|------------|------------|-------|
| Primary | Primary Blue | White | Primary actions |
| Secondary | Gray 100 | Gray 700 | Secondary actions |
| Ghost | Transparent | Gray 600 | Lightweight actions |
| Danger | Error | White | Destructive actions |

### Cards

- Background: White
- Border: Gray 200, 1px
- Border Radius: md (8px)
- Padding: 4 (16px)
- Shadow: md

### Input Fields

- Background: White
- Border: Gray 300, 1px
- Border Radius: sm (4px)
- Padding: 3 (12px) vertical, 4 (16px) horizontal
- Focus border: Primary Blue, 2px

### News Cards

- Background: White
- Border: Gray 200, 1px
- Border Radius: md (8px)
- Padding: 4 (16px)
- Hover shadow: lg

---

## 📱 Responsive Breakpoints

| Name | Min Width | Usage |
|------|-----------|-------|
| sm | 640px | Large phones |
| md | 768px | Tablets |
| lg | 1024px | Small laptops |
| xl | 1280px | Standard desktops |
| 2xl | 1536px | Large screens |

---

## ♿ Accessibility Requirements

### Color Contrast

- Normal text: at least **4.5:1**
- Large text (18px+): at least **3:1**
- UI components: at least **3:1**

### Keyboard Navigation

- All interactive elements are focusable
- Focus state is clearly visible (2px Primary Blue border)
- Logical Tab order

### Screen Readers

- Images have alt text
- Icons have aria-label
- Forms have labels

---

## 🎨 Figma Design Files

### Main Design File

📎 **Figma Link**: [WRHITW Design System](https://www.figma.com/file/TODO_CREATE_LATER)

*(Figma file to be created; link will be updated later)*

### File Structure

```
WRHITW Design System
├── 📄 Cover
├── 📚 Design System
│   ├── Colors
│   ├── Typography
│   ├── Spacing
│   ├── Components
│   └── Icons
├── 📱 Pages
│   ├── Home
│   ├── Event List
│   ├── Event Detail
│   └── Search
└── 🔧 Components
    ├── Buttons
    ├── Cards
    ├── Inputs
    └── Navigation
```

---

## 📚 References

### Design System References
- [Material Design](https://material.io/design)
- [Apple HIG](https://developer.apple.com/design/human-interface-guidelines)
- [Carbon Design System](https://carbondesignsystem.com)

### Inspiration
- [Ground News](https://ground.news) - Multi-perspective news layout
- [Reuters](https://www.reuters.com) - Professional news website
- [The Verge](https://www.theverge.com) - Modern media design
- [Medium](https://medium.com) - Reading experience optimization

---

## 🔄 Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-03-04 | v1.0 | Initial version | Design Bot |

---

**Last Updated**: 2026-03-04

**Status**: 🟡 In Progress - Figma file pending creation
