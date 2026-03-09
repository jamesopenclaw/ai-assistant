# 🎨 小优 AI 助手 - 设计规范文档

> UI 角色输出 | 日期：2026-03-09

---

## ⚠️ 重要说明

**项目当前状态**：目前使用的是**自定义 CSS**，而非 Ant Design Pro。

如果计划迁移到 Ant Design Pro，请参考以下规范；如果继续使用自定义样式，当前设计已具备良好的视觉一致性。

---

## 1️⃣ Design Token 定制需求

### 色彩系统

| Token | 当前值 | 用途 | 建议 Ant Design Token |
|-------|--------|------|----------------------|
| `colorPrimary` | `#FF6B35` | 主色（按钮、Logo高亮、active态） | `colorPrimary: '#FF6B35'` |
| `colorPrimaryHover` | `#E55A2B` | 主色 Hover 态 | `colorPrimaryHover: '#E55A2B'` |
| `colorBgContainer` | `#FFFFFF` | 卡片、Header 背景 | `colorBgContainer: '#FFFFFF'` |
| `colorBgLayout` | `#F5F5F7` | 页面主背景 | `colorBgLayout: '#F5F5F7'` |
| `colorBgSidebar` | `#1A1A2E` | 侧边栏背景 | `colorBgSidebar: '#1A1A2E'` |
| `colorBorder` | `#E5E7EB` | 输入框、分割线边框 | `colorBorder: '#E5E7EB'` |
| `colorText` | `#1A1A2E` | 主标题 | `colorText: '#1A1A2E'` |
| `colorTextSecondary` | `#374151` | 次级文字 | `colorTextSecondary: '#374151'` |
| `colorTextTertiary` | `#9CA3AF` | 辅助文字、占位符 | `colorTextTertiary: '#9CA3AF'` |

### 圆角系统

| Token | 当前值 | 组件 |
|-------|--------|------|
| `borderRadius` | `16px` | 登录/注册卡片 |
| `borderRadiusLG` | `10px` | 输入框 |
| `borderRadiusSM` | `8px` | 侧边栏导航项 |
| `borderRadiusXS` | `6px` | 按钮 |

### 间距系统

| Token | 当前值 | 用途 |
|-------|--------|------|
| `paddingLG` | `40px` | 登录注册卡片内边距 |
| `padding` | `24px 16px` | 侧边栏内边距 |
| `paddingSM` | `12px 16px` | 导航项内边距 |
| `marginLG` | `32px` | Logo 与内容区间距 |
| `gapSM` | `8px` | 元素间隙 |
| `gapMD` | `12px` | 元素间隙 |
| `gapLG` | `16px` | 元素间隙 |

### 字体系统

| Token | 当前值 | 用途 |
|-------|--------|------|
| `fontFamily` | `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` | 全局字体 |
| `fontSize` | `15px` | 正文 |
| `fontSizeSM` | `14px` | 次级文字 |
| `fontSizeLG` | `18px` | 页面标题 |
| `fontSizeXL` | `20px` | Logo |
| `fontSizeXXL` | `28px` | 登录页 Logo |
| `fontWeight` | `400` | 正文 |
| `fontWeightMedium` | `500` | 标签 |
| `fontWeightBold` | `700` | 标题、Logo |

---

## 2️⃣ 组件交互规范

### 按钮 (Button)

| 状态 | 样式 |
|------|------|
| Default | `background: #FF6B35; color: white; border-radius: 6px` |
| Hover | `background: #E55A2B` |
| Active | `background: #CC4F25` |
| Disabled | `opacity: 0.5; cursor: not-allowed` |

**过渡动画**: `transition: all 0.2s`

### 输入框 (Input)

| 状态 | 样式 |
|------|------|
| Default | `border: 2px solid #E5E7EB; border-radius: 10px` |
| Focus | `border-color: #FF6B35; box-shadow: 0 0 0 3px rgba(255,107,53,0.1)` |
| Hover | `border-color: #D1D5DB` |

### 导航项 (Nav Item)

| 状态 | 样式 |
|------|------|
| Default | `background: transparent` |
| Hover | `background: rgba(255,255,255,0.1)` |
| Active | `background: #FF6B35` |

**过渡动画**: `transition: background 0.2s`

### 卡片 (Card)

- 圆角: `16px`
- 阴影: `box-shadow: 0 20px 60px rgba(0,0,0,0.3)` (登录页)
- 白色背景: `#FFFFFF`
- 内边距: `40px`

---

## 3️⃣ 视觉一致性审核

### ✅ 已确认一致

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 主色调 | ✅ | `#FF6B35` 在所有页面一致使用 |
| 侧边栏样式 | ✅ | chat.html、cicd.html 侧边栏结构一致 |
| 字体族 | ✅ | 统一使用系统字体栈 |
| 导航交互 | ✅ | hover/active 效果一致 |
| 按钮样式 | ✅ | 主按钮使用相同样式 |
| 登录/注册页 | ✅ | 视觉风格统一 |

### ⚠️ 需关注

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 页面背景色 | ✅ | 统一使用 `#F5F5F7` |
| Header 高度 | ✅ | 统一 `padding: 16px 32px` |
| 侧边栏宽度 | ✅ | 统一 `width: 260px` |

---

## 4️⃣ 设计还原度检查清单

### 页面结构

- [ ] 侧边栏宽度为 260px
- [ ] 侧边栏背景色 #1A1A2E
- [ ] 顶部 Header 白色背景，有底边分隔线
- [ ] 主内容区背景 #F5F5F7

### 颜色还原

- [ ] 主色 #FF6B35 应用于：Logo 强调、导航 Active 态、按钮
- [ ] 输入框边框 #E5E7EB
- [ ] 文字颜色层级：#1A1A2E（标题）、#374151（正文）、#9CA3AF（辅助）

### 圆角还原

- [ ] 卡片圆角 16px
- [ ] 输入框圆角 10px
- [ ] 按钮圆角 6px
- [ ] 导航项圆角 8px

### 交互还原

- [ ] 按钮 Hover 变色 #E55A2B
- [ ] 输入框 Focus 有橙色边框 + 阴影
- [ ] 导航项 Hover 有半透明背景
- [ ] 所有过渡动画时长 0.2s

### 响应式

- [ ] 登录/注册卡片最大宽度 420px
- [ ] 页面在移动端正常显示

---

## 📋 后续建议

1. **如需迁移 Ant Design Pro**：建议创建 `ConfigProvider` 主题配置，覆盖上述 Token 值
2. **如继续维护自定义样式**：建议抽离 CSS 变量，便于统一管理
3. **组件库备选**：若需要更多企业级组件，考虑使用 `@ant-design/pro-components`

---

*UI 角色输出完毕，等待 PM 审核*
